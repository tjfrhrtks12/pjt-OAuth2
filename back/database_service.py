from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from models import Teacher, Student, ExamScore
from config import engine

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseService:
    @staticmethod
    def get_student_by_name(name: str) -> Optional[Dict]:
        """이름으로 학생 정보 조회"""
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.student_name.like(f"%{name}%")).first()
            if student:
                return {
                    "id": student.id,
                    "name": student.student_name,
                    "grade": student.student_grade,
                    "phone": student.student_phone,
                    "score": student.score
                }
            return None
        finally:
            db.close()

    @staticmethod
    def get_teacher_by_name(name: str) -> Optional[Dict]:
        """이름으로 선생님 정보 조회"""
        db = SessionLocal()
        try:
            teacher = db.query(Teacher).filter(Teacher.teacher_name.like(f"%{name}%")).first()
            if teacher:
                return {
                    "id": teacher.id,
                    "teacher_id": teacher.teacher_id,
                    "name": teacher.teacher_name
                }
            return None
        finally:
            db.close()

    @staticmethod
    def get_all_students() -> List[Dict]:
        """모든 학생 정보 조회"""
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            return [
                {
                    "id": student.id,
                    "name": student.student_name,
                    "grade": student.student_grade,
                    "phone": student.student_phone,
                    "score": student.score
                }
                for student in students
            ]
        finally:
            db.close()

    @staticmethod
    def get_all_teachers() -> List[Dict]:
        """모든 선생님 정보 조회"""
        db = SessionLocal()
        try:
            teachers = db.query(Teacher).all()
            return [
                {
                    "id": teacher.id,
                    "teacher_id": teacher.teacher_id,
                    "name": teacher.teacher_name
                }
                for teacher in teachers
            ]
        finally:
            db.close()

    @staticmethod
    def search_students(keyword: str) -> List[Dict]:
        """키워드로 학생 검색"""
        db = SessionLocal()
        try:
            students = db.query(Student).filter(Student.student_name.like(f"%{keyword}%")).all()
            return [
                {
                    "id": student.id,
                    "name": student.student_name,
                    "grade": student.student_grade,
                    "phone": student.student_phone,
                    "score": student.score
                }
                for student in students
            ]
        finally:
            db.close()

    @staticmethod
    def search_teachers(keyword: str) -> List[Dict]:
        """키워드로 선생님 검색"""
        db = SessionLocal()
        try:
            teachers = db.query(Teacher).filter(Teacher.teacher_name.like(f"%{keyword}%")).all()
            return [
                {
                    "id": teacher.id,
                    "teacher_id": teacher.teacher_id,
                    "name": teacher.teacher_name
                }
                for teacher in teachers
            ]
        finally:
            db.close()

    @staticmethod
    def update_student_score(student_id: int, score: int) -> bool:
        """학생 점수 업데이트"""
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.score = score
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"점수 업데이트 오류: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def get_students_by_score_range(min_score: int, max_score: int) -> List[Dict]:
        """점수 범위로 학생 검색"""
        db = SessionLocal()
        try:
            students = db.query(Student).filter(
                Student.score >= min_score,
                Student.score <= max_score
            ).all()
            return [
                {
                    "id": student.id,
                    "name": student.student_name,
                    "grade": student.student_grade,
                    "phone": student.student_phone,
                    "score": student.score
                }
                for student in students
            ]
        finally:
            db.close()

    # 새로운 exam_scores 관련 메서드들
    @staticmethod
    def get_all_exam_scores() -> List[Dict]:
        """모든 시험 성적 정보 조회"""
        db = SessionLocal()
        try:
            exam_scores = db.query(ExamScore).all()
            return [
                {
                    "id": score.id,
                    "student_name": score.student_name,
                    "subject": score.subject,
                    "exam_type": score.exam_type,
                    "score": score.score
                }
                for score in exam_scores
            ]
        finally:
            db.close()

    @staticmethod
    def get_exam_scores_by_student(student_name: str) -> List[Dict]:
        """특정 학생의 시험 성적 조회"""
        db = SessionLocal()
        try:
            exam_scores = db.query(ExamScore).filter(
                ExamScore.student_name == student_name
            ).all()
            return [
                {
                    "id": score.id,
                    "student_name": score.student_name,
                    "subject": score.subject,
                    "exam_type": score.exam_type,
                    "score": score.score
                }
                for score in exam_scores
            ]
        finally:
            db.close()

    @staticmethod
    def get_exam_scores_by_subject(subject: str) -> List[Dict]:
        """특정 과목의 시험 성적 조회"""
        db = SessionLocal()
        try:
            exam_scores = db.query(ExamScore).filter(
                ExamScore.subject == subject
            ).all()
            return [
                {
                    "id": score.id,
                    "student_name": score.student_name,
                    "subject": score.subject,
                    "exam_type": score.exam_type,
                    "score": score.score
                }
                for score in exam_scores
            ]
        finally:
            db.close()

    @staticmethod
    def get_exam_scores_by_exam_type(exam_type: str) -> List[Dict]:
        """특정 시험 유형의 성적 조회"""
        db = SessionLocal()
        try:
            exam_scores = db.query(ExamScore).filter(
                ExamScore.exam_type == exam_type
            ).all()
            return [
                {
                    "id": score.id,
                    "student_name": score.student_name,
                    "subject": score.subject,
                    "exam_type": score.exam_type,
                    "score": score.score
                }
                for score in exam_scores
            ]
        finally:
            db.close() 