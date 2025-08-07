from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Class, Student, Grade, Subject, Exam, AttendanceType, AttendanceReason, Attendance, MonthlyAttendance, YearlyAttendance
from config import SessionLocal
from typing import List, Dict, Optional

class DatabaseService:
    """기본 데이터베이스 서비스 클래스"""
    
    @staticmethod
    def get_session():
        return SessionLocal()
    
    @staticmethod
    def test_connection() -> bool:
        """데이터베이스 연결 테스트"""
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return False
    
    @staticmethod
    def get_database_info() -> Dict:
        """데이터베이스 정보 조회"""
        try:
            db = SessionLocal()
            result = db.execute("SELECT VERSION()").fetchone()
            db.close()
            return {
                "status": "connected",
                "version": result[0] if result else "unknown"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_all_tables() -> List[str]:
        """모든 테이블 목록 조회"""
        try:
            db = SessionLocal()
            result = db.execute("SHOW TABLES").fetchall()
            db.close()
            return [row[0] for row in result]
        except Exception as e:
            print(f"테이블 목록 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    # 반 관련 기능들
    @staticmethod
    def get_all_classes(academic_year: int = 2024) -> List[Dict]:
        """모든 반 정보 조회"""
        try:
            db = SessionLocal()
            classes = db.query(Class).filter(Class.academic_year == academic_year).all()
            
            return [
                {
                    "id": class_obj.id,
                    "academic_year": class_obj.academic_year,
                    "grade": class_obj.grade,
                    "class_num": class_obj.class_num,
                    "teacher_name": class_obj.teacher.name if class_obj.teacher else None,
                    "teacher_id": class_obj.teacher_id
                }
                for class_obj in classes
            ]
        except Exception as e:
            print(f"반 정보 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_classes_by_teacher(teacher_id: int, academic_year: int = 2024) -> List[Dict]:
        """특정 선생님이 담당하는 모든 반 조회"""
        try:
            db = SessionLocal()
            classes = db.query(Class).filter(
                Class.teacher_id == teacher_id,
                Class.academic_year == academic_year
            ).all()
            
            return [
                {
                    "id": class_obj.id,
                    "academic_year": class_obj.academic_year,
                    "grade": class_obj.grade,
                    "class_num": class_obj.class_num
                }
                for class_obj in classes
            ]
        except Exception as e:
            print(f"선생님 반 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_all_teachers() -> List[Dict]:
        """모든 선생님 조회"""
        try:
            db = SessionLocal()
            users = db.query(User).filter(User.is_active == True).all()
            
            return [
                {
                    "id": user.id,
                    "name": user.name,
                    "login_id": user.login_id,
                    "classes": [
                        {
                            "academic_year": class_obj.academic_year,
                            "grade": class_obj.grade,
                            "class_num": class_obj.class_num
                        }
                        for class_obj in user.classes
                    ]
                }
                for user in users
            ]
        except Exception as e:
            print(f"선생님 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_homeroom_teacher(grade: int, class_num: int, academic_year: int = 2024) -> Optional[Dict]:
        """특정 반의 담임선생님 조회"""
        try:
            db = SessionLocal()
            class_obj = db.query(Class).filter(
                Class.academic_year == academic_year,
                Class.grade == grade, 
                Class.class_num == class_num
            ).first()
            
            if not class_obj or not class_obj.teacher:
                return None
            
            teacher = class_obj.teacher
            return {
                "id": teacher.id,
                "name": teacher.name,
                "login_id": teacher.login_id,
                "grade": class_obj.grade,
                "class_num": class_obj.class_num,
                "academic_year": class_obj.academic_year
            }
        except Exception as e:
            print(f"담임선생님 조회 오류: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def create_class(grade: int, class_num: int, teacher_id: int, academic_year: int = 2024) -> bool:
        """새로운 반 생성"""
        try:
            db = SessionLocal()
            
            # 이미 존재하는지 확인
            existing_class = db.query(Class).filter(
                Class.academic_year == academic_year,
                Class.grade == grade, 
                Class.class_num == class_num
            ).first()
            if existing_class:
                print(f"{academic_year}년 {grade}학년 {class_num}반이 이미 존재합니다.")
                return False
            
            # 새 반 생성
            new_class = Class(academic_year=academic_year, grade=grade, class_num=class_num, teacher_id=teacher_id)
            db.add(new_class)
            db.commit()
            
            print(f"{academic_year}년 {grade}학년 {class_num}반이 성공적으로 생성되었습니다.")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"반 생성 오류: {e}")
            return False
        finally:
            db.close()
    
    # 학생 관련 기능들
    @staticmethod
    def create_student(name: str, class_id: int, academic_year: int = 2024) -> bool:
        """새로운 학생 생성"""
        try:
            db = SessionLocal()
            
            # 반이 존재하는지 확인
            class_obj = db.query(Class).filter(Class.id == class_id).first()
            if not class_obj:
                print(f"반 ID {class_id}가 존재하지 않습니다.")
                return False
            
            # 새 학생 생성
            new_student = Student(name=name, class_id=class_id, academic_year=academic_year)
            db.add(new_student)
            db.commit()
            
            print(f"학생 '{name}'이(가) 성공적으로 생성되었습니다.")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"학생 생성 오류: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_students_by_class(class_id: int, academic_year: int = 2024) -> List[Dict]:
        """특정 반의 학생들 조회"""
        try:
            db = SessionLocal()
            students = db.query(Student).filter(
                Student.class_id == class_id,
                Student.academic_year == academic_year
            ).all()
            
            return [
                {
                    "id": student.id,
                    "name": student.name,
                    "academic_year": student.academic_year,
                    "class_id": student.class_id
                }
                for student in students
            ]
        except Exception as e:
            print(f"학생 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_all_students(academic_year: int = 2024) -> List[Dict]:
        """모든 학생 조회"""
        try:
            db = SessionLocal()
            students = db.query(Student).filter(Student.academic_year == academic_year).all()
            
            return [
                {
                    "id": student.id,
                    "name": student.name,
                    "academic_year": student.academic_year,
                    "class_id": student.class_id,
                    "class_info": f"{student.class_info.grade}학년 {student.class_info.class_num}반" if student.class_info else None
                }
                for student in students
            ]
        except Exception as e:
            print(f"전체 학생 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    # 성적 관련 기능들
    @staticmethod
    def create_grade(student_id: int, subject_id: int, exam_id: int, score: int, academic_year: int = 2024) -> bool:
        """새로운 성적 생성"""
        try:
            db = SessionLocal()
            
            # 학생이 존재하는지 확인
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                print(f"학생 ID {student_id}가 존재하지 않습니다.")
                return False
            
            # 과목이 존재하는지 확인
            subject = db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                print(f"과목 ID {subject_id}가 존재하지 않습니다.")
                return False
            
            # 시험이 존재하는지 확인
            exam = db.query(Exam).filter(Exam.id == exam_id).first()
            if not exam:
                print(f"시험 ID {exam_id}가 존재하지 않습니다.")
                return False
            
            # 이미 동일한 성적이 있는지 확인
            existing_grade = db.query(Grade).filter(
                Grade.student_id == student_id,
                Grade.subject_id == subject_id,
                Grade.exam_id == exam_id,
                Grade.academic_year == academic_year
            ).first()
            
            if existing_grade:
                print(f"이미 동일한 성적이 존재합니다.")
                return False
            
            # 새 성적 생성
            new_grade = Grade(
                student_id=student_id,
                subject_id=subject_id,
                exam_id=exam_id,
                score=score,
                academic_year=academic_year
            )
            db.add(new_grade)
            db.commit()
            
            print(f"성적이 성공적으로 생성되었습니다.")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"성적 생성 오류: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_student_grades(student_id: int, academic_year: int = 2024) -> List[Dict]:
        """특정 학생의 성적 조회"""
        try:
            db = SessionLocal()
            grades = db.query(
                Grade.score,
                Subject.name.label('subject_name'),
                Exam.name.label('exam_name')
            ).join(
                Subject, Grade.subject_id == Subject.id
            ).join(
                Exam, Grade.exam_id == Exam.id
            ).filter(
                Grade.student_id == student_id,
                Grade.academic_year == academic_year
            ).all()
            
            return [
                {
                    "subject": grade.subject_name,
                    "exam": grade.exam_name,
                    "score": grade.score
                }
                for grade in grades
            ]
        except Exception as e:
            print(f"학생 성적 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_class_grades(class_id: int, academic_year: int = 2024) -> List[Dict]:
        """특정 반의 모든 성적 조회"""
        try:
            db = SessionLocal()
            grades = db.query(
                Student.name.label('student_name'),
                Subject.name.label('subject_name'),
                Exam.name.label('exam_name'),
                Grade.score
            ).join(
                Student, Grade.student_id == Student.id
            ).join(
                Subject, Grade.subject_id == Subject.id
            ).join(
                Exam, Grade.exam_id == Exam.id
            ).filter(
                Student.class_id == class_id,
                Grade.academic_year == academic_year
            ).all()
            
            return [
                {
                    "student_name": grade.student_name,
                    "subject": grade.subject_name,
                    "exam": grade.exam_name,
                    "score": grade.score
                }
                for grade in grades
            ]
        except Exception as e:
            print(f"반 성적 조회 오류: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def create_attendance_type(name: str, code: str, description: str = None) -> bool:
        """출결 유형 생성"""
        try:
            with DatabaseService.get_session() as session:
                new_attendance_type = AttendanceType(
                    name=name,
                    code=code,
                    description=description
                )
                session.add(new_attendance_type)
                session.commit()
                return True
        except Exception as e:
            print(f"출결 유형 생성 실패: {e}")
            return False

    @staticmethod
    def get_all_attendance_types():
        """모든 출결 유형 조회"""
        try:
            with DatabaseService.get_session() as session:
                attendance_types = session.query(AttendanceType).all()
                return [
                    {
                        "id": at.id,
                        "name": at.name,
                        "code": at.code,
                        "description": at.description
                    } for at in attendance_types
                ]
        except Exception as e:
            print(f"출결 유형 조회 실패: {e}")
            return []

    @staticmethod
    def initialize_attendance_types():
        """기본 출결 유형 초기화"""
        try:
            default_types = [
                {"name": "출석", "code": "PRESENT", "description": "정상 출석"},
                {"name": "결석", "code": "ABSENT", "description": "결석"},
                {"name": "지각", "code": "LATE", "description": "지각"},
                {"name": "조퇴", "code": "EARLY", "description": "조퇴"},
                {"name": "공결", "code": "OFFICIAL", "description": "공식 결석"}
            ]
            
            with DatabaseService.get_session() as session:
                for type_data in default_types:
                    existing = session.query(AttendanceType).filter(AttendanceType.code == type_data["code"]).first()
                    if not existing:
                        new_type = AttendanceType(**type_data)
                        session.add(new_type)
                
                session.commit()
                print("✅ 기본 출결 유형 초기화 완료!")
                return True
        except Exception as e:
            print(f"❌ 출결 유형 초기화 실패: {e}")
            return False
    
    @staticmethod
    def create_attendance_reason(name: str, code: str, description: str = None) -> bool:
        """결석 사유 생성"""
        try:
            with DatabaseService.get_session() as session:
                new_attendance_reason = AttendanceReason(
                    name=name,
                    code=code,
                    description=description
                )
                session.add(new_attendance_reason)
                session.commit()
                return True
        except Exception as e:
            print(f"결석 사유 생성 실패: {e}")
            return False

    @staticmethod
    def get_all_attendance_reasons():
        """모든 결석 사유 조회"""
        try:
            with DatabaseService.get_session() as session:
                attendance_reasons = session.query(AttendanceReason).all()
                return [
                    {
                        "id": ar.id,
                        "name": ar.name,
                        "code": ar.code,
                        "description": ar.description
                    } for ar in attendance_reasons
                ]
        except Exception as e:
            print(f"결석 사유 조회 실패: {e}")
            return []

    @staticmethod
    def initialize_attendance_reasons():
        """기본 결석 사유 초기화"""
        try:
            default_reasons = [
                {"name": "질병", "code": "ILLNESS", "description": "병원진단서, 의사소견서"},
                {"name": "개인사", "code": "PERSONAL", "description": "개인적 사정"},
                {"name": "가족사", "code": "FAMILY", "description": "가족 행사, 사고"},
                {"name": "학교행사", "code": "SCHOOL", "description": "대회, 대표활동"},
                {"name": "기타", "code": "OTHER", "description": "기타 사유"}
            ]
            
            with DatabaseService.get_session() as session:
                for reason_data in default_reasons:
                    existing = session.query(AttendanceReason).filter(AttendanceReason.code == reason_data["code"]).first()
                    if not existing:
                        new_reason = AttendanceReason(**reason_data)
                        session.add(new_reason)
                
                session.commit()
                print("✅ 기본 결석 사유 초기화 완료!")
                return True
        except Exception as e:
            print(f"❌ 결석 사유 초기화 실패: {e}")
            return False
    
    @staticmethod
    def create_attendance(student_id: int, type_id: int, date: str, reason_id: int = None, reason_detail: str = None, note: str = None) -> bool:
        """출결 기록 생성"""
        try:
            with DatabaseService.get_session() as session:
                new_attendance = Attendance(
                    student_id=student_id,
                    type_id=type_id,
                    reason_id=reason_id,
                    date=date,
                    reason_detail=reason_detail,
                    note=note
                )
                session.add(new_attendance)
                session.commit()
                return True
        except Exception as e:
            print(f"출결 기록 생성 실패: {e}")
            return False

    @staticmethod
    def get_student_attendances(student_id: int, start_date: str = None, end_date: str = None):
        """학생별 출결 기록 조회"""
        try:
            with DatabaseService.get_session() as session:
                query = session.query(Attendance).filter(Attendance.student_id == student_id)
                
                if start_date:
                    query = query.filter(Attendance.date >= start_date)
                if end_date:
                    query = query.filter(Attendance.date <= end_date)
                
                attendances = query.order_by(Attendance.date.desc()).all()
                return [
                    {
                        "id": a.id,
                        "student_id": a.student_id,
                        "type_id": a.type_id,
                        "reason_id": a.reason_id,
                        "date": a.date.strftime("%Y-%m-%d"),
                        "reason_detail": a.reason_detail,
                        "note": a.note,
                        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    } for a in attendances
                ]
        except Exception as e:
            print(f"학생 출결 기록 조회 실패: {e}")
            return []

    @staticmethod
    def get_class_attendances(class_id: int, date: str = None):
        """반별 출결 기록 조회"""
        try:
            with DatabaseService.get_session() as session:
                query = session.query(Attendance).join(Student).filter(Student.class_id == class_id)
                
                if date:
                    query = query.filter(Attendance.date == date)
                
                attendances = query.order_by(Attendance.date.desc()).all()
                return [
                    {
                        "id": a.id,
                        "student_id": a.student_id,
                        "student_name": a.student.name,
                        "type_id": a.type_id,
                        "reason_id": a.reason_id,
                        "date": a.date.strftime("%Y-%m-%d"),
                        "reason_detail": a.reason_detail,
                        "note": a.note
                    } for a in attendances
                ]
        except Exception as e:
            print(f"반 출결 기록 조회 실패: {e}")
            return []
    
    @staticmethod
    def create_monthly_attendance(student_id: int, year: int, month: int, total_days: int = 0, present_days: int = 0, absent_days: int = 0, late_days: int = 0, early_leave_days: int = 0) -> bool:
        """월별 출결 통계 생성"""
        try:
            # 출석률 계산
            attendance_rate = 0
            if total_days > 0:
                attendance_rate = int((present_days / total_days) * 100)
            
            with DatabaseService.get_session() as session:
                # 기존 데이터 확인
                existing = session.query(MonthlyAttendance).filter(
                    MonthlyAttendance.student_id == student_id,
                    MonthlyAttendance.year == year,
                    MonthlyAttendance.month == month
                ).first()
                
                if existing:
                    # 기존 데이터 업데이트
                    existing.total_days = total_days
                    existing.present_days = present_days
                    existing.absent_days = absent_days
                    existing.late_days = late_days
                    existing.early_leave_days = early_leave_days
                    existing.attendance_rate = attendance_rate
                else:
                    # 새 데이터 생성
                    new_monthly = MonthlyAttendance(
                        student_id=student_id,
                        year=year,
                        month=month,
                        total_days=total_days,
                        present_days=present_days,
                        absent_days=absent_days,
                        late_days=late_days,
                        early_leave_days=early_leave_days,
                        attendance_rate=attendance_rate
                    )
                    session.add(new_monthly)
                
                session.commit()
                return True
        except Exception as e:
            print(f"월별 출결 통계 생성 실패: {e}")
            return False

    @staticmethod
    def get_student_monthly_attendance(student_id: int, year: int = None):
        """학생별 월별 출결 통계 조회"""
        try:
            with DatabaseService.get_session() as session:
                query = session.query(MonthlyAttendance).filter(MonthlyAttendance.student_id == student_id)
                
                if year:
                    query = query.filter(MonthlyAttendance.year == year)
                
                monthly_attendances = query.order_by(MonthlyAttendance.year.desc(), MonthlyAttendance.month.desc()).all()
                return [
                    {
                        "id": ma.id,
                        "student_id": ma.student_id,
                        "year": ma.year,
                        "month": ma.month,
                        "total_days": ma.total_days,
                        "present_days": ma.present_days,
                        "absent_days": ma.absent_days,
                        "late_days": ma.late_days,
                        "early_leave_days": ma.early_leave_days,
                        "attendance_rate": ma.attendance_rate
                    } for ma in monthly_attendances
                ]
        except Exception as e:
            print(f"학생 월별 출결 통계 조회 실패: {e}")
            return []

    @staticmethod
    def calculate_monthly_attendance(student_id: int, year: int, month: int) -> bool:
        """월별 출결 통계 자동 계산"""
        try:
            with DatabaseService.get_session() as session:
                # 해당 월의 출결 데이터 조회
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1}-01-01"
                else:
                    end_date = f"{year}-{month+1:02d}-01"
                
                attendances = session.query(Attendance).filter(
                    Attendance.student_id == student_id,
                    Attendance.date >= start_date,
                    Attendance.date < end_date
                ).all()
                
                # 통계 계산
                total_days = len(attendances)
                present_days = len([a for a in attendances if a.type_id == 1])  # 출석
                absent_days = len([a for a in attendances if a.type_id == 2])   # 결석
                late_days = len([a for a in attendances if a.type_id == 3])     # 지각
                early_leave_days = len([a for a in attendances if a.type_id == 4])  # 조퇴
                
                # 월별 통계 생성/업데이트
                return DatabaseService.create_monthly_attendance(
                    student_id=student_id,
                    year=year,
                    month=month,
                    total_days=total_days,
                    present_days=present_days,
                    absent_days=absent_days,
                    late_days=late_days,
                    early_leave_days=early_leave_days
                )
                
        except Exception as e:
            print(f"월별 출결 통계 계산 실패: {e}")
            return False
    
    @staticmethod
    def create_yearly_attendance(student_id: int, year: int, total_days: int = 0, present_days: int = 0, absent_days: int = 0, late_days: int = 0, early_leave_days: int = 0) -> bool:
        """연도별 출결 통계 생성"""
        try:
            # 출석률 계산
            attendance_rate = 0
            if total_days > 0:
                attendance_rate = int((present_days / total_days) * 100)
            
            with DatabaseService.get_session() as session:
                # 기존 데이터 확인
                existing = session.query(YearlyAttendance).filter(
                    YearlyAttendance.student_id == student_id,
                    YearlyAttendance.year == year
                ).first()
                
                if existing:
                    # 기존 데이터 업데이트
                    existing.total_days = total_days
                    existing.present_days = present_days
                    existing.absent_days = absent_days
                    existing.late_days = late_days
                    existing.early_leave_days = early_leave_days
                    existing.attendance_rate = attendance_rate
                else:
                    # 새 데이터 생성
                    new_yearly = YearlyAttendance(
                        student_id=student_id,
                        year=year,
                        total_days=total_days,
                        present_days=present_days,
                        absent_days=absent_days,
                        late_days=late_days,
                        early_leave_days=early_leave_days,
                        attendance_rate=attendance_rate
                    )
                    session.add(new_yearly)
                
                session.commit()
                return True
        except Exception as e:
            print(f"연도별 출결 통계 생성 실패: {e}")
            return False

    @staticmethod
    def get_student_yearly_attendance(student_id: int, year: int = None):
        """학생별 연도별 출결 통계 조회"""
        try:
            with DatabaseService.get_session() as session:
                query = session.query(YearlyAttendance).filter(YearlyAttendance.student_id == student_id)
                
                if year:
                    query = query.filter(YearlyAttendance.year == year)
                
                yearly_attendances = query.order_by(YearlyAttendance.year.desc()).all()
                return [
                    {
                        "id": ya.id,
                        "student_id": ya.student_id,
                        "year": ya.year,
                        "total_days": ya.total_days,
                        "present_days": ya.present_days,
                        "absent_days": ya.absent_days,
                        "late_days": ya.late_days,
                        "early_leave_days": ya.early_leave_days,
                        "attendance_rate": ya.attendance_rate
                    } for ya in yearly_attendances
                ]
        except Exception as e:
            print(f"학생 연도별 출결 통계 조회 실패: {e}")
            return []

    @staticmethod
    def calculate_yearly_attendance(student_id: int, year: int) -> bool:
        """연도별 출결 통계 자동 계산"""
        try:
            with DatabaseService.get_session() as session:
                # 해당 연도의 출결 데이터 조회
                start_date = f"{year}-01-01"
                end_date = f"{year+1}-01-01"
                
                attendances = session.query(Attendance).filter(
                    Attendance.student_id == student_id,
                    Attendance.date >= start_date,
                    Attendance.date < end_date
                ).all()
                
                # 통계 계산
                total_days = len(attendances)
                present_days = len([a for a in attendances if a.type_id == 1])  # 출석
                absent_days = len([a for a in attendances if a.type_id == 2])   # 결석
                late_days = len([a for a in attendances if a.type_id == 3])     # 지각
                early_leave_days = len([a for a in attendances if a.type_id == 4])  # 조퇴
                
                # 연도별 통계 생성/업데이트
                return DatabaseService.create_yearly_attendance(
                    student_id=student_id,
                    year=year,
                    total_days=total_days,
                    present_days=present_days,
                    absent_days=absent_days,
                    late_days=late_days,
                    early_leave_days=early_leave_days
                )
                
        except Exception as e:
            print(f"연도별 출결 통계 계산 실패: {e}")
            return False
    
 