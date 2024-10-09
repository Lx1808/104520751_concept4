import os
import shutil
from typing import List, Dict
from datetime import date, datetime, timedelta
import pytz
from fastapi import UploadFile
from ..core.database import files
from bson import ObjectId

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    file_location = os.path.join(destination, upload_file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(upload_file.file, file_object)
    return file_location

def is_valid_file_type(filename: str, allowed_types: list) -> bool:
    return any(filename.lower().endswith(file_type) for file_type in allowed_types)

def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)

def update_scan_result(file_id: str, scan_results: List[Dict[str, any]], scan_status: str):
    # 更新数据库中的扫描结果
    files.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {"scan_results": scan_results, "scan_status": scan_status}}
    )


async def get_daily_upload_counts(start_date: date, end_date: date) -> dict:
    MELBOURNE_TZ = pytz.timezone('Australia/Melbourne')

    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=MELBOURNE_TZ)
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=MELBOURNE_TZ)

    pipeline = [
        {
            "$match": {
                "upload_time": {
                    "$gte": start_datetime.isoformat(),
                    "$lte": end_datetime.isoformat()
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$substr": ["$upload_time", 0, 10]  # Extract YYYY-MM-DD part
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    results = list(files.aggregate(pipeline))

    all_dates = {(start_date + timedelta(days=x)).strftime("%Y-%m-%d"): 0
                 for x in range((end_date - start_date).days + 1)}

    for result in results:
        all_dates[result["_id"]] = result["count"]

    return all_dates
