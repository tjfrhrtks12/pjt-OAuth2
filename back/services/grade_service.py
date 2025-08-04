from sqlalchemy.orm import Session
from sqlalchemy import func, text
from models import Student, Class, Grade, Subject, Exam

def get_student_grades(db: Session, student_name: str, academic_year: int = 2024):
    """특정 학생의 성적 조회"""
    try:
        # 학생 조회
        student = db.query(Student).filter(Student.name == student_name).first()
        if not student:
            return None
        
        # 성적 조회
        grades = db.query(
            Subject.name.label('subject_name'),
            Exam.name.label('exam_name'),
            Grade.score
        ).join(
            Subject, Grade.subject_id == Subject.id
        ).join(
            Exam, Grade.exam_id == Exam.id
        ).filter(
            Grade.student_id == student.id,
            Grade.academic_year == academic_year
        ).all()
        
        return {
            "student_name": student.name,
            "class_info": f"{student.class_info.grade}학년 {student.class_info.class_num}반",
            "grades": [
                {
                    "subject": grade.subject_name,
                    "exam": grade.exam_name,
                    "score": grade.score
                } for grade in grades
            ]
        }
    except Exception as e:
        print(f"학생 성적 조회 오류: {e}")
        return None

def get_class_grades_summary(db: Session, grade: int, class_num: int, academic_year: int = 2024):
    """특정 반의 성적 요약 조회"""
    try:
        # 반 조회
        class_obj = db.query(Class).filter(
            Class.academic_year == academic_year,
            Class.grade == grade, 
            Class.class_num == class_num
        ).first()
        
        if not class_obj:
            return None
        
        # 반 학생들의 성적 요약
        summary = db.query(
            Student.name,
            func.avg(Grade.score).label('avg_score'),
            func.count(Grade.id).label('grade_count')
        ).join(
            Grade, Student.id == Grade.student_id
        ).filter(
            Student.class_id == class_obj.id
        ).group_by(
            Student.id, Student.name
        ).order_by(
            func.avg(Grade.score).desc()
        ).all()
        
        return {
            "class_info": f"{grade}학년 {class_num}반",
            "students": [
                {
                    "name": row.name,
                    "avg_score": round(row.avg_score, 1),
                    "grade_count": row.grade_count
                } for row in summary
            ]
        }
    except Exception as e:
        print(f"반 성적 요약 조회 오류: {e}")
        return None

def get_subject_analysis(db: Session, subject_name: str):
    """특정 과목의 성적 분석"""
    try:
        # 과목 조회
        subject = db.query(Subject).filter(Subject.name == subject_name).first()
        if not subject:
            return None
        
        # 과목별 성적 통계
        stats = db.query(
            func.avg(Grade.score).label('avg_score'),
            func.min(Grade.score).label('min_score'),
            func.max(Grade.score).label('max_score'),
            func.count(Grade.id).label('total_grades')
        ).filter(
            Grade.subject_id == subject.id
        ).first()
        
        # 학년별 평균
        grade_stats = db.query(
            Class.grade,
            func.avg(Grade.score).label('avg_score')
        ).join(
            Student, Class.id == Student.class_id
        ).join(
            Grade, Student.id == Grade.student_id
        ).filter(
            Grade.subject_id == subject.id
        ).group_by(
            Class.grade
        ).order_by(
            Class.grade
        ).all()
        
        return {
            "subject_name": subject_name,
            "overall_stats": {
                "avg_score": round(stats.avg_score, 1),
                "min_score": stats.min_score,
                "max_score": stats.max_score,
                "total_grades": stats.total_grades
            },
            "grade_stats": [
                {
                    "grade": row.grade,
                    "avg_score": round(row.avg_score, 1)
                } for row in grade_stats
            ]
        }
    except Exception as e:
        print(f"과목 분석 조회 오류: {e}")
        return None

def get_top_students(db: Session, limit: int = 10, grade: int = None):
    """성적 상위 학생 조회 (학년별 필터링 가능)"""
    try:
        query = db.query(
            Student.name,
            Class.grade,
            Class.class_num,
            func.avg(Grade.score).label('avg_score'),
            func.count(Grade.id).label('grade_count')
        ).join(
            Class, Student.class_id == Class.id
        ).join(
            Grade, Student.id == Grade.student_id
        )
        
        # 학년 필터 적용
        if grade:
            query = query.filter(Class.grade == grade)
        
        top_students = query.group_by(
            Student.id, Student.name, Class.grade, Class.class_num
        ).order_by(
            func.avg(Grade.score).desc()
        ).limit(limit).all()
        
        return [
            {
                "name": row.name,
                "class": f"{row.grade}학년 {row.class_num}반",
                "avg_score": round(row.avg_score, 1),
                "grade_count": row.grade_count
            } for row in top_students
        ]
    except Exception as e:
        print(f"상위 학생 조회 오류: {e}")
        return []

def get_bottom_students(db: Session, limit: int = 10, grade: int = None):
    """성적 하위 학생 조회 (꼴등)"""
    try:
        query = db.query(
            Student.name,
            Class.grade,
            Class.class_num,
            func.avg(Grade.score).label('avg_score'),
            func.count(Grade.id).label('grade_count')
        ).join(
            Grade, Student.id == Grade.student_id
        ).join(
            Class, Student.class_id == Class.id
        ).group_by(
            Student.id, Student.name, Class.grade, Class.class_num
        )
        
        # 학년 필터 적용
        if grade:
            query = query.filter(Class.grade == grade)
        
        # 평균 성적 오름차순 정렬 (낮은 점수부터)
        bottom_students = query.order_by(
            func.avg(Grade.score).asc()
        ).limit(limit).all()
        
        return [
            {
                "name": student.name,
                "class": f"{student.grade}학년 {student.class_num}반",
                "avg_score": round(student.avg_score, 1),
                "grade_count": student.grade_count
            } for student in bottom_students
        ]
    except Exception as e:
        print(f"하위 학생 조회 오류: {e}")
        return None

def get_grade_bottom_students(db: Session, grade: int, limit: int = 10):
    """특정 학년의 성적 하위 학생 조회"""
    return get_bottom_students(db, limit, grade)

def get_exam_analysis(db: Session, exam_name: str, grade: int = None, class_num: int = None):
    """특정 시험의 성적 분석"""
    try:
        # 시험 조회
        exam = db.query(Exam).filter(Exam.name == exam_name).first()
        if not exam:
            return None
        
        # 기본 쿼리
        query = db.query(
            Student.name,
            Class.grade,
            Class.class_num,
            Subject.name.label('subject_name'),
            Grade.score
        ).join(
            Class, Student.class_id == Class.id
        ).join(
            Grade, Student.id == Grade.student_id
        ).join(
            Subject, Grade.subject_id == Subject.id
        ).filter(
            Grade.exam_id == exam.id
        )
        
        # 학년/반 필터 적용
        if grade:
            query = query.filter(Class.grade == grade)
        if class_num:
            query = query.filter(Class.class_num == class_num)
        
        results = query.all()
        
        if not results:
            return None
        
        # 과목별 평균 계산
        subject_averages = {}
        for result in results:
            subject = result.subject_name
            if subject not in subject_averages:
                subject_averages[subject] = []
            subject_averages[subject].append(result.score)
        
        subject_stats = {}
        for subject, scores in subject_averages.items():
            subject_stats[subject] = {
                'avg_score': round(sum(scores) / len(scores), 1),
                'min_score': min(scores),
                'max_score': max(scores),
                'count': len(scores)
            }
        
        # 전체 평균
        all_scores = [result.score for result in results]
        overall_avg = round(sum(all_scores) / len(all_scores), 1)
        
        return {
            "exam_name": exam_name,
            "grade_filter": grade,
            "class_filter": class_num,
            "overall_avg": overall_avg,
            "total_students": len(set([(r.name, r.grade, r.class_num) for r in results])),
            "subject_stats": subject_stats
        }
    except Exception as e:
        print(f"시험 분석 조회 오류: {e}")
        return None

def get_subject_exam_analysis(db: Session, exam_name: str, subject_name: str, grade: int = None, class_num: int = None):
    """특정 시험의 특정 과목 성적 분석"""
    try:
        # 시험 조회
        exam = db.query(Exam).filter(Exam.name == exam_name).first()
        if not exam:
            return None
        
        # 과목 조회
        subject = db.query(Subject).filter(Subject.name == subject_name).first()
        if not subject:
            return None
        
        # 기본 쿼리
        query = db.query(
            Student.name,
            Class.grade,
            Class.class_num,
            Grade.score
        ).join(
            Class, Student.class_id == Class.id
        ).join(
            Grade, Student.id == Grade.student_id
        ).filter(
            Grade.exam_id == exam.id,
            Grade.subject_id == subject.id
        )
        
        # 학년/반 필터 적용
        if grade:
            query = query.filter(Class.grade == grade)
        if class_num:
            query = query.filter(Class.class_num == class_num)
        
        results = query.all()
        
        if not results:
            return None
        
        # 통계 계산
        scores = [result.score for result in results]
        avg_score = round(sum(scores) / len(scores), 1)
        min_score = min(scores)
        max_score = max(scores)
        
        # 학생별 성적 (상위 5명)
        student_scores = [(result.name, result.score) for result in results]
        student_scores.sort(key=lambda x: x[1], reverse=True)
        top_students = student_scores[:5]
        
        return {
            "exam_name": exam_name,
            "subject_name": subject_name,
            "grade_filter": grade,
            "class_filter": class_num,
            "avg_score": avg_score,
            "min_score": min_score,
            "max_score": max_score,
            "total_students": len(scores),
            "top_students": top_students
        }
    except Exception as e:
        print(f"과목별 시험 분석 조회 오류: {e}")
        return None 

def get_student_academic_history(db: Session, student_name: str):
    """학생의 1학년, 2학년, 3학년 전체 성적 이력 조회"""
    try:
        # 학생 조회 (여러 학년도의 동일한 이름 학생들)
        students = db.query(Student).filter(Student.name == student_name).all()
        if not students:
            return None
        
        academic_history = {}
        
        for student in students:
            academic_year = student.academic_year
            
            # 해당 학년도의 성적 조회
            grades = db.query(
                Subject.name.label('subject_name'),
                Exam.name.label('exam_name'),
                Grade.score,
                Grade.academic_year
            ).join(
                Subject, Grade.subject_id == Subject.id
            ).join(
                Exam, Grade.exam_id == Exam.id
            ).filter(
                Grade.student_id == student.id,
                Grade.academic_year == academic_year
            ).all()
            
            if grades:
                # 과목별 평균 계산
                subject_averages = {}
                for grade in grades:
                    if grade.subject_name not in subject_averages:
                        subject_averages[grade.subject_name] = []
                    subject_averages[grade.subject_name].append(grade.score)
                
                # 전체 평균 계산
                all_scores = [grade.score for grade in grades]
                overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
                
                academic_history[academic_year] = {
                    "student_id": student.id,
                    "class_info": f"{student.class_info.grade}학년 {student.class_info.class_num}반",
                    "grades": [
                        {
                            "subject": grade.subject_name,
                            "exam": grade.exam_name,
                            "score": grade.score
                        } for grade in grades
                    ],
                    "subject_averages": {
                        subject: sum(scores) / len(scores) 
                        for subject, scores in subject_averages.items()
                    },
                    "overall_average": round(overall_avg, 1),
                    "total_grades": len(grades)
                }
        
        return {
            "student_name": student_name,
            "academic_history": academic_history
        }
        
    except Exception as e:
        print(f"학생 학년별 성적 이력 조회 오류: {e}")
        return None

def get_student_grades_by_academic_year(db: Session, student_name: str, academic_year: int):
    """특정 학년도의 학생 성적 조회"""
    try:
        # 해당 학년도의 학생 조회
        student = db.query(Student).filter(
            Student.name == student_name,
            Student.academic_year == academic_year
        ).first()
        
        if not student:
            return None
        
        # 성적 조회
        grades = db.query(
            Subject.name.label('subject_name'),
            Exam.name.label('exam_name'),
            Grade.score
        ).join(
            Subject, Grade.subject_id == Subject.id
        ).join(
            Exam, Grade.exam_id == Exam.id
        ).filter(
            Grade.student_id == student.id,
            Grade.academic_year == academic_year
        ).all()
        
        if not grades:
            return None
        
        # 과목별 평균 계산
        subject_averages = {}
        for grade in grades:
            if grade.subject_name not in subject_averages:
                subject_averages[grade.subject_name] = []
            subject_averages[grade.subject_name].append(grade.score)
        
        # 전체 평균 계산
        all_scores = [grade.score for grade in grades]
        overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return {
            "student_name": student.name,
            "academic_year": academic_year,
            "class_info": f"{student.class_info.grade}학년 {student.class_info.class_num}반",
            "grades": [
                {
                    "subject": grade.subject_name,
                    "exam": grade.exam_name,
                    "score": grade.score
                } for grade in grades
            ],
            "subject_averages": {
                subject: round(sum(scores) / len(scores), 1)
                for subject, scores in subject_averages.items()
            },
            "overall_average": round(overall_avg, 1),
            "total_grades": len(grades)
        }
        
    except Exception as e:
        print(f"특정 학년도 학생 성적 조회 오류: {e}")
        return None

def analyze_student_progress(db: Session, student_name: str):
    """학생의 학년별 성적 변화 분석"""
    try:
        history = get_student_academic_history(db, student_name)
        if not history or not history['academic_history']:
            return None
        
        academic_years = sorted(history['academic_history'].keys())
        if len(academic_years) < 2:
            return None
        
        progress_analysis = {
            "student_name": student_name,
            "academic_years": academic_years,
            "overall_progress": {},
            "subject_progress": {},
            "improvement_areas": [],
            "strength_areas": []
        }
        
        # 전체 평균 변화 분석
        overall_averages = []
        for year in academic_years:
            overall_averages.append(history['academic_history'][year]['overall_average'])
        
        progress_analysis['overall_progress'] = {
            "averages": overall_averages,
            "improvement": round(overall_averages[-1] - overall_averages[0], 1) if len(overall_averages) > 1 else 0,
            "trend": "상승" if len(overall_averages) > 1 and overall_averages[-1] > overall_averages[0] else "하락" if len(overall_averages) > 1 and overall_averages[-1] < overall_averages[0] else "유지"
        }
        
        # 과목별 변화 분석
        subjects = set()
        for year_data in history['academic_history'].values():
            subjects.update(year_data['subject_averages'].keys())
        
        for subject in subjects:
            subject_scores = []
            for year in academic_years:
                if subject in history['academic_history'][year]['subject_averages']:
                    subject_scores.append(history['academic_history'][year]['subject_averages'][subject])
                else:
                    subject_scores.append(0)
            
            if len(subject_scores) > 1:
                improvement = round(subject_scores[-1] - subject_scores[0], 1)
                trend = "상승" if improvement > 0 else "하락" if improvement < 0 else "유지"
                
                progress_analysis['subject_progress'][subject] = {
                    "scores": subject_scores,
                    "improvement": improvement,
                    "trend": trend
                }
                
                if improvement > 5:
                    progress_analysis['strength_areas'].append(subject)
                elif improvement < -5:
                    progress_analysis['improvement_areas'].append(subject)
        
        return progress_analysis
        
    except Exception as e:
        print(f"학생 성적 변화 분석 오류: {e}")
        return None 