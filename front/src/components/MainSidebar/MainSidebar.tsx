import React, { useState } from 'react';
import './MainSidebar.css';

interface MainSidebarProps {
  isExpanded: boolean;
  onExpandChange: (expanded: boolean) => void;
  onItemClick: (item: string) => void;
}

const MainSidebar: React.FC<MainSidebarProps> = ({ isExpanded, onExpandChange, onItemClick }) => {
  const [selectedItem, setSelectedItem] = useState('');
  
  const menuItems = [
    { id: '1학년', label: '1학년', icon: '1' },
    { id: '2학년', label: '2학년', icon: '2' },
    { id: '3학년', label: '3학년', icon: '3' },
    { id: '일정표', label: '일정표', icon: '📅' }
  ];

  const handleItemClick = (item: string) => {
    setSelectedItem(item);
    onItemClick(item);
    // 클릭 시 사이드바 축소
    onExpandChange(false);
  };

  return (
    <div 
      className={`main-sidebar${isExpanded ? ' expanded' : ''}`}
      onMouseEnter={() => onExpandChange(true)}
      onMouseLeave={() => onExpandChange(false)}
    >
      <div className="sidebar-header">
        <h3>{isExpanded ? '메뉴' : '≡'}</h3>
      </div>
      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          {menuItems.map((item) => (
            <li 
              key={item.id}
              className={`sidebar-item ${selectedItem === item.id ? 'active' : ''}`}
              onClick={() => handleItemClick(item.id)}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className={`sidebar-label ${isExpanded ? 'visible' : ''}`}>
                {item.label}
              </span>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default MainSidebar; 