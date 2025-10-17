'use client';

import { forwardRef } from 'react';
import { twMerge } from 'tailwind-merge';
import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <label className="flex w-full flex-col gap-1 text-sm font-medium text-slate-700">
        {label}
        <input
          ref={ref}
          className={twMerge(
            'w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20',
            error ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-300' : '',
            className
          )}
          {...props}
        />
        {error ? <span className="text-xs text-rose-500">{error}</span> : null}
      </label>
    );
  }
);

Input.displayName = 'Input';
