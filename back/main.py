from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config import get_db, engine, Base
from models import User
from auth import router as auth_router
from chatbot import router as chatbot_router
import uvicorn
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Last Project API",
    description="FastAPI with MySQL Backend - User Authentication",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(chatbot_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Last Project API!"}

@app.get("/health")
async def health_check():
    try:
        return {"status": "healthy", "message": "Server is running"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/version")
async def get_version():
    return {"version": "1.0.0", "framework": "FastAPI"}

@app.get("/api/status")
async def get_system_status():
    """시스템 전체 상태 확인"""
    from database_service import DatabaseService
    
    db_status = DatabaseService.get_database_info()
    
    return {
        "database": db_status,
        "oauth": {
            "provider": "google",
            "status": "ready",
            "client_id": os.getenv("GOOGLE_CLIENT_ID", "설정되지 않음")
        },
        "ai": {
            "status": "connected",
            "model": "gpt-4o"
        },
        "server": {
            "status": "running",
            "framework": "FastAPI"
        }
    }

@app.get("/api/oauth/google/url")
async def get_google_oauth_url():
    """Google OAuth2 로그인 URL 반환"""
    from oauth_service import OAuthService
    auth_url = OAuthService.get_google_auth_url()
    return {"auth_url": auth_url}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 