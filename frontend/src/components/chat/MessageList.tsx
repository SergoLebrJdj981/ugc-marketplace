'use client';

import type { ChatMessage } from '@/types/chat';

interface MessageListProps {
  messages: ChatMessage[];
  currentUserId?: string | null;
}

export function MessageList({ messages, currentUserId }: MessageListProps) {
  if (!messages.length) {
    return <p className="text-sm text-slate-500">Начните диалог, чтобы увидеть сообщения.</p>;
  }

  return (
    <div className="flex max-h-96 flex-col gap-3 overflow-y-auto pr-1">
      {messages.map((message) => {
        const isOwn = currentUserId ? message.senderId === currentUserId : false;
        const time = new Date(message.timestamp).toLocaleTimeString('ru-RU', {
          hour: '2-digit',
          minute: '2-digit',
        });

        return (
          <div key={message.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-3 py-2 text-sm shadow-sm transition
                ${isOwn ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-900 dark:bg-slate-700 dark:text-slate-100'}`}
            >
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
              <span className={`mt-1 block text-xs ${isOwn ? 'text-indigo-100/80' : 'text-slate-500 dark:text-slate-300'}`}>
                {time}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
