import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [teacherId, setTeacherId] = useState('');
  const [teacherPw, setTeacherPw] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      console.log('로그인 시도:', { teacher_id: teacherId, teacher_pw: teacherPw });
      
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          teacher_id: teacherId,
          teacher_pw: teacherPw
        })
      });

      const data = await response.json();
      console.log('백엔드 응답:', data);

      if (data.success) {
        setSuccess('로그인 성공! 메인 페이지로 이동합니다...');
        localStorage.setItem('token', data.token);
        localStorage.setItem('teacher_name', data.teacher_name || '교사');
        
        // 1초 후 메인 페이지로 이동
        setTimeout(() => {
          navigate('/main');
        }, 1000);
      } else {
        setError(data.message || '로그인에 실패했습니다.');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError('로그인 처리 중 오류가 발생했습니다. 서버 연결을 확인해주세요.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="login-card">
          <div className="login-header">
            <div className="logo">
              <div className="logo-icon">🎓</div>
              <h1>School Management</h1>
            </div>
            <p className="subtitle">교사 로그인</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <div className="input-group">
              <div className="input-wrapper">
                <span className="input-icon">👤</span>
                <input
                  type="text"
                  placeholder="교사 아이디"
                  value={teacherId}
                  onChange={(e) => setTeacherId(e.target.value)}
                  required
                  className="login-input"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type="password"
                  placeholder="비밀번호"
                  value={teacherPw}
                  onChange={(e) => setTeacherPw(e.target.value)}
                  required
                  className="login-input"
                  disabled={isLoading}
                />
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button 
              type="submit" 
              className={`login-button ${isLoading ? 'loading' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  로그인 중...
                </div>
              ) : (
                '로그인'
              )}
            </button>
          </form>

          <div className="login-footer">
            <p>© 2024 School Management System</p>
            <div className="test-credentials">
              <p>테스트 계정:</p>
              <p>아이디: test123 / 비밀번호: 1234</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 