import asyncio
import signal
import sys
from utils.logger import get_logger

logger = get_logger(__name__)

class JobExecutor:
    def __init__(self, jobs):
        self.jobs = jobs
        self.tasks = []
        self.shutdown_event = asyncio.Event()

    async def run_all(self):
        # Windows에서 호환 가능한 signal 처리
        self._setup_signal_handlers()

        self.tasks = [asyncio.create_task(self._run_job(name, func)) for name, func in self.jobs]

        # shutdown 이벤트 대기와 job 실행을 동시에 처리
        await asyncio.wait(
            [*self.tasks, self.shutdown_event.wait()],
            return_when=asyncio.FIRST_COMPLETED
        )

        if self.shutdown_event.is_set():
            logger.warning("Shutdown event set. Cancelling all jobs...")
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
            logger.info("All jobs cancelled due to shutdown.")

    async def _run_job(self, name, func):
        logger.info(f"Starting job: {name}")
        try:
            await func()
            logger.info(f"Finished job: {name}")
        except asyncio.CancelledError:
            logger.warning(f"Job cancelled: {name}")
        except Exception as e:
            logger.error(f"Error in job '{name}': {e}")

    def _setup_signal_handlers(self):
        def handler(sig, frame):
            logger.warning(f"Received signal {sig}. Initiating shutdown...")
            self.shutdown_event.set()

        # SIGINT (Ctrl+C)와 SIGTERM 모두에 대해 핸들러 설정
        signal.signal(signal.SIGINT, handler)
        if sys.platform != "win32":  # Windows에서는 SIGTERM 지원 안됨
            signal.signal(signal.SIGTERM, handler)
