'use client';

import { twMerge } from 'tailwind-merge';

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
}

export function Progress({ value, max = 100, className }: ProgressProps) {
  const percentage = Math.min(Math.max(value, 0), max);
  const width = `${(percentage / max) * 100}%`;

  return (
    <div className={twMerge('h-2 w-full overflow-hidden rounded-full bg-slate-200', className)}>
      <div className="h-full rounded-full bg-slate-900 transition-all" style={{ width }} />
    </div>
  );
}
