import os
from dotenv import load_dotenv

# 기본 환경 설정 (없으면 development)
ENV_MODE = os.getenv("ENV", "development")
dotenv_path = f".env.{ENV_MODE}"

# 해당 환경 파일 로드
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(f"{dotenv_path} not found")

DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT", 5432)),
    'database': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD")
}