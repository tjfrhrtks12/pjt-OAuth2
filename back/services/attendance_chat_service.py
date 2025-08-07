"""
출석 관련 챗봇 서비스
출석 조회, 출석률 분석 등의 자연어 처리 기능
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models import User, Class, Student, Attendance, AttendanceType
from services.attendance_service import get_student_attendance_by_name
import re


def get_student_attendance_by_grade(student_name: str) -> str:
    """학년별 출석률 조회"""
    try:
        from database_service import DatabaseService
        
        with DatabaseService.get_session() as session:
            # 학생 정보 조회
            student = session.query(Student).filter(Student.name == student_name).first()
            if not student:
                return f"{student_name} 학생을 찾을 수 없습니다."
            
            # 1학년, 2학년, 3학년 출석률 조회
            attendance_data = {}
            
            for year in [2023, 2024, 2025]:  # 1학년, 2학년, 3학년
                # 해당 연도의 출석 데이터 조회
                attendance_records = session.query(Attendance).filter(
                    Attendance.student_id == student.id,
                    Attendance.academic_year == year
                ).all()
                
                if attendance_records:
                    total_days = len(attendance_records)
                    
                    # 출석 타입별로 카운트
                    present_days = 0
                    absent_days = 0
                    late_days = 0
                    early_leave_days = 0
                    
                    for record in attendance_records:
                        if record.attendance_type.name == '출석':
                            present_days += 1
                        elif record.attendance_type.name == '결석':
                            absent_days += 1
                        elif record.attendance_type.name == '지각':
                            late_days += 1
                        elif record.attendance_type.name == '조퇴':
                            early_leave_days += 1
                    
                    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                    
                    attendance_data[year] = {
                        'total_days': total_days,
                        'present_days': present_days,
                        'absent_days': absent_days,
                        'late_days': late_days,
                        'early_leave_days': early_leave_days,
                        'attendance_rate': attendance_rate
                    }
            
            if not attendance_data:
                return f"{student_name} 학생의 출석 정보가 없습니다."
            
            # 결과 메시지 생성
            result = f"📊 {student_name} 학생의 학년별 출석률입니다:\n\n"
            
            for year, data in attendance_data.items():
                grade_level = year - 2022  # 2023년이 1학년
                result += f"🎓 {grade_level}학년 ({year}년)\n"
                result += f"  📅 총 수업일: {data['total_days']}일\n"
                result += f"  ✅ 출석: {data['present_days']}일\n"
                result += f"  ❌ 결석: {data['absent_days']}일\n"
                result += f"  ⏰ 지각: {data['late_days']}일\n"
                result += f"  🏃 조퇴: {data['early_leave_days']}일\n"
                result += f"  📈 출석률: {data['attendance_rate']:.1f}%\n\n"
            
            return result
            
    except Exception as e:
        print(f"학년별 출석률 조회 오류: {e}")
        return "학년별 출석률 조회 중 오류가 발생했습니다."


def get_lowest_attendance_students(limit: int = 5) -> str:
    """출석률이 가장 낮은 학생들 조회"""
    try:
        from database_service import DatabaseService
        
        with DatabaseService.get_session() as session:
            # 2025년도 학생들의 출석률 계산
            query = text("""
                SELECT 
                    s.name,
                    COUNT(a.id) as total_days,
                    SUM(CASE WHEN at.name = '출석' THEN 1 ELSE 0 END) as present_days,
                    ROUND(SUM(CASE WHEN at.name = '출석' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 1) as attendance_rate
                FROM students s
                LEFT JOIN attendances a ON s.id = a.student_id AND a.academic_year = 2025
                LEFT JOIN attendance_types at ON a.type_id = at.id
                WHERE s.academic_year = 2025
                GROUP BY s.id, s.name
                HAVING COUNT(a.id) > 0
                ORDER BY attendance_rate ASC
                LIMIT :limit
            """)
            
            result = session.execute(query, {'limit': limit})
            students = result.fetchall()
            
            if not students:
                return "2025년도 출석 데이터가 없습니다."
            
            response = f"📊 출석률이 가장 낮은 학생들 (상위 {len(students)}명):\n\n"
            
            for i, student in enumerate(students, 1):
                name, total_days, present_days, attendance_rate = student
                absent_days = total_days - present_days
                
                response += f"{i}. {name}\n"
                response += f"   📅 총 수업일: {total_days}일\n"
                response += f"   ✅ 출석: {present_days}일\n"
                response += f"   ❌ 결석: {absent_days}일\n"
                response += f"   📈 출석률: {attendance_rate}%\n\n"
            
            return response
            
    except Exception as e:
        print(f"낮은 출석률 학생 조회 오류: {e}")
        return "출석률이 낮은 학생 조회 중 오류가 발생했습니다."


def get_highest_attendance_students(limit: int = 5) -> str:
    """출석률이 가장 높은 학생들 조회"""
    try:
        from database_service import DatabaseService
        
        with DatabaseService.get_session() as session:
            # 2025년도 학생들의 출석률 계산
            query = text("""
                SELECT 
                    s.name,
                    COUNT(a.id) as total_days,
                    SUM(CASE WHEN at.name = '출석' THEN 1 ELSE 0 END) as present_days,
                    ROUND(SUM(CASE WHEN at.name = '출석' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 1) as attendance_rate
                FROM students s
                LEFT JOIN attendances a ON s.id = a.student_id AND a.academic_year = 2025
                LEFT JOIN attendance_types at ON a.type_id = at.id
                WHERE s.academic_year = 2025
                GROUP BY s.id, s.name
                HAVING COUNT(a.id) > 0
                ORDER BY attendance_rate DESC
                LIMIT :limit
            """)
            
            result = session.execute(query, {'limit': limit})
            students = result.fetchall()
            
            if not students:
                return "2025년도 출석 데이터가 없습니다."
            
            response = f"📊 출석률이 가장 높은 학생들 (상위 {len(students)}명):\n\n"
            
            for i, student in enumerate(students, 1):
                name, total_days, present_days, attendance_rate = student
                absent_days = total_days - present_days
                
                response += f"{i}. {name}\n"
                response += f"   📅 총 수업일: {total_days}일\n"
                response += f"   ✅ 출석: {present_days}일\n"
                response += f"   ❌ 결석: {absent_days}일\n"
                response += f"   📈 출석률: {attendance_rate}%\n\n"
            
            return response
            
    except Exception as e:
        print(f"높은 출석률 학생 조회 오류: {e}")
        return "출석률이 높은 학생 조회 중 오류가 발생했습니다."


def get_student_attendance_info(student_name: str) -> str:
    """학생 출석 정보 조회"""
    try:
        from database_service import DatabaseService
        
        with DatabaseService.get_session() as session:
            # 학생 정보 조회
            student = session.query(Student).filter(Student.name == student_name).first()
            if not student:
                return f"{student_name} 학생을 찾을 수 없습니다."
            
            # 2025년도 출석 데이터 조회
            attendance_records = session.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.academic_year == 2025
            ).order_by(Attendance.date.desc()).limit(10).all()  # 최근 10일
            
            if not attendance_records:
                return f"{student_name} 학생의 2025년도 출석 정보가 없습니다."
            
            # 전체 출석률 계산
            total_records = session.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.academic_year == 2025
            ).all()
            
            total_days = len(total_records)
            present_days = 0
            absent_days = 0
            late_days = 0
            early_leave_days = 0
            
            for record in total_records:
                if record.attendance_type.name == '출석':
                    present_days += 1
                elif record.attendance_type.name == '결석':
                    absent_days += 1
                elif record.attendance_type.name == '지각':
                    late_days += 1
                elif record.attendance_type.name == '조퇴':
                    early_leave_days += 1
            
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            # 결과 메시지 생성
            result = f"📊 {student_name} 학생의 출석 정보입니다:\n\n"
            result += f"📅 총 수업일: {total_days}일\n"
            result += f"✅ 출석: {present_days}일\n"
            result += f"❌ 결석: {absent_days}일\n"
            result += f"⏰ 지각: {late_days}일\n"
            result += f"🏃 조퇴: {early_leave_days}일\n"
            result += f"📈 출석률: {attendance_rate:.1f}%\n\n"
            
            # 최근 출석 기록
            result += "📋 최근 출석 기록:\n"
            for record in attendance_records:
                status_emoji = {
                    '출석': '✅',
                    '결석': '❌',
                    '지각': '⏰',
                    '조퇴': '🏃'
                }.get(record.attendance_type.name, '❓')
                
                result += f"  {record.date.strftime('%m월 %d일')}: {status_emoji} {record.attendance_type.name}\n"
            
            return result
            
    except Exception as e:
        print(f"학생 출석 정보 조회 오류: {e}")
        return "학생 출석 정보 조회 중 오류가 발생했습니다."


def process_attendance_query(chat_request, context: Dict, db: Session) -> str:
    """출석 관련 질문 처리"""
    try:
        student_names = context.get('students', [])
        student_name = None
        
        # 학생 이름이 포함된 경우
        for name in student_names:
            if name in chat_request.message:
                student_name = name
                break
        
        if not student_name:
            # 출석률 비교 질문 처리
            if any(keyword in chat_request.message for keyword in ["가장 안좋은", "제일 안좋은", "낮은", "최악"]):
                return get_lowest_attendance_students()
            elif any(keyword in chat_request.message for keyword in ["가장 좋은", "제일 좋은", "높은", "최고"]):
                return get_highest_attendance_students()
            else:
                return "어떤 학생의 출석 정보를 알고 싶으신가요? 학생 이름을 말씀해주세요."
        
        # 학년별 출석률 조회
        if any(keyword in chat_request.message for keyword in ["1학년2학년3학년", "1학년 2학년 3학년", "학년별 출석률", "학년별 출결률"]):
            return get_student_attendance_by_grade(student_name)
        
        # 일반 출석 정보 조회
        return get_student_attendance_info(student_name)
        
    except Exception as e:
        print(f"출석 조회 처리 오류: {e}")
        return "출석 정보 조회 중 오류가 발생했습니다." 