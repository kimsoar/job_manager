import asyncio
from concurrent.futures import ThreadPoolExecutor
from utils.logger import get_logger

logger = get_logger(__name__)

class JobExecutor:
    def __init__(self, jobs):
        self.jobs = jobs
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def _run_job(self, name, func):
        logger.info(f"Starting job: {name}")
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(self.executor, func)
            logger.info(f"Finished job: {name}")
        except Exception as e:
            logger.error(f"Error in job '{name}': {e}")

    async def run_all(self):
        tasks = [self._run_job(name, func) for name, func in self.jobs]
        await asyncio.gather(*tasks)
