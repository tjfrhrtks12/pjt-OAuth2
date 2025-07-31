from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config import get_db, engine, Base
from models import User
from auth import router as auth_router
from chatbot import router as chatbot_router
import uvicorn

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

@app.get("/api/debug/users")
async def debug_users(db: Session = Depends(get_db)):
    """DB에 있는 모든 사용자 데이터를 확인하는 디버그 엔드포인트"""
    try:
        users = db.query(User).all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "google_id": user.google_id,
                "is_active": user.is_active,
                "created_at": user.created_at
            })
        return {
            "count": len(user_list),
            "users": user_list
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 