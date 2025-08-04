from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config import Base

# 기본 모델 클래스 - 필요시 확장
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    login_pw = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정 - 한 명의 사용자가 여러 반을 담당할 수 있음
    classes = relationship("Class", back_populates="teacher")

class Class(BaseModel):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)  # class_id 대신 id 사용
    academic_year = Column(Integer, nullable=False)  # 학년도 (2022, 2023, 2024)
    grade = Column(Integer, nullable=False)  # 학년 (1, 2, 3)
    class_num = Column(Integer, nullable=False)  # 반 번호 (1, 2, 3, ...)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 담임 선생님
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    teacher = relationship("User", back_populates="classes")
    students = relationship("Student", back_populates="class_info")
    
    # 복합 유니크 제약조건 (같은 학년에 같은 반 번호가 중복되지 않도록)
    __table_args__ = (
        # MySQL에서는 UniqueConstraint 사용
    )

class Student(BaseModel):
    __tablename__ = "students"
    
    name = Column(String(255), nullable=False)
    academic_year = Column(Integer, nullable=False)  # 학년도 (2022, 2023, 2024)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)  # 소속 반
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    class_info = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")

class Grade(BaseModel):
    __tablename__ = "grades"
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    academic_year = Column(Integer, nullable=False)  # 학년도 (2022, 2023, 2024)
    score = Column(Integer, nullable=False)  # 0-100점
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    exam = relationship("Exam", back_populates="grades")

class Subject(BaseModel):
    __tablename__ = "subjects"
    
    name = Column(String(50), nullable=False)  # "국어", "수학", "사회", "과학", "영어"
    code = Column(String(10), nullable=False)  # "KOR", "MATH", "SOC", "SCI", "ENG"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    grades = relationship("Grade", back_populates="subject")

class Exam(BaseModel):
    __tablename__ = "exams"
    
    name = Column(String(100), nullable=False)  # "1학기중간고사", "1학기기말고사", "2학기중간고사", "2학기기말고사"
    semester = Column(Integer, nullable=False)  # 1, 2
    type = Column(String(20), nullable=False)   # "midterm", "final"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    grades = relationship("Grade", back_populates="exam") 