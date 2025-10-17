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
      <body className={`${inter.className} min-h-screen bg-slate-50`}> 
        <Providers>
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
