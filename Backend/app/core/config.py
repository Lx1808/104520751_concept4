from typing import Optional
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Virus Scanning Website"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "LINOH=921893u239OIefiowja")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库设置
    MONGO_URI: Optional[str] = os.getenv("MONGO_URI")
    DATABASE_NAME: str = "Users"
    USER_COLLECTION_NAME: str = "users"
    FILE_COLLECTION_NAME: str = "files"

    # File upload settings
    UPLOAD_DIRECTORY: str = "uploaded_files"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB

    class Config:
        env_file = ".env"


settings = Settings()

# 如果环境变量中没有设置 MONGO_URI，则使用默认值
if settings.MONGO_URI is None:
    settings.MONGO_URI = ("mongodb+srv://lx941008:lx79112661@cluster0.16uwt.mongodb.net/?retryWrites=true&w=majority"
                          "&appName=Cluster0")
