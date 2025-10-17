'use client';

import { ReactNode } from 'react';
import { AuthProvider, ChatProvider, NotificationProvider, ThemeProvider } from '@/context';
import { ToastProvider } from '@/components/feedback/ToastProvider';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <NotificationProvider>
        <ChatProvider>
          <ThemeProvider>
            <ToastProvider>{children}</ToastProvider>
          </ThemeProvider>
        </ChatProvider>
      </NotificationProvider>
    </AuthProvider>
  );
}
