import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SubSidebar.css';

interface SubSidebarProps {
  visible: boolean;
  onClose: () => void;
  isMainSidebarExpanded: boolean;
}

const menuItems = [
  { id: '1-1', label: '1-1', hasSubMenu: true },
  { id: '1-2', label: '1-2' },
  { id: '1-3', label: '1-3' },
  { id: 'schedule', label: '일정표', icon: '📅' }
];

const subMenuItems = [
  { id: 'student-management', label: '학생관리', icon: '👨‍🎓' },
  { id: 'timetable', label: '시간표', icon: '📅' }
];

const SubSidebar: React.FC<SubSidebarProps> = ({ visible, onClose, isMainSidebarExpanded }) => {
  const [expandedItem, setExpandedItem] = useState<string>('');
  const navigate = useNavigate();

  if (!visible) return null;

  const handleItemClick = (itemId: string) => {
    if (itemId === '1-1') {
      setExpandedItem(expandedItem === '1-1' ? '' : '1-1');
    }
  };

  const handleSubItemClick = (subItemId: string) => {
    if (subItemId === 'student-management') {
      navigate('/student-management');
    }
  };

  return (
    <div className={`sub-sidebar${isMainSidebarExpanded ? ' behind' : ''}`}> 
      <div className="sub-sidebar-header">
        <span>1학년 반</span>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      <ul className="sub-sidebar-menu">
        {menuItems.map(item => (
          <li key={item.id}>
            <div 
              className={`sub-sidebar-item ${expandedItem === item.id ? 'expanded' : ''}`}
              onClick={() => handleItemClick(item.id)}
            >
              <span className="sub-sidebar-label">
                {item.icon ? item.icon : ''} {item.label}
              </span>
              {item.hasSubMenu && (
                <span className={`expand-arrow ${expandedItem === item.id ? 'expanded' : ''}`}>
                  ▼
                </span>
              )}
            </div>
            {item.hasSubMenu && expandedItem === item.id && (
              <ul className="sub-menu">
                {subMenuItems.map(subItem => (
                  <li 
                    key={subItem.id} 
                    className="sub-menu-item"
                    onClick={() => handleSubItemClick(subItem.id)}
                  >
                    <span className="sub-menu-label">
                      {subItem.icon} {subItem.label}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SubSidebar; 