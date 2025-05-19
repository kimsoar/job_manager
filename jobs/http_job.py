from manager.job_registry import job
from utils.db import with_db_save
import requests

@job(name="http")
@with_db_save("http_data")
def http_job():
    res = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    res.raise_for_status()
    return res.json()
