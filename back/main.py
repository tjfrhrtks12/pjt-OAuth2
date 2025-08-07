from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database_service import DatabaseService
from simple_auth import get_db, get_all_users, initialize_users
import simple_auth
from services.user_service import get_teacher_list, get_student_list, get_teacher_students, get_class_students
from services.grade_service import get_student_grades, get_class_grades_summary, get_subject_analysis, get_top_students, get_bottom_students, get_grade_bottom_students, get_exam_analysis, get_subject_exam_analysis
from services.calendar_service import CalendarService
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI(title="학교 관리 시스템 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class StudentCreateRequest(BaseModel):
    name: str
    class_id: int
    academic_year: int = 2024

class GradeCreateRequest(BaseModel):
    student_id: int
    subject_id: int
    exam_id: int
    score: int
    academic_year: int = 2024

class CalendarEventCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: str
    end_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    event_type: str
    color: str = "#3788d8"
    is_all_day: bool = False
    location: Optional[str] = None

class CalendarEventUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    event_type: Optional[str] = None
    color: Optional[str] = None
    is_all_day: Optional[bool] = None
    location: Optional[str] = None

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "학교 관리 시스템 API에 오신 것을 환영합니다!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}

@app.get("/api/status")
async def get_system_status():
    """시스템 상태 조회"""
    try:
        db_status = DatabaseService.test_connection()
        return {
            "status": "running",
            "database": "connected" if db_status else "disconnected",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "framework": "FastAPI"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "framework": "FastAPI"
        }

@app.get("/api/auth/info")
async def get_auth_info():
    """인증 시스템 정보 반환"""
    return {
        "auth_type": "simple",
        "login_endpoint": "/api/login",
        "default_users": [
            {"login_id": "teacher1", "login_pw": "password123", "name": "김선생님"},
            {"login_id": "teacher2", "login_pw": "password123", "name": "이선생님"},
            {"login_id": "teacher3", "login_pw": "password123", "name": "박선생님"}
        ]
    }

# 반 관련 API 엔드포인트들
@app.get("/api/classes")
async def get_all_classes(academic_year: int = 2024):
    """모든 반 정보 조회"""
    try:
        classes = DatabaseService.get_all_classes(academic_year)
        return {
            "success": True,
            "data": classes,
            "academic_year": academic_year,
            "count": len(classes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 정보 조회 실패: {str(e)}")

@app.get("/api/teachers/{teacher_id}/classes")
async def get_teacher_classes(teacher_id: int, academic_year: int = 2024):
    """특정 선생님이 담당하는 모든 반 조회"""
    try:
        classes = DatabaseService.get_classes_by_teacher(teacher_id, academic_year)
        return {
            "success": True,
            "data": classes,
            "teacher_id": teacher_id,
            "academic_year": academic_year,
            "count": len(classes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선생님 반 조회 실패: {str(e)}")

@app.get("/api/teachers")
async def get_all_teachers():
    """모든 선생님 조회"""
    try:
        teachers = DatabaseService.get_all_teachers()
        return {
            "success": True,
            "data": teachers,
            "count": len(teachers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선생님 조회 실패: {str(e)}")

@app.get("/api/classes/{grade}/{class_num}/homeroom-teacher")
async def get_homeroom_teacher(grade: int, class_num: int, academic_year: int = 2024):
    """특정 반의 담임선생님 조회"""
    try:
        teacher = DatabaseService.get_homeroom_teacher(grade, class_num, academic_year)
        if not teacher:
            raise HTTPException(status_code=404, detail="담임선생님을 찾을 수 없습니다.")
        
        return {
            "success": True,
            "data": teacher
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"담임선생님 조회 실패: {str(e)}")

@app.post("/api/classes")
async def create_class(grade: int, class_num: int, teacher_id: int, academic_year: int = 2024):
    """새로운 반 생성"""
    try:
        success = DatabaseService.create_class(grade, class_num, teacher_id, academic_year)
        if not success:
            raise HTTPException(status_code=400, detail="반 생성에 실패했습니다.")
        
        return {
            "success": True,
            "message": f"{academic_year}년 {grade}학년 {class_num}반이 성공적으로 생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 생성 실패: {str(e)}")

# 학생 관련 API 엔드포인트들
@app.post("/api/students")
async def create_student(request: StudentCreateRequest):
    """새로운 학생 생성"""
    try:
        success = DatabaseService.create_student(
            request.name, 
            request.class_id, 
            request.academic_year
        )
        if not success:
            raise HTTPException(status_code=400, detail="학생 생성에 실패했습니다.")
        
        return {
            "success": True,
            "message": f"학생 '{request.name}'이(가) 성공적으로 생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 생성 실패: {str(e)}")

@app.get("/api/students")
async def get_all_students(academic_year: int = 2024):
    """모든 학생 조회"""
    try:
        students = DatabaseService.get_all_students(academic_year)
        return {
            "success": True,
            "data": students,
            "academic_year": academic_year,
            "count": len(students)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 조회 실패: {str(e)}")

@app.get("/api/classes/{class_id}/students")
async def get_students_by_class(class_id: int, academic_year: int = 2024):
    """특정 반의 학생들 조회"""
    try:
        students = DatabaseService.get_students_by_class(class_id, academic_year)
        return {
            "success": True,
            "data": students,
            "class_id": class_id,
            "academic_year": academic_year,
            "count": len(students)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 학생 조회 실패: {str(e)}")

# 성적 관련 API 엔드포인트들
@app.post("/api/grades")
async def create_grade(request: GradeCreateRequest):
    """새로운 성적 생성"""
    try:
        success = DatabaseService.create_grade(
            request.student_id,
            request.subject_id,
            request.exam_id,
            request.score,
            request.academic_year
        )
        if not success:
            raise HTTPException(status_code=400, detail="성적 생성에 실패했습니다.")
        
        return {
            "success": True,
            "message": "성적이 성공적으로 생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성적 생성 실패: {str(e)}")

@app.get("/api/students/{student_id}/grades")
async def get_student_grades_api(student_id: int, academic_year: int = 2024):
    """특정 학생의 성적 조회"""
    try:
        grades = DatabaseService.get_student_grades(student_id, academic_year)
        return {
            "success": True,
            "data": grades,
            "student_id": student_id,
            "academic_year": academic_year,
            "count": len(grades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 성적 조회 실패: {str(e)}")

@app.get("/api/classes/{class_id}/grades")
async def get_class_grades_api(class_id: int, academic_year: int = 2024):
    """특정 반의 모든 성적 조회"""
    try:
        grades = DatabaseService.get_class_grades(class_id, academic_year)
        return {
            "success": True,
            "data": grades,
            "class_id": class_id,
            "academic_year": academic_year,
            "count": len(grades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 성적 조회 실패: {str(e)}")

# 기존 서비스 함수들 연결
@app.get("/api/tables")
async def get_all_tables():
    """데이터베이스의 모든 테이블 목록 조회"""
    try:
        tables = DatabaseService.get_all_tables()
        return {
            "success": True,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테이블 목록 조회 실패: {str(e)}")

# 인증 관련 엔드포인트들
app.include_router(simple_auth.router, prefix="/api", tags=["인증"])

# 채팅 관련 엔드포인트
@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """채팅 메시지 처리 (새로운 서비스 사용)"""
    try:
        from services.chat_router import process_chat_message
        # 사용자 ID 설정 (요청에서 받거나 기본값 1)
        user_id = chat_request.user_id if chat_request.user_id else 1
        response = process_chat_message(chat_request, db, user_id)
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 실패: {str(e)}")

# 기존 서비스 함수들 (호환성 유지)
@app.get("/api/teacher-list")
async def get_teacher_list_api(db: Session = Depends(get_db)):
    """선생님 명단 조회 (기존 호환성)"""
    try:
        teacher_list = get_teacher_list(db)
        return {
            "success": True,
            "teachers": teacher_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"선생님 명단 조회 실패: {str(e)}")

@app.get("/api/student-list")
async def get_student_list_api(db: Session = Depends(get_db)):
    """전체 학생 명단 조회 (기존 호환성)"""
    try:
        student_list = get_student_list(db)
        return {
            "success": True,
            "students": student_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 명단 조회 실패: {str(e)}")

# 출결 유형 관련 API 엔드포인트들
@app.get("/api/attendance-types")
async def get_all_attendance_types():
    """모든 출결 유형 조회"""
    try:
        attendance_types = DatabaseService.get_all_attendance_types()
        return {
            "success": True,
            "data": attendance_types,
            "count": len(attendance_types)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"출결 유형 조회 실패: {str(e)}")

@app.post("/api/attendance-types/init")
async def initialize_attendance_types():
    """기본 출결 유형 초기화"""
    try:
        success = DatabaseService.initialize_attendance_types()
        if not success:
            raise HTTPException(status_code=500, detail="출결 유형 초기화에 실패했습니다.")
        
        return {
            "success": True,
            "message": "기본 출결 유형이 성공적으로 초기화되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"출결 유형 초기화 실패: {str(e)}")

# 결석 사유 관련 API 엔드포인트들
@app.get("/api/attendance-reasons")
async def get_all_attendance_reasons():
    """모든 결석 사유 조회"""
    try:
        attendance_reasons = DatabaseService.get_all_attendance_reasons()
        return {
            "success": True,
            "data": attendance_reasons,
            "count": len(attendance_reasons)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결석 사유 조회 실패: {str(e)}")

@app.post("/api/attendance-reasons/init")
async def initialize_attendance_reasons():
    """기본 결석 사유 초기화"""
    try:
        success = DatabaseService.initialize_attendance_reasons()
        if not success:
            raise HTTPException(status_code=500, detail="결석 사유 초기화에 실패했습니다.")
        
        return {
            "success": True,
            "message": "기본 결석 사유가 성공적으로 초기화되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결석 사유 초기화 실패: {str(e)}")

# 출결 기록 관련 API 엔드포인트들
@app.post("/api/attendance")
async def create_attendance(student_id: int, type_id: int, date: str, reason_id: int = None, reason_detail: str = None, note: str = None):
    """출결 기록 생성"""
    try:
        success = DatabaseService.create_attendance(
            student_id=student_id,
            type_id=type_id,
            date=date,
            reason_id=reason_id,
            reason_detail=reason_detail,
            note=note
        )
        if not success:
            raise HTTPException(status_code=400, detail="출결 기록 생성에 실패했습니다.")
        
        return {
            "success": True,
            "message": "출결 기록이 성공적으로 생성되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"출결 기록 생성 실패: {str(e)}")

@app.get("/api/students/{student_id}/attendance")
async def get_student_attendance(student_id: int, start_date: str = None, end_date: str = None):
    """학생별 출결 기록 조회"""
    try:
        attendances = DatabaseService.get_student_attendances(student_id, start_date, end_date)
        return {
            "success": True,
            "data": attendances,
            "student_id": student_id,
            "count": len(attendances)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 출결 기록 조회 실패: {str(e)}")

@app.get("/api/classes/{class_id}/attendance")
async def get_class_attendance(class_id: int, date: str = None):
    """반별 출결 기록 조회"""
    try:
        attendances = DatabaseService.get_class_attendances(class_id, date)
        return {
            "success": True,
            "data": attendances,
            "class_id": class_id,
            "count": len(attendances)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 출결 기록 조회 실패: {str(e)}")

# 월별 출결 통계 관련 API 엔드포인트들
@app.get("/api/students/{student_id}/monthly-attendance")
async def get_student_monthly_attendance(student_id: int, year: int = None):
    """학생별 월별 출결 통계 조회"""
    try:
        monthly_attendances = DatabaseService.get_student_monthly_attendance(student_id, year)
        return {
            "success": True,
            "data": monthly_attendances,
            "student_id": student_id,
            "count": len(monthly_attendances)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 월별 출결 통계 조회 실패: {str(e)}")

@app.post("/api/students/{student_id}/calculate-monthly/{year}/{month}")
async def calculate_monthly_attendance(student_id: int, year: int, month: int):
    """학생 월별 출결 통계 계산"""
    try:
        success = DatabaseService.calculate_monthly_attendance(student_id, year, month)
        if not success:
            raise HTTPException(status_code=500, detail="월별 출결 통계 계산에 실패했습니다.")
        
        return {
            "success": True,
            "message": f"{year}년 {month}월 출결 통계가 성공적으로 계산되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"월별 출결 통계 계산 실패: {str(e)}")

# 연도별 출결 통계 관련 API 엔드포인트들
@app.get("/api/students/{student_id}/yearly-attendance")
async def get_student_yearly_attendance(student_id: int, year: int = None):
    """학생별 연도별 출결 통계 조회"""
    try:
        yearly_attendances = DatabaseService.get_student_yearly_attendance(student_id, year)
        return {
            "success": True,
            "data": yearly_attendances,
            "student_id": student_id,
            "count": len(yearly_attendances)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 연도별 출결 통계 조회 실패: {str(e)}")

@app.post("/api/students/{student_id}/calculate-yearly/{year}")
async def calculate_yearly_attendance(student_id: int, year: int):
    """학생 연도별 출결 통계 계산"""
    try:
        success = DatabaseService.calculate_yearly_attendance(student_id, year)
        if not success:
            raise HTTPException(status_code=500, detail="연도별 출결 통계 계산에 실패했습니다.")
        
        return {
            "success": True,
            "message": f"{year}년 출결 통계가 성공적으로 계산되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연도별 출결 통계 계산 실패: {str(e)}")

# 캘린더 관련 API 엔드포인트들
@app.get("/api/calendar/events")
async def get_calendar_events(user_id: int, year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    """사용자의 캘린더 이벤트 조회"""
    try:
        calendar_service = CalendarService(db)
        
        if year and month:
            events = calendar_service.get_events_by_month(user_id, year, month)
        else:
            events = calendar_service.get_events_by_user(user_id)
        
        # 이벤트를 JSON 직렬화 가능한 형태로 변환
        events_data = []
        for event in events:
            event_data = {
                "id": event.id,
                "user_id": event.user_id,
                "title": event.title,
                "description": event.description,
                "start_date": event.start_date.isoformat() if event.start_date else None,
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "event_type": event.event_type,
                "color": event.color,
                "is_all_day": event.is_all_day,
                "location": event.location,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "updated_at": event.updated_at.isoformat() if event.updated_at else None
            }
            events_data.append(event_data)
        
        return {
            "success": True,
            "data": events_data,
            "user_id": user_id,
            "count": len(events_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 조회 실패: {str(e)}")

@app.get("/api/calendar/events/{event_id}")
async def get_calendar_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    """특정 캘린더 이벤트 조회"""
    try:
        calendar_service = CalendarService(db)
        event = calendar_service.get_event_by_id(event_id, user_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
        
        event_data = {
            "id": event.id,
            "user_id": event.user_id,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "event_type": event.event_type,
            "color": event.color,
            "is_all_day": event.is_all_day,
            "location": event.location,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "updated_at": event.updated_at.isoformat() if event.updated_at else None
        }
        
        return {
            "success": True,
            "data": event_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 조회 실패: {str(e)}")

@app.post("/api/calendar/events")
async def create_calendar_event(request: CalendarEventCreateRequest, user_id: int, db: Session = Depends(get_db)):
    """새로운 캘린더 이벤트 생성"""
    try:
        calendar_service = CalendarService(db)
        
        # 요청 데이터를 딕셔너리로 변환
        event_data = {
            "user_id": user_id,
            "title": request.title,
            "description": request.description,
            "start_date": date.fromisoformat(request.start_date),
            "end_date": date.fromisoformat(request.end_date),
            "event_type": request.event_type,
            "color": request.color,
            "is_all_day": request.is_all_day,
            "location": request.location
        }
        
        # 시간이 있는 경우 추가
        if request.start_time:
            from datetime import time
            event_data["start_time"] = time.fromisoformat(request.start_time)
        if request.end_time:
            from datetime import time
            event_data["end_time"] = time.fromisoformat(request.end_time)
        
        event = calendar_service.create_event(event_data)
        
        return {
            "success": True,
            "message": "캘린더 이벤트가 성공적으로 생성되었습니다.",
            "data": {
                "id": event.id,
                "title": event.title
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 생성 실패: {str(e)}")

@app.put("/api/calendar/events/{event_id}")
async def update_calendar_event(event_id: int, request: CalendarEventUpdateRequest, user_id: int, db: Session = Depends(get_db)):
    """캘린더 이벤트 수정"""
    try:
        calendar_service = CalendarService(db)
        
        # 요청 데이터를 딕셔너리로 변환 (None이 아닌 값만)
        event_data = {}
        if request.title is not None:
            event_data["title"] = request.title
        if request.description is not None:
            event_data["description"] = request.description
        if request.start_date is not None:
            event_data["start_date"] = date.fromisoformat(request.start_date)
        if request.end_date is not None:
            event_data["end_date"] = date.fromisoformat(request.end_date)
        if request.event_type is not None:
            event_data["event_type"] = request.event_type
        if request.color is not None:
            event_data["color"] = request.color
        if request.is_all_day is not None:
            event_data["is_all_day"] = request.is_all_day
        if request.location is not None:
            event_data["location"] = request.location
        
        # 시간이 있는 경우 추가
        if request.start_time is not None:
            from datetime import time
            event_data["start_time"] = time.fromisoformat(request.start_time)
        if request.end_time is not None:
            from datetime import time
            event_data["end_time"] = time.fromisoformat(request.end_time)
        
        event = calendar_service.update_event(event_id, user_id, event_data)
        
        if not event:
            raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "message": "캘린더 이벤트가 성공적으로 수정되었습니다.",
            "data": {
                "id": event.id,
                "title": event.title
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 수정 실패: {str(e)}")

@app.delete("/api/calendar/events/{event_id}")
async def delete_calendar_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    """캘린더 이벤트 삭제"""
    try:
        calendar_service = CalendarService(db)
        success = calendar_service.delete_event(event_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "message": "캘린더 이벤트가 성공적으로 삭제되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캘린더 이벤트 삭제 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 