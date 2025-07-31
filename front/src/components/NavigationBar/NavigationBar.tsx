import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './NavigationBar.css';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
}

interface NavigationBarProps {
  onTAIClick: () => void;
  onLogout: () => void;
  user: User | null;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onTAIClick, onLogout, user }) => {
  const [isTAIActive, setIsTAIActive] = useState<boolean>(false);
  const [showUserMenu, setShowUserMenu] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleTAIClick = () => {
    setIsTAIActive(!isTAIActive);
    onTAIClick();
  };

  const handleTzoneClick = () => {
    navigate('/main');
  };

  const handleUserMenuToggle = () => {
    setShowUserMenu(!showUserMenu);
  };

  const handleLogoutClick = () => {
    setShowUserMenu(false);
    onLogout();
  };

  return (
    <nav className="navigation-bar">
      <div className="nav-left">
        <div className="brand">
          <span 
            className="brand-text" 
            onClick={handleTzoneClick}
          >
            Tzone
          </span>
        </div>
      </div>
      
      <div className="nav-right">
        <button 
          className={`tai-button ${isTAIActive ? 'active' : ''}`}
          onClick={handleTAIClick}
        >
          <span className="tai-icon">🤖</span>
          <span className="tai-text">TAI</span>
        </button>

        <div className="user-menu-container">
          <button 
            className="user-menu-button"
            onClick={handleUserMenuToggle}
          >
            {user?.picture ? (
              <img 
                src={user.picture} 
                alt={user.name} 
                className="user-avatar"
              />
            ) : (
              <div className="user-avatar-placeholder">
                {user?.name?.charAt(0) || 'U'}
              </div>
            )}
            <span className="user-name">{user?.name || '사용자'}</span>
            <span className="dropdown-arrow">▼</span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown">
              <div className="user-info">
                <div className="user-email">{user?.email}</div>
              </div>
              <div className="dropdown-divider"></div>
              <button 
                className="dropdown-item logout-button"
                onClick={handleLogoutClick}
              >
                <span className="logout-icon">🚪</span>
                로그아웃
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default NavigationBar; 