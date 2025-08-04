import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import axios from 'axios';

interface User {
  id: number;
  login_id: string;
  name: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (loginId: string, loginPw: string) => Promise<boolean>;
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
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // API 기본 설정
  axios.defaults.baseURL = 'http://localhost:8000';

  // 로컬 스토리지에서 사용자 정보 확인
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('AuthContext - 저장된 사용자 정보 파싱 오류:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

  // 로그인 함수
  const login = async (loginId: string, loginPw: string): Promise<boolean> => {
    try {
      console.log('AuthContext - 로그인 시작');
      const response = await axios.post('/api/login', {
        login_id: loginId,
        login_pw: loginPw
      });

      if (response.data.success) {
        const userData = response.data.user;
        setUser(userData);
        setIsAuthenticated(true);
        localStorage.setItem('user', JSON.stringify(userData));
        console.log('AuthContext - 로그인 성공');
        return true;
      }
      return false;
    } catch (error) {
      console.error('AuthContext - 로그인 실패:', error);
      return false;
    }
  };

  // 로그아웃
  const logout = () => {
    console.log('AuthContext - 로그아웃 시작');
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
    console.log('AuthContext - 로그아웃 완료');
  };

  // 인증 상태 확인 (간단한 버전)
  const checkAuth = async () => {
    // 로컬 스토리지에 사용자 정보가 있으면 인증된 것으로 간주
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('AuthContext - 저장된 사용자 정보 파싱 오류:', error);
        localStorage.removeItem('user');
        setUser(null);
        setIsAuthenticated(false);
      }
    }
  };

  const value: AuthContextType = {
    user,
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