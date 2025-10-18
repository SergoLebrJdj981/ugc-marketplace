'use client';

import { useState, type FormEvent, type KeyboardEvent } from 'react';

import { Button, Input } from '@/components/ui';

interface ChatBoxProps {
  onSend: (content: string) => Promise<void> | void;
  placeholder?: string;
  disabled?: boolean;
}

export function ChatBox({ onSend, placeholder, disabled }: ChatBoxProps) {
  const [value, setValue] = useState('');
  const [isSending, setIsSending] = useState(false);

  const send = async () => {
    if (!value.trim() || disabled || isSending) return;
    setIsSending(true);
    try {
      await onSend(value.trim());
      setValue('');
    } finally {
      setIsSending(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await send();
  };

  const handleKeyDown = async (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      await send();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <Input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder ?? 'Напишите сообщение'}
        disabled={disabled || isSending}
        className="flex-1"
      />
      <Button type="submit" variant="primary" disabled={disabled || isSending || !value.trim()}>
        {isSending ? 'Отправка...' : 'Отправить'}
      </Button>
    </form>
  );
}
