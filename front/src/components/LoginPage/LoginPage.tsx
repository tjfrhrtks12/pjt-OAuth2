import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [loginId, setLoginId] = useState('');
  const [loginPw, setLoginPw] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const success = await login(loginId, loginPw);
      if (success) {
        // 로그인 성공 시 메인 페이지로 이동
        navigate('/main');
      } else {
        setError('로그인에 실패했습니다. ID와 비밀번호를 확인해주세요.');
        setIsLoading(false);
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError('로그인에 실패했습니다. 다시 시도해주세요.');
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

          <div className="login-form">
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <input
                  type="text"
                  id="loginId"
                  value={loginId}
                  onChange={(e) => setLoginId(e.target.value)}
                  placeholder="로그인 ID를 입력하세요"
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="form-group">
                <input
                  type="password"
                  id="loginPw"
                  value={loginPw}
                  onChange={(e) => setLoginPw(e.target.value)}
                  placeholder="비밀번호를 입력하세요"
                  required
                  disabled={isLoading}
                />
              </div>

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

              {error && <div className="error-message">{error}</div>}
            </form>

          </div>

          <div className="login-footer">
            <p>© 2024 School Management System</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 