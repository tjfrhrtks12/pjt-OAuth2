from sqlalchemy import Column, Integer, String
from config import Base

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String(100), unique=True, nullable=False)  # 교사 아이디
    teacher_pw = Column(String(255), nullable=False)  # 교사 비밀번호
    teacher_name = Column(String(100), nullable=False)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    student_grade = Column(Integer, nullable=False)
    student_phone = Column(String(20))
    score = Column(Integer, nullable=True)  # 학생 점수 (선택사항) 