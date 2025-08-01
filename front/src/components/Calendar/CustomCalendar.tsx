import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import './CustomCalendar.css';

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
  colorId?: string;
}

interface CustomCalendarProps {
  events: CalendarEvent[];
  onDateClick: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

const CustomCalendar: React.FC<CustomCalendarProps> = ({ 
  events, 
  onDateClick, 
  onEventClick 
}) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  // 이벤트 색상 매핑
  const eventColors = [
    '#4285f4', // 파란색
    '#ea4335', // 빨간색
    '#fbbc04', // 노란색
    '#34a853', // 초록색
    '#ff6d01', // 주황색
    '#46bdc6', // 청록색
    '#7b1fa2', // 보라색
    '#d81b60', // 분홍색
    '#5c6bc0', // 인디고색
    '#26a69a', // 티얼색
  ];

  // 날짜별 이벤트 그룹화
  const eventsByDate = useMemo(() => {
    const grouped: { [key: string]: CalendarEvent[] } = {};
    
    events.forEach(event => {
      const startDate = new Date(event.start.dateTime);
      const dateKey = startDate.toISOString().split('T')[0];
      
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(event);
    });
    
    return grouped;
  }, [events]);

  // 달력 그리드 생성
  const calendarGrid = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const grid = [];
    const totalDays = 42; // 6주 x 7일
    
    for (let i = 0; i < totalDays; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const dateKey = date.toISOString().split('T')[0];
      const dayEvents = eventsByDate[dateKey] || [];
      
      grid.push({
        date: new Date(date),
        isCurrentMonth: date.getMonth() === month,
        isToday: date.toDateString() === new Date().toDateString(),
        events: dayEvents
      });
    }
    
    return grid;
  }, [currentDate, eventsByDate]);

  // 이전/다음 달 이동
  const goToPreviousMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  // 날짜 클릭 핸들러
  const handleDateClick = (date: Date) => {
    setSelectedDate(date);
    onDateClick(date);
  };

  // 이벤트 클릭 핸들러
  const handleEventClick = (event: CalendarEvent, e: React.MouseEvent) => {
    e.stopPropagation();
    onEventClick(event);
  };

  // 이벤트 색상 가져오기
  const getEventColor = (event: CalendarEvent, index: number) => {
    if (event.colorId) {
      return eventColors[parseInt(event.colorId) % eventColors.length];
    }
    return eventColors[index % eventColors.length];
  };

  const monthNames = [
    '1월', '2월', '3월', '4월', '5월', '6월',
    '7월', '8월', '9월', '10월', '11월', '12월'
  ];

  const dayNames = ['일', '월', '화', '수', '목', '금', '토'];

  return (
    <div className="custom-calendar">
      <div className="calendar-header">
        <div className="calendar-nav">
          <button onClick={goToPreviousMonth} className="nav-btn">
            ‹
          </button>
          <h2 className="calendar-title">
            {currentDate.getFullYear()}년 {monthNames[currentDate.getMonth()]}
          </h2>
          <button onClick={goToNextMonth} className="nav-btn">
            ›
          </button>
        </div>
        <button onClick={goToToday} className="today-btn">
          오늘
        </button>
      </div>

      <div className="calendar-grid">
        {/* 요일 헤더 */}
        <div className="calendar-weekdays">
          {dayNames.map(day => (
            <div key={day} className="weekday">
              {day}
            </div>
          ))}
        </div>

        {/* 날짜 그리드 */}
        <div className="calendar-days">
          {calendarGrid.map((day, index) => (
            <div
              key={index}
              className={`calendar-day ${
                !day.isCurrentMonth ? 'other-month' : ''
              } ${
                day.isToday ? 'today' : ''
              } ${
                selectedDate && day.date.toDateString() === selectedDate.toDateString() 
                  ? 'selected' : ''
              }`}
              onClick={() => handleDateClick(day.date)}
            >
              <div className="day-number">{day.date.getDate()}</div>
              
              {/* 이벤트 표시 */}
              <div className="day-events">
                {day.events.slice(0, 3).map((event, eventIndex) => (
                  <div
                    key={event.id}
                    className="day-event"
                    style={{
                      backgroundColor: getEventColor(event, eventIndex),
                      color: 'white'
                    }}
                    onClick={(e) => handleEventClick(event, e)}
                    title={event.summary}
                  >
                    {event.summary}
                  </div>
                ))}
                {day.events.length > 3 && (
                  <div className="more-events">
                    +{day.events.length - 3}개 더
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 이벤트 범례 */}
      <div className="calendar-legend">
        <h4>일정 범례</h4>
        <div className="legend-items">
          {eventColors.slice(0, 5).map((color, index) => (
            <div key={index} className="legend-item">
              <div 
                className="legend-color" 
                style={{ backgroundColor: color }}
              />
              <span>일정 {index + 1}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CustomCalendar; 