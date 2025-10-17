'use client';

import dynamic from 'next/dynamic';
import type { ReactNode } from 'react';

import { Header } from './Header';
import type { SidebarLink } from './Sidebar';

const Sidebar = dynamic(() => import('./Sidebar'), {
  ssr: false,
  loading: () => <div className="hidden w-64 border-r border-slate-200 bg-white/80 px-4 py-6 sm:block" />
});
const RoleHeader = dynamic(() => import('./RoleHeader'), {
  ssr: false,
  loading: () => (
    <div className="border-b border-slate-200 bg-white/70 px-6 py-4 backdrop-blur">
      <div className="h-6 w-48 animate-pulse rounded bg-slate-200" />
    </div>
  )
});

interface LayoutShellProps {
  title: string;
  description?: string;
  sidebarLinks: SidebarLink[];
  children: ReactNode;
  actions?: ReactNode;
}

export function LayoutShell({ title, description, sidebarLinks, children, actions }: LayoutShellProps) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar links={sidebarLinks} />
      <div className="flex flex-1 flex-col">
        <Header />
        <RoleHeader title={title} description={description} actions={actions} />
        <main className="flex-1 px-6 py-8">
          <div className="max-w-6xl space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
