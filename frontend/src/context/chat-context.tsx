'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { useAuth } from './auth-context';
import { notify } from '@/lib/toast';
import {
  buildWsUrl,
  deriveChatId,
  fetchChatHistory,
  mergeMessages,
  postChatMessage,
  mapChatMessage,
} from '@/lib/chat';
import type { ChatMessage } from '@/types/chat';

interface ChatContextValue {
  messages: ChatMessage[];
  isLoading: boolean;
  activeChatId: string | null;
  receiverId: string | null;
  receiverName: string | null;
  selectChat: (receiverId: string, receiverName?: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  clear: () => void;
}

const ChatContext = createContext<ChatContextValue | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const { user, accessToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [receiverId, setReceiverId] = useState<string | null>(null);
  const [receiverName, setReceiverName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      try {
        socketRef.current.close();
      } catch (error) {
        console.warn('Failed to close chat socket', error);
      }
      socketRef.current = null;
    }
  }, []);

  const handleIncomingMessage = useCallback(
    (payload: unknown) => {
      if (!payload || typeof payload !== 'object') return;
      const data = (payload as { event?: string; data?: unknown }).data;
      const event = (payload as { event?: string }).event;
      if (event !== 'message' || !data || typeof data !== 'object') return;
      try {
        const message = mapChatMessage(data as { [key: string]: unknown } as never);
        setMessages((prev) => mergeMessages(prev, message));
        if (user?.id && message.senderId !== user.id) {
          notify.info(`Новое сообщение${receiverName ? ` от ${receiverName}` : ''}`, message.content);
        }
      } catch (error) {
        console.warn('Failed to process incoming chat message', error);
      }
    },
    [receiverName, user?.id],
  );

  const connectSocket = useCallback(
    (chatId: string) => {
      if (!accessToken) return;
      disconnect();
      try {
        const url = buildWsUrl(chatId, accessToken);
        const socket = new WebSocket(url);
        socketRef.current = socket;
        socket.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data as string);
            handleIncomingMessage(parsed);
          } catch (error) {
            console.warn('Failed to parse chat message event', error);
          }
        };
        socket.onerror = () => {
          notify.error('Соединение чата временно недоступно');
        };
        socket.onclose = () => {
          socketRef.current = null;
        };
      } catch (error) {
        console.warn('Unable to establish chat WebSocket connection', error);
        notify.error('Не удалось подключиться к чату');
      }
    },
    [accessToken, disconnect, handleIncomingMessage],
  );

  useEffect(() => disconnect, [disconnect]);

  useEffect(() => {
    if (!accessToken || !activeChatId) {
      disconnect();
      setMessages([]);
      return;
    }

    let cancelled = false;
    setIsLoading(true);

    fetchChatHistory(activeChatId, accessToken)
      .then((history) => {
        if (cancelled) return;
        setMessages(history);
      })
      .catch((error) => {
        if (!cancelled) {
          console.warn('Failed to fetch chat history', error);
          notify.error(error instanceof Error ? error.message : 'Не удалось загрузить историю чата');
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    connectSocket(activeChatId);

    return () => {
      cancelled = true;
      disconnect();
    };
  }, [accessToken, activeChatId, connectSocket, disconnect]);

  useEffect(() => {
    if (!accessToken || !user?.id) {
      setMessages([]);
      setActiveChatId(null);
      setReceiverId(null);
      setReceiverName(null);
      disconnect();
    }
  }, [accessToken, disconnect, user?.id]);

  const selectChat = useCallback(
    async (targetId: string, targetName?: string) => {
      if (!user?.id) {
        notify.error('Необходимо войти в систему для начала чата');
        return;
      }
      if (!targetId) {
        notify.error('Укажите собеседника');
        return;
      }
      try {
        setMessages([]);
        const chatId = await deriveChatId(user.id, targetId);
        setReceiverId(targetId);
        setReceiverName(targetName ?? null);
        setActiveChatId(chatId);
      } catch (error) {
        console.warn('Failed to derive chat id', error);
        notify.error('Не удалось инициализировать чат');
        throw error;
      }
    },
    [user?.id],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;
      if (!accessToken || !activeChatId || !receiverId || !user?.id) {
        notify.error('Выберите активный чат перед отправкой сообщения');
        return;
      }
      try {
        const message = await postChatMessage({
          chatId: activeChatId,
          receiverId,
          senderId: user.id,
          content,
          token: accessToken,
        });
        setMessages((prev) => mergeMessages(prev, message));
      } catch (error) {
        console.warn('Failed to send chat message', error);
        throw (error instanceof Error ? error : new Error('Не удалось отправить сообщение'));
      }
    },
    [accessToken, activeChatId, receiverId, user?.id],
  );

  const clear = useCallback(() => {
    setMessages([]);
    setActiveChatId(null);
    setReceiverId(null);
    setReceiverName(null);
    disconnect();
  }, [disconnect]);

  const value = useMemo<ChatContextValue>(
    () => ({
      messages,
      isLoading,
      activeChatId,
      receiverId,
      receiverName,
      selectChat,
      sendMessage,
      clear,
    }),
    [messages, isLoading, activeChatId, receiverId, receiverName, selectChat, sendMessage, clear],
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
