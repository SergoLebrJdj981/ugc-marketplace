'use client';

import { useEffect, useRef, useState } from 'react';

import { useNotifications } from '@/context';
import { NotificationItem } from '@/components/notifications/NotificationItem';

export function NotificationCenter() {
  const { notifications, unreadCount, markAsRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (event: MouseEvent) => {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  const handleToggle = () => setOpen((state) => !state);

  const handleMarkRead = async (id: string) => {
    await markAsRead([id]);
  };

  const hasNotifications = notifications.length > 0;

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={handleToggle}
        className="relative flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-xl shadow-sm transition hover:bg-slate-50"
        aria-label="Уведомления"
      >
        <span aria-hidden>🔔</span>
        {unreadCount > 0 ? (
          <span className="absolute -top-1 -right-1 inline-flex min-h-[1.25rem] min-w-[1.25rem] items-center justify-center rounded-full bg-rose-500 px-1 text-xs font-semibold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div className="absolute right-0 z-20 mt-3 w-80 max-w-[90vw] rounded-xl border border-slate-200 bg-white p-4 shadow-lg">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-900">Уведомления</p>
            {hasNotifications ? (
              <button
                type="button"
                onClick={() => markAsRead(notifications.filter((item) => !item.is_read).map((item) => item.id))}
                className="text-xs text-slate-500 hover:text-slate-700"
              >
                Отметить все прочитанными
              </button>
            ) : null}
          </div>
          <div className="flex max-h-80 flex-col gap-3 overflow-y-auto">
            {hasNotifications ? (
              notifications.map((notification) => (
                <NotificationItem key={notification.id} notification={notification} onMarkRead={handleMarkRead} />
              ))
            ) : (
              <p className="text-sm text-slate-500">Новых уведомлений нет.</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
