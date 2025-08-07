"""
챗봇 메인 라우터
사용자 메시지를 분석하여 적절한 서비스로 분기하는 기능
"""

from typing import Dict
from sqlalchemy.orm import Session
from services.calendar_chat_service import (
    get_today_schedule, get_tomorrow_schedule, get_weekly_schedule,
    get_specific_date_schedule, create_event_from_natural_language,
    delete_event_from_natural_language
)
from services.student_chat_service import process_student_grade_query
from services.attendance_chat_service import process_attendance_query
from services.ai_service import ai_service


def get_database_context(db: Session) -> Dict:
    """데이터베이스 컨텍스트 수집 (2025년도 기준)"""
    try:
        from models import User, Class, Student
        
        # 2025년도 학생 수
        total_students = db.query(Student).filter(Student.academic_year == 2025).count()
        
        # 2025년도 반 수
        total_classes = db.query(Class).filter(Class.academic_year == 2025).count()
        
        # 전체 선생님 수 (is_active가 True인 사용자)
        total_teachers = db.query(User).filter(User.is_active == True).count()
        
        # 선생님 명단
        teachers = db.query(User).filter(User.is_active == True).all()
        teacher_names = [teacher.name for teacher in teachers]
        
        # 2025년도 반 정보
        classes = db.query(Class).filter(Class.academic_year == 2025).all()
        class_info = [f"{cls.grade}학년 {cls.class_num}반" for cls in classes]
        
        # 2025년도 학생 명단
        students = db.query(Student).filter(Student.academic_year == 2025).all()
        student_names = [student.name for student in students]
        
        return {
            'total_students': total_students,
            'total_classes': total_classes,
            'total_teachers': total_teachers,
            'teachers': teacher_names,
            'classes': class_info,
            'students': student_names
        }
    except Exception as e:
        print(f"데이터베이스 컨텍스트 수집 오류: {e}")
        return {}


def process_chat_message(chat_request, db: Session, user_id: int = 1) -> str:
    """챗봇 메시지 처리 메인 함수"""
    try:
        # 데이터베이스 컨텍스트 수집
        context = get_database_context(db)
        
        # AI 모델 정보 질문 처리
        if any(keyword in chat_request.message.lower() for keyword in ["현재 연동", "연동된 모델", "어떤 모델", "ai 모델", "모델 정보"]):
            provider_info = ai_service.get_provider_info()
            if provider_info['provider'] == 'OpenAI':
                return f"현재 {provider_info['provider']}의 {provider_info['model']} 모델을 사용하고 있습니다."
            elif provider_info['provider'] == 'Gemini':
                return f"현재 {provider_info['provider']}의 {provider_info['model']} 모델을 사용하고 있습니다."
            else:
                return "현재 사용 중인 AI 모델을 확인할 수 없습니다."

        # 일정 등록 질문 처리 (가장 먼저 체크)
        if any(keyword in chat_request.message for keyword in ["등록해줘", "등록", "추가해줘", "추가", "일정 등록", "일정 추가"]):
            return create_event_from_natural_language(chat_request.message, user_id)
        
        # 일정 삭제 질문 처리
        if any(keyword in chat_request.message for keyword in ["삭제해줘", "삭제", "취소해줘", "취소", "일정 삭제", "일정 취소"]):
            return delete_event_from_natural_language(chat_request.message, user_id)
        
        # 일정 조회 질문 처리
        if any(keyword in chat_request.message for keyword in ["오늘 일정", "오늘의 일정", "오늘 스케줄", "오늘 일정이", "오늘 일정은"]):
            return get_today_schedule(user_id)
        
        # 특정 날짜 일정 조회 (내일, 모레, 글피 등)
        if any(keyword in chat_request.message for keyword in ["내일 일정", "내일의 일정", "내일 스케줄", "내일 일정이", "내일 일정은"]):
            return get_tomorrow_schedule(user_id)
        
        if any(keyword in chat_request.message for keyword in ["모레 일정", "모레의 일정", "모레 스케줄"]):
            return get_specific_date_schedule("모레", user_id)
        
        if any(keyword in chat_request.message for keyword in ["글피 일정", "글피의 일정", "글피 스케줄"]):
            return get_specific_date_schedule("글피", user_id)
        
        if any(keyword in chat_request.message for keyword in ["이번 주 일정", "이번주 일정", "주간 일정", "이번 주 스케줄"]):
            return get_weekly_schedule(user_id)
        
        # 특정 날짜 일정 조회 질문 처리 (등록/삭제가 아닌 경우만)
        if any(keyword in chat_request.message for keyword in ["일정", "스케줄"]) and any(keyword in chat_request.message for keyword in ["월", "/"]):
            # 등록/삭제 키워드가 포함되어 있지 않은지 확인
            if not any(keyword in chat_request.message for keyword in ["등록", "추가", "삭제", "취소"]):
                # 날짜 추출 시도
                import re
                
                # "8월 6일", "8월6일", "8/6" 등의 패턴 매칭
                date_patterns = [
                    r'(\d+)월\s*(\d+)일',
                    r'(\d+)/(\d+)',
                    r'(\d+)\s+(\d+)'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, chat_request.message)
                    if match:
                        month, day = map(int, match.groups())
                        date_str = f"{month}월 {day}일"
                        return get_specific_date_schedule(date_str, user_id)
                
                # 패턴이 매칭되지 않으면 기본 응답
                return "어떤 날짜의 일정을 알고 싶으신가요? '8월 6일' 또는 '8/6' 형식으로 입력해주세요."

        # 출석 관련 질문 처리
        if "출결" in chat_request.message or "출석" in chat_request.message:
            return process_attendance_query(chat_request, context, db)

        # 성적 관련 질문 처리
        if "성적" in chat_request.message or "점수" in chat_request.message:
            return process_student_grade_query(chat_request, context, db)

        # 기본 AI 응답 (오류 처리 강화)
        try:
            system_prompt = f"""당신은 학교 관리 시스템의 AI 어시스턴트입니다.

현재 시스템 정보:
- 전체 학생 수: {context.get('total_students', 0)}명
- 전체 반 수: {context.get('total_classes', 0)}개
- 전체 선생님 수: {context.get('total_teachers', 0)}명

선생님 명단: {', '.join(context.get('teachers', []))}

반 정보:
{chr(10).join([f"- {cls}" for cls in context.get('classes', [])])}

학생 명단 (일부): {', '.join(context.get('students', [])[:10])}

친근하고 도움이 되는 답변을 한국어로 제공해주세요."""

            return ai_service.get_response(system_prompt, chat_request.message)
        except Exception as ai_error:
            print(f"AI 응답 생성 오류: {ai_error}")
            return "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
        
    except Exception as e:
        print(f"채팅 메시지 처리 오류: {e}")
        return "죄송합니다. 메시지 처리 중 오류가 발생했습니다." 