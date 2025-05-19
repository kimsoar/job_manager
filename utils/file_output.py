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
        def wrapper(*args, **kwargs):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            result = func(*args, **kwargs)

            if filename:
                filepath = os.path.join(OUTPUT_DIR, filename)
            else:
                date_str = datetime.now().strftime("%Y-%m-%d") if date_partition else datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{filename_prefix}_{date_str}.{format}"
                filepath = os.path.join(OUTPUT_DIR, fname)

            try:
                _save_data(filepath, result, format=format, fields=fields, append=append)
                logger.info(f"Saved result to file: {filepath}")
                return {"file_path": filepath, "status": "saved"}
            except Exception as e:
                logger.error(f"Failed to save result to file: {e}")
                raise
        return wrapper
    return decorator

def _save_data(filepath, data, format, fields=None, append=False):
    if format == "json":
        existing = []
        if append and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = [existing]
                except Exception:
                    existing = []
        if fields:
            if isinstance(data, list):
                data = [{k: d.get(k) for k in fields} for d in data]
            elif isinstance(data, dict):
                data = {k: data.get(k) for k in fields}
        merged = existing + (data if isinstance(data, list) else [data])
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

    elif format == "txt":
        with open(filepath, "a" if append else "w", encoding="utf-8") as f:
            f.write(str(data) + "\n")

    elif format == "csv":
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
            raise ValueError("CSV format requires a list of dicts")

        fieldnames = fields or data[0].keys()
        write_header = not os.path.exists(filepath) or not append

        with open(filepath, "a", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(data)
    else:
        raise ValueError(f"Unsupported format: {format}")
