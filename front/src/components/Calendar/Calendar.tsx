import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import CustomCalendar from './CustomCalendar';
import './Calendar.css';

interface CalendarEvent {
  id: string;
  summary: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
  description?: string;
  location?: string;
  htmlLink: string;
}

interface CalendarProps {
  isVisible: boolean;
}

const Calendar: React.FC<CalendarProps> = ({ isVisible }) => {
  const { token } = useAuth();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCalendarWidget, setShowCalendarWidget] = useState(true);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [newEvent, setNewEvent] = useState({
    summary: '',
    start_time: '',
    end_time: '',
    description: '',
    location: ''
  });

  // 이벤트 목록 조회
  const fetchEvents = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // 현재 달의 시작과 끝 시간 계산
      const now = new Date();
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
      const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      
      const response = await axios.get(`http://localhost:8000/api/calendar/events?token=${token}&max_results=100`);
      setEvents(response.data.events || []);
    } catch (err: any) {
      console.error('Calendar 이벤트 조회 오류:', err);
      setError(err.response?.data?.detail || '이벤트를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 새 이벤트 생성
  const createEvent = async () => {
    if (!token || !newEvent.summary || !newEvent.start_time || !newEvent.end_time) {
      setError('필수 정보를 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.post(`http://localhost:8000/api/calendar/events?token=${token}`, newEvent);
      setNewEvent({
        summary: '',
        start_time: '',
        end_time: '',
        description: '',
        location: ''
      });
      setShowCreateForm(false);
      fetchEvents(); // 이벤트 목록 새로고침
    } catch (err: any) {
      console.error('이벤트 생성 오류:', err);
      setError(err.response?.data?.detail || '이벤트 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 이벤트 삭제
  const deleteEvent = async (eventId: string) => {
    if (!token) return;

    if (!window.confirm('이 이벤트를 삭제하시겠습니까?')) return;

    setLoading(true);
    setError(null);

    try {
      await axios.delete(`http://localhost:8000/api/calendar/events/${eventId}?token=${token}`);
      fetchEvents(); // 이벤트 목록 새로고침
    } catch (err: any) {
      console.error('이벤트 삭제 오류:', err);
      setError(err.response?.data?.detail || '이벤트 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 날짜 포맷팅
  const formatDateTime = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 날짜 클릭 핸들러
  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
    setShowCreateForm(true);
    // 선택된 날짜로 새 이벤트 시간 설정
    const dateStr = date.toISOString().slice(0, 16);
    setNewEvent(prev => ({
      ...prev,
      start_time: dateStr,
      end_time: dateStr
    }));
  };

  // 이벤트 클릭 핸들러
  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    window.open(event.htmlLink, '_blank');
  };

  // 테스트 일정 생성
  const createTestEvent = async () => {
    if (!token) return;

    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dayAfterTomorrow = new Date(now);
    dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 2);

    const testEvents = [
      {
        summary: '🧪 테스트 미팅',
        start_time: tomorrow.toISOString().slice(0, 16),
        end_time: new Date(tomorrow.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16),
        description: '이것은 테스트 일정입니다.',
        location: '회의실 A'
      },
      {
        summary: '📚 스터디 세션',
        start_time: dayAfterTomorrow.toISOString().slice(0, 16),
        end_time: new Date(dayAfterTomorrow.getTime() + 2 * 60 * 60 * 1000).toISOString().slice(0, 16),
        description: '프로그래밍 스터디',
        location: '카페'
      }
    ];

    setLoading(true);
    setError(null);

    try {
      for (const eventData of testEvents) {
        await axios.post(`http://localhost:8000/api/calendar/events?token=${token}`, eventData);
      }
      fetchEvents(); // 이벤트 목록 새로고침
      alert('테스트 일정이 생성되었습니다!');
    } catch (err: any) {
      console.error('테스트 이벤트 생성 오류:', err);
      setError(err.response?.data?.detail || '테스트 이벤트 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트가 보일 때 이벤트 조회
  useEffect(() => {
    if (isVisible && token) {
      fetchEvents();
    }
  }, [isVisible, token]);

  if (!isVisible) return null;

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h2>📅 Google Calendar</h2>
        <div className="calendar-controls">
          <button 
            className={`view-toggle-btn ${showCalendarWidget ? 'active' : ''}`}
            onClick={() => setShowCalendarWidget(true)}
          >
            📅 달력 보기
          </button>
          <button 
            className={`view-toggle-btn ${!showCalendarWidget ? 'active' : ''}`}
            onClick={() => setShowCalendarWidget(false)}
          >
            📋 목록 보기
          </button>
          <button 
            className="create-event-btn"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? '취소' : '+ 새 일정'}
          </button>
          <button 
            className="test-event-btn"
            onClick={createTestEvent}
            style={{
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)',
              color: 'white',
              border: 'none',
              padding: '12px 20px',
              borderRadius: '25px',
              fontSize: '0.9rem',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(255, 107, 107, 0.3)'
            }}
          >
            🧪 테스트 일정
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 새 이벤트 생성 폼 */}
      {showCreateForm && (
        <div className="create-event-form">
          <h3>새 일정 만들기</h3>
          <div className="form-group">
            <label>제목 *</label>
            <input
              type="text"
              value={newEvent.summary}
              onChange={(e) => setNewEvent({...newEvent, summary: e.target.value})}
              placeholder="일정 제목"
            />
          </div>
          <div className="form-group">
            <label>시작 시간 *</label>
            <input
              type="datetime-local"
              value={newEvent.start_time}
              onChange={(e) => setNewEvent({...newEvent, start_time: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>종료 시간 *</label>
            <input
              type="datetime-local"
              value={newEvent.end_time}
              onChange={(e) => setNewEvent({...newEvent, end_time: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>설명</label>
            <textarea
              value={newEvent.description}
              onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
              placeholder="일정 설명"
            />
          </div>
          <div className="form-group">
            <label>장소</label>
            <input
              type="text"
              value={newEvent.location}
              onChange={(e) => setNewEvent({...newEvent, location: e.target.value})}
              placeholder="장소"
            />
          </div>
          <div className="form-actions">
            <button 
              className="save-btn"
              onClick={createEvent}
              disabled={loading}
            >
              {loading ? '저장 중...' : '저장'}
            </button>
            <button 
              className="cancel-btn"
              onClick={() => setShowCreateForm(false)}
            >
              취소
            </button>
          </div>
        </div>
      )}

      {/* 커스텀 캘린더 또는 이벤트 목록 */}
      {showCalendarWidget ? (
        <div className="custom-calendar-container">
          <div className="calendar-widget-header">
            <h3>📅 나의 일정 캘린더</h3>
            <p>Google Calendar와 실시간 연동됩니다. 날짜를 클릭하면 새 일정을 만들고, 일정을 클릭하면 Google Calendar에서 편집할 수 있습니다.</p>
          </div>
          <div className="calendar-widget">
            <CustomCalendar
              events={events}
              onDateClick={handleDateClick}
              onEventClick={handleEventClick}
            />
          </div>
          <div className="calendar-widget-footer">
            <a 
              href="https://calendar.google.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="open-calendar-btn"
            >
              🔗 Google Calendar에서 열기
            </a>
          </div>
        </div>
      ) : (
        <div className="events-list">
          <h3>일정 목록</h3>
          {loading ? (
            <div className="loading">일정을 불러오는 중...</div>
          ) : events.length === 0 ? (
            <div className="no-events">등록된 일정이 없습니다.</div>
          ) : (
            <div className="events-grid">
              {events.map((event) => (
                <div key={event.id} className="event-card">
                  <div className="event-header">
                    <h4>{event.summary}</h4>
                    <button 
                      className="delete-btn"
                      onClick={() => deleteEvent(event.id)}
                      title="삭제"
                    >
                      🗑️
                    </button>
                  </div>
                  <div className="event-details">
                    <p><strong>시작:</strong> {formatDateTime(event.start.dateTime)}</p>
                    <p><strong>종료:</strong> {formatDateTime(event.end.dateTime)}</p>
                    {event.description && (
                      <p><strong>설명:</strong> {event.description}</p>
                    )}
                    {event.location && (
                      <p><strong>장소:</strong> {event.location}</p>
                    )}
                  </div>
                  <div className="event-actions">
                    <a 
                      href={event.htmlLink} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="view-btn"
                    >
                      Google Calendar에서 보기
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Calendar; 