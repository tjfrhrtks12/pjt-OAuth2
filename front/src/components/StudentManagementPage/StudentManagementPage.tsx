import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainSidebar from '../MainSidebar';
import NavigationBar from '../NavigationBar';
import SubSidebar from '../SubSidebar/SubSidebar';
import Chatbot from '../Chatbot';
import './StudentManagementPage.css';

const StudentManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMenuItem, setSelectedMenuItem] = useState<string>('grade1');
  const [isSidebarExpanded, setIsSidebarExpanded] = useState<boolean>(false);
  const [showSubSidebar, setShowSubSidebar] = useState<boolean>(true);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [isChatbotOpen, setIsChatbotOpen] = useState<boolean>(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const handleSidebarSelect = (item: string) => {
    setSelectedMenuItem(item);
    if (item === 'grade1') {
      setShowSubSidebar(true);
    } else {
      setShowSubSidebar(false);
      navigate('/main');
    }
  };

  const handleTAIClick = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  const handleChatbotClose = () => {
    setIsChatbotOpen(false);
  };

  const handleStudentSelect = (studentId: string) => {
    setSelectedStudent(studentId);
  };

  return (
    <div className="student-management-container">
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
      <div className="student-management-content-wrapper">
        <NavigationBar onTAIClick={handleTAIClick} />
        
        <main className="student-management-content">
          <div className="page-header">
            <h1>1학년 1반 학생 관리</h1>
            <p>학생 정보를 관리하고 조회할 수 있습니다.</p>
          </div>

          <div className="student-management-layout">
            {/* 왼쪽: 학생 목록 영역 */}
            <div className="student-list-section">
              <div className="section-header">
                <h2>학생 목록</h2>
                <button className="add-student-btn">+ 학생 추가</button>
              </div>
              <div className="student-list-container">
                <div className="search-box">
                  <input 
                    type="text" 
                    placeholder="학생 이름으로 검색..." 
                    className="search-input"
                  />
                </div>
                <div className="student-list">
                  {/* 학생 목록이 들어갈 공간 */}
                  <div className="student-list-placeholder">
                    학생 목록이 여기에 표시됩니다.
                  </div>
                </div>
              </div>
            </div>

            {/* 오른쪽: 학생 인적사항 영역 */}
            <div className="student-detail-section">
              <div className="section-header">
                <h2>학생 인적사항</h2>
              </div>
              <div className="student-detail-container">
                {selectedStudent ? (
                  <div className="student-detail-content">
                    {/* 선택된 학생의 상세 정보가 들어갈 공간 */}
                    <div className="student-detail-placeholder">
                      선택된 학생의 상세 정보가 여기에 표시됩니다.
                    </div>
                  </div>
                ) : (
                  <div className="student-detail-placeholder">
                    왼쪽에서 학생을 선택하면 상세 정보가 표시됩니다.
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
      
      <Chatbot isOpen={isChatbotOpen} onClose={handleChatbotClose} />
    </div>
  );
};

export default StudentManagementPage; 