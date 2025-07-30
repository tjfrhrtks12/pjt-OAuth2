import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './NavigationBar.css';

interface NavigationBarProps {
  onTAIClick: () => void;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ onTAIClick }) => {
  const [isTAIActive, setIsTAIActive] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleTAIClick = () => {
    setIsTAIActive(!isTAIActive);
    onTAIClick();
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