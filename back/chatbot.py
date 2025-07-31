from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy.orm import Session
from config import get_db
from models import User, Student
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool

# OpenAI 클라이언트 생성 (환경변수에서 API 키 읽기)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_teacher_list(db: Session):
    """선생님 명단 조회"""
    try:
        # is_active가 True이거나 NULL인 모든 사용자 조회
        teachers = db.query(User).filter(
            (User.is_active == True) | (User.is_active.is_(None))
        ).all()
        teacher_names = [teacher.name for teacher in teachers]
        return teacher_names
    except Exception as e:
        print(f"선생님 명단 조회 오류: {e}")
        return []

def get_student_list(db: Session):
    """전체 학생 명단 조회"""
    try:
        students = db.query(Student).filter(Student.is_active == True).all()
        student_info = []
        for student in students:
            teacher = db.query(User).filter(User.id == student.teacher_id).first()
            student_info.append(f"{student.name} ({student.grade} {student.class_name}, 담당: {teacher.name if teacher else '알 수 없음'})")
        return student_info
    except Exception as e:
        print(f"학생 명단 조회 오류: {e}")
        return []

def get_teacher_students(db: Session, teacher_name: str):
    """특정 선생님의 학생 명단 조회"""
    try:
        # 선생님 찾기
        teacher = db.query(User).filter(
            (User.name == teacher_name) & 
            ((User.is_active == True) | (User.is_active.is_(None)))
        ).first()
        
        if not teacher:
            return []
        
        # 해당 선생님의 학생들 조회
        students = db.query(Student).filter(
            (Student.teacher_id == teacher.id) & 
            (Student.is_active == True)
        ).all()
        
        student_list = [f"{student.name} ({student.grade} {student.class_name})" for student in students]
        return student_list, teacher.name
    except Exception as e:
        print(f"선생님별 학생 조회 오류: {e}")
        return [], ""

@router.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 선생님 명단 조회
        teacher_list = get_teacher_list(db)
        teacher_names = ", ".join(teacher_list) if teacher_list else "등록된 선생님이 없습니다"
        
        # 전체 학생 명단 조회
        student_list = get_student_list(db)
        student_names = "\n".join(student_list) if student_list else "등록된 학생이 없습니다"
        
        # OpenAI API 호출 (GPT-4o 모델 사용)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""당신은 학교 관리 시스템의 AI 어시스턴트입니다. 
                    교사와 학생들을 도와주는 친근하고 전문적인 어시스턴트입니다. 
                    한국어로 답변해주세요.
                    
                    현재 시스템에는 데이터베이스 연결과 AI 연결이 설정되어 있습니다.
                    
                    **현재 등록된 선생님 명단: {teacher_names}**
                    
                    **전체 학생 명단:**
                    {student_names}
                    
                    사용자가 다음과 같은 질문을 할 수 있습니다:
                    1. "선생님 명단을 알려줘" → 선생님 목록 제공
                    2. "학생 명단을 알려줘" → 전체 학생 목록 제공
                    3. "[선생님 이름] 선생님의 학생 명단을 알려줘" → 해당 선생님의 학생들만 제공
                    4. "박성주 선생님의 학생 명단을 알려줘" → 박성주 선생님의 학생들만 제공
                    
                    사용자의 질문에 대해 도움이 될 수 있는 답변을 제공해주세요."""
                },
                {
                    "role": "user",
                    "content": chat_request.message
                }
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # AI 응답 추출
        ai_response = response.choices[0].message.content
        
        return ChatResponse(
            response=ai_response,
            success=True
        )
        
    except Exception as e:
        print(f"AI 챗봇 오류: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"AI 챗봇 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/api/ai/status")
async def get_ai_status():
    """AI 연결 상태 확인"""
    try:
        # 간단한 테스트 요청으로 AI 연결 확인
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "안녕하세요"
                }
            ],
            max_tokens=10
        )
        
        return {
            "status": "connected",
            "model": "gpt-4o",
            "message": "AI 연결이 정상입니다."
        }
        
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "message": "AI 연결에 실패했습니다."
        } 