import requests
from typing import Optional, Dict
from sqlalchemy.orm import Session
from models import User
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

class OAuthService:
    """Google OAuth2 서비스 클래스"""
    
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @staticmethod
    def get_google_auth_url() -> str:
        """Google OAuth2 인증 URL 생성"""
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{OAuthService.GOOGLE_AUTH_URL}?{query_string}"
    
    @staticmethod
    def get_google_tokens(code: str) -> Optional[Dict]:
        """Google OAuth2 코드로 액세스 토큰 교환"""
        try:
            data = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI
            }
            
            response = requests.post(OAuthService.GOOGLE_TOKEN_URL, data=data)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Google 토큰 교환 오류: {e}")
            return None
    
    @staticmethod
    def get_google_user_info(access_token: str) -> Optional[Dict]:
        """Google 사용자 정보 조회"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(OAuthService.GOOGLE_USERINFO_URL, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Google 사용자 정보 조회 오류: {e}")
            return None
    
    @staticmethod
    def get_or_create_user(db: Session, google_user_info: Dict, tokens: Dict = None) -> User:
        """Google 사용자 정보로 DB에서 사용자 조회 또는 생성"""
        # Google ID로 기존 사용자 찾기
        user = db.query(User).filter(User.google_id == google_user_info.get("id")).first()
        
        if not user:
            # 이메일로 기존 사용자 찾기
            user = db.query(User).filter(User.email == google_user_info.get("email")).first()
            
            if user:
                # 기존 사용자에 Google ID 추가
                user.google_id = google_user_info.get("id")
                user.picture = google_user_info.get("picture")
                db.commit()
            else:
                # 새 사용자 생성
                user = User(
                    email=google_user_info.get("email"),
                    name=google_user_info.get("name"),
                    picture=google_user_info.get("picture"),
                    google_id=google_user_info.get("id")
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # 토큰 정보 업데이트 (있는 경우)
        if tokens:
            user.google_access_token = tokens.get("access_token")
            user.google_refresh_token = tokens.get("refresh_token")
            if tokens.get("expires_in"):
                from datetime import datetime, timedelta
                user.google_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in"))
            db.commit()
            db.refresh(user)
        
        return user 