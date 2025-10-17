'use client';

import { ReactNode } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider, ChatProvider, NotificationProvider, ThemeProvider } from '@/context';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>
          <ChatProvider>
            {children}
            <ToastContainer newestOnTop pauseOnFocusLoss={false} />
          </ChatProvider>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
