from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
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

class ExamScore(Base):
    __tablename__ = "exam_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), ForeignKey("students.student_name"), nullable=False)
    subject = Column(String(20), nullable=False)  # 국어, 수학, 사회, 과학
    exam_type = Column(String(20), nullable=False)  # 1학기중간, 1학기기말, 2학기중간, 2학기기말
    score = Column(Integer, nullable=True)  # 점수 (0-100)
    
    # 관계 설정
    student = relationship("Student", back_populates="exam_scores")

# Student 모델에 관계 추가
Student.exam_scores = relationship("ExamScore", back_populates="student") 