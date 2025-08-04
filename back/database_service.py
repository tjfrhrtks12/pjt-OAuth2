from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Class, Student, Grade, Subject, Exam
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
    
 