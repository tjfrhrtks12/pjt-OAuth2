"""
캘린더 관련 챗봇 서비스
일정 조회, 등록, 삭제 등의 자연어 처리 기능
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models import CalendarEvent
from services.calendar_service import CalendarService
from database_service import DatabaseService
import re


def get_today_schedule(user_id: int) -> str:
    """오늘의 일정 조회"""
    try:
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            today = date.today()
            
            # 오늘의 이벤트 조회
            events = calendar_service.get_events_by_user(user_id, today, today)
            
            if not events:
                return f"오늘({today.strftime('%Y년 %m월 %d일')})은 일정이 없습니다."
            
            result = f"📅 오늘({today.strftime('%Y년 %m월 %d일')})의 일정입니다:\n\n"
            
            # 시간순으로 정렬
            events.sort(key=lambda x: x.start_time if x.start_time else datetime.min.time())
            
            for i, event in enumerate(events, 1):
                result += f"{i}. {event.title}\n"
                
                if event.is_all_day:
                    result += "   📅 종일 일정\n"
                elif event.start_time and event.end_time:
                    result += f"   ⏰ {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                
                if event.location:
                    result += f"   📍 {event.location}\n"
                
                if event.description:
                    result += f"   📝 {event.description}\n"
                
                result += f"   🏷️ {event.event_type}\n\n"
            
            return result
            
    except Exception as e:
        print(f"오늘의 일정 조회 오류: {e}")
        return "오늘의 일정 조회 중 오류가 발생했습니다."


def get_tomorrow_schedule(user_id: int) -> str:
    """내일의 일정 조회"""
    try:
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            # 내일의 이벤트 조회
            events = calendar_service.get_events_by_user(user_id, tomorrow, tomorrow)
            
            if not events:
                return f"내일({tomorrow.strftime('%Y년 %m월 %d일')})은 일정이 없습니다."
            
            result = f"📅 내일({tomorrow.strftime('%Y년 %m월 %d일')})의 일정입니다:\n\n"
            
            # 시간순으로 정렬
            events.sort(key=lambda x: x.start_time if x.start_time else datetime.min.time())
            
            for i, event in enumerate(events, 1):
                result += f"{i}. {event.title}\n"
                
                if event.is_all_day:
                    result += "   📅 종일 일정\n"
                elif event.start_time and event.end_time:
                    result += f"   ⏰ {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                
                if event.location:
                    result += f"   📍 {event.location}\n"
                
                if event.description:
                    result += f"   📝 {event.description}\n"
                
                result += f"   🏷️ {event.event_type}\n\n"
            
            return result
            
    except Exception as e:
        print(f"내일의 일정 조회 오류: {e}")
        return "내일의 일정 조회 중 오류가 발생했습니다."


def get_weekly_schedule(user_id: int) -> str:
    """이번 주 일정 조회"""
    try:
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            today = date.today()
            
            # 이번 주 시작일 (월요일)
            week_start = today - timedelta(days=today.weekday())
            # 이번 주 종료일 (일요일)
            week_end = week_start + timedelta(days=6)
            
            # 이번 주 이벤트 조회
            events = calendar_service.get_events_by_user(user_id, week_start, week_end)
            
            if not events:
                return f"이번 주({week_start.strftime('%m월 %d일')} ~ {week_end.strftime('%m월 %d일')})은 일정이 없습니다."
            
            result = f"📅 이번 주({week_start.strftime('%m월 %d일')} ~ {week_end.strftime('%m월 %d일')}) 일정입니다:\n\n"
            
            # 날짜별로 그룹화
            events_by_date = {}
            for event in events:
                event_date = event.start_date
                if event_date not in events_by_date:
                    events_by_date[event_date] = []
                events_by_date[event_date].append(event)
            
            # 날짜순으로 정렬
            for event_date in sorted(events_by_date.keys()):
                day_name = event_date.strftime('%A')  # 요일
                day_name_kr = {
                    'Monday': '월요일',
                    'Tuesday': '화요일', 
                    'Wednesday': '수요일',
                    'Thursday': '목요일',
                    'Friday': '금요일',
                    'Saturday': '토요일',
                    'Sunday': '일요일'
                }.get(day_name, day_name)
                
                result += f"📆 {event_date.strftime('%m월 %d일')} ({day_name_kr})\n"
                
                # 시간순으로 정렬
                day_events = sorted(events_by_date[event_date], 
                                  key=lambda x: x.start_time if x.start_time else datetime.min.time())
                
                for event in day_events:
                    result += f"  • {event.title}\n"
                    
                    if event.is_all_day:
                        result += "    📅 종일 일정\n"
                    elif event.start_time and event.end_time:
                        result += f"    ⏰ {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                    
                    result += f"    🏷️ {event.event_type}\n"
                
                result += "\n"
            
            return result
            
    except Exception as e:
        print(f"이번 주 일정 조회 오류: {e}")
        return "이번 주 일정 조회 중 오류가 발생했습니다."


def get_specific_date_schedule(date_str: str, user_id: int) -> str:
    """특정 날짜의 일정 조회"""
    try:
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            
            # 날짜 파싱 (다양한 형식 지원)
            try:
                today = date.today()
                
                # 키워드 기반 날짜 처리
                if date_str == "내일":
                    target_date = today + timedelta(days=1)
                elif date_str == "모레":
                    target_date = today + timedelta(days=2)
                elif date_str == "글피":
                    target_date = today + timedelta(days=3)
                elif "월" in date_str and "일" in date_str:
                    # "8월 6일" 형식
                    month_day = date_str.replace("월", " ").replace("일", "").strip()
                    month, day = map(int, month_day.split())
                    target_date = date(2025, month, day)
                elif "/" in date_str:
                    # "8/6" 형식
                    month, day = map(int, date_str.split("/"))
                    target_date = date(2025, month, day)
                else:
                    # 숫자만 있는 경우 (예: "8월 6일" -> "8 6")
                    parts = date_str.split()
                    if len(parts) >= 2:
                        month, day = map(int, parts[:2])
                        target_date = date(2025, month, day)
                    else:
                        return "날짜 형식을 인식할 수 없습니다. '8월 6일' 또는 '8/6' 형식으로 입력해주세요."
            except ValueError:
                return "날짜 형식이 올바르지 않습니다. '8월 6일' 또는 '8/6' 형식으로 입력해주세요."
            
            # 해당 날짜의 이벤트 조회
            events = calendar_service.get_events_by_user(user_id, target_date, target_date)
            
            if not events:
                return f"{target_date.strftime('%Y년 %m월 %d일')}은 일정이 없습니다."
            
            result = f"📅 {target_date.strftime('%Y년 %m월 %d일')}의 일정입니다:\n\n"
            
            # 시간순으로 정렬
            events.sort(key=lambda x: x.start_time if x.start_time else datetime.min.time())
            
            for i, event in enumerate(events, 1):
                result += f"{i}. {event.title}\n"
                
                if event.is_all_day:
                    result += "   📅 종일 일정\n"
                elif event.start_time and event.end_time:
                    result += f"   ⏰ {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                
                if event.location:
                    result += f"   📍 {event.location}\n"
                
                if event.description:
                    result += f"   📝 {event.description}\n"
                
                result += f"   🏷️ {event.event_type}\n\n"
            
            return result
            
    except Exception as e:
        print(f"특정 날짜 일정 조회 오류: {e}")
        return "특정 날짜 일정 조회 중 오류가 발생했습니다."


def create_event_from_natural_language(message: str, user_id: int) -> str:
    """자연어로 일정 생성"""
    try:
        print(f"일정 등록 시작: {message}")
        
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            
            # 날짜 추출
            today = date.today()
            target_date = today
            
            # "오늘", "내일", "모레" 등의 키워드 처리
            if "오늘" in message:
                target_date = today
            elif "내일" in message:
                target_date = today + timedelta(days=1)
            elif "모레" in message:
                target_date = today + timedelta(days=2)
            elif "글피" in message:
                target_date = today + timedelta(days=3)
            
            # 특정 날짜 패턴 (예: "8월 6일", "8/6")
            date_patterns = [
                r'(\d+)월\s*(\d+)일',
                r'(\d+)/(\d+)',
                r'(\d+)\s+(\d+)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, message)
                if match:
                    month, day = map(int, match.groups())
                    target_date = date(2025, month, day)
                    break
            
            # 시간 추출
            time_pattern = r'(\d{1,2})시\s*(\d{0,2})?분?'
            time_match = re.search(time_pattern, message)
            
            start_time = None
            end_time = None
            
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                start_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
                # 기본적으로 1시간 후 종료
                end_hour = (hour + 1) % 24
                end_time = datetime.strptime(f"{end_hour:02d}:{minute:02d}", "%H:%M").time()
            
            # 제목 추출 (시간 정보 제거 후 남은 텍스트)
            title = message
            # 시간 정보 제거
            title = re.sub(time_pattern, '', title)
            # 날짜 정보 제거
            title = re.sub(r'오늘|내일|모레|글피', '', title)
            title = re.sub(r'(\d+)월\s*(\d+)일', '', title)
            title = re.sub(r'(\d+)/(\d+)', '', title)
            # 등록 관련 키워드 제거
            title = re.sub(r'등록해줘|등록|추가해줘|추가|일정\s*등록|일정\s*추가', '', title)
            title = re.sub(r'에\s*', '', title)
            title = re.sub(r'일정을\s*', '', title)
            title = title.strip()
            
            # 제목이 비어있거나 의미없는 경우, 기본 제목 설정
            if not title or title.strip() == "":
                title = f"{event_type}"
            
            # 이벤트 타입 추정
            event_type = "개인일정"
            if any(keyword in title for keyword in ["수업", "강의", "교육"]):
                event_type = "수업"
            elif any(keyword in title for keyword in ["시험", "고사", "평가", "검사"]):
                event_type = "시험"
            elif any(keyword in title for keyword in ["상담", "면담", "미팅"]):
                event_type = "상담"
            elif any(keyword in title for keyword in ["행사", "축제", "대회", "식"]):
                event_type = "행사"
            
            # 색상 설정
            color_map = {
                "수업": "#3788d8",
                "시험": "#dc3545", 
                "상담": "#6f42c1",
                "행사": "#28a745",
                "개인일정": "#ffc107"
            }
            color = color_map.get(event_type, "#3788d8")
            
            # 이벤트 데이터 생성
            event_data = {
                "user_id": user_id,
                "title": title,
                "description": f"{event_type} 관련 일정입니다.",
                "start_date": target_date,
                "end_date": target_date,
                "event_type": event_type,
                "color": color,
                "is_all_day": start_time is None,
                "location": "학교"
            }
            
            if start_time:
                event_data["start_time"] = start_time
            if end_time:
                event_data["end_time"] = end_time
            
            print(f"생성할 이벤트 데이터: {event_data}")
            
            # 이벤트 생성
            try:
                event = calendar_service.create_event(event_data)
                
                # 응답 메시지 생성
                date_str = target_date.strftime('%m월 %d일')
                time_str = ""
                if start_time and end_time:
                    time_str = f" {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
                
                return f"✅ 일정이 성공적으로 등록되었습니다!\n\n📅 {date_str}{time_str}\n📝 {title}\n🏷️ {event_type}"
            except Exception as create_error:
                print(f"이벤트 생성 오류: {create_error}")
                return f"일정 등록 중 오류가 발생했습니다: {str(create_error)}"
            
    except Exception as e:
        print(f"자연어 일정 생성 오류: {e}")
        return "일정 등록 중 오류가 발생했습니다. 다시 시도해주세요."


def delete_event_from_natural_language(message: str, user_id: int) -> str:
    """자연어로 일정 삭제"""
    try:
        with DatabaseService.get_session() as session:
            calendar_service = CalendarService(session)
            
            # 날짜 추출
            today = date.today()
            target_date = today
            
            # "오늘", "내일", "모레" 등의 키워드 처리
            if "오늘" in message:
                target_date = today
            elif "내일" in message:
                target_date = today + timedelta(days=1)
            elif "모레" in message:
                target_date = today + timedelta(days=2)
            elif "글피" in message:
                target_date = today + timedelta(days=3)
            
            # 특정 날짜 패턴 (예: "8월 6일", "8/6")
            date_patterns = [
                r'(\d+)월\s*(\d+)일',
                r'(\d+)/(\d+)',
                r'(\d+)\s+(\d+)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, message)
                if match:
                    month, day = map(int, match.groups())
                    target_date = date(2025, month, day)
                    break
            
            # 시간 추출
            time_pattern = r'(\d{1,2})시\s*(\d{0,2})?분?'
            time_match = re.search(time_pattern, message)
            
            target_time = None
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                target_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
            
            # 제목 추출
            title = message
            # 시간 정보 제거
            title = re.sub(time_pattern, '', title)
            # 날짜 정보 제거
            title = re.sub(r'오늘|내일|모레|글피', '', title)
            title = re.sub(r'(\d+)월\s*(\d+)일', '', title)
            title = re.sub(r'(\d+)/(\d+)', '', title)
            # 삭제 관련 키워드 제거
            title = re.sub(r'삭제해줘|삭제|취소해줘|취소|일정\s*삭제|일정\s*취소', '', title)
            title = re.sub(r'에\s*', '', title)
            title = re.sub(r'일정을\s*', '', title)
            title = re.sub(r'일정이\s*', '', title)
            title = re.sub(r'일정\s*', '', title)
            title = re.sub(r'을\s*', '', title)
            title = re.sub(r'이\s*', '', title)
            title = re.sub(r'가\s*', '', title)
            title = title.strip()
            
            # 해당 날짜의 이벤트 조회
            events = calendar_service.get_events_by_user(user_id, target_date, target_date)
            
            if not events:
                return f"{target_date.strftime('%Y년 %m월 %d일')}에는 삭제할 일정이 없습니다."
            
            # 제목과 시간으로 일치하는 이벤트 찾기
            matched_events = []
            for event in events:
                # 제목이 비어있으면 시간만으로 매칭
                if not title or title.strip() == "":
                    if target_time and event.start_time:
                        # 시간 차이가 30분 이내인 경우 매칭
                        time_diff = abs((event.start_time.hour * 60 + event.start_time.minute) - 
                                      (target_time.hour * 60 + target_time.minute))
                        if time_diff <= 30:
                            matched_events.append(event)
                else:
                    # 제목이 포함되어 있는지 확인
                    if title.lower() in event.title.lower():
                        if target_time and event.start_time:
                            # 시간도 일치하는지 확인
                            time_diff = abs((event.start_time.hour * 60 + event.start_time.minute) - 
                                          (target_time.hour * 60 + target_time.minute))
                            if time_diff <= 30:
                                matched_events.append(event)
                        else:
                            # 시간이 없으면 제목만으로 매칭
                            matched_events.append(event)
            
            if not matched_events:
                return f"{target_date.strftime('%Y년 %m월 %d일')}에 '{title}' 일정을 찾을 수 없습니다."
            
            # 첫 번째 매칭된 이벤트 삭제
            event_to_delete = matched_events[0]
            success = calendar_service.delete_event(event_to_delete.id, user_id)
            
            if success:
                return f"✅ '{event_to_delete.title}' 일정이 성공적으로 삭제되었습니다."
            else:
                return "일정 삭제 중 오류가 발생했습니다."
            
    except Exception as e:
        print(f"자연어 일정 삭제 오류: {e}")
        return "일정 삭제 중 오류가 발생했습니다. 다시 시도해주세요." 