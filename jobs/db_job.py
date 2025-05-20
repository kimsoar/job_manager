from manager.job_registry import job
from utils.db import with_db_select
import requests

@job(name="print_users")
@with_db_select("SELECT id, name FROM users")
async def print_users(rows):
    for row in rows:
        print(dict(row))