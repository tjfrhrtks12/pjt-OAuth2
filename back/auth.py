from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db
from models import Teacher
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    teacher_id: str
    teacher_pw: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    teacher_name: str = None

@router.post("/api/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        # 데이터베이스에서 교사 정보 확인
        teacher = db.query(Teacher).filter(
            Teacher.teacher_id == login_data.teacher_id,
            Teacher.teacher_pw == login_data.teacher_pw
        ).first()
        
        if teacher:
            # 로그인 성공
            return LoginResponse(
                success=True,
                message="로그인 성공",
                token="dummy_token_12345",  # 실제로는 JWT 토큰 생성
                teacher_name=teacher.teacher_name
            )
        else:
            # 로그인 실패
            return LoginResponse(
                success=False,
                message="아이디 또는 비밀번호가 잘못되었습니다."
            )
            
    except Exception as e:
        # 로그 출력을 위해 예외 정보를 포함
        print(f"Login error: {str(e)}")
        return LoginResponse(
            success=False,
            message="로그인 처리 중 오류가 발생했습니다."
        ) 