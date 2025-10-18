import React, { useEffect } from 'react';
import { render, screen, waitFor } from '@testing-library/react';

import { NotificationProvider, useNotifications } from '@/context';

jest.mock('@/context/auth-context', () => ({
  useAuth: () => ({
    accessToken: 'token',
    logout: jest.fn(),
    user: { id: 'user-123', email: 'u@example.com', full_name: 'User' }
  })
}));

jest.mock('@/lib/api', () => ({
  apiRequest: jest.fn().mockResolvedValue({ data: { total: 0, items: [] } }),
  API_URL: 'http://localhost:8000'
}));

jest.mock('react-toastify', () => ({
  toast: { success: jest.fn(), error: jest.fn(), info: jest.fn() },
  ToastContainer: () => null
}));

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onopen: (() => void) | null = null;
  public onclose: (() => void) | null = null;
  public onerror: (() => void) | null = null;

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
    setTimeout(() => {
      this.onopen?.();
    }, 0);
  }

  send() {}

  close() {
    this.onclose?.();
  }
}

global.WebSocket = MockWebSocket as unknown as typeof WebSocket;

type HarnessProps = { onReady?: () => void };

function Harness({ onReady }: HarnessProps) {
  const { notifications, unreadCount, pushNotification } = useNotifications();

  useEffect(() => {
    pushNotification(
      {
        id: '1',
        user_id: 'user',
        type: 'admin_notice',
        title: 'Заголовок',
        content: 'Текст',
        is_read: false,
        created_at: new Date().toISOString()
      },
      { silent: true }
    );
    onReady?.();
  }, [onReady, pushNotification]);

  return (
    <>
      <span data-testid="unread">{unreadCount}</span>
      <span data-testid="total">{notifications.length}</span>
    </>
  );
}

test('pushNotification stores item and increments unread count', async () => {
  const handleReady = jest.fn();
  render(
    <NotificationProvider>
      <Harness onReady={handleReady} />
    </NotificationProvider>
  );

  await waitFor(() => {
    expect(screen.getByTestId('unread').textContent).toBe('1');
    expect(screen.getByTestId('total').textContent).toBe('1');
  });
  expect(handleReady).toHaveBeenCalled();
});
