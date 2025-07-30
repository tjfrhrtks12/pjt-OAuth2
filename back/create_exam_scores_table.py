from config import engine, Base
from models import Teacher, Student, ExamScore

def create_exam_scores_table():
    """exam_scores 테이블 생성"""
    print("exam_scores 테이블 생성 중...")
    
    try:
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("exam_scores 테이블이 성공적으로 생성되었습니다!")
        
        # 테이블 정보 확인
        print("\n생성된 테이블 구조:")
        print("- id: 기본키 (자동증가)")
        print("- student_name: 외래키 (students.student_name 참조)")
        print("- subject: 과목 (국어, 수학, 사회, 과학)")
        print("- exam_type: 시험종류 (1학기중간, 1학기기말, 2학기중간, 2학기기말)")
        print("- score: 점수 (0-100)")
        
    except Exception as e:
        print(f"테이블 생성 오류: {e}")

if __name__ == "__main__":
    create_exam_scores_table() 