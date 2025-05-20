from manager.job_registry import job
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

@job(name="dummy")
async def dummy_job():
    try:
        for i in range(100000):
            await asyncio.sleep(1)
            logger.info(f"Dummy job count: {i}")
    except asyncio.CancelledError:
        logger.warning("Dummy job cancelled.")
        raise
