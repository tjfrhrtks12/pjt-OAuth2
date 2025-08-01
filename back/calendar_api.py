from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import get_db, JWT_SECRET_KEY, JWT_ALGORITHM
from models import User
from calendar_service import CalendarService

router = APIRouter()

class EventCreateRequest(BaseModel):
    summary: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""
    calendar_id: str = "primary"

class EventUpdateRequest(BaseModel):
    summary: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    summary: str
    start: dict
    end: dict
    description: str = ""
    location: str = ""
    html_link: str

def get_current_user(token: str = Query(..., alias="token"), db: Session = Depends(get_db)) -> User:
    """JWT 토큰으로 현재 사용자 조회"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/api/calendar/calendars")
async def get_calendars(token: str = Query(...), db: Session = Depends(get_db)):
    """사용자의 캘린더 목록 조회"""
    try:
        user = get_current_user(token, db)
        
        # 사용자의 Google 액세스 토큰을 DB에서 가져오기
        if not user.google_access_token:
            raise HTTPException(status_code=401, detail="Google Calendar 권한이 없습니다. 다시 로그인해주세요.")
        
        access_token = user.google_access_token
        refresh_token = user.google_refresh_token
        
        calendars = CalendarService.get_calendars(access_token, refresh_token)
        return {"calendars": calendars}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar 조회 실패: {str(e)}")

@router.get("/api/calendar/events")
async def get_events(
    token: str = Query(...),
    calendar_id: str = Query("primary"),
    time_min: Optional[str] = Query(None),
    time_max: Optional[str] = Query(None),
    max_results: int = Query(50),
    db: Session = Depends(get_db)
):
    """캘린더 이벤트 조회"""
    try:
        user = get_current_user(token, db)
        
        # 사용자의 Google 액세스 토큰을 DB에서 가져오기
        if not user.google_access_token:
            raise HTTPException(status_code=401, detail="Google Calendar 권한이 없습니다. 다시 로그인해주세요.")
        
        access_token = user.google_access_token
        refresh_token = user.google_refresh_token
        
        events = CalendarService.get_events(
            access_token=access_token,
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
            refresh_token=refresh_token
        )
        
        return {"events": events}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 조회 실패: {str(e)}")

@router.post("/api/calendar/events")
async def create_event(
    event_request: EventCreateRequest,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """새 이벤트 생성"""
    try:
        user = get_current_user(token, db)
        
        # 사용자의 Google 액세스 토큰을 DB에서 가져오기
        if not user.google_access_token:
            raise HTTPException(status_code=401, detail="Google Calendar 권한이 없습니다. 다시 로그인해주세요.")
        
        access_token = user.google_access_token
        refresh_token = user.google_refresh_token
        
        event_data = CalendarService.format_event_data(
            summary=event_request.summary,
            start_time=event_request.start_time,
            end_time=event_request.end_time,
            description=event_request.description,
            location=event_request.location
        )
        
        event = CalendarService.create_event(
            access_token=access_token,
            event_data=event_data,
            calendar_id=event_request.calendar_id,
            refresh_token=refresh_token
        )
        
        if not event:
            raise HTTPException(status_code=500, detail="이벤트 생성 실패")
        
        return {"event": event, "message": "이벤트가 성공적으로 생성되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 생성 실패: {str(e)}")

@router.put("/api/calendar/events/{event_id}")
async def update_event(
    event_id: str,
    event_request: EventUpdateRequest,
    token: str = Query(...),
    calendar_id: str = Query("primary"),
    db: Session = Depends(get_db)
):
    """이벤트 수정"""
    try:
        user = get_current_user(token, db)
        
        # 사용자의 Google 액세스 토큰을 DB에서 가져오기
        if not user.google_access_token:
            raise HTTPException(status_code=401, detail="Google Calendar 권한이 없습니다. 다시 로그인해주세요.")
        
        access_token = user.google_access_token
        refresh_token = user.google_refresh_token
        
        # 기존 이벤트 조회
        existing_events = CalendarService.get_events(access_token, calendar_id, refresh_token=refresh_token)
        existing_event = None
        for event in existing_events:
            if event.get('id') == event_id:
                existing_event = event
                break
        
        if not existing_event:
            raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
        
        # 업데이트할 데이터 준비
        update_data = existing_event.copy()
        if event_request.summary is not None:
            update_data['summary'] = event_request.summary
        if event_request.start_time is not None:
            update_data['start']['dateTime'] = event_request.start_time
        if event_request.end_time is not None:
            update_data['end']['dateTime'] = event_request.end_time
        if event_request.description is not None:
            update_data['description'] = event_request.description
        if event_request.location is not None:
            update_data['location'] = event_request.location
        
        updated_event = CalendarService.update_event(
            access_token=access_token,
            event_id=event_id,
            event_data=update_data,
            calendar_id=calendar_id,
            refresh_token=refresh_token
        )
        
        if not updated_event:
            raise HTTPException(status_code=500, detail="이벤트 수정 실패")
        
        return {"event": updated_event, "message": "이벤트가 성공적으로 수정되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 수정 실패: {str(e)}")

@router.delete("/api/calendar/events/{event_id}")
async def delete_event(
    event_id: str,
    token: str = Query(...),
    calendar_id: str = Query("primary"),
    db: Session = Depends(get_db)
):
    """이벤트 삭제"""
    try:
        user = get_current_user(token, db)
        
        # 사용자의 Google 액세스 토큰을 DB에서 가져오기
        if not user.google_access_token:
            raise HTTPException(status_code=401, detail="Google Calendar 권한이 없습니다. 다시 로그인해주세요.")
        
        access_token = user.google_access_token
        refresh_token = user.google_refresh_token
        
        success = CalendarService.delete_event(
            access_token=access_token,
            event_id=event_id,
            calendar_id=calendar_id,
            refresh_token=refresh_token
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="이벤트 삭제 실패")
        
        return {"message": "이벤트가 성공적으로 삭제되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이벤트 삭제 실패: {str(e)}")

@router.get("/api/calendar/status")
async def get_calendar_status(token: str = Query(...), db: Session = Depends(get_db)):
    """Calendar API 연결 상태 확인"""
    try:
        user = get_current_user(token, db)
        
        return {
            "status": "ready",
            "message": "Google Calendar API가 준비되었습니다.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar 상태 확인 실패: {str(e)}") 