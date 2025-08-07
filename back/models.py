from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, Time, DECIMAL, TIMESTAMP, SmallInteger
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
    login_id = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    login_pw = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)  # TINYINT (0-255) - MySQL에서는 TINYINT로 매핑됨
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 관계 설정 - 한 명의 사용자가 여러 반을 담당할 수 있음
    classes = relationship("Class", back_populates="teacher")
    calendar_events = relationship("CalendarEvent", back_populates="user")

class Class(BaseModel):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)  # class_id 대신 id 사용
    academic_year = Column(Integer, nullable=False, default=2024)  # 학년도 (2022, 2023, 2024)
    grade = Column(Integer, nullable=False)  # 학년 (1, 2, 3)
    class_num = Column(Integer, nullable=False)  # 반 번호 (1, 2, 3, ...)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 담임 선생님
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 관계 설정
    teacher = relationship("User", back_populates="classes")
    students = relationship("Student", back_populates="class_info")
    
    # 복합 유니크 제약조건 (같은 학년에 같은 반 번호가 중복되지 않도록)
    __table_args__ = (
        # MySQL에서는 UniqueConstraint 사용
    )

class Student(BaseModel):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # VARCHAR(100)로 변경
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    academic_year = Column(Integer, nullable=False)
    birth_year = Column(Integer)  # 출생연도 추가
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경

    # 관계 설정
    class_info = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    monthly_attendances = relationship("MonthlyAttendance", back_populates="student")
    yearly_attendances = relationship("YearlyAttendance", back_populates="student")

class Grade(BaseModel):
    __tablename__ = "grades"
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    academic_year = Column(Integer, nullable=False)  # 학년도 (2022, 2023, 2024)
    score = Column(DECIMAL(5, 2), nullable=False)  # DECIMAL(5,2)로 변경
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    exam = relationship("Exam", back_populates="grades")

class Subject(BaseModel):
    __tablename__ = "subjects"
    
    name = Column(String(100), nullable=False)  # VARCHAR(100)로 변경
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    grades = relationship("Grade", back_populates="subject")

class Exam(BaseModel):
    __tablename__ = "exams"
    
    name = Column(String(100), nullable=False)  # "1학기중간고사", "1학기기말고사", "2학기중간고사", "2학기기말고사"
    semester = Column(Integer, nullable=False)  # 1, 2
    type = Column(String(50), nullable=False)   # VARCHAR(50)로 변경
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    grades = relationship("Grade", back_populates="exam")

class AttendanceType(BaseModel):
    __tablename__ = "attendance_types"
    
    name = Column(String(50), nullable=False)  # "출석", "결석", "지각", "조퇴", "공결"
    code = Column(String(20), nullable=False, unique=True)  # "PRESENT", "ABSENT", "LATE", "EARLY", "OFFICIAL"
    description = Column(String(200))  # 상세 설명
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    attendances = relationship("Attendance", back_populates="attendance_type")

class AttendanceReason(BaseModel):
    __tablename__ = "attendance_reasons"
    
    name = Column(String(50), nullable=False)  # "질병", "개인사", "가족사", "학교행사", "기타"
    code = Column(String(20), nullable=False, unique=True)  # "ILLNESS", "PERSONAL", "FAMILY", "SCHOOL", "OTHER"
    description = Column(String(200))  # 상세 설명
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    attendances = relationship("Attendance", back_populates="attendance_reason")

class Attendance(BaseModel):
    __tablename__ = "attendances"
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)  # DATETIME으로 변경
    type_id = Column(Integer, ForeignKey("attendance_types.id"), nullable=False)
    reason_id = Column(Integer, ForeignKey("attendance_reasons.id"), nullable=True)
    academic_year = Column(Integer, nullable=True)  # nullable=True로 변경
    reason_detail = Column(String(500), nullable=True)  # 추가된 컬럼
    note = Column(Text, nullable=True)  # 추가된 컬럼
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    student = relationship("Student", back_populates="attendances")
    attendance_type = relationship("AttendanceType", back_populates="attendances")
    attendance_reason = relationship("AttendanceReason", back_populates="attendances")

class MonthlyAttendance(BaseModel):
    __tablename__ = "monthly_attendances"
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    year = Column(Integer, nullable=False)  # 연도 (2024, 2025, ...)
    month = Column(Integer, nullable=False)  # 월 (1-12)
    total_days = Column(Integer, default=0)  # 총 일수
    present_days = Column(Integer, default=0)  # 출석 일수
    absent_days = Column(Integer, default=0)  # 결석 일수
    late_days = Column(Integer, default=0)  # 지각 일수
    early_leave_days = Column(Integer, default=0)  # 조퇴 일수
    attendance_rate = Column(Integer, default=0)  # 출석률 (0-100)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    student = relationship("Student", back_populates="monthly_attendances")

class YearlyAttendance(BaseModel):
    __tablename__ = "yearly_attendances"
    
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    year = Column(Integer, nullable=False)  # 연도 (2024, 2025, ...)
    total_days = Column(Integer, default=0)  # 총 일수
    present_days = Column(Integer, default=0)  # 출석 일수
    absent_days = Column(Integer, default=0)  # 결석 일수
    late_days = Column(Integer, default=0)  # 지각 일수
    early_leave_days = Column(Integer, default=0)  # 조퇴 일수
    attendance_rate = Column(Integer, default=0)  # 출석률 (0-100)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)  # TIMESTAMP로 변경
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=False)  # TIMESTAMP로 변경
    
    # 관계 설정
    student = relationship("Student", back_populates="yearly_attendances")

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_events"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    event_type = Column(String(50), nullable=False)  # 수업, 시험, 상담, 행사, 개인일정
    color = Column(String(20), default="#3788d8")  # 기본 색상
    is_all_day = Column(Integer, default=0)  # TINYINT (0-255) - MySQL에서는 TINYINT로 매핑됨
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="calendar_events") 