import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // API 기본 설정
  axios.defaults.baseURL = 'http://localhost:8000';

  // URL 파라미터에서 토큰 확인 (OAuth2 콜백 처리) - 가장 먼저 실행
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const callbackToken = urlParams.get('token');
    const userId = urlParams.get('user_id');

    console.log('AuthContext - URL 파라미터 확인:', {
      hasToken: !!callbackToken,
      hasUserId: !!userId,
      pathname: window.location.pathname
    });

    if (callbackToken && userId && window.location.pathname === '/auth/callback') {
      console.log('AuthContext - OAuth2 콜백에서 토큰 받음');
      setToken(callbackToken);
      localStorage.setItem('token', callbackToken);
      localStorage.setItem('user_id', userId);
      
      // URL에서 파라미터 제거
      window.history.replaceState({}, document.title, window.location.pathname);
      console.log('AuthContext - URL 파라미터 제거 완료');
    }
  }, []); // 의존성 배열을 비워서 한 번만 실행

  // 토큰이 변경될 때마다 axios 헤더 설정
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
      console.log('AuthContext - 토큰 설정 완료:', token.substring(0, 20) + '...');
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
      console.log('AuthContext - 토큰 제거 완료');
    }
  }, [token]);

  // 인증 상태 확인
  const checkAuth = useCallback(async () => {
    if (!token) {
      console.log('AuthContext - 토큰이 없어서 인증 확인 생략');
      setIsAuthenticated(false);
      setUser(null);
      return;
    }

    try {
      console.log('AuthContext - 인증 상태 확인 시작');
      const response = await axios.get('/api/auth/me');
      console.log('AuthContext - 사용자 정보 받음:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      // 성공했을 때는 토큰을 유지!
      console.log('AuthContext - 인증 확인 성공, 토큰 유지');
    } catch (error) {
      console.error('AuthContext - 인증 확인 실패:', error);
      // 토큰이 유효하지 않을 때만 제거 (401, 403 오류)
      if (axios.isAxiosError(error) && (error.response?.status === 401 || error.response?.status === 403)) {
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
        console.log('AuthContext - 인증 실패로 토큰 제거');
      } else {
        // 네트워크 오류 등은 토큰 유지
        console.log('AuthContext - 네트워크 오류, 토큰 유지');
      }
    }
  }, [token]);

  // 컴포넌트 마운트 시 인증 상태 확인 (토큰 설정 후)
  useEffect(() => {
    if (token) {
      checkAuth();
    }
  }, [token, checkAuth]);

  // Google OAuth2 로그인
  const login = () => {
    console.log('AuthContext - Google OAuth2 로그인 시작');
    window.location.href = 'http://localhost:8000/auth/google';
  };

  // 로그아웃
  const logout = async () => {
    try {
      console.log('AuthContext - 로그아웃 시작');
      await axios.post('/api/auth/logout');
    } catch (error) {
      console.error('AuthContext - 로그아웃 오류:', error);
    } finally {
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      console.log('AuthContext - 로그아웃 완료');
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 