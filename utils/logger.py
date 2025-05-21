from config import ENV_MODE

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def get_logger(name):
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join("logs", ENV_MODE, current_date)
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "job_manager.log")

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s')

        # 최대 10MB, 최대 5개까지 롤링
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
