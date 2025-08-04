from sqlalchemy.orm import Session
from models import User, Class, Student

def get_teacher_list(db: Session):
    """선생님 명단 조회"""
    try:
        # 모든 활성 사용자 조회 (모든 사용자가 선생님)
        teachers = db.query(User).filter(User.is_active == True).all()
        
        teacher_list = []
        for teacher in teachers:
            # 담당하는 반들 정보
            class_info = ""
            if teacher.classes:
                classes_info = []
                for class_obj in teacher.classes:
                    classes_info.append(f"{class_obj.grade}학년 {class_obj.class_num}반")
                class_info = f" (담임: {', '.join(classes_info)})"
            else:
                class_info = " (담임 없음)"
            
            teacher_list.append(f"{teacher.name} ({teacher.login_id}){class_info}")
        
        return teacher_list
    except Exception as e:
        print(f"선생님 명단 조회 오류: {e}")
        return []

def get_student_list(db: Session):
    """전체 학생 명단 조회"""
    try:
        # 모든 학생 조회
        students = db.query(Student).all()
        
        student_list = []
        for student in students:
            class_info = f" ({student.class_info.grade}학년 {student.class_info.class_num}반)" if student.class_info else " (반 미배정)"
            student_list.append(f"{student.name}{class_info}")
        
        return student_list
    except Exception as e:
        print(f"학생 명단 조회 오류: {e}")
        return []

def get_teacher_students(db: Session, teacher_name: str):
    """특정 선생님의 담당 반 조회"""
    try:
        # 선생님 이름에서 정보 제거
        teacher_name_clean = teacher_name.split(" (")[0]
        
        # 해당 선생님 조회 (이름으로 검색)
        teacher = db.query(User).filter(
            (User.name == teacher_name_clean) & 
            (User.is_active == True)
        ).first()
        
        # 이름으로 찾지 못한 경우 login_id로 검색
        if not teacher:
            teacher = db.query(User).filter(
                (User.login_id == teacher_name_clean) & 
                (User.is_active == True)
            ).first()
        
        if not teacher or not teacher.classes:
            return []
        
        # 담당하는 반들 정보
        class_list = []
        for class_obj in teacher.classes:
            class_list.append(f"{class_obj.grade}학년 {class_obj.class_num}반")
        
        return class_list
    except Exception as e:
        print(f"선생님 반 조회 오류: {e}")
        return []

def get_class_students(db: Session, grade: int, class_num: int):
    """특정 반의 학생 명단 조회"""
    try:
        # 반 조회
        class_obj = db.query(Class).filter(
            Class.grade == grade, 
            Class.class_num == class_num
        ).first()
        
        if not class_obj:
            return []
        
        # 해당 반의 학생들 조회
        students = db.query(Student).filter(Student.class_id == class_obj.id).all()
        
        return [student.name for student in students]
    except Exception as e:
        print(f"반 학생 조회 오류: {e}")
        return []

def get_homeroom_teacher(db: Session, grade: int, class_num: int):
    """특정 반의 담임선생님 조회"""
    try:
        # 반 조회
        class_obj = db.query(Class).filter(
            Class.grade == grade, 
            Class.class_num == class_num
        ).first()
        
        if not class_obj or not class_obj.teacher:
            return None
        
        teacher = class_obj.teacher
        return {
            "name": teacher.name,
            "login_id": teacher.login_id,
            "grade": class_obj.grade,
            "class_num": class_obj.class_num
        }
    except Exception as e:
        print(f"담임선생님 조회 오류: {e}")
        return None 