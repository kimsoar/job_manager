import asyncpg
from config import DB_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class AsyncPostgresDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(**DB_CONFIG)
        logger.info("PostgreSQL connection pool created")

    async def save(self, table, data):
        async with self.pool.acquire() as conn:
            columns = ', '.join(data.keys())
            values = ', '.join(f"${i+1}" for i in range(len(data)))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            await conn.execute(sql, *data.values())
            logger.info(f"Saved to DB table '{table}': {data}")

    async def update(self, table, data, where):
        async with self.pool.acquire() as conn:
            set_clause = ', '.join(f"{k} = ${i+1}" for i, k in enumerate(data.keys()))
            where_offset = len(data)
            where_clause = ' AND '.join(
                f"{k} = ${i+1+where_offset}" for i, k in enumerate(where.keys())
            )
            values = list(data.values()) + list(where.values())
            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            await conn.execute(sql, *values)
            logger.info(f"Updated DB table '{table}': SET {data} WHERE {where}")

    async def upsert(self, table, data, conflict_keys):
        async with self.pool.acquire() as conn:
            columns = ', '.join(data.keys())
            values = ', '.join(f"${i+1}" for i in range(len(data)))
            update_clause = ', '.join(f"{k}=EXCLUDED.{k}" for k in data.keys() if k not in conflict_keys)
            conflict_clause = ', '.join(conflict_keys)
            sql = (
                f"INSERT INTO {table} ({columns}) VALUES ({values}) "
                f"ON CONFLICT ({conflict_clause}) DO UPDATE SET {update_clause}"
            )
            await conn.execute(sql, *data.values())
            logger.info(f"Upserted DB table '{table}': {data}")

    async def bulk_save(self, table, data_list):
        if not data_list:
            return
        async with self.pool.acquire() as conn:
            columns = ', '.join(data_list[0].keys())
            values_template = ', '.join(f"${i+1}" for i in range(len(data_list[0])))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values_template})"
            await conn.executemany(sql, [tuple(d.values()) for d in data_list])
            logger.info(f"Bulk inserted into '{table}': {len(data_list)} rows")

    async def fetch(self, query, *args, single=False):
        async with self.pool.acquire() as conn:
            try:
                if single:
                    return await conn.fetchrow(query, *args)
                return await conn.fetch(query, *args)
            except Exception as e:
                logger.error(f"Fetch Error: {e}")
                raise

# 전역 인스턴스
db_instance = AsyncPostgresDB()

def with_db_save(table):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if result:
                try:
                    await db_instance.save(table, result)
                except Exception as e:
                    logger.error(f"DB Save Error: {e}")
            return result
        return wrapper
    return decorator

def with_db_update(table):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if result and isinstance(result, dict):
                data = result.get("data")
                where = result.get("where")
                if data and where:
                    try:
                        await db_instance.update(table, data, where)
                    except Exception as e:
                        logger.error(f"DB Update Error: {e}")
            return result
        return wrapper
    return decorator

def with_db_upsert(table, conflict_keys):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if result:
                try:
                    await db_instance.upsert(table, result, conflict_keys)
                except Exception as e:
                    logger.error(f"DB Upsert Error: {e}")
            return result
        return wrapper
    return decorator

def with_db_select(query, single=False):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await db_instance.fetch(query, single=single)
                return await func(result, *args, **kwargs)
            except Exception as e:
                logger.error(f"DB Select Error: {e}")
                raise
        return wrapper
    return decorator
