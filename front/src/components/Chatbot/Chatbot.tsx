import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../contexts/ChatContext';
import { useAuth } from '../../contexts/AuthContext';
import './Chatbot.css';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const { isChatbotOpen: isOpen, messages, closeChat: onClose, addMessage, triggerEventUpdate } = useChat();
  const { user } = useAuth();
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      // 초기 높이 리셋
      textarea.style.height = 'auto';
      
      // 정확한 스크롤 높이 계산
      const scrollHeight = textarea.scrollHeight;
      const lineHeight = parseInt(getComputedStyle(textarea).lineHeight);
      const paddingTop = parseInt(getComputedStyle(textarea).paddingTop);
      const paddingBottom = parseInt(getComputedStyle(textarea).paddingBottom);
      
      // 7줄 높이 계산 (패딩 포함)
      const sevenLineHeight = (lineHeight * 7) + paddingTop + paddingBottom;
      
      if (scrollHeight > sevenLineHeight) {
        // 8줄 이상일 때
        textarea.style.height = `${sevenLineHeight}px`;
        textarea.style.overflowY = 'auto';
        // 스크롤바가 나타날 때 추가 패딩 적용
        textarea.style.paddingRight = '20px';
      } else {
        // 7줄 이하일 때
        textarea.style.height = `${scrollHeight}px`;
        textarea.style.overflowY = 'hidden';
        // 스크롤바가 없을 때 기본 패딩
        textarea.style.paddingRight = '16px';
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputText]);

  // 일정 추가/삭제/수정 관련 키워드 체크
  const checkForEventUpdate = (responseText: string) => {
    const eventKeywords = [
      // 일정 추가 관련
      '일정이 성공적으로 등록되었습니다',
      '일정을 추가했습니다',
      '일정이 추가되었습니다',
      '일정을 생성했습니다',
      '일정이 생성되었습니다',
      '캘린더에 추가했습니다',
      '캘린더에 등록했습니다',
      '일정을 등록했습니다',
      '일정이 등록되었습니다',
      '성공적으로 등록되었습니다',
      '등록되었습니다',
      
      // 일정 삭제 관련
      '일정이 성공적으로 삭제되었습니다',
      '일정을 삭제했습니다',
      '일정이 삭제되었습니다',
      '캘린더에서 삭제했습니다',
      '캘린더에서 제거했습니다',
      '일정을 제거했습니다',
      '일정이 제거되었습니다',
      '성공적으로 삭제되었습니다',
      '삭제되었습니다',
      '제거되었습니다',
      
      // 일정 수정 관련
      '일정이 성공적으로 수정되었습니다',
      '일정을 수정했습니다',
      '일정이 수정되었습니다',
      '일정을 변경했습니다',
      '일정이 변경되었습니다',
      '캘린더에서 수정했습니다',
      '캘린더에서 변경했습니다',
      '성공적으로 수정되었습니다',
      '수정되었습니다',
      '변경되었습니다',
      '업데이트되었습니다'
    ];
    
    return eventKeywords.some(keyword => responseText.includes(keyword));
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    addMessage(userMessage);
    setInputText('');
    setIsTyping(true);

    // 입력창 완전 초기화
    if (textareaRef.current) {
      textareaRef.current.style.height = '44px';
      textareaRef.current.style.overflowY = 'hidden';
      textareaRef.current.style.paddingRight = '16px';
    }

    try {
      console.log('챗봇 API 호출 시작:', inputText);
      
      // 백엔드 API 호출
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputText,
          user_id: user?.id || 1
        })
      });

      if (!response.ok) {
        throw new Error('챗봇 응답 실패');
      }

      const result = await response.json();
      console.log('챗봇 API 응답:', result);

      if (result.success) {
        const botMessage: Message = {
          id: Date.now() + 1,
          text: result.response,
          isUser: false,
          timestamp: new Date()
        };

        addMessage(botMessage);

        // 일정 추가 관련 응답인지 확인하고 캘린더 업데이트
        if (checkForEventUpdate(result.response)) {
          console.log('일정 추가/삭제/수정 감지, 캘린더 업데이트 트리거');
          setTimeout(() => {
            triggerEventUpdate();
          }, 1000); // 1초 후 업데이트 (사용자가 응답을 볼 수 있도록)
        }
      } else {
        throw new Error(result.error || '챗봇 응답 오류');
      }
    } catch (error) {
      console.error('챗봇 API 호출 실패:', error);
      
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date()
      };

      addMessage(errorMessage);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`chatbot-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="chatbot-sidebar-content">
        <div className="chatbot-header">
          <div className="chatbot-title">
            <span className="chatbot-icon">🤖</span>
            <span>AI 어시스턴트</span>
          </div>
          <button 
            className="chatbot-close"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.isUser ? 'user' : 'ai'}`}
            >
              <div className="message-content">
                {message.text}
              </div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message ai">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            rows={1}
            ref={textareaRef}
          />
          <button 
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isTyping}
            className="send-button"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot; 