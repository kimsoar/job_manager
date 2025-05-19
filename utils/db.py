import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
from config import DB_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True

    def save(self, table, data):
        with self.conn.cursor() as cur:
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
            cur.execute(sql, list(data.values()))

db_instance = PostgresDB()

def with_db_save(table):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result:
                try:
                    db_instance.save(table, result)
                    logger.info(f"Saved to DB table '{table}': {result}")
                except Exception as e:
                    logger.error(f"DB Save Error: {e}")
            return result
        return wrapper
    return decorator


def with_db_select(query, args=(), fetch='all', as_dict=False):
    """
    query: SQL 쿼리 문자열
    args: 튜플 형태의 파라미터
    fetch: 'all' | 'one'
    as_dict: True면 dict형으로 반환 (RealDictCursor 사용)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            cursor_factory = RealDictCursor if as_dict else None
            try:
                with db_instance.conn.cursor(cursor_factory=cursor_factory) as cur:
                    cur.execute(query, args)
                    if fetch == 'one':
                        result = cur.fetchone()
                    else:
                        result = cur.fetchall()
                    logger.info(f"DB Select success: {query}")
            except Exception as e:
                logger.error(f"DB Select error: {e}")
                result = None

            return func(result, *func_args, **func_kwargs)
        return wrapper
    return decorator
