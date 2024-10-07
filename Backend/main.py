from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.file_upload.routes import router as file_upload_router
from app.core.config import settings
from app.core.database import close_mongo_connection

app = FastAPI(title=settings.PROJECT_NAME)

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(file_upload_router, prefix="/file", tags=["file"])

@app.on_event("shutdown")
def shutdown_event():
    close_mongo_connection()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)