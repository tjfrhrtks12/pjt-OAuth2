from openai import OpenAI
import os
from services.grade_service import (
    get_student_grades, 
    get_class_grades_summary, 
    get_subject_analysis, 
    get_top_students,
    get_bottom_students,
    get_grade_bottom_students,
    get_exam_analysis,
    get_subject_exam_analysis,
    get_student_academic_history,
    get_student_grades_by_academic_year,
    analyze_student_progress
)
from services.user_service import (
    get_teacher_list,
    get_student_list,
    get_class_students,
    get_homeroom_teacher
)

# OpenAI 클라이언트 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def prepare_chat_context(db):
    """챗봇 컨텍스트 준비"""
    # 선생님 명단 조회
    teacher_list = get_teacher_list(db)
    teacher_names = ", ".join(teacher_list) if teacher_list else "등록된 선생님이 없습니다"
    
    # 전체 학생 명단 조회
    student_list = get_student_list(db)
    student_names = "\n".join(student_list) if student_list else "등록된 학생이 없습니다"
    
    # 반별 학생 명단 조회
    class_students_info = []
    for grade in [1, 2, 3]:
        for class_num in [1, 2]:
            students = get_class_students(db, grade, class_num)
            if students:
                class_students_info.append(f"{grade}학년 {class_num}반: {', '.join(students)}")
    
    class_students_text = "\n".join(class_students_info) if class_students_info else "반별 학생 정보가 없습니다"
    
    # 담임선생님 정보 조회
    homeroom_teachers = []
    for grade in [1, 2, 3]:
        for class_num in [1, 2]:
            teacher = get_homeroom_teacher(db, grade, class_num)
            if teacher:
                homeroom_teachers.append(f"{grade}학년 {class_num}반 담임: {teacher['name']} 선생님")
    
    homeroom_info = "\n".join(homeroom_teachers) if homeroom_teachers else "담임 정보가 없습니다"
    
    # 성적 분석 데이터 준비
    # 상위 10명 학생 조회
    top_students = get_top_students(db, 10)
    top_students_text = ""
    if top_students:
        top_students_text = "\n".join([
            f"- {student['name']} ({student['class']}): 평균 {student['avg_score']}점"
            for student in top_students
        ])
    
    # 과목별 분석 데이터
    subjects_analysis = []
    for subject_name in ["국어", "수학", "사회", "과학", "영어"]:
        analysis = get_subject_analysis(db, subject_name)
        if analysis:
            subjects_analysis.append(f"{subject_name}: 평균 {analysis['overall_stats']['avg_score']}점 (최저 {analysis['overall_stats']['min_score']}점, 최고 {analysis['overall_stats']['max_score']}점)")
    
    subjects_text = "\n".join(subjects_analysis) if subjects_analysis else "과목별 분석 데이터가 없습니다"
    
    return {
        "teacher_names": teacher_names,
        "student_names": student_names,
        "class_students_text": class_students_text,
        "homeroom_info": homeroom_info,
        "top_students_text": top_students_text,
        "subjects_text": subjects_text
    }

def process_chat_message(chat_request, db):
    """챗봇 메시지 처리"""
    # 성적 분석 요청 처리
    user_message = chat_request.message.lower()
    ai_response = None  # 변수 초기화
    
    # 학년별 성적 이력 조회 (우선순위 높음)
    if any(keyword in user_message for keyword in ["1학년", "2학년", "3학년"]) and any(keyword in user_message for keyword in ["성적", "점수", "성적을", "점수를"]):
        # 학생 이름 추출
        student_found = False
        for student_name in ["김철수", "이영희", "박민수", "최지원", "정수진", "강동현", "윤서연", "임태현", "한소영", "송민지", 
                           "박준호", "김미영", "이성민", "최유진", "정현우", "강지은", "윤도현", "임수빈", "한승우", "송예진",
                           "김태우", "이하나", "박지훈", "최민석", "정소연", "강현준", "윤지민", "임동욱", "한예은", "송준영",
                           "김서연", "이준호", "박민지", "최성현", "정유진", "강도현", "윤수빈", "임승우", "한예진", "송태우",
                           "김하나", "이지훈", "박민석", "최소연", "정현준", "강지민", "윤동욱", "임예은", "한준영", "송서연",
                           "김준호", "이민지", "박성현", "최유진", "정도현", "강수빈", "윤승우", "임예진", "한태우", "송하나"]:
            if student_name in chat_request.message:
                # 학년별 성적 이력 조회
                academic_history = get_student_academic_history(db, student_name)
                if academic_history and academic_history['academic_history']:
                    # 성적 변화 분석
                    progress_analysis = analyze_student_progress(db, student_name)
                    
                    # 응답 생성
                    response_parts = [f"**{student_name} 학생의 학년별 성적 이력:**\n"]
                    
                    # 학년별 성적 상세 정보
                    for academic_year in sorted(academic_history['academic_history'].keys()):
                        year_data = academic_history['academic_history'][academic_year]
                        response_parts.append(f"\n**{academic_year}년도 ({year_data['class_info']}):**")
                        response_parts.append(f"• 전체 평균: {year_data['overall_average']}점")
                        
                        # 과목별 평균
                        subject_avgs = []
                        for subject, avg in year_data['subject_averages'].items():
                            subject_avgs.append(f"{subject}: {avg:.1f}점")
                        response_parts.append(f"• 과목별 평균: {', '.join(subject_avgs)}")
                    
                    # 성적 변화 분석 추가
                    if progress_analysis:
                        response_parts.append(f"\n**📊 성적 변화 분석:**")
                        response_parts.append(f"• 전체 성적 변화: {progress_analysis['overall_progress']['improvement']:+}점 ({progress_analysis['overall_progress']['trend']})")
                        
                        if progress_analysis['strength_areas']:
                            response_parts.append(f"• 강점 과목: {', '.join(progress_analysis['strength_areas'])}")
                        if progress_analysis['improvement_areas']:
                            response_parts.append(f"• 개선 필요 과목: {', '.join(progress_analysis['improvement_areas'])}")
                        
                        # 과목별 변화 상세
                        response_parts.append(f"\n**과목별 변화:**")
                        for subject, progress in progress_analysis['subject_progress'].items():
                            response_parts.append(f"• {subject}: {progress['improvement']:+}점 ({progress['trend']})")
                    
                    ai_response = "\n".join(response_parts)
                    student_found = True
                    break
        
        if not student_found:
            ai_response = "해당 학생의 학년별 성적 정보를 찾을 수 없습니다."
    
    # 학생 개별 성적 조회 (기존 로직)
    elif "성적 알려줘" in user_message or "성적은?" in user_message:
        student_found = False
        for student_name in ["김철수", "이영희", "박민수", "최지원", "정수진", "강동현", "윤서연", "임태현", "한소영", "송민지", 
                           "박준호", "김미영", "이성민", "최유진", "정현우", "강지은", "윤도현", "임수빈", "한승우", "송예진",
                           "김태우", "이하나", "박지훈", "최민석", "정소연", "강현준", "윤지민", "임동욱", "한예은", "송준영",
                           "김서연", "이준호", "박민지", "최성현", "정유진", "강도현", "윤수빈", "임승우", "한예진", "송태우",
                           "김하나", "이지훈", "박민석", "최소연", "정현준", "강지민", "윤동욱", "임예은", "한준영", "송서연",
                           "김준호", "이민지", "박성현", "최유진", "정도현", "강수빈", "윤승우", "임예진", "한태우", "송하나"]:
            if student_name in chat_request.message:
                # 현재 학년 성적 조회 (기본값: 2024년)
                student_grades = get_student_grades(db, student_name)
                if student_grades:
                    grades_text = "\n".join([
                        f"- {grade['subject']} {grade['exam']}: {grade['score']}점"
                        for grade in student_grades['grades']
                    ])
                    ai_response = f"**{student_grades['student_name']} ({student_grades['class_info']}) 성적:**\n\n{grades_text}"
                    student_found = True
                    break
        
        if not student_found:
            ai_response = "해당 학생의 성적 정보를 찾을 수 없습니다."
    
    # 반별 성적 분석
    elif "성적 분석해줘" in user_message or "성적 분석" in user_message:
        class_found = False
        for grade in [1, 2, 3]:
            for class_num in [1, 2]:
                if f"{grade}학년 {class_num}반" in chat_request.message:
                    class_summary = get_class_grades_summary(db, grade, class_num)
                    if class_summary:
                        students_text = "\n".join([
                            f"{i+1}위: {student['name']} - 평균 {student['avg_score']}점"
                            for i, student in enumerate(class_summary['students'])
                        ])
                        ai_response = f"**{class_summary['class_info']} 성적 분석:**\n\n{students_text}"
                        class_found = True
                        break
            if class_found:
                break
        
        if not class_found:
            ai_response = "해당 반의 성적 정보를 찾을 수 없습니다."
    
    # 과목별 분석
    elif "과목 분석해줘" in user_message or "과목 분석" in user_message:
        subject_found = False
        for subject_name in ["국어", "수학", "사회", "과학", "영어"]:
            if subject_name in chat_request.message:
                subject_analysis = get_subject_analysis(db, subject_name)
                if subject_analysis:
                    grade_text = "\n".join([
                        f"- {grade['grade']}학년: 평균 {grade['avg_score']}점"
                        for grade in subject_analysis['grade_stats']
                    ])
                    ai_response = f"**{subject_analysis['subject_name']} 과목 분석:**\n\n**전체 통계:**\n- 평균: {subject_analysis['overall_stats']['avg_score']}점\n- 최저: {subject_analysis['overall_stats']['min_score']}점\n- 최고: {subject_analysis['overall_stats']['max_score']}점\n- 총 성적 수: {subject_analysis['overall_stats']['total_grades']}개\n\n**학년별 평균:**\n{grade_text}"
                    subject_found = True
                    break
        
        if not subject_found:
            ai_response = "해당 과목의 성적 정보를 찾을 수 없습니다."
    
    # 상위 학생 조회
    elif "상위 학생" in user_message or "성적 좋은 학생" in user_message or "1등" in user_message or "평균 1등" in user_message:
        # "1등만" 요청인지 확인 (더 정교한 패턴 매칭)
        only_first = (
            "1등만" in user_message or 
            "1위만" in user_message or 
            "첫째만" in user_message or
            "1등은누구야" in user_message or
            "1등이누구야" in user_message or
            "1등은?" in user_message or
            "1등이?" in user_message or
            "누가1등" in user_message or
            "1등누구" in user_message
        )
        
        # 학년별 필터 확인
        grade_filter = None
        for grade in [1, 2, 3]:
            if f"{grade}학년" in chat_request.message:
                grade_filter = grade
                break
        
        # 학년별 상위 학생 조회
        if grade_filter:
            limit = 1 if only_first else 10
            top_students = get_top_students(db, limit, grade_filter)
            if top_students:
                if only_first:
                    student = top_students[0]
                    ai_response = f"**{grade_filter}학년 1등: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점**"
                else:
                    top_text = "\n".join([
                        f"{i+1}위: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점"
                        for i, student in enumerate(top_students)
                    ])
                    ai_response = f"**{grade_filter}학년 성적 상위 10명 학생:**\n\n{top_text}"
            else:
                ai_response = f"{grade_filter}학년 성적 상위 학생 정보를 찾을 수 없습니다."
        else:
            # 전체 상위 학생 조회
            limit = 1 if only_first else 10
            top_students = get_top_students(db, limit)
            if top_students:
                if only_first:
                    student = top_students[0]
                    ai_response = f"**전체 1등: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점**"
                else:
                    top_text = "\n".join([
                        f"{i+1}위: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점"
                        for i, student in enumerate(top_students)
                    ])
                    ai_response = f"**전체 성적 상위 10명 학생:**\n\n{top_text}"
            else:
                ai_response = "성적 상위 학생 정보를 찾을 수 없습니다."
    
    # 꼴등 학생 조회
    elif "꼴등" in user_message or "성적 안좋은 학생" in user_message or "꼴찌" in user_message or "꼴등은누구야" in user_message or "꼴등이누구야" in user_message:
        # "꼴등만" 요청인지 확인
        only_last = (
            "꼴등만" in user_message or 
            "꼴찌만" in user_message or 
            "마지막만" in user_message or
            "꼴등은누구야" in user_message or
            "꼴등이누구야" in user_message or
            "꼴등은?" in user_message or
            "꼴등이?" in user_message or
            "누가꼴등" in user_message or
            "꼴등누구" in user_message or
            "꼴등 1명만" in user_message or
            "1명만" in user_message
        )
        
        # 학년별 필터 확인 (더 정교한 패턴 매칭)
        grade_filter = None
        message_lower = chat_request.message.lower()
        
        # "1학년 전체성적 꼴등" 같은 패턴 확인
        if "1학년" in chat_request.message:
            grade_filter = 1
        elif "2학년" in chat_request.message:
            grade_filter = 2
        elif "3학년" in chat_request.message:
            grade_filter = 3
        
        # 학년별 꼴등 학생 조회
        if grade_filter:
            limit = 1 if only_last else 10
            bottom_students = get_grade_bottom_students(db, grade_filter, limit)
            if bottom_students:
                if only_last:
                    student = bottom_students[0]
                    ai_response = f"**{grade_filter}학년 꼴등: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점**"
                else:
                    bottom_text = "\n".join([
                        f"{i+1}위: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점"
                        for i, student in enumerate(bottom_students)
                    ])
                    ai_response = f"**{grade_filter}학년 성적 하위 10명 학생:**\n\n{bottom_text}"
            else:
                ai_response = f"{grade_filter}학년 성적 하위 학생 정보를 찾을 수 없습니다."
        else:
            # 전체 꼴등 학생 조회
            limit = 1 if only_last else 10
            bottom_students = get_bottom_students(db, limit)
            if bottom_students:
                if only_last:
                    student = bottom_students[0]
                    ai_response = f"**전체 꼴등: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점**"
                else:
                    bottom_text = "\n".join([
                        f"{i+1}위: {student['name']} ({student['class']}) - 평균 {student['avg_score']}점"
                        for i, student in enumerate(bottom_students)
                    ])
                    ai_response = f"**전체 성적 하위 10명 학생:**\n\n{bottom_text}"
            else:
                ai_response = "성적 하위 학생 정보를 찾을 수 없습니다."
    
    # 시험별 분석 (1학기 중간고사, 1학기 기말고사 등)
    elif "중간고사" in user_message or "기말고사" in user_message:
        # 시험명 매칭 (공백 유무 상관없이)
        exam_name = None
        message_clean = chat_request.message.replace(" ", "")  # 공백 제거
        
        if "1학기중간고사" in message_clean:
            exam_name = "1학기중간고사"
        elif "1학기기말고사" in message_clean:
            exam_name = "1학기기말고사"
        elif "2학기중간고사" in message_clean:
            exam_name = "2학기중간고사"
        elif "2학기기말고사" in message_clean:
            exam_name = "2학기기말고사"
        
        if exam_name:
            # 과목명 확인
            subject_name = None
            for subject in ["국어", "수학", "사회", "과학", "영어"]:
                if subject in chat_request.message:
                    subject_name = subject
                    break
            
            # 학년/반 필터 확인
            grade_filter = None
            class_filter = None
            found_filter = False
            
            for grade in [1, 2, 3]:
                for class_num in [1, 2]:
                    if f"{grade}학년 {class_num}반" in chat_request.message:
                        grade_filter = grade
                        class_filter = class_num
                        found_filter = True
                        break
                if found_filter:
                    break
            
            # 특정 과목이 지정된 경우
            if subject_name:
                if found_filter:
                    # 특정 반의 특정 과목 분석
                    subject_analysis = get_subject_exam_analysis(db, exam_name, subject_name, grade_filter, class_filter)
                    if subject_analysis:
                        top_students_text = "\n".join([
                            f"{i+1}위: {student[0]} - {student[1]}점"
                            for i, student in enumerate(subject_analysis['top_students'])
                        ])
                        
                        ai_response = f"**{subject_analysis['exam_name']} {subject_analysis['subject_name']} ({subject_analysis['grade_filter']}학년 {subject_analysis['class_filter']}반) 성적 분석:**\n\n**평균: {subject_analysis['avg_score']}점**\n**최저: {subject_analysis['min_score']}점**\n**최고: {subject_analysis['max_score']}점**\n**참여 학생: {subject_analysis['total_students']}명**\n\n**상위 5명:**\n{top_students_text}"
                else:
                    # 전체 반의 특정 과목 분석
                    all_analyses = []
                    for grade in [1, 2, 3]:
                        for class_num in [1, 2]:
                            subject_analysis = get_subject_exam_analysis(db, exam_name, subject_name, grade, class_num)
                            if subject_analysis:
                                all_analyses.append(f"**{grade}학년 {class_num}반:** 평균 {subject_analysis['avg_score']}점 (최저 {subject_analysis['min_score']}점, 최고 {subject_analysis['max_score']}점)")
                    
                    if all_analyses:
                        ai_response = f"**{exam_name} {subject_name} 전체 반별 성적 분석:**\n\n" + "\n\n".join(all_analyses)
                    else:
                        ai_response = f"해당 시험의 {subject_name} 성적 정보를 찾을 수 없습니다."
            
            # 과목이 지정되지 않은 경우 (기존 로직)
            else:
                # 특정 반이 지정되지 않았으면 전체 분석
                if not found_filter:
                    # 전체 학년별 분석
                    all_analyses = []
                    for grade in [1, 2, 3]:
                        for class_num in [1, 2]:
                            exam_analysis = get_exam_analysis(db, exam_name, grade, class_num)
                            if exam_analysis:
                                subject_text = "\n".join([
                                    f"  - {subject}: 평균 {stats['avg_score']}점"
                                    for subject, stats in exam_analysis['subject_stats'].items()
                                ])
                                all_analyses.append(f"**{grade}학년 {class_num}반:**\n**평균: {exam_analysis['overall_avg']}점**\n{subject_text}")
                    
                    if all_analyses:
                        ai_response = f"**{exam_name} 전체 반별 성적 분석:**\n\n" + "\n\n".join(all_analyses)
                    else:
                        ai_response = f"해당 시험의 성적 정보를 찾을 수 없습니다."
                else:
                    # 특정 반 분석
                    exam_analysis = get_exam_analysis(db, exam_name, grade_filter, class_filter)
                    if exam_analysis:
                        subject_text = "\n".join([
                            f"- {subject}: 평균 {stats['avg_score']}점 (최저 {stats['min_score']}점, 최고 {stats['max_score']}점)"
                            for subject, stats in exam_analysis['subject_stats'].items()
                        ])
                        
                        ai_response = f"**{exam_analysis['exam_name']} ({exam_analysis['grade_filter']}학년 {exam_analysis['class_filter']}반) 성적 분석:**\n\n**전체 평균: {exam_analysis['overall_avg']}점**\n**참여 학생: {exam_analysis['total_students']}명**\n\n**과목별 분석:**\n{subject_text}"
                    else:
                        ai_response = f"해당 시험의 성적 정보를 찾을 수 없습니다."
        else:
            ai_response = "시험명을 인식할 수 없습니다. '1학기 중간고사', '1학기 기말고사', '2학기 중간고사', '2학기 기말고사' 중 하나를 입력해주세요."
    
    return ai_response

def get_ai_response(chat_request, context):
    """AI 응답 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""당신은 학교 관리 시스템의 AI 어시스턴트입니다. 
                    교사와 학생들을 도와주는 친근하고 전문적인 어시스턴트입니다. 
                    한국어로 답변해주세요.
                    
                    현재 시스템에는 데이터베이스 연결과 AI 연결이 설정되어 있으며, 
                    학생들의 성적 데이터가 모두 입력되어 있습니다.
                    
                    **현재 등록된 선생님 명단: {context['teacher_names']}**
                    
                    **전체 학생 명단:**
                    {context['student_names']}
                    
                    **반별 학생 명단:**
                    {context['class_students_text']}
                    
                    **담임선생님 정보:**
                    {context['homeroom_info']}
                    
                    **성적 상위 10명 학생:**
                    {context['top_students_text']}
                    
                    **과목별 성적 분석:**
                    {context['subjects_text']}
                    
                    사용자가 다음과 같은 질문을 할 수 있습니다:
                    
                    **기본 정보 질문:**
                    1. "선생님 명단을 알려줘" → 선생님 목록 제공
                    2. "[선생님 이름] 선생님의 담당 반을 알려줘" → 해당 선생님이 담당하는 반들 제공
                    3. "1학년 1반 담임선생님 알려줘" → 1학년 1반 담임선생님 정보 제공
                    4. "전체 학생 명단을 알려줘" → 모든 학생 목록 제공
                    5. "1학년 1반 학생 명단을 알려줘" → 1학년 1반 학생들만 제공
                    6. "김철수는 몇 반이야?" → 해당 학생의 반 정보 제공
                    7. "전체 학생 수는 몇 명이야?" → 전체 학생 수 제공
                    
                    **성적 분석 질문:**
                    8. "[학생이름] 성적 알려줘" → 해당 학생의 모든 과목, 시험별 성적 제공
                    9. "[학년]학년 [반]반 성적 분석해줘" → 해당 반의 학생별 평균 성적 순위 제공
                    10. "[과목명] 과목 분석해줘" → 해당 과목의 전체 통계 및 학년별 평균 제공
                    11. "성적 상위 학생들 알려줘" → 평균 성적 상위 학생들 목록 제공
                    12. "수학 성적이 좋은 학생들 알려줘" → 특정 과목 성적이 좋은 학생들 분석
                    13. "1학년 1반에서 수학 성적이 제일 좋은 학생은?" → 반별 특정 과목 최고 성적 학생
                    14. "전체 평균 성적은?" → 전체 학생의 평균 성적 통계
                    15. "학년별 평균 성적 비교해줘" → 1학년, 2학년, 3학년 평균 성적 비교
                    
                    성적 분석 시에는 구체적이고 유용한 인사이트를 제공해주세요. 
                    예를 들어, 어떤 과목에서 강점/약점이 있는지, 학년별 성적 추이, 
                    개선이 필요한 부분 등을 분석해주세요."""
                },
                {
                    "role": "user",
                    "content": chat_request.message
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI 응답 생성 오류: {e}")
        return "죄송합니다. AI 응답 생성 중 오류가 발생했습니다." 