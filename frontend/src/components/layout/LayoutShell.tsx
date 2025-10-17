'use client';

import type { ReactNode } from 'react';

import { Header } from './Header';
import { Sidebar, type SidebarLink } from './Sidebar';

interface LayoutShellProps {
  title: string;
  description?: string;
  sidebarLinks: SidebarLink[];
  children: ReactNode;
}

export function LayoutShell({ title, description, sidebarLinks, children }: LayoutShellProps) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar links={sidebarLinks} />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 px-6 py-8">
          <div className="max-w-6xl space-y-6">
            <div className="space-y-2">
              <h1 className="text-3xl font-semibold text-slate-900">{title}</h1>
              {description ? <p className="text-sm text-slate-600">{description}</p> : null}
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
