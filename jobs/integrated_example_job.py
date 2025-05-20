from manager.job_registry import job
from utils.db import with_db_select
from utils.file_output import save_result_to_file
from utils.retry import retry_async
from utils.logger import get_logger

import aiohttp

logger = get_logger(__name__)


@job(name="integrated_example")
@save_result_to_file(
    format="csv",
    fields=["id", "name", "email"],
    filename_prefix="users_export",
    append=False,
    date_partition=True
)
@with_db_select("SELECT id, name, email FROM users", single=True)
@retry_async(retries=3, delay=2, backoff=2)
async def integrated_example_job(rows):
    logger.info(f"Fetched {len(rows)} users from DB")

    # 시뮬레이션: 각 사용자 이메일을 외부 API로 인증 (재시도 적용됨)
    async with aiohttp.ClientSession() as session:
        for row in rows:
            email = row['email']
            try:
                async with session.get(f"https://api.eva.pingutil.com/email?email={email}") as resp:
                    if resp.status != 200:
                        raise Exception(f"API error: {resp.status}")
                    data = await resp.json()
                    logger.info(f"Verified email {email}: {data.get('data', {}).get('status')}")
            except Exception as e:
                logger.warning(f"Failed to verify email {email}: {e}")

    # 최종 저장용 데이터는 list of dict
    return [dict(row) for row in rows]
