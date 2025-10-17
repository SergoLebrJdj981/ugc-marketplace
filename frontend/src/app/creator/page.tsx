'use client';

import Link from 'next/link';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, Card, EmptyState, ErrorState, Loader, Table } from '@/components/ui';
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

interface CreatorFeedResponse {
  items: Array<{
    id: string;
    title: string;
    brand: string;
    reward: number;
    deadline: string;
    format: string;
  }>;
}

const sidebarLinks = [
  { href: '/creator', label: 'Обзор', exact: true },
  { href: '/creator/feed', label: 'Лента' },
  { href: '/creator/orders', label: 'Заказы' },
  { href: '/creator/balance', label: 'Баланс' },
  { href: '/creator/rating', label: 'Рейтинг' },
  { href: '/creator/learning', label: 'Обучение' }
];

export default function CreatorDashboard() {
  const {
    data: ordersData,
    isLoading: ordersLoading,
    error: ordersError
  } = useDashboardData<CreatorOrdersResponse>('/api/creator/orders', {
    fallbackData: creatorOrdersFallback
  });
  const {
    data: feedData,
    isLoading: feedLoading,
    error: feedError
  } = useDashboardData<CreatorFeedResponse>('/api/creator/feed', {
    fallbackData: creatorFeedFallback
  });

  const isLoading = ordersLoading || feedLoading;
  const hasError = Boolean(ordersError || feedError);

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Панель креатора"
        description="Следите за заказами, балансом и рейтингом качества."
        sidebarLinks={sidebarLinks}
        actions={<Button variant="secondary">Создать портфолио</Button>}
      >
        {isLoading ? <Loader /> : null}
        {hasError ? (
          <ErrorState
            message="Не удалось полностью загрузить данные. Показаны сохранённые значения."
            onRetry={() => window.location.reload()}
          />
        ) : null}

        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard title="В работе" value={ordersData?.summary.in_progress ?? 0} />
          <StatCard title="На проверке" value={ordersData?.summary.awaiting_review ?? 0} />
          <StatCard title="Завершено" value={ordersData?.summary.completed ?? 0} />
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Текущие заказы</h2>
            <Link href="/creator/orders">
              <Button variant="secondary">Все заказы</Button>
            </Link>
          </div>
          {ordersData && ordersData.items.length ? (
            <Table
              columns={['ID заказа', 'Кампания', 'Статус', 'Срок', 'Выплата']}
              data={ordersData.items.map((order) => [
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
            <EmptyState
              title="Заказы пока отсутствуют"
              description="Откликайтесь на кампании и отслеживайте статус исполнения заказа здесь."
            />
          )}
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Рекомендованные кампании</h2>
            <Link href="/creator/feed">
              <Button variant="secondary">Перейти в ленту</Button>
            </Link>
          </div>
          {feedData && feedData.items.length ? (
            <Table
              columns={['Кампания', 'Бренд', 'Формат', 'Вознаграждение', 'Дедлайн']}
              data={feedData.items.map((item) => [
                item.title,
                item.brand,
                item.format,
                `${item.reward.toLocaleString('ru-RU')} ₽`,
                new Date(item.deadline).toLocaleDateString('ru-RU')
              ])}
            />
          ) : (
            <EmptyState
              title="Нет доступных кампаний"
              description="Следите за обновлениями ленты — новые кампании появляются ежедневно."
            />
          )}
        </section>
      </LayoutShell>
    </ProtectedRoute>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
    </Card>
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

const creatorFeedFallback: CreatorFeedResponse = {
  items: [
    {
      id: 'cmp-feed-1',
      title: 'Обзор новой коллекции',
      brand: 'FashionHub',
      reward: 24000,
      deadline: new Date().toISOString(),
      format: 'Shorts'
    }
  ]
};
