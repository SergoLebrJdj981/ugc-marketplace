import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';

import { Providers } from './providers';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin', 'cyrillic'] });

export const metadata: Metadata = {
  title: 'UGC Marketplace',
  description: 'Платформа для брендов и креаторов с поддержкой UGC кампаний'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru" className="h-full">
      <body
        className={`${inter.className} min-h-screen bg-white text-gray-900 transition-colors duration-300 dark:bg-gray-900 dark:text-gray-100`}
      >
        <Providers>
          <div className="min-h-screen bg-gradient-to-br from-white via-slate-50 to-slate-100 dark:from-gray-900 dark:via-slate-900 dark:to-slate-950">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
