import React, { useState } from 'react';
import axios from 'axios';
import './LoginPage.css';

const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // 백엔드에서 Google OAuth2 URL 가져오기
      const response = await axios.get('http://localhost:8000/auth/google');
      const { auth_url } = response.data;
      
      // Google 로그인 페이지로 리다이렉트
      window.location.href = auth_url;
    } catch (err: any) {
      console.error('Google login error:', err);
      setError('Google 로그인 처리 중 오류가 발생했습니다.');
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
            <p className="subtitle">Google 계정으로 로그인</p>
          </div>

          <div className="login-form">
            <div className="oauth-section">
              <div className="oauth-description">
                <p>안전하고 빠른 Google 계정 로그인을 사용하세요.</p>
                <ul>
                  <li>✅ 안전한 인증</li>
                  <li>✅ 빠른 로그인</li>
                  <li>✅ 계정 정보 자동 동기화</li>
                </ul>
              </div>

              <button 
                onClick={handleGoogleLogin}
                className={`google-login-button ${isLoading ? 'loading' : ''}`}
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="loading-spinner">
                    <div className="spinner"></div>
                    로그인 중...
                  </div>
                ) : (
                  <>
                    <div className="google-icon">
                      <svg viewBox="0 0 24 24" width="24" height="24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                      </svg>
                    </div>
                    <span>Google로 로그인</span>
                  </>
                )}
              </button>

              {error && <div className="error-message">{error}</div>}

              <div className="login-info">
                <p>Google 계정이 없으신가요?</p>
                <a 
                  href="https://accounts.google.com/signup" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="google-signup-link"
                >
                  Google 계정 만들기
                </a>
              </div>
            </div>
          </div>

          <div className="login-footer">
            <p>© 2024 School Management System</p>
            <p className="security-note">
              🔒 모든 로그인 정보는 Google의 안전한 인증 시스템을 통해 처리됩니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 