'use client';

import { forwardRef } from 'react';
import { twMerge } from 'tailwind-merge';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  children: ReactNode;
  loading?: boolean;
}

const variantStyles: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: 'bg-brand text-white hover:bg-brand-dark focus-visible:ring-brand',
  secondary: 'bg-white text-brand border border-brand hover:bg-brand-light/10 focus-visible:ring-brand',
  ghost: 'bg-transparent text-brand hover:bg-brand-light/20 focus-visible:ring-brand'
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
