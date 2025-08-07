import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ChatProvider, useChat } from './contexts/ChatContext';
import LoginPage from './components/LoginPage';
import MainPage from './components/MainPage';
import SchedulePage from './components/SchedulePage';
import Chatbot from './components/Chatbot';

import './App.css';

// 보호된 라우트 컴포넌트
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// 메인 앱 컴포넌트
const AppRoutes: React.FC = () => {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const { isChatbotOpen } = useChat();

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route 
          path="/main" 
          element={
            <ProtectedRoute>
              <MainPage 
                isSidebarExpanded={isSidebarExpanded}
                onSidebarExpandChange={setIsSidebarExpanded}
              />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/schedule" 
          element={
            <ProtectedRoute>
              <SchedulePage />
            </ProtectedRoute>
          } 
        />
      </Routes>
      <Chatbot />
    </>
  );
};

function App() {
  return (
    <ChatProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <AppRoutes />
          </div>
        </Router>
      </AuthProvider>
    </ChatProvider>
  );
}

export default App;
