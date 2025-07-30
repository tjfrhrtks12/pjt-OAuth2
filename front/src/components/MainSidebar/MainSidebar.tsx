import React, { useState } from 'react';
import './MainSidebar.css';

interface MainSidebarProps {
  onSelectItem: (item: string) => void;
  selectedItem: string;
  isExpanded: boolean;
  onExpandChange: (expanded: boolean) => void;
}

const MainSidebar: React.FC<MainSidebarProps> = ({ onSelectItem, selectedItem, isExpanded, onExpandChange }) => {
  const menuItems = [
    { id: 'grade1', label: '1학년', icon: '1' },
    { id: 'grade2', label: '2학년', icon: '2' },
    { id: 'grade3', label: '3학년', icon: '3' },
    { id: 'schedule', label: '일정표', icon: '📅' }
  ];

  const handleItemClick = (item: string) => {
    onSelectItem(item);
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