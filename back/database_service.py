from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from config import engine

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseService:
    """기본 데이터베이스 서비스 클래스"""
    
    @staticmethod
    def get_session():
        """데이터베이스 세션 반환"""
        return SessionLocal()
    
    @staticmethod
    def test_connection() -> bool:
        """데이터베이스 연결 테스트"""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return False
    
    @staticmethod
    def get_database_info() -> Dict:
        """데이터베이스 정보 반환"""
        return {
            "status": "connected" if DatabaseService.test_connection() else "disconnected",
            "message": "데이터베이스 연결이 정상입니다." if DatabaseService.test_connection() else "데이터베이스 연결에 실패했습니다."
        } 