'use client';

import type { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

const badgeStyles: Record<NonNullable<BadgeProps['variant']>, string> = {
  info: 'bg-sky-100 text-sky-700 ring-sky-200',
  success: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  warning: 'bg-amber-100 text-amber-700 ring-amber-200',
  danger: 'bg-rose-100 text-rose-700 ring-rose-200',
  neutral: 'bg-slate-100 text-slate-700 ring-slate-200'
};

interface BadgeProps {
  children: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'danger' | 'neutral';
  className?: string;
}

export function Badge({ children, variant = 'neutral', className }: BadgeProps) {
  return (
    <span
      className={twMerge(
        'inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset',
        badgeStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
