'use client';

import { useMemo } from 'react';

import type { NotificationItem as Notification } from '@/context/notification-context';
import { Button } from '@/components/ui/Button';

interface Props {
  notification: Notification;
  onMarkRead: (id: string) => void;
}

function formatTimestamp(timestamp?: string | null) {
  if (!timestamp) return '';
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('ru-RU');
  } catch {
    return timestamp;
  }
}

export function NotificationItem({ notification, onMarkRead }: Props) {
  const tone = useMemo(() => {
    switch (notification.type) {
      case 'payment_success':
        return 'text-emerald-600';
      case 'admin_notice':
        return 'text-indigo-600';
      case 'chat_message':
        return 'text-sky-600';
      default:
        return 'text-slate-600';
    }
  }, [notification.type]);

  return (
    <div className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <span className={`mt-0.5 text-lg ${tone}`} aria-hidden>
        {notification.type === 'chat_message'
          ? '💬'
          : notification.type === 'payment_success'
            ? '✨'
            : notification.type === 'admin_notice'
              ? '📢'
              : '🔔'}
      </span>
      <div className="flex-1 space-y-1 text-sm">
        <div className="flex items-center justify-between gap-2">
          <p className="font-medium text-slate-900">{notification.title}</p>
          <time className="text-xs text-slate-500">{formatTimestamp(notification.created_at)}</time>
        </div>
        <p className="text-slate-600">{notification.content}</p>
        {!notification.is_read ? (
          <Button
            className="mt-1 h-7 w-fit px-2 text-xs"
            variant="ghost"
            onClick={() => onMarkRead(notification.id)}
          >
            Отметить прочитанным
          </Button>
        ) : null}
      </div>
    </div>
  );
}
