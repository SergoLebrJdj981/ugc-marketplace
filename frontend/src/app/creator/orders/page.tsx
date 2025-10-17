'use client';

import { useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface CreatorOrdersResponse {
  summary: {
    in_progress: number;
    awaiting_review: number;
    completed: number;
  };
  items: Array<{
    id: string;
    campaign: string;
    status: string;
    deadline: string;
    payout: number;
  }>;
}

const sidebarLinks = [
  { href: '/creator', label: 'Обзор' },
  { href: '/creator/feed', label: 'Лента' },
  { href: '/creator/orders', label: 'Заказы', exact: true },
  { href: '/creator/balance', label: 'Баланс' },
  { href: '/creator/rating', label: 'Рейтинг' },
  { href: '/creator/learning', label: 'Обучение' }
];

const filters = [
  { value: 'all', label: 'Все' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'awaiting_review', label: 'На проверке' },
  { value: 'completed', label: 'Завершено' }
];

export default function CreatorOrdersPage() {
  const [filter, setFilter] = useState<string>('all');
  const { data, isLoading, error, mutate } = useDashboardData<CreatorOrdersResponse>('/api/creator/orders', {
    fallbackData: creatorOrdersFallback,
    revalidateOnFocus: true
  });

  const filteredItems = useMemo(() => {
    if (!data) return [];
    if (filter === 'all') return data.items;
    return data.items.filter((item) => item.status === filter);
  }, [data, filter]);

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Заказы"
        description="Контролируйте сроки, статусы и выплаты по заказам."
        sidebarLinks={sidebarLinks}
        actions={
          <div className="flex items-center gap-2">
            {filters.map((option) => (
              <Button
                key={option.value}
                variant={filter === option.value ? 'primary' : 'outline'}
                onClick={() => setFilter(option.value)}
              >
                {option.label}
              </Button>
            ))}
          </div>
        }
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить заказы"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {filteredItems.length ? (
          <Table
            columns={['ID', 'Кампания', 'Статус', 'Срок', 'Выплата']}
            data={filteredItems.map((order) => [
              order.id,
              order.campaign,
              <Badge key={`${order.id}-status`} variant={statusToVariant(order.status)}>
                {statusLabel(order.status)}
              </Badge>,
              new Date(order.deadline).toLocaleDateString('ru-RU'),
              `${order.payout.toLocaleString('ru-RU')} ₽`
            ])}
          />
        ) : (
          <EmptyState title="Нет заказов" description="Попробуйте показать все статусы или обновите данные." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function statusLabel(status: string) {
  switch (status) {
    case 'in_progress':
      return 'В работе';
    case 'awaiting_review':
      return 'На проверке';
    case 'completed':
      return 'Завершён';
    default:
      return status;
  }
}

function statusToVariant(status: string): 'default' | 'success' | 'warning' | 'danger' {
  switch (status) {
    case 'completed':
      return 'success';
    case 'awaiting_review':
      return 'warning';
    default:
      return 'default';
  }
}

const creatorOrdersFallback: CreatorOrdersResponse = {
  summary: {
    in_progress: 2,
    awaiting_review: 1,
    completed: 8
  },
  items: [
    {
      id: 'order-101',
      campaign: 'Осенний lookbook',
      status: 'in_progress',
      deadline: new Date().toISOString(),
      payout: 26000
    },
    {
      id: 'order-102',
      campaign: 'Видео-отзыв для TechLab',
      status: 'awaiting_review',
      deadline: new Date().toISOString(),
      payout: 18000
    }
  ]
};
