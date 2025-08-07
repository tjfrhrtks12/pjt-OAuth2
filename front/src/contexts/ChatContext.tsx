import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatContextType {
  isChatbotOpen: boolean;
  messages: Message[];
  toggleChat: () => void;
  closeChat: () => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  resetChat: () => void;
  setEventUpdateCallback: (callback: () => Promise<void>) => void;
  triggerEventUpdate: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "안녕하세요! AI 어시스턴트입니다. 무엇을 도와드릴까요? 🤖",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [eventUpdateCallback, setEventUpdateCallback] = useState<(() => Promise<void>) | null>(null);

  const toggleChat = () => {
    setIsChatbotOpen(!isChatbotOpen);
  };

  const closeChat = () => {
    setIsChatbotOpen(false);
  };

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const clearMessages = () => {
    setMessages([
      {
        id: 1,
        text: "안녕하세요! AI 어시스턴트입니다. 무엇을 도와드릴까요? 🤖",
        isUser: false,
        timestamp: new Date()
      }
    ]);
  };

  const resetChat = () => {
    clearMessages();
    setIsChatbotOpen(false);
  };

  const setEventUpdateCallbackHandler = (callback: () => Promise<void>) => {
    setEventUpdateCallback(() => callback);
  };

  const triggerEventUpdate = async () => {
    if (eventUpdateCallback) {
      try {
        await eventUpdateCallback();
        console.log('캘린더 이벤트 업데이트 완료');
      } catch (error) {
        console.error('캘린더 이벤트 업데이트 실패:', error);
      }
    }
  };

  const value: ChatContextType = {
    isChatbotOpen,
    messages,
    toggleChat,
    closeChat,
    addMessage,
    clearMessages,
    resetChat,
    setEventUpdateCallback: setEventUpdateCallbackHandler,
    triggerEventUpdate,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}; 