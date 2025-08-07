import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useChat } from '../../contexts/ChatContext';
import MainSidebar from '../MainSidebar';
import NavigationBar from '../NavigationBar';
import Chatbot from '../Chatbot';
import './SchedulePage.css';

interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  event_type: string;
  color: string;
  is_all_day: boolean;
  location?: string;
}

const SchedulePage: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { setEventUpdateCallback } = useChat();

  // 현재 월의 첫 번째 날과 마지막 날 계산
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  
  // 캘린더 시작일 (이전 달의 날짜들 포함)
  const startDate = new Date(firstDayOfMonth);
  startDate.setDate(startDate.getDate() - firstDayOfMonth.getDay());
  
  // 캘린더 종료일 (다음 달의 날짜들 포함)
  const endDate = new Date(lastDayOfMonth);
  endDate.setDate(endDate.getDate() + (6 - lastDayOfMonth.getDay()));

  // 캘린더 날짜 배열 생성
  const calendarDays = [];
  const current = new Date(startDate);
  
  while (current <= endDate) {
    calendarDays.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }

  // 이벤트 데이터 가져오기
  const fetchEvents = async () => {
    try {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;
      
      // 로그인한 사용자의 ID 사용
      const currentUserId = user?.id || 1;
      
      const response = await fetch(`http://localhost:8000/api/calendar/events?user_id=${currentUserId}&year=${year}&month=${month}`);
      
      console.log('API 호출 URL:', `http://localhost:8000/api/calendar/events?user_id=${currentUserId}&year=${year}&month=${month}`);
      console.log('API 응답 상태:', response.status);
      
      if (!response.ok) {
        throw new Error('이벤트 로딩 실패');
      }
      
      const result = await response.json();
      console.log('API 응답 데이터:', result);
      
      if (result.success) {
        console.log('설정된 이벤트:', result.data);
        setEvents(result.data);
      } else {
        console.error('API 응답 오류:', result);
      }
    } catch (error) {
      console.error('이벤트 로딩 실패:', error);
      // 에러 시 빈 배열로 설정 (사용자별 일정이 없을 수 있음)
      setEvents([]);
    }
  };

  // 초기 로딩용 함수 (로딩 상태 포함)
  const fetchEventsWithLoading = async () => {
    try {
      setLoading(true);
      await fetchEvents();
    } finally {
      setLoading(false);
    }
  };

  // ChatContext에 이벤트 업데이트 콜백 등록
  useEffect(() => {
    setEventUpdateCallback(fetchEventsWithLoading);
  }, [setEventUpdateCallback, currentDate, user?.id]);

  useEffect(() => {
    fetchEventsWithLoading();
  }, [currentDate, user?.id]);

  // 특정 날짜의 이벤트 가져오기
  const getEventsForDate = (date: Date) => {
    // 날짜를 YYYY-MM-DD 형식으로 변환 (시간대 문제 해결)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
    return events.filter(event => {
      const eventStart = event.start_date;
      const eventEnd = event.end_date;
      return dateStr >= eventStart && dateStr <= eventEnd;
    });
  };

  // 이전 달로 이동
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  // 다음 달로 이동
  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  // 오늘로 이동
  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // 사이드바 아이템 클릭 처리
  const handleSidebarSelect = (item: string) => {
    if (item === '일정표') {
      // 이미 일정표 페이지에 있으므로 아무것도 하지 않음
      return;
    } else {
      // 다른 메뉴 선택 시 메인 페이지로 이동
      navigate('/main');
    }
  };

  // 로그아웃
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };



  if (loading) {
    return (
      <div className="schedule-page">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="schedule-container">
      <MainSidebar 
        isExpanded={isSidebarExpanded} 
        onExpandChange={setIsSidebarExpanded}
        onItemClick={handleSidebarSelect}
      />
      <div className="schedule-content">
        <NavigationBar user={user} onLogout={handleLogout} />
        <div className="schedule-page">
          <div className="schedule-header">
            <h1>{user?.name || '사용자'}님의 일정표</h1>
            <div className="calendar-controls">
              <button onClick={goToPreviousMonth} className="nav-btn">‹</button>
              <button onClick={goToToday} className="today-btn">오늘</button>
              <button onClick={goToNextMonth} className="nav-btn">›</button>
            </div>
            <h2 className="current-month">
              {currentDate.getFullYear()}년 {currentDate.getMonth() + 1}월
            </h2>
          </div>

          <div className="calendar-container">
            <div className="calendar-header">
              {['일', '월', '화', '수', '목', '금', '토'].map(day => (
                <div key={day} className="calendar-day-header">{day}</div>
              ))}
            </div>
            
            <div className="calendar-grid">
              {calendarDays.map((day, index) => {
                const dayEvents = getEventsForDate(day);
                const isCurrentMonth = day.getMonth() === currentDate.getMonth();
                const isToday = day.toDateString() === new Date().toDateString();
                
                return (
                  <div 
                    key={index} 
                    className={`calendar-day ${!isCurrentMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}`}
                  >
                    <div className="day-number">{day.getDate()}</div>
                    <div className="day-events">
                      {dayEvents.map(event => (
                        <div 
                          key={event.id} 
                          className="event-item"
                          style={{ backgroundColor: event.color }}
                          title={event.title}
                        >
                          {event.is_all_day ? (
                            <span className="all-day-event">{event.title}</span>
                          ) : (
                            <span className="time-event">
                              {event.start_time} {event.title}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulePage; 