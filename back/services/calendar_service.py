from sqlalchemy.orm import Session
from models import CalendarEvent
from datetime import datetime, date
from typing import List, Optional

class CalendarService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_events_by_user(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[CalendarEvent]:
        """사용자의 이벤트 조회"""
        query = self.db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
        
        if start_date:
            query = query.filter(CalendarEvent.start_date >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.end_date <= end_date)
            
        return query.order_by(CalendarEvent.start_date).all()

    def get_event_by_id(self, event_id: int, user_id: int) -> Optional[CalendarEvent]:
        """특정 이벤트 조회"""
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == user_id
        ).first()

    def create_event(self, event_data: dict) -> CalendarEvent:
        """새 이벤트 생성"""
        event = CalendarEvent(**event_data)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: int, user_id: int, event_data: dict) -> Optional[CalendarEvent]:
        """이벤트 수정"""
        event = self.get_event_by_id(event_id, user_id)
        if not event:
            return None
            
        for key, value in event_data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        event.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: int, user_id: int) -> bool:
        """이벤트 삭제"""
        event = self.get_event_by_id(event_id, user_id)
        if not event:
            return False
            
        self.db.delete(event)
        self.db.commit()
        return True

    def get_events_by_month(self, user_id: int, year: int, month: int) -> List[CalendarEvent]:
        """특정 월의 이벤트 조회"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - date.resolution
        else:
            end_date = date(year, month + 1, 1) - date.resolution
            
        return self.get_events_by_user(user_id, start_date, end_date) 