'use client';

import type { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface CardProps {
  title?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export function Card({ title, description, children, footer, className }: CardProps) {
  return (
    <article className={twMerge('rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md', className)}>
      {(title || description) && (
        <header className="border-b border-slate-100 px-6 py-4">
          {title ? <h3 className="text-lg font-semibold text-slate-900">{title}</h3> : null}
          {description ? <p className="mt-1 text-sm text-slate-600">{description}</p> : null}
        </header>
      )}
      {children ? <div className="px-6 py-4 text-sm text-slate-700">{children}</div> : null}
      {footer ? <footer className="border-t border-slate-100 px-6 py-3 text-sm text-slate-500">{footer}</footer> : null}
    </article>
  );
}
