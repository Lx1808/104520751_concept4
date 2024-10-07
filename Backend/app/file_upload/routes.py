from fastapi import APIRouter, File, UploadFile, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from .utils import save_upload_file
from ..auth.utils import get_current_user
from ..ml_model.scanner import scan_file
from ..core.database import files
import os
from bson import ObjectId
from datetime import datetime
import pytz


router = APIRouter()


UPLOAD_DIRECTORY = "uploaded_files"

MELBOURNE_TZ = pytz.timezone('Australia/Melbourne')

def serialize_document(doc):
    """
    序列化 MongoDB 文档，处理 ObjectId 和 datetime 对象
    """
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_document(v) for v in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc

@router.post("/upload/")
async def create_upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        current_user: dict = Depends(get_current_user)
):
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    user_upload_dir = os.path.join(UPLOAD_DIRECTORY, str(current_user['_id']))
    if not os.path.exists(user_upload_dir):
        os.makedirs(user_upload_dir)

    file_location = await save_upload_file(file, user_upload_dir)

    melbourne_time = datetime.now(MELBOURNE_TZ).isoformat()

    # Create a file record in the database
    file_id = files.insert_one({
        "filename": file.filename,
        "location": file_location,
        "user_id": current_user['_id'],
        "upload_time": melbourne_time,
        "scan_status": "pending"
    }).inserted_id

    # Run file scan as a background task
    background_tasks.add_task(scan_file, file_location, str(file_id))

    return JSONResponse(content={
        "file_id": str(file_id),
        "filename": file.filename,
        "saved_location": file_location,
        "scan_status": "pending"
    }, status_code=200)

@router.get("/scan-result/{file_id}")
async def get_scan_result(file_id: str, current_user: dict = Depends(get_current_user)):
    file = files.find_one({"_id": ObjectId(file_id), "user_id": current_user['_id']})
    if not file:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    return JSONResponse(content={
        "filename": file['filename'],
        "scan_status": file['scan_status'],
        "scan_results": file.get('scan_results')
    }, status_code=200)


@router.get("/user-files/")
async def get_user_files(current_user: dict = Depends(get_current_user)):
    user_files = list(files.find({"user_id": current_user['_id']}))

    # 序列化文件数据
    serialized_files = [serialize_document(file) for file in user_files]

    return JSONResponse(content={
        "total_files": len(serialized_files),
        "files": serialized_files
    }, status_code=200)

