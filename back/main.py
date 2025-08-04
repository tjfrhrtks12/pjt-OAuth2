from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database_service import DatabaseService
from simple_auth import get_db, get_all_users, initialize_users
import simple_auth
from services.user_service import get_teacher_list, get_student_list, get_teacher_students, get_class_students
from services.grade_service import get_student_grades, get_class_grades_summary, get_subject_analysis, get_top_students, get_bottom_students, get_grade_bottom_students, get_exam_analysis, get_subject_exam_analysis
from services.chat_service import process_chat_message
from pydantic import BaseModel
from typing import List, Optional

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
    """채팅 메시지 처리"""
    try:
        response = process_chat_message(chat_request, db)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 