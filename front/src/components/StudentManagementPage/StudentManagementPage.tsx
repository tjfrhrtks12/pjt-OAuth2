import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import MainSidebar from '../MainSidebar';
import NavigationBar from '../NavigationBar';
import SubSidebar from '../SubSidebar';
import Chatbot from '../Chatbot';
import './StudentManagementPage.css';

interface Student {
  id: string;
  name: string;
  studentNumber: string;
  grade: string;
  className: string;
  phone: string;
  email: string;
  address: string;
  parentName: string;
  parentPhone: string;
  status: 'active' | 'inactive';
}

const StudentManagementPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isSidebarExpanded, setIsSidebarExpanded] = useState<boolean>(false);
  const [isSubSidebarVisible, setIsSubSidebarVisible] = useState<boolean>(true);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [isChatbotOpen, setIsChatbotOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');

  // 샘플 학생 데이터
  const sampleStudents: Student[] = [
    {
      id: '1',
      name: '김철수',
      studentNumber: '2024001',
      grade: '1',
      className: '1',
      phone: '010-1234-5678',
      email: 'kim@school.com',
      address: '서울시 강남구',
      parentName: '김부모',
      parentPhone: '010-9876-5432',
      status: 'active'
    },
    {
      id: '2',
      name: '이영희',
      studentNumber: '2024002',
      grade: '1',
      className: '1',
      phone: '010-2345-6789',
      email: 'lee@school.com',
      address: '서울시 서초구',
      parentName: '이부모',
      parentPhone: '010-8765-4321',
      status: 'active'
    },
    {
      id: '3',
      name: '박민수',
      studentNumber: '2024003',
      grade: '1',
      className: '1',
      phone: '010-3456-7890',
      email: 'park@school.com',
      address: '서울시 송파구',
      parentName: '박부모',
      parentPhone: '010-7654-3210',
      status: 'active'
    }
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSidebarSelect = (item: string) => {
    if (item === '1학년') {
      setIsSubSidebarVisible(true);
    } else {
      setIsSubSidebarVisible(false);
      navigate('/main');
    }
  };

  const handleTAIClick = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  const handleChatbotClose = () => {
    setIsChatbotOpen(false);
  };

  const handleSubSidebarClose = () => {
    setIsSubSidebarVisible(false);
  };

  const handleStudentSelect = (student: Student) => {
    setSelectedStudent(student);
  };

  const filteredStudents = sampleStudents.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.studentNumber.includes(searchTerm)
  );

  return (
    <div className="student-management-container">
      <MainSidebar 
        isExpanded={isSidebarExpanded}
        onExpandChange={setIsSidebarExpanded}
        onItemClick={handleSidebarSelect}
      />
      <SubSidebar 
        visible={isSubSidebarVisible}
        onClose={handleSubSidebarClose}
        isMainSidebarExpanded={isSidebarExpanded}
      />
      <div className="student-management-content-wrapper">
        <NavigationBar onTAIClick={handleTAIClick} onLogout={handleLogout} user={user} />
        
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
                    placeholder="학생 이름 또는 학번으로 검색..." 
                    className="search-input"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="student-list">
                  {filteredStudents.length > 0 ? (
                    filteredStudents.map((student) => (
                      <div 
                        key={student.id}
                        className={`student-item ${selectedStudent?.id === student.id ? 'selected' : ''}`}
                        onClick={() => handleStudentSelect(student)}
                      >
                        <div className="student-avatar">
                          {student.name.charAt(0)}
                        </div>
                        <div className="student-info">
                          <h4>{student.name}</h4>
                          <p>{student.studentNumber}</p>
                        </div>
                        <div className="student-status">
                          <span className={`status-badge ${student.status}`}>
                            {student.status === 'active' ? '재학' : '휴학'}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-results">
                      검색 결과가 없습니다.
                    </div>
                  )}
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
                    <div className="student-profile">
                      <div className="profile-avatar">
                        {selectedStudent.name.charAt(0)}
                      </div>
                      <div className="profile-info">
                        <h3>{selectedStudent.name}</h3>
                        <p className="student-number">{selectedStudent.studentNumber}</p>
                        <span className={`status-badge ${selectedStudent.status}`}>
                          {selectedStudent.status === 'active' ? '재학' : '휴학'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="detail-sections">
                      <div className="detail-section">
                        <h4>기본 정보</h4>
                        <div className="info-grid">
                          <div className="info-item">
                            <label>학년/반</label>
                            <span>{selectedStudent.grade}학년 {selectedStudent.className}반</span>
                          </div>
                          <div className="info-item">
                            <label>연락처</label>
                            <span>{selectedStudent.phone}</span>
                          </div>
                          <div className="info-item">
                            <label>이메일</label>
                            <span>{selectedStudent.email}</span>
                          </div>
                          <div className="info-item">
                            <label>주소</label>
                            <span>{selectedStudent.address}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="detail-section">
                        <h4>보호자 정보</h4>
                        <div className="info-grid">
                          <div className="info-item">
                            <label>보호자명</label>
                            <span>{selectedStudent.parentName}</span>
                          </div>
                          <div className="info-item">
                            <label>보호자 연락처</label>
                            <span>{selectedStudent.parentPhone}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="action-buttons">
                      <button className="edit-btn">수정</button>
                      <button className="delete-btn">삭제</button>
                    </div>
                  </div>
                ) : (
                  <div className="student-detail-placeholder">
                    <div className="placeholder-icon">👨‍🎓</div>
                    <h3>학생을 선택하세요</h3>
                    <p>왼쪽에서 학생을 선택하면 상세 정보가 표시됩니다.</p>
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