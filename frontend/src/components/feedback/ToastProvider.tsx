'use client';

import type { ReactNode } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export function ToastProvider({ children }: { children: ReactNode }) {
  return (
    <>
      {children}
      <ToastContainer newestOnTop pauseOnFocusLoss={false} position="bottom-right" />
    </>
  );
}
