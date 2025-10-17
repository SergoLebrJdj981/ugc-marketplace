'use client';

import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

interface ChatMessage {
  id: string;
  userId: string;
  message: string;
  createdAt: string;
}

interface ChatContextValue {
  messages: ChatMessage[];
  sendMessage: (content: string) => void;
  clear: () => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const value = useMemo<ChatContextValue>(() => ({
    messages,
    sendMessage: (content: string) => {
      const message: ChatMessage = {
        id: crypto.randomUUID(),
        userId: 'local',
        message: content,
        createdAt: new Date().toISOString()
      };
      setMessages((prev) => [...prev, message]);
    },
    clear: () => setMessages([])
  }), [messages]);

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
