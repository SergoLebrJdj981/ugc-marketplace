'use client';

import { API_URL, apiRequest } from '@/lib/api';
import type { ChatMessage } from '@/types/chat';

type ApiMessage = {
  id: string;
  chat_id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  is_read: boolean;
  timestamp: string;
};

type MessageListResponse = {
  total: number;
  items: ApiMessage[];
};

type MessageSendResponse = {
  status: string;
  message_id: string;
  timestamp: string;
};

export type SendChatMessageParams = {
  chatId: string;
  receiverId: string;
  senderId: string;
  content: string;
  token: string;
};

function mapChatMessage(message: ApiMessage): ChatMessage {
  return {
    id: message.id,
    chatId: message.chat_id,
    senderId: message.sender_id,
    receiverId: message.receiver_id,
    content: message.content,
    timestamp: message.timestamp,
    isRead: message.is_read,
  };
}

export async function fetchChatHistory(chatId: string, token: string): Promise<ChatMessage[]> {
  const { data, error } = await apiRequest<MessageListResponse>(`/api/chat/${chatId}`, {
    token,
  });
  if (error || !data) {
    throw new Error(error?.message ?? 'Не удалось загрузить сообщения чата');
  }
  return data.items.map(mapChatMessage);
}

export async function postChatMessage(params: SendChatMessageParams): Promise<ChatMessage> {
  const { data, error } = await apiRequest<MessageSendResponse>('/api/chat/send', {
    method: 'POST',
    token: params.token,
    data: {
      chat_id: params.chatId,
      receiver_id: params.receiverId,
      content: params.content,
    },
    showErrorToast: false,
  });
  if (error || !data) {
    let message: string | undefined;
    if (typeof error === 'string') {
      message = error;
    } else if (error) {
      const extended = error as { detail?: string };
      message = error.message || extended.detail;
      if (!message) {
        try {
          message = JSON.stringify(error);
        } catch {
          message = undefined;
        }
      }
    }
    throw new Error(message || 'Не удалось отправить сообщение');
  }
  return {
    id: data.message_id,
    chatId: params.chatId,
    senderId: params.senderId,
    receiverId: params.receiverId,
    content: params.content,
    timestamp: data.timestamp,
    isRead: true,
  };
}

export function buildWsUrl(chatId: string, token: string): string {
  const base = (API_URL ?? '').replace(/\/$/, '');
  const protocol = base.startsWith('https') ? 'wss' : 'ws';
  const path = `${protocol}${base.replace(/^https?/, '')}/ws/chat/${chatId}`;
  const query = `token=${encodeURIComponent(token)}`;
  return `${path}?${query}`;
}

export async function deriveChatId(a: string, b: string): Promise<string> {
  const globalCrypto = typeof globalThis !== 'undefined' ? (globalThis as typeof globalThis).crypto : undefined;
  if (!globalCrypto || !globalCrypto.subtle) {
    if (globalCrypto?.randomUUID) {
      return globalCrypto.randomUUID();
    }
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}-${Math.random()
      .toString(36)
      .slice(2, 10)}`;
  }

  const participants = [a, b].sort();
  const encoder = new TextEncoder();
  const data = encoder.encode(participants.join(':'));
  const hashBuffer = await globalCrypto.subtle.digest('SHA-1', data);
  const hashBytes = new Uint8Array(hashBuffer).slice(0, 16);
  hashBytes[6] = (hashBytes[6] & 0x0f) | 0x50;
  hashBytes[8] = (hashBytes[8] & 0x3f) | 0x80;
  const segments = [
    Array.from(hashBytes.slice(0, 4)),
    Array.from(hashBytes.slice(4, 6)),
    Array.from(hashBytes.slice(6, 8)),
    Array.from(hashBytes.slice(8, 10)),
    Array.from(hashBytes.slice(10, 16)),
  ];
  return segments
    .map((segment) => segment.map((byte) => byte.toString(16).padStart(2, '0')).join(''))
    .join('-');
}

export function mergeMessages(existing: ChatMessage[], incoming: ChatMessage): ChatMessage[] {
  const map = new Map(existing.map((message) => [message.id, message]));
  map.set(incoming.id, incoming);
  return Array.from(map.values()).sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
  );
}

export { mapChatMessage };
