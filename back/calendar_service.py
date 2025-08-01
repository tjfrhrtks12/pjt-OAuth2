from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import os
import json
from datetime import datetime, timedelta
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

class CalendarService:
    """Google Calendar 서비스 클래스"""
    
    # Calendar API 스코프
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    @staticmethod
    def create_credentials_from_tokens(access_token: str, refresh_token: str = None) -> Credentials:
        """액세스 토큰과 리프레시 토큰으로 Credentials 객체 생성"""
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=CalendarService.SCOPES
        )
        return creds
    
    @staticmethod
    def get_calendar_service(access_token: str, refresh_token: str = None):
        """Calendar API 서비스 객체 생성"""
        try:
            creds = CalendarService.create_credentials_from_tokens(access_token, refresh_token)
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            print(f"Calendar 서비스 생성 오류: {e}")
            return None
    
    @staticmethod
    def get_calendars(access_token: str, refresh_token: str = None) -> List[Dict]:
        """사용자의 캘린더 목록 조회"""
        try:
            service = CalendarService.get_calendar_service(access_token, refresh_token)
            if not service:
                return []
            
            calendars = service.calendarList().list().execute()
            return calendars.get('items', [])
        except HttpError as error:
            print(f"캘린더 목록 조회 오류: {error}")
            return []
    
    @staticmethod
    def get_events(access_token: str, calendar_id: str = 'primary', 
                   time_min: str = None, time_max: str = None, 
                   max_results: int = 10, refresh_token: str = None) -> List[Dict]:
        """캘린더 이벤트 조회"""
        try:
            service = CalendarService.get_calendar_service(access_token, refresh_token)
            if not service:
                return []
            
            # 기본 시간 설정 (현재 달의 시작부터 다음 달의 끝까지)
            if not time_min:
                now = datetime.utcnow()
                time_min = datetime(now.year, now.month, 1).isoformat() + 'Z'
            if not time_max:
                now = datetime.utcnow()
                if now.month == 12:
                    time_max = datetime(now.year + 1, 1, 1).isoformat() + 'Z'
                else:
                    time_max = datetime(now.year, now.month + 1, 1).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            print(f"이벤트 조회 오류: {error}")
            return []
    
    @staticmethod
    def create_event(access_token: str, event_data: Dict, 
                    calendar_id: str = 'primary', refresh_token: str = None) -> Optional[Dict]:
        """새 이벤트 생성"""
        try:
            service = CalendarService.get_calendar_service(access_token, refresh_token)
            if not service:
                return None
            
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return event
        except HttpError as error:
            print(f"이벤트 생성 오류: {error}")
            return None
    
    @staticmethod
    def update_event(access_token: str, event_id: str, event_data: Dict,
                    calendar_id: str = 'primary', refresh_token: str = None) -> Optional[Dict]:
        """이벤트 수정"""
        try:
            service = CalendarService.get_calendar_service(access_token, refresh_token)
            if not service:
                return None
            
            event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            return event
        except HttpError as error:
            print(f"이벤트 수정 오류: {error}")
            return None
    
    @staticmethod
    def delete_event(access_token: str, event_id: str,
                    calendar_id: str = 'primary', refresh_token: str = None) -> bool:
        """이벤트 삭제"""
        try:
            service = CalendarService.get_calendar_service(access_token, refresh_token)
            if not service:
                return False
            
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return True
        except HttpError as error:
            print(f"이벤트 삭제 오류: {error}")
            return False
    
    @staticmethod
    def format_event_data(summary: str, start_time: str, end_time: str, 
                         description: str = "", location: str = "") -> Dict:
        """이벤트 데이터 포맷팅"""
        return {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Seoul',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        } 