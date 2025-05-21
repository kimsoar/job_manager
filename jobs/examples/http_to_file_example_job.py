from manager.job_registry import job
from utils.file_output import save_result_to_file
import requests

@job(name="http_to_file_example")
@save_result_to_file(
    format="json",
    fields=["id", "title"],
    filename_prefix="http_log",
    append=True,
    date_partition=True
)
def http_append_job():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()
