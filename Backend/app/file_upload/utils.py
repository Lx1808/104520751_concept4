import os
import shutil
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

def update_scan_result(file_id: str, scan_result: dict):
    files.update_one(
        {"_id": ObjectId(file_id)},
        {
            "$set": {
                "scan_status": "completed",
                "scan_results": scan_result
            }
        }
    )
