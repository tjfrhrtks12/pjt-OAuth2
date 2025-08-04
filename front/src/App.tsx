import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import MainPage from './components/MainPage';
import StudentManagementPage from './components/StudentManagementPage';

import './App.css';

// 보호된 라우트 컴포넌트
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// 메인 앱 컴포넌트
const AppRoutes: React.FC = () => {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);

  return (
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
        path="/student-management" 
        element={
          <ProtectedRoute>
            <StudentManagementPage />
          </ProtectedRoute>
        } 
      />

    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
