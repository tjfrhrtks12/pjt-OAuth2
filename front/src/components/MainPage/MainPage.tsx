import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import MainSidebar from '../MainSidebar';
import SubSidebar from '../SubSidebar';
import NavigationBar from '../NavigationBar';
import Chatbot from '../Chatbot';
import './MainPage.css';

interface MainPageProps {
  isSidebarExpanded: boolean;
  onSidebarExpandChange: (expanded: boolean) => void;
}

const MainPage: React.FC<MainPageProps> = ({ isSidebarExpanded, onSidebarExpandChange }) => {
  const [isSubSidebarVisible, setIsSubSidebarVisible] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleSidebarSelect = (item: string) => {
    if (item === '1학년') {
      setIsSubSidebarVisible(true);
    } else if (item === '일정표') {
      navigate('/schedule');
    } else {
      setIsSubSidebarVisible(false);
    }
  };

  const handleStudentManagementClick = () => {
    onSidebarExpandChange(false);
    navigate('/student-management');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };



  // 학교 일정 데이터
  const schoolEvents = [
    { id: 1, title: '2024학년도 1학기 시작', date: '2024-03-01', type: 'academic', priority: 'high' },
    { id: 2, title: '입학식', date: '2024-03-04', type: 'ceremony', priority: 'high' },
    { id: 3, title: '중간고사', date: '2024-04-15', type: 'exam', priority: 'medium' },
    { id: 4, title: '체육대회', date: '2024-05-20', type: 'event', priority: 'medium' },
    { id: 5, title: '기말고사', date: '2024-06-20', type: 'exam', priority: 'high' },
    { id: 6, title: '여름방학', date: '2024-07-15', type: 'holiday', priority: 'low' }
  ];

  // 학교 통계 데이터
  const schoolStats = [
    { id: 1, title: '전체 학생 수', value: '1,247명', change: '+12', trend: 'up', icon: '👥' },
    { id: 2, title: '전체 교직원', value: '89명', change: '+3', trend: 'up', icon: '👨‍🏫' },
    { id: 3, title: '학급 수', value: '42개', change: '+2', trend: 'up', icon: '🏫' },
    { id: 4, title: '평균 출석률', value: '96.8%', change: '+1.2%', trend: 'up', icon: '📊' }
  ];

  // 최근 공지사항
  const announcements = [
    { id: 1, title: '2024학년도 1학기 시간표 변경 안내', date: '2024-02-28', category: '학사안내' },
    { id: 2, title: '코로나19 예방접종 관련 안내', date: '2024-02-27', category: '보건안내' },
    { id: 3, title: '2024학년도 신입생 오리엔테이션 안내', date: '2024-02-26', category: '입학안내' },
    { id: 4, title: '학교 시설물 점검 일정 안내', date: '2024-02-25', category: '시설안내' }
  ];

  // 오늘의 날씨 정보 (예시)
  const weatherInfo = {
    temperature: '18°C',
    condition: '맑음',
    humidity: '65%',
    windSpeed: '3m/s'
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'academic': return '#5b9bd5';
      case 'exam': return '#e74c3c';
      case 'event': return '#f39c12';
      case 'ceremony': return '#9b59b6';
      case 'holiday': return '#27ae60';
      default: return '#95a5a6';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#27ae60';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="main-container">
      <MainSidebar 
        isExpanded={isSidebarExpanded} 
        onExpandChange={onSidebarExpandChange}
        onItemClick={handleSidebarSelect}
      />
      {isSubSidebarVisible && <SubSidebar />}
      
      <div className="main-content-wrapper">
        <NavigationBar user={user} onLogout={handleLogout} />
        <div className="main-content">
          {/* 헤더 섹션 */}
          <div className="dashboard-header">
            <div className="header-content">
              <div className="welcome-section">
                <h1>🏫 학교 관리 시스템</h1>
                <p>2024학년도 1학기 학교 현황 및 일정 관리</p>
              </div>
              <div className="weather-widget">
                <div className="weather-icon">☀️</div>
                <div className="weather-info">
                  <div className="temperature">{weatherInfo.temperature}</div>
                  <div className="condition">{weatherInfo.condition}</div>
                </div>
              </div>
            </div>
          </div>

          {/* 통계 카드 섹션 */}
          <div className="stats-section">
            {schoolStats.map((stat) => (
              <div key={stat.id} className="stat-card">
                <div className="stat-icon">{stat.icon}</div>
                <div className="stat-content">
                  <h3>{stat.title}</h3>
                  <div className="stat-number">{stat.value}</div>
                  <div className={`stat-change ${stat.trend}`}>
                    {stat.change}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* 메인 콘텐츠 그리드 */}
          <div className="dashboard-grid">
            {/* 학교 일정 */}
            <div className="dashboard-card schedule-card">
              <div className="card-header">
                <h3>📅 학교 일정</h3>
                <span className="card-subtitle">2024학년도 주요 일정</span>
              </div>
              <div className="schedule-list">
                {schoolEvents.slice(0, 5).map((event) => (
                  <div key={event.id} className="schedule-item">
                    <div className="event-date">
                      <span className="date">{new Date(event.date).getDate()}</span>
                      <span className="month">{new Date(event.date).toLocaleDateString('ko-KR', { month: 'short' })}</span>
                    </div>
                    <div className="event-info">
                      <div className="event-title">{event.title}</div>
                      <div className="event-meta">
                        <span 
                          className="event-type" 
                          style={{ backgroundColor: getEventTypeColor(event.type) }}
                        >
                          {event.type === 'academic' ? '학사' : 
                           event.type === 'exam' ? '시험' :
                           event.type === 'event' ? '행사' :
                           event.type === 'ceremony' ? '식전' : '휴일'}
                        </span>
                        <span 
                          className="priority-badge"
                          style={{ backgroundColor: getPriorityColor(event.priority) }}
                        >
                          {event.priority === 'high' ? '중요' : 
                           event.priority === 'medium' ? '보통' : '일반'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <button className="view-all-btn">전체 일정 보기</button>
            </div>

            {/* 공지사항 */}
            <div className="dashboard-card announcements-card">
              <div className="card-header">
                <h3>📢 공지사항</h3>
                <span className="card-subtitle">최근 업데이트</span>
              </div>
              <div className="announcements-list">
                {announcements.map((announcement) => (
                  <div key={announcement.id} className="announcement-item">
                    <div className="announcement-content">
                      <div className="announcement-title">{announcement.title}</div>
                      <div className="announcement-meta">
                        <span className="category">{announcement.category}</span>
                        <span className="date">{announcement.date}</span>
                      </div>
                    </div>
                    <div className="announcement-arrow">→</div>
                  </div>
                ))}
              </div>
              <button className="view-all-btn">전체 공지사항 보기</button>
            </div>

            {/* 빠른 액션 */}
            <div className="dashboard-card quick-actions-card">
              <div className="card-header">
                <h3>⚡ 빠른 액션</h3>
                <span className="card-subtitle">자주 사용하는 기능</span>
              </div>
              <div className="quick-actions-grid">
                <button className="action-btn" onClick={handleStudentManagementClick}>
                  <div className="action-icon">👥</div>
                  <span>학생 관리</span>
                </button>
                <button className="action-btn">
                  <div className="action-icon">📊</div>
                  <span>성적 관리</span>
                </button>
                <button className="action-btn">
                  <div className="action-icon">📅</div>
                  <span>일정 관리</span>
                </button>
                <button className="action-btn">
                  <div className="action-icon">📋</div>
                  <span>출석 관리</span>
                </button>
                <button className="action-btn">
                  <div className="action-icon">📚</div>
                  <span>수업 관리</span>
                </button>
                <button className="action-btn">
                  <div className="action-icon">⚙️</div>
                  <span>설정</span>
                </button>
              </div>
            </div>

            {/* 학교 현황 */}
            <div className="dashboard-card school-status-card">
              <div className="card-header">
                <h3>🏫 학교 현황</h3>
                <span className="card-subtitle">실시간 현황</span>
              </div>
              <div className="status-grid">
                <div className="status-item">
                  <div className="status-label">현재 시간</div>
                  <div className="status-value">{new Date().toLocaleTimeString('ko-KR')}</div>
                </div>
                <div className="status-item">
                  <div className="status-label">오늘 날짜</div>
                  <div className="status-value">{new Date().toLocaleDateString('ko-KR')}</div>
                </div>
                <div className="status-item">
                  <div className="status-label">학기 진행률</div>
                  <div className="status-value">15%</div>
                </div>
                <div className="status-item">
                  <div className="status-label">시스템 상태</div>
                  <div className="status-value online">정상</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainPage; 