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
    <article
      className={twMerge(
        'rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-sm transition hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100',
        className
      )}
    >
      {(title || description) && (
        <header className="border-b border-slate-100 px-6 py-4 dark:border-slate-700">
          {title ? <h3 className="text-lg font-semibold">{title}</h3> : null}
          {description ? <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{description}</p> : null}
        </header>
      )}
      {children ? <div className="px-6 py-4 text-sm text-slate-700 dark:text-slate-200">{children}</div> : null}
      {footer ? (
        <footer className="border-t border-slate-100 px-6 py-3 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-300">
          {footer}
        </footer>
      ) : null}
    </article>
  );
}
