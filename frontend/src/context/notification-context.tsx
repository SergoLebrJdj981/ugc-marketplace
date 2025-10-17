'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from 'react';

import { apiRequest } from '@/lib/api';
import { notify } from '@/lib/toast';
import { useAuth } from './auth-context';

export interface NotificationItem {
  id: string;
  user_id: string;
  type: string;
  message: string;
  is_read: boolean;
  created_at?: string | null;
}

interface NotificationContextValue {
  notifications: NotificationItem[];
  unreadCount: number;
  refresh: () => Promise<void>;
  markAsRead: (ids: string[]) => Promise<void>;
  loading: boolean;
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const { accessToken, logout } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);

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
        const response = await apiRequest('/api/notifications/mark-read', {
          method: 'POST',
          token: accessToken,
          data: { notification_ids: ids },
          onUnauthorized: logout,
          showErrorToast: false
        });
        if (response.error) {
          if (!response.error.unauthorized) {
            notify.error(response.message || 'Не удалось обновить уведомления');
          }
          return;
        }
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

  const value = useMemo<NotificationContextValue>(() => {
    const unreadCount = notifications.filter((item) => !item.is_read).length;
    return {
      notifications,
      unreadCount,
      loading,
      refresh: fetchNotifications,
      markAsRead
    };
  }, [fetchNotifications, loading, markAsRead, notifications]);

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}

export function useNotifications(): NotificationContextValue {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
