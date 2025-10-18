'use client';

import type { ModerationUser } from './types';
import { Modal } from '@/components/ui';

interface WarningModalProps {
  open: boolean;
  user: ModerationUser | null;
  message: string;
  loading: boolean;
  onChange: (value: string) => void;
  onClose: () => void;
  onSubmit: () => void;
}

export function WarningModal({ open, user, message, loading, onChange, onClose, onSubmit }: WarningModalProps) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={user ? `Предупреждение для ${user.email}` : 'Предупреждение пользователю'}
      primaryAction={{
        label: 'Отправить',
        onClick: onSubmit,
        loading
      }}
    >
      <div className="space-y-3">
        <p className="text-sm text-slate-600">
          Введите текст предупреждения, который будет отправлен пользователю через систему уведомлений.
        </p>
        <textarea
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
          rows={5}
          value={message}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Опишите нарушение или требования к исправлению ситуации..."
        />
      </div>
    </Modal>
  );
}
