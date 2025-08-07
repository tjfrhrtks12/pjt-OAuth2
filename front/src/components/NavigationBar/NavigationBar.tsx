import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../../contexts/ChatContext';
import { useAuth } from '../../contexts/AuthContext';
import './NavigationBar.css';

interface User {
  id: number;
  login_id: string;
  name: string;
  is_active: boolean;
}

interface NavigationBarProps {
  onLogout?: () => void;
  onBack?: () => void;
  user?: User | null;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onLogout, onBack, user }) => {
  const [isTAIActive, setIsTAIActive] = useState<boolean>(false);
  const navigate = useNavigate();
  const { toggleChat } = useChat();
  const { user: authUser } = useAuth();

  const handleTAIClick = () => {
    setIsTAIActive(!isTAIActive);
    toggleChat();
  };

  const handleTzoneClick = () => {
    navigate('/main');
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
        {authUser && (
          <span className="user-title">
            {authUser.name}선생님
          </span>
        )}
        <button 
          className={`tai-button ${isTAIActive ? 'active' : ''}`}
          onClick={handleTAIClick}
        >
          <span className="tai-icon">🤖</span>
          <span className="tai-text">TAI</span>
        </button>
      </div>
    </nav>
  );
};

export default NavigationBar; 