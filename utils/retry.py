import asyncio
import functools
import random
from utils.logger import get_logger

logger = get_logger(__name__)

def retry_async(retries=3, delay=2, backoff=2, jitter=True, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == retries:
                        logger.error(f"Retry failed after {retries} attempts: {e}")
                        raise
                    sleep_time = current_delay + (random.uniform(0, 1) if jitter else 0)
                    logger.warning(f"Retry {attempt}/{retries} failed. Retrying in {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                    current_delay *= backoff
        return wrapper
    return decorator
