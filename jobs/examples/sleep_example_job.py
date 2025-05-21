from manager.job_registry import job
from utils.logger import get_logger

import asyncio

logger = get_logger(__name__)

@job(name="sleep_example_job")
async def dummy_job():
    try:
        for i in range(1000):
            await asyncio.sleep(0.5)
            logger.info(f"Dummy job count: {i}")
    except asyncio.CancelledError:
        logger.warning("Dummy job cancelled.")
        raise
