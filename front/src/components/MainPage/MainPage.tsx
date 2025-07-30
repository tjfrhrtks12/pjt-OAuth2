import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Chatbot from '../Chatbot';
import MainSidebar from '../MainSidebar';
import NavigationBar from '../NavigationBar';
import SubSidebar from '../SubSidebar/SubSidebar';
import './MainPage.css';

const MainPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMenuItem, setSelectedMenuItem] = useState<string>('');
  const [isSidebarExpanded, setIsSidebarExpanded] = useState<boolean>(false);
  const [showSubSidebar, setShowSubSidebar] = useState<boolean>(false);
  const [isChatbotOpen, setIsChatbotOpen] = useState<boolean>(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const handleSidebarSelect = (item: string) => {
    setSelectedMenuItem(item);
    if (item === 'grade1') setShowSubSidebar(true);
    else setShowSubSidebar(false);
  };

  const handleTAIClick = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  const handleChatbotClose = () => {
    setIsChatbotOpen(false);
  };

  return (
    <div className="main-container">
      <MainSidebar 
        onSelectItem={handleSidebarSelect}
        selectedItem={selectedMenuItem}
        isExpanded={isSidebarExpanded}
        onExpandChange={setIsSidebarExpanded}
      />
      <SubSidebar 
        visible={showSubSidebar}
        onClose={() => setShowSubSidebar(false)}
        isMainSidebarExpanded={isSidebarExpanded}
      />
      <div className="main-content-wrapper">
        <NavigationBar onTAIClick={handleTAIClick} />
        <main className="main-content">
          <div className="welcome-section">
            <h2>환영합니다! 👋</h2>
            <p>교사 관리 시스템에 로그인되었습니다.</p>
          </div>
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <div className="card-icon">👨‍🏫</div>
              <h3>교사 관리</h3>
              <p>교사 정보를 관리합니다</p>
              <button className="card-button">관리하기</button>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">👨‍🎓</div>
              <h3>학생 관리</h3>
              <p>학생 정보를 관리합니다</p>
              <button className="card-button">관리하기</button>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">📊</div>
              <h3>통계</h3>
              <p>시스템 통계를 확인합니다</p>
              <button className="card-button">확인하기</button>
            </div>
            <div className="dashboard-card">
              <div className="card-icon">⚙️</div>
              <h3>설정</h3>
              <p>시스템 설정을 관리합니다</p>
              <button className="card-button">설정하기</button>
            </div>
          </div>
        </main>
      </div>
      <Chatbot isOpen={isChatbotOpen} onClose={handleChatbotClose} />
    </div>
  );
};

export default MainPage; 