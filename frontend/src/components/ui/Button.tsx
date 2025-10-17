'use client';

import { forwardRef } from 'react';
import { twMerge } from 'tailwind-merge';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'danger';
  children: ReactNode;
  loading?: boolean;
}

const variantStyles: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: 'bg-brand text-white hover:bg-brand-dark focus-visible:ring-brand',
  secondary: 'bg-white text-brand border border-brand hover:bg-brand-light/10 focus-visible:ring-brand',
  ghost: 'bg-transparent text-brand hover:bg-brand-light/20 focus-visible:ring-brand',
  outline: 'bg-transparent border border-slate-300 text-slate-700 hover:bg-slate-100 focus-visible:ring-slate-300',
  danger: 'bg-rose-600 text-white hover:bg-rose-700 focus-visible:ring-rose-500'
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', className, disabled, loading, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={twMerge(
          'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60',
          variantStyles[variant],
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? 'Загрузка...' : children}
      </button>
    );
  }
);

Button.displayName = 'Button';
