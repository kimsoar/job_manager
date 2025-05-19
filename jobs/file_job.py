from manager.job_registry import job
from utils.db import with_db_save

@job(name="file")
@with_db_save("file_data")
def file_job():
    with open("sample.txt", "r") as f:
        content = f.read()
        return {"filename": "sample.txt", "content": content.upper()}
