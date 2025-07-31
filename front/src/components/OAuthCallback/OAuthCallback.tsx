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

    console.log('OAuthCallback - URL 파라미터:', {
      hasToken: !!token,
      isAuthenticated,
      error,
      errorMessage,
      tokenLength: token ? token.length : 0
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

    // AuthContext에서 토큰이 설정되었는지 확인
    if (token && isAuthenticated) {
      console.log('OAuthCallback - AuthContext에서 토큰과 인증 상태 확인됨');
      setStatus('success');
      setMessage('로그인에 성공했습니다! 메인 페이지로 이동합니다.');
      
      setTimeout(() => {
        console.log('OAuthCallback - 메인 페이지로 리다이렉트');
        navigate('/main');
      }, 2000);
    } else if (token && !isAuthenticated) {
      console.log('OAuthCallback - 토큰은 있지만 인증 상태 확인 필요');
      // 인증 상태 확인
      checkAuth().then(() => {
        console.log('OAuthCallback - 인증 상태 확인 완료');
        setStatus('success');
        setMessage('로그인에 성공했습니다! 메인 페이지로 이동합니다.');
        setTimeout(() => {
          console.log('OAuthCallback - 메인 페이지로 리다이렉트');
          navigate('/main');
        }, 2000);
      }).catch((err) => {
        console.error('OAuthCallback - 인증 확인 실패:', err);
        setStatus('error');
        setMessage('인증 확인에 실패했습니다.');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      });
    } else {
      console.log('OAuthCallback - 토큰이 없음, 잠시 대기');
      // 토큰이 아직 설정되지 않았을 수 있으므로 잠시 대기
      const timer = setTimeout(() => {
        console.log('OAuthCallback - 대기 후 토큰 상태 재확인:', { hasToken: !!token, isAuthenticated });
        if (!token) {
          console.log('OAuthCallback - 토큰을 받지 못함');
          setStatus('error');
          setMessage('토큰을 받지 못했습니다.');
          setTimeout(() => {
            navigate('/login');
          }, 3000);
        }
      }, 3000); // 3초로 증가

      return () => clearTimeout(timer);
    }
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