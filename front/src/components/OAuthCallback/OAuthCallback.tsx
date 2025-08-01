import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './OAuthCallback.css';

const OAuthCallback: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const { token, isAuthenticated, checkAuth } = useAuth();

  useEffect(() => {
    console.log('OAuthCallback - 컴포넌트 마운트');
    
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const errorMessage = urlParams.get('message');
    const storedToken = localStorage.getItem('token');

    console.log('OAuthCallback - URL 파라미터:', {
      hasToken: !!token,
      hasStoredToken: !!storedToken,
      isAuthenticated,
      error,
      errorMessage,
      tokenLength: token ? token.length : 0,
      storedTokenLength: storedToken ? storedToken.length : 0
    });

    if (error || errorMessage) {
      console.log('OAuthCallback - OAuth2 오류 발생:', errorMessage);
      setStatus('error');
      setMessage(errorMessage || '인증에 실패했습니다.');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      return;
    }

    // 단순히 메인 페이지로 리다이렉트 (토큰 검증 제거)
    console.log('OAuthCallback - 메인 페이지로 리다이렉트');
    setStatus('success');
    setMessage('로그인에 성공했습니다! 메인 페이지로 이동합니다.');
    
    setTimeout(() => {
      navigate('/main');
    }, 2000);
  }, [token, isAuthenticated, checkAuth, navigate]);

  return (
    <div className="oauth-callback">
      <div className="oauth-callback-container">
        {status === 'loading' && (
          <div className="loading">
            <div className="spinner"></div>
            <h2>인증 처리 중...</h2>
            <p>잠시만 기다려주세요.</p>
          </div>
        )}
        
        {status === 'success' && (
          <div className="success">
            <div className="success-icon">✅</div>
            <h2>로그인 성공!</h2>
            <p>{message}</p>
          </div>
        )}
        
        {status === 'error' && (
          <div className="error">
            <div className="error-icon">❌</div>
            <h2>로그인 실패</h2>
            <p>{message}</p>
            <button onClick={() => navigate('/login')} className="retry-button">
              다시 시도
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback; 