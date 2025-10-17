'use client';

import type { ReactNode } from 'react';

import { Header } from './Header';
import { RoleHeader } from './RoleHeader';
import { Sidebar, type SidebarLink } from './Sidebar';

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
