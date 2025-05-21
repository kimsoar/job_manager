from manager.job_registry import job
from utils.file_output import save_result_to_file
from utils.retry import retry_async

import requests
import random

@job(name="retry_example")
@retry_async(retries=5, delay=1)
async def unstable_job():
    if random.random() < 0.7:
        raise ValueError("Random failure!")
    return {"result": "success"}
