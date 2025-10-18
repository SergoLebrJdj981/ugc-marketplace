'use client';

import { useEffect, useMemo, useState } from 'react';

import { Card, Input, Button, Loader } from '@/components/ui';
import { useAuth, useChat } from '@/context';
import { notify } from '@/lib/toast';
import { ChatBox } from './ChatBox';
import { MessageList } from './MessageList';
import type { ChatContact } from '@/types/chat';
import { toast } from 'react-toastify';

interface ChatWidgetProps {
  title: string;
  description?: string;
  contacts?: ChatContact[];
  emptyState?: string;
}

export function ChatWidget({ title, description, contacts = [], emptyState }: ChatWidgetProps) {
  const { user } = useAuth();
  const { messages, isLoading, activeChatId, receiverId, receiverName, selectChat, sendMessage } = useChat();
  const [selectedContactId, setSelectedContactId] = useState<string>('');
  const [manualReceiver, setManualReceiver] = useState('');
  const [isLaunching, setIsLaunching] = useState(false);

  useEffect(() => {
    if (contacts.length) {
      setSelectedContactId((prev) => prev || contacts[0]?.id || '');
    }
  }, [contacts]);

  const activeContactName = useMemo(() => {
    if (receiverName) return receiverName;
    if (!receiverId) return null;
    const contact = contacts.find((item) => item.id === receiverId);
    return contact?.name ?? null;
  }, [contacts, receiverId, receiverName]);

  const handleStartChat = async () => {
    const targetId = manualReceiver.trim() || selectedContactId;
    if (!targetId) {
      notify.error('Укажите идентификатор собеседника');
      return;
    }
    if (!user?.id) {
      notify.error('Для общения необходимо авторизоваться');
      return;
    }
    setIsLaunching(true);
    try {
      const contactName = contacts.find((item) => item.id === targetId)?.name;
      await selectChat(targetId, contactName);
    } catch (error) {
      console.warn('Failed to launch chat session', error);
    } finally {
      setIsLaunching(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    try {
      await sendMessage(content);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Ошибка при отправке сообщения';
      toast.error(message || 'Ошибка при отправке сообщения');
    }
  };

  return (
    <Card
      title={title}
      description={
        description ??
        'Выберите собеседника или укажите его ID, чтобы открыть диалог. Сообщения обновляются в реальном времени.'
      }
      footer={
        activeChatId ? (
          <div className="flex flex-col gap-1">
            <span className="text-xs text-slate-500 dark:text-slate-300">Текущий чат: {activeChatId}</span>
            {activeContactName ? (
              <span className="text-xs text-slate-500 dark:text-slate-300">Собеседник: {activeContactName}</span>
            ) : null}
          </div>
        ) : (
          <span className="text-xs text-slate-500 dark:text-slate-300">
            Укажите ID собеседника и нажмите «Начать диалог», чтобы получить идентификатор чата.
          </span>
        )
      }
      className="flex flex-col gap-4"
    >
      <div className="flex flex-col gap-2">
        {contacts.length ? (
          <label className="flex w-full flex-col gap-1 text-sm font-medium text-slate-700">
            Выбор собеседника
            <select
              value={selectedContactId}
              onChange={(event) => setSelectedContactId(event.target.value)}
              className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-brand focus:ring-2 focus:ring-brand/20"
            >
              <option value="">— Не выбрано —</option>
              {contacts.map((contact) => (
                <option key={contact.id} value={contact.id}>
                  {contact.name}
                  {contact.role ? ` · ${contact.role}` : ''}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <Input
          label="ID собеседника"
          placeholder="Вставьте идентификатор пользователя"
          value={manualReceiver}
          onChange={(event) => setManualReceiver(event.target.value)}
        />

        <div className="flex items-center gap-2">
          <Button type="button" variant="secondary" onClick={handleStartChat} disabled={isLaunching}>
            {isLaunching ? 'Подключение...' : 'Начать диалог'}
          </Button>
          {receiverId ? (
            <span className="text-xs text-slate-500 dark:text-slate-300">Активный собеседник: {receiverId}</span>
          ) : null}
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-6">
          <Loader />
        </div>
      ) : activeChatId ? (
        <MessageList messages={messages} currentUserId={user?.id ?? null} />
      ) : (
        <p className="text-sm text-slate-500">
          {emptyState ?? 'Выберите собеседника и запустите чат, чтобы начать переписку.'}
        </p>
      )}

      <ChatBox onSend={handleSendMessage} disabled={!activeChatId} placeholder="Введите текст сообщения" />
    </Card>
  );
}
