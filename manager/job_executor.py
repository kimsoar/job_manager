import asyncio
import signal
from utils.logger import get_logger

logger = get_logger(__name__)

class JobExecutor:
    def __init__(self, jobs):
        self.jobs = jobs
        self.tasks = []

    async def run_all(self):
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.shutdown(s)))

        self.tasks = [asyncio.create_task(self._run_job(name, func)) for name, func in self.jobs]

        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def _run_job(self, name, func):
        logger.info(f"Starting job: {name}")
        try:
            await func()
            logger.info(f"Finished job: {name}")
        except asyncio.CancelledError:
            logger.warning(f"Job cancelled: {name}")
        except Exception as e:
            logger.error(f"Error in job '{name}': {e}")

    async def shutdown(self, sig):
        logger.warning(f"Received exit signal {sig.name}... cancelling jobs.")
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("All jobs cancelled.")
        asyncio.get_running_loop().stop()
