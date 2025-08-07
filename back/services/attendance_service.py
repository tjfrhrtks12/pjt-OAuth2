from database_service import DatabaseService
from datetime import datetime
from sqlalchemy import func, and_, or_
from models import Student, Class, Attendance, AttendanceType, AttendanceReason, MonthlyAttendance, YearlyAttendance

def get_student_attendance_by_name(student_name):
    """학생 이름으로 출결 데이터 조회"""
    try:
        with DatabaseService.get_session() as session:
            # 학생 정보 조회
            student = session.query(Student).filter(
                Student.name == student_name
            ).first()
            
            if not student:
                return None
            
            # 연도별 출결 통계 조회
            yearly_attendance = session.query(YearlyAttendance).filter(
                YearlyAttendance.student_id == student.id
            ).order_by(YearlyAttendance.year.desc()).all()
            
            # 월별 출결 통계 조회 (최근 3개월)
            monthly_attendance = session.query(MonthlyAttendance).filter(
                MonthlyAttendance.student_id == student.id
            ).order_by(MonthlyAttendance.year.desc(), MonthlyAttendance.month.desc()).limit(3).all()
            
            # 최근 출결 기록 조회 (최근 10일)
            recent_attendance = session.query(
                Attendance, AttendanceType, AttendanceReason
            ).join(
                AttendanceType, Attendance.type_id == AttendanceType.id
            ).outerjoin(
                AttendanceReason, Attendance.reason_id == AttendanceReason.id
            ).filter(
                Attendance.student_id == student.id
            ).order_by(
                Attendance.date.desc()
            ).limit(10).all()
            
            return {
                'student': {
                    'id': student.id,
                    'name': student.name,
                    'class_id': student.class_id,
                    'academic_year': student.academic_year
                },
                'yearly_attendance': [
                    {
                        'year': ya.year,
                        'total_days': ya.total_days,
                        'present_days': ya.present_days,
                        'absent_days': ya.absent_days,
                        'late_days': ya.late_days,
                        'early_leave_days': ya.early_leave_days,
                        'attendance_rate': ya.attendance_rate
                    } for ya in yearly_attendance
                ],
                'monthly_attendance': [
                    {
                        'year': ma.year,
                        'month': ma.month,
                        'total_days': ma.total_days,
                        'present_days': ma.present_days,
                        'absent_days': ma.absent_days,
                        'late_days': ma.late_days,
                        'early_leave_days': ma.early_leave_days,
                        'attendance_rate': ma.attendance_rate
                    } for ma in monthly_attendance
                ],
                'recent_attendance': [
                    {
                        'date': att.date.strftime('%Y-%m-%d'),
                        'type': att_type.name,
                        'reason': att_reason.name if att_reason else None,
                        'note': att.note
                    } for att, att_type, att_reason in recent_attendance
                ]
            }
    except Exception as e:
        print(f"학생 출결 데이터 조회 오류: {e}")
        return None

def get_class_attendance_summary(grade, class_num, year=2024):
    """학급별 출결 통계 조회"""
    try:
        with DatabaseService.get_session() as session:
            # 해당 반 학생들의 연도별 출결 통계
            class_attendance = session.query(
                Student.name,
                YearlyAttendance.total_days,
                YearlyAttendance.present_days,
                YearlyAttendance.absent_days,
                YearlyAttendance.late_days,
                YearlyAttendance.early_leave_days,
                YearlyAttendance.attendance_rate
            ).join(
                YearlyAttendance, Student.id == YearlyAttendance.student_id
            ).join(
                Class, Student.class_id == Class.id
            ).filter(
                Class.grade == grade,
                Class.class_num == class_num,
                YearlyAttendance.year == year
            ).order_by(
                YearlyAttendance.attendance_rate.desc()
            ).all()
            
            if not class_attendance:
                return None
            
            # 반 전체 통계 계산
            total_students = len(class_attendance)
            avg_attendance_rate = sum(ca.attendance_rate for ca in class_attendance) / total_students
            perfect_attendance_count = sum(1 for ca in class_attendance if ca.attendance_rate == 100.0)
            
            return {
                'class_info': f"{grade}학년 {class_num}반",
                'year': year,
                'total_students': total_students,
                'avg_attendance_rate': round(avg_attendance_rate, 1),
                'perfect_attendance_count': perfect_attendance_count,
                'students': [
                    {
                        'name': ca.name,
                        'total_days': ca.total_days,
                        'present_days': ca.present_days,
                        'absent_days': ca.absent_days,
                        'late_days': ca.late_days,
                        'early_leave_days': ca.early_leave_days,
                        'attendance_rate': ca.attendance_rate
                    } for ca in class_attendance
                ]
            }
    except Exception as e:
        print(f"학급 출결 통계 조회 오류: {e}")
        return None

def get_grade_attendance_analysis(grade, year=2024):
    """학년별 출결 분석"""
    try:
        with DatabaseService.get_session() as session:
            # 학년 전체 학생들의 출결 통계
            grade_attendance = session.query(
                Student.name,
                Class.class_num,
                YearlyAttendance.attendance_rate
            ).join(
                YearlyAttendance, Student.id == YearlyAttendance.student_id
            ).join(
                Class, Student.class_id == Class.id
            ).filter(
                Class.grade == grade,
                YearlyAttendance.year == year
            ).order_by(
                YearlyAttendance.attendance_rate.desc()
            ).all()
            
            if not grade_attendance:
                return None
            
            # 통계 계산
            total_students = len(grade_attendance)
            avg_attendance_rate = sum(ga.attendance_rate for ga in grade_attendance) / total_students
            perfect_attendance_count = sum(1 for ga in grade_attendance if ga.attendance_rate == 100.0)
            
            # 반별 평균 출석률
            class_stats = {}
            for ga in grade_attendance:
                if ga.class_num not in class_stats:
                    class_stats[ga.class_num] = {'total': 0, 'sum': 0}
                class_stats[ga.class_num]['total'] += 1
                class_stats[ga.class_num]['sum'] += ga.attendance_rate
            
            class_averages = {
                class_num: round(stats['sum'] / stats['total'], 1)
                for class_num, stats in class_stats.items()
            }
            
            return {
                'grade': grade,
                'year': year,
                'total_students': total_students,
                'avg_attendance_rate': round(avg_attendance_rate, 1),
                'perfect_attendance_count': perfect_attendance_count,
                'class_averages': class_averages,
                'top_students': [
                    {
                        'name': ga.name,
                        'class': f"{grade}학년 {ga.class_num}반",
                        'attendance_rate': ga.attendance_rate
                    } for ga in grade_attendance[:5]  # 상위 5명
                ],
                'bottom_students': [
                    {
                        'name': ga.name,
                        'class': f"{grade}학년 {ga.class_num}반",
                        'attendance_rate': ga.attendance_rate
                    } for ga in grade_attendance[-5:]  # 하위 5명
                ]
            }
    except Exception as e:
        print(f"학년 출결 분석 오류: {e}")
        return None

def get_attendance_pattern_analysis(student_name):
    """학생의 출결 패턴 분석"""
    try:
        with DatabaseService.get_session() as session:
            # 학생 정보 조회
            student = session.query(Student).filter(
                Student.name == student_name
            ).first()
            
            if not student:
                return None
            
            # 결석/지각/조퇴 사유 분석
            attendance_reasons = session.query(
                AttendanceReason.name,
                func.count(Attendance.id).label('count')
            ).join(
                Attendance, Attendance.reason_id == AttendanceReason.id
            ).filter(
                Attendance.student_id == student.id
            ).group_by(
                AttendanceReason.name
            ).order_by(
                func.count(Attendance.id).desc()
            ).all()
            
            # 월별 출결 패턴
            monthly_pattern = session.query(
                MonthlyAttendance.month,
                MonthlyAttendance.attendance_rate,
                MonthlyAttendance.absent_days,
                MonthlyAttendance.late_days
            ).filter(
                MonthlyAttendance.student_id == student.id
            ).order_by(
                MonthlyAttendance.year.desc(),
                MonthlyAttendance.month.desc()
            ).limit(12).all()
            
            # 연도별 출결 변화
            yearly_change = session.query(
                YearlyAttendance.year,
                YearlyAttendance.attendance_rate,
                YearlyAttendance.absent_days,
                YearlyAttendance.late_days
            ).filter(
                YearlyAttendance.student_id == student.id
            ).order_by(
                YearlyAttendance.year.desc()
            ).all()
            
            return {
                'student_name': student.name,
                'reasons_analysis': [
                    {
                        'reason': ar.name,
                        'count': ar.count
                    } for ar in attendance_reasons
                ],
                'monthly_pattern': [
                    {
                        'month': mp.month,
                        'attendance_rate': mp.attendance_rate,
                        'absent_days': mp.absent_days,
                        'late_days': mp.late_days
                    } for mp in monthly_pattern
                ],
                'yearly_change': [
                    {
                        'year': yc.year,
                        'attendance_rate': yc.attendance_rate,
                        'absent_days': yc.absent_days,
                        'late_days': yc.late_days
                    } for yc in yearly_change
                ]
            }
    except Exception as e:
        print(f"출결 패턴 분석 오류: {e}")
        return None

def get_low_attendance_students(grade=None, limit=10):
    """출석률이 낮은 학생들 조회"""
    try:
        with DatabaseService.get_session() as session:
            query = session.query(
                Student.name,
                Class.grade,
                Class.class_num,
                YearlyAttendance.attendance_rate,
                YearlyAttendance.absent_days,
                YearlyAttendance.late_days
            ).join(
                YearlyAttendance, Student.id == YearlyAttendance.student_id
            ).join(
                Class, Student.class_id == Class.id
            ).filter(
                YearlyAttendance.year == 2024
            )
            
            if grade:
                query = query.filter(Class.grade == grade)
            
            low_attendance_students = query.order_by(
                YearlyAttendance.attendance_rate.asc()
            ).limit(limit).all()
            
            return [
                {
                    'name': las.name,
                    'class': f"{las.grade}학년 {las.class_num}반",
                    'attendance_rate': las.attendance_rate,
                    'absent_days': las.absent_days,
                    'late_days': las.late_days
                } for las in low_attendance_students
            ]
    except Exception as e:
        print(f"낮은 출석률 학생 조회 오류: {e}")
        return []

def get_perfect_attendance_students(grade=None):
    """완벽 출석 학생들 조회"""
    try:
        with DatabaseService.get_session() as session:
            query = session.query(
                Student.name,
                Class.grade,
                Class.class_num,
                YearlyAttendance.attendance_rate
            ).join(
                YearlyAttendance, Student.id == YearlyAttendance.student_id
            ).join(
                Class, Student.class_id == Class.id
            ).filter(
                YearlyAttendance.year == 2024,
                YearlyAttendance.attendance_rate == 100.0
            )
            
            if grade:
                query = query.filter(Class.grade == grade)
            
            perfect_students = query.order_by(
                Student.grade,
                Student.class_num,
                Student.name
            ).all()
            
            return [
                {
                    'name': ps.name,
                    'class': f"{ps.grade}학년 {ps.class_num}반",
                    'attendance_rate': ps.attendance_rate
                } for ps in perfect_students
            ]
    except Exception as e:
        print(f"완벽 출석 학생 조회 오류: {e}")
        return [] 