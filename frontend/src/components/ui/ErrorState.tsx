import type { ReactNode } from 'react';
import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  actionLabel?: string;
  onRetry?: () => void;
  icon?: ReactNode;
}

export function ErrorState({
  title = 'Что-то пошло не так',
  message,
  actionLabel = 'Повторить',
  onRetry,
  icon
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-rose-200 bg-rose-50 p-10 text-center">
      {icon ? <div className="mb-4 text-4xl text-rose-500">{icon}</div> : null}
      <h3 className="text-lg font-semibold text-rose-600">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-rose-500">{message}</p>
      {onRetry ? (
        <Button className="mt-4" variant="secondary" onClick={onRetry}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}
