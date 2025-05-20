from manager.job_registry import job
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

@job(name="test")
async def dummy_job():
    try:
        for i in range(100000):
            await asyncio.sleep(1)
            logger.info(f"test job count: {i}")
    except asyncio.CancelledError:
        logger.warning("test job cancelled.")
        raise
