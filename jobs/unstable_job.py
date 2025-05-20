from manager.job_registry import job
from utils.file_output import save_result_to_file
import requests
from utils.retry import retry_async
import random

@job(name="unstable_task")
@retry_async(retries=5, delay=1)
async def unstable_job():
    if random.random() < 0.7:
        raise ValueError("Random failure!")
    return {"result": "success"}
