from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from config import get_db
from models import User
from oauth_service import OAuthService
from jwt_utils import create_access_token, verify_token
import urllib.parse

router = APIRouter()

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    picture: Optional[str] = None

@router.get("/auth/google")
async def google_login():
    """Google OAuth2 로그인 시작"""
    auth_url = OAuthService.get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/auth/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Google OAuth2 콜백 처리"""
    try:
        print(f"Google OAuth2 콜백 시작 - 코드: {code[:10]}...")
        
        # Google 토큰 교환
        tokens = OAuthService.get_google_tokens(code)
        if not tokens:
            print("Google 토큰 교환 실패")
            raise HTTPException(status_code=400, detail="Google 토큰 교환 실패")
        
        print("Google 토큰 교환 성공")
        
        # Google 사용자 정보 조회
        user_info = OAuthService.get_google_user_info(tokens["access_token"])
        if not user_info:
            print("Google 사용자 정보 조회 실패")
            raise HTTPException(status_code=400, detail="Google 사용자 정보 조회 실패")
        
        print(f"Google 사용자 정보 조회 성공: {user_info.get('email')}")
        
        # DB에서 사용자 조회 또는 생성
        user = OAuthService.get_or_create_user(db, user_info)
        print(f"사용자 처리 완료: ID={user.id}, 이메일={user.email}")
        
        # JWT 토큰 생성
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        access_token = create_access_token(token_data)
        print(f"JWT 토큰 생성 완료: {access_token[:20]}...")
        
        # 프론트엔드로 리다이렉트 (토큰 포함) - URL 인코딩 추가
        token_encoded = urllib.parse.quote(access_token)
        user_id_encoded = urllib.parse.quote(str(user.id))
        
        frontend_url = f"http://localhost:3000/auth/callback?token={token_encoded}&user_id={user_id_encoded}"
        print(f"프론트엔드 리다이렉트 URL: {frontend_url}")
        
        return RedirectResponse(url=frontend_url, status_code=302)
        
    except Exception as e:
        print(f"Google OAuth2 콜백 오류: {e}")
        error_message = urllib.parse.quote(str(e))
        error_url = f"http://localhost:3000/auth/callback?error=true&message={error_message}"
        return RedirectResponse(url=error_url, status_code=302)

@router.post("/api/login", response_model=LoginResponse)
async def login(login_data: dict, db: Session = Depends(get_db)):
    """기존 로그인 (하위 호환성)"""
    try:
        # Google OAuth2 URL 반환
        auth_url = OAuthService.get_google_auth_url()
        return LoginResponse(
            success=True,
            message="Google OAuth2 로그인을 사용하세요",
            token=None
        )
    except Exception as e:
        return LoginResponse(
            success=False,
            message="로그인 처리 중 오류가 발생했습니다."
        )

@router.get("/api/auth/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """현재 로그인한 사용자 정보 조회"""
    try:
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="토큰이 필요합니다")
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
        
        # DB에서 사용자 정보 조회
        user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            picture=user.picture
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 정보 조회 오류: {str(e)}")

@router.get("/api/auth/status")
async def get_auth_status():
    """인증 시스템 상태 확인"""
    return {
        "status": "ready",
        "oauth_provider": "google",
        "message": "Google OAuth2 인증 시스템이 준비되었습니다."
    }

@router.post("/api/auth/logout")
async def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return {
        "success": True,
        "message": "로그아웃되었습니다. 클라이언트에서 토큰을 삭제하세요."
    } 