'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode
} from 'react';

import { apiRequest } from '@/lib/api';
import { notify } from '@/lib/toast';
import { buildWsUrl } from '@/lib/ws';
import { useAuth } from './auth-context';

export interface NotificationItem {
  id: string;
  user_id: string;
  type: string;
  title: string;
  content: string;
  related_id?: string | null;
  is_read: boolean;
  created_at?: string | null;
}

interface NotificationContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  refresh: () => Promise<void>;
  markAsRead: (ids: string[]) => Promise<void>;
  pushNotification: (notification: NotificationItem, options?: { silent?: boolean }) => void;
  loading: boolean;
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { accessToken, logout, user } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const previousUserIdRef = useRef<string | null>(null);

  const pushNotification = useCallback(
    (notification: NotificationItem, options?: { silent?: boolean }) => {
      setNotifications((prev) => {
        const exists = prev.find((item) => item.id === notification.id);
        if (exists) {
          return prev.map((item) => (item.id === notification.id ? notification : item));
        }
        return [notification, ...prev];
      });

      if (options?.silent) return;

      const message = notification.title || 'Новое уведомление';
      switch (notification.type) {
        case 'payment_success':
          notify.success(message);
          break;
        case 'admin_notice':
          notify.info(message);
          break;
        case 'chat_message':
          notify.info(notification.content || 'Новое сообщение');
          break;
        default:
          notify.info(message);
      }
    },
    []
  );

  const fetchNotifications = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const response = await apiRequest<{ total: number; items: NotificationItem[] }>('/api/notifications', {
        method: 'GET',
        token: accessToken,
        onUnauthorized: logout,
        showErrorToast: false
      });
      if (response.error) {
        if (!response.error.unauthorized) {
          notify.error(response.message || 'Не удалось загрузить уведомления');
        }
        return;
      }
      setNotifications(response.data?.items ?? []);
    } finally {
      setLoading(false);
    }
  }, [accessToken, logout]);

  const markAsRead = useCallback(
    async (ids: string[]) => {
      if (!accessToken || ids.length === 0) return;
      try {
        await Promise.all(
          ids.map((id) =>
            apiRequest(`/api/notifications/${id}/read`, {
              method: 'PATCH',
              token: accessToken,
              onUnauthorized: logout,
              showErrorToast: false
            })
          )
        );
        setNotifications((prev) =>
          prev.map((item) => (ids.includes(item.id) ? { ...item, is_read: true } : item))
        );
      } catch (error) {
        notify.error((error as Error).message || 'Не удалось обновить уведомления');
      }
    },
    [accessToken, logout]
  );

  useEffect(() => {
    if (!accessToken) {
      setNotifications([]);
      return;
    }
    fetchNotifications();
  }, [accessToken, fetchNotifications]);

  useEffect(() => {
    if (!accessToken || !user?.id) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      previousUserIdRef.current = null;
      return;
    }

    if (previousUserIdRef.current === user.id && socketRef.current) {
      return;
    }

    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }

    const url = buildWsUrl(`/ws/notifications/${user.id}`, accessToken);
    const socket = new WebSocket(url);
    socketRef.current = socket;
    previousUserIdRef.current = user.id;

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data as string) as { event?: string; data?: NotificationItem };
        if (parsed.event !== 'notification' || !parsed.data) return;
        pushNotification(parsed.data);
      } catch (error) {
        console.warn('Failed to parse notification event', error);
      }
    };

    socket.onerror = () => {
      notify.error('Соединение уведомлений временно недоступно');
    };

    socket.onclose = () => {
      socketRef.current = null;
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, [accessToken, pushNotification, user?.id]);

  const value = useMemo<NotificationContextValue>(() => {
    const unreadCount = notifications.filter((item) => !item.is_read).length;
    return {
      notifications,
      unreadCount,
      loading,
      refresh: fetchNotifications,
      markAsRead,
      pushNotification
    };
  }, [fetchNotifications, loading, markAsRead, notifications, pushNotification]);

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotifications(): NotificationContextValue {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
