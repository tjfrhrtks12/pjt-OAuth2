"""
학생 정보 관련 챗봇 서비스
학생 정보 조회, 성적 조회 등의 자연어 처리 기능
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import User, Class, Student, Grade, Subject, Exam
from services.grade_service import get_student_grades
import re


def extract_student_name(message: str, student_names: List[str]) -> Optional[str]:
    """메시지에서 학생 이름 추출"""
    try:
        # 학생 이름이 포함된 메시지인지 확인
        for student_name in student_names:
            if student_name in message:
                return student_name
        
        # 정규식으로 더 정확한 매칭 시도
        for student_name in student_names:
            # "~학생의", "~의", "~학생" 패턴 매칭
            patterns = [
                rf"{student_name}학생",
                rf"{student_name}의",
                rf"{student_name}",
                rf"{student_name} 학생"
            ]
            for pattern in patterns:
                if re.search(pattern, message):
                    return student_name
        
        return None
    except Exception as e:
        print(f"학생 이름 추출 오류: {e}")
        return None


def get_student_info(db: Session, student_name: str) -> Optional[Dict]:
    """학생 정보 조회"""
    try:
        student = db.query(Student).filter(Student.name == student_name).first()
        if student:
            class_info = db.query(Class).filter(Class.id == student.class_id).first()
            return {
                'name': student.name,
                'class': f"{class_info.grade}학년 {class_info.class_num}반" if class_info else "알 수 없음",
                'academic_year': student.academic_year
            }
        return None
    except Exception as e:
        print(f"학생 정보 조회 오류: {e}")
        return None


def get_class_info(db: Session, grade: int, class_num: int) -> Optional[Dict]:
    """반 정보 조회"""
    try:
        class_info = db.query(Class).filter(Class.grade == grade, Class.class_num == class_num).first()
        if class_info:
            students = db.query(Student).filter(Student.class_id == class_info.id).all()
            return {
                'grade': grade,
                'class_num': class_num,
                'student_count': len(students),
                'students': [student.name for student in students]
            }
        return None
    except Exception as e:
        print(f"반 정보 조회 오류: {e}")
        return None


def get_teacher_info(db: Session, teacher_name: str) -> Optional[Dict]:
    """선생님 정보 조회"""
    try:
        teacher = db.query(User).filter(User.name == teacher_name, User.is_active == True).first()
        if teacher:
            return {
                'name': teacher.name,
                'login_id': teacher.login_id,
                'is_active': teacher.is_active
            }
        return None
    except Exception as e:
        print(f"선생님 정보 조회 오류: {e}")
        return None


def get_student_grades_by_year(db: Session, student_name: str, academic_year: int) -> Optional[Dict]:
    """특정 연도의 학생 성적 조회"""
    try:
        student = db.query(Student).filter(Student.name == student_name).first()
        if not student:
            return None
        
        grades = db.query(Grade).filter(
            Grade.student_id == student.id,
            Grade.academic_year == academic_year
        ).all()
        
        if not grades:
            return None
        
        # 과목별로 그룹화
        subjects = db.query(Subject).all()
        subject_names = {subject.id: subject.name for subject in subjects}
        
        # 시험별로 그룹화
        exams = db.query(Exam).all()
        exam_names = {exam.id: exam.name for exam in exams}
        
        grade_data = []
        for grade in grades:
            subject_name = subject_names.get(grade.subject_id, "알 수 없음")
            exam_name = exam_names.get(grade.exam_id, "알 수 없음")
            
            grade_data.append({
                'subject': subject_name,
                'exam': exam_name,
                'score': grade.score,
                'exam_date': grade.exam_date
            })
        
        return {
            'student_name': student_name,
            'academic_year': academic_year,
            'grades': grade_data
        }
        
    except Exception as e:
        print(f"학생 성적 조회 오류: {e}")
        return None


def get_student_grades_comparison(db: Session, student_name: str) -> Optional[str]:
    """학년별 성적 비교 조회"""
    try:
        student = db.query(Student).filter(Student.name == student_name).first()
        if not student:
            return f"{student_name} 학생을 찾을 수 없습니다."
        
        # 1학년, 2학년, 3학년 성적 조회
        grades_by_year = {}
        for year in [2023, 2024, 2025]:  # 1학년, 2학년, 3학년
            grades = db.query(Grade).filter(
                Grade.student_id == student.id,
                Grade.academic_year == year
            ).all()
            
            if grades:
                # 과목별 평균 계산
                subjects = db.query(Subject).all()
                subject_names = {subject.id: subject.name for subject in subjects}
                
                subject_scores = {}
                for grade in grades:
                    subject_name = subject_names.get(grade.subject_id, "알 수 없음")
                    if subject_name not in subject_scores:
                        subject_scores[subject_name] = []
                    subject_scores[subject_name].append(grade.score)
                
                # 과목별 평균 계산
                subject_averages = {}
                for subject, scores in subject_scores.items():
                    subject_averages[subject] = sum(scores) / len(scores)
                
                grades_by_year[year] = subject_averages
        
        if not grades_by_year:
            return f"{student_name} 학생의 성적 정보가 없습니다."
        
        # 결과 메시지 생성
        result = f"📊 {student_name} 학생의 학년별 성적 비교입니다:\n\n"
        
        for year, subject_averages in grades_by_year.items():
            grade_level = year - 2022  # 2023년이 1학년
            result += f"🎓 {grade_level}학년 ({year}년)\n"
            
            for subject, average in subject_averages.items():
                result += f"  • {subject}: {average:.1f}점\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        print(f"학년별 성적 비교 조회 오류: {e}")
        return "학년별 성적 비교 조회 중 오류가 발생했습니다."


def process_student_grade_query(chat_request, context: Dict, db: Session) -> str:
    """학생 성적 관련 질문 처리"""
    try:
        student_names = context.get('students', [])
        student_name = extract_student_name(chat_request.message, student_names)
        
        if not student_name:
            print(f"학생 이름 추출 실패. 메시지: {chat_request.message}")
            print(f"사용 가능한 학생들: {student_names[:10]}...")
            return "어떤 학생의 성적을 알고 싶으신가요? 학생 이름을 말씀해주세요."
        
        print(f"학생 이름 추출 성공: {student_name}")
        
        # 학년별 성적 비교 질문 처리
        if any(keyword in chat_request.message for keyword in ["1학년2학년3학년", "1학년 2학년 3학년", "학년별 성적", "3년간 성적"]):
            return get_student_grades_comparison(db, student_name)
        
        # 일반 성적 조회
        grades_info = get_student_grades(db, student_name, 2025)
        if grades_info and grades_info.get('grades'):
            grades_text = "\n".join([
                f"- {grade['subject']} {grade['exam']}: {grade['score']}점"
                for grade in grades_info['grades']
            ])
            return f"{student_name} 학생의 성적입니다:\n{grades_text}"
        else:
            return f"{student_name} 학생의 성적 정보를 찾을 수 없습니다."
            
    except Exception as e:
        print(f"학생 성적 조회 처리 오류: {e}")
        return "학생 성적 조회 중 오류가 발생했습니다." 