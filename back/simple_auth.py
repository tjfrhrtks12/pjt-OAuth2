from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from config import get_db
from models import User
import hashlib
import os
from datetime import datetime, timedelta

router = APIRouter()

class LoginRequest(BaseModel):
    login_id: str
    login_pw: str

class UserResponse(BaseModel):
    id: int
    login_id: str
    name: str
    is_active: bool

def hash_password(login_pw: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(login_pw.encode()).hexdigest()

def create_default_users(db: Session):
    """기본 사용자 생성"""
    try:
        # 기본 교사 계정들 생성
        default_users = [
            {
                "login_id": "teacher1",
                "login_pw": "password123",
                "name": "김선생님"
            },
            {
                "login_id": "teacher2", 
                "login_pw": "password123",
                "name": "이선생님"
            },
            {
                "login_id": "teacher3",
                "login_pw": "password123", 
                "name": "박선생님"
            }
        ]
        
        for user_data in default_users:
            # 이미 존재하는지 확인
            existing_user = db.query(User).filter(User.login_id == user_data["login_id"]).first()
            if not existing_user:
                hashed_password = hash_password(user_data["login_pw"])
                new_user = User(
                    login_id=user_data["login_id"],
                    name=user_data["name"],
                    login_pw=hashed_password,
                    is_active=True
                )
                db.add(new_user)
        
        db.commit()
        print("✅ 기본 사용자 계정 생성 완료!")
        
    except Exception as e:
        print(f"❌ 기본 사용자 생성 오류: {e}")
        db.rollback()

@router.post("/login")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """간단한 로그인"""
    try:
        # 사용자 조회
        user = db.query(User).filter(User.login_id == login_request.login_id).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="로그인 ID 또는 비밀번호가 잘못되었습니다.")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="비활성화된 계정입니다.")
        
        # 비밀번호 확인 (평문 비교)
        if user.login_pw != login_request.login_pw:
            raise HTTPException(status_code=401, detail="로그인 ID 또는 비밀번호가 잘못되었습니다.")
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "login_id": user.login_id,
                "name": user.name,
                "is_active": user.is_active
            },
            "message": "로그인 성공"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류: {str(e)}")

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    """모든 사용자 조회"""
    try:
        users = db.query(User).filter(User.is_active == True).all()
        return {
            "success": True,
            "users": [
                {
                    "id": user.id,
                    "login_id": user.login_id,
                    "name": user.name,
                    "is_active": user.is_active
                } for user in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 조회 실패: {str(e)}")

@router.post("/init-users")
async def initialize_users(db: Session = Depends(get_db)):
    """기본 사용자 초기화"""
    try:
        create_default_users(db)
        return {"success": True, "message": "기본 사용자 계정이 생성되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 초기화 실패: {str(e)}") 