'use client';

import type { ReactNode } from 'react';

import { Breadcrumbs } from '@/components/layout/Breadcrumbs';

interface RoleHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function RoleHeader({ title, description, actions }: RoleHeaderProps) {
  return (
    <div className="border-b border-slate-200 bg-white/70 px-6 py-4 backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <Breadcrumbs />
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">{title}</h1>
          {description ? <p className="text-sm text-slate-600">{description}</p> : null}
        </div>
        {actions ? <div className="flex items-center gap-3">{actions}</div> : null}
      </div>
    </div>
  );
}
