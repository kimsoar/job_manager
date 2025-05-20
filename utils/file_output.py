import aiofiles
import aiofiles.os
import os
import json
import csv
from functools import wraps
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)
OUTPUT_DIR = "output"

def save_result_to_file(format="json", fields=None, filename=None, filename_prefix="result", append=False, date_partition=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            result = await func(*args, **kwargs)

            if filename:
                filepath = os.path.join(OUTPUT_DIR, filename)
            else:
                date_str = datetime.now().strftime("%Y-%m-%d") if date_partition else datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{filename_prefix}_{date_str}.{format}"
                filepath = os.path.join(OUTPUT_DIR, fname)

            try:
                await _save_data(filepath, result, format=format, fields=fields, append=append)
                logger.info(f"Saved result to file: {filepath}")
                return {"file_path": filepath, "status": "saved"}
            except Exception as e:
                logger.error(f"Failed to save result to file: {e}")
                raise
        return wrapper
    return decorator

async def _save_data(filepath, data, format, fields=None, append=False):
    if format == "json":
        existing = []
        if append and os.path.exists(filepath):
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                try:
                    content = await f.read()
                    existing = json.loads(content)
                    if not isinstance(existing, list):
                        existing = [existing]
                except:
                    existing = []
        if fields:
            data = [{k: d.get(k) for k in fields} for d in data] if isinstance(data, list) else {k: data.get(k) for k in fields}
        merged = existing + (data if isinstance(data, list) else [data])
        async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
            await f.write(json.dumps(merged, ensure_ascii=False, indent=2))

    elif format == "txt":
        async with aiofiles.open(filepath, "a" if append else "w", encoding="utf-8") as f:
            await f.write(str(data) + "\n")

    elif format == "csv":
        mode = "a" if append and os.path.exists(filepath) else "w"
        async with aiofiles.open(filepath, mode, encoding="utf-8", newline="") as f:
            if isinstance(data, dict):
                data = [data]
            if not data:
                return
            fieldnames = fields if fields else data[0].keys()
            writer = csv.DictWriter(await f.__aenter__(), fieldnames=fieldnames)
            if mode == "w":
                await f.write(",".join(fieldnames) + "\n")
            for row in data:
                line = ",".join(str(row.get(field, "")) for field in fieldnames) + "\n"
                await f.write(line)
    else:
        raise ValueError(f"Unsupported format: {format}")
