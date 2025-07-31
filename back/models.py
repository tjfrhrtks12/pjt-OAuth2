from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from config import Base

# 기본 모델 클래스 - 필요시 확장
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    picture = Column(String(500), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 