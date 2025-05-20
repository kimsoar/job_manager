from manager.job_registry import job
import time
from utils.logger import get_logger

logger = get_logger(__name__)

@job(name="long_task")
async def long_running_job():
    for i in range(10):
        time.sleep(1)
        logger.info(f"[long_task] Iteration: {i}")
