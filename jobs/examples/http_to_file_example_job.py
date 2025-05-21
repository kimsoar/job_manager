from manager.job_registry import job
from utils.file_output import save_result_to_file
from utils.logger import get_logger

import aiohttp

logger = get_logger(__name__)

@job(name="http_to_file_example")
@save_result_to_file(
    format="json",
    fields=["id", "title"],
    filename_prefix="http_log",
    append=True,
    date_partition=True
)
async def http_append_job():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://jsonplaceholder.typicode.com/posts/1") as resp:
                if resp.status != 200:
                    raise Exception(f"API error: {resp.status}")
                data = await resp.json()
                return data
        except Exception as e:
            logger.warning(f"Failed to fetch data: {e}")
            
