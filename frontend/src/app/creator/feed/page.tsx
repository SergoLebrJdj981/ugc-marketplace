'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

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
  { href: '/creator', label: 'Обзор' },
  { href: '/creator/feed', label: 'Лента', exact: true },
  { href: '/creator/orders', label: 'Заказы' },
  { href: '/creator/balance', label: 'Баланс' },
  { href: '/creator/rating', label: 'Рейтинг' },
  { href: '/creator/learning', label: 'Обучение' }
];

export default function CreatorFeedPage() {
  const { data, isLoading, error, mutate } = useDashboardData<CreatorFeedResponse>('/api/creator/feed', {
    fallbackData: creatorFeedFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Лента кампаний"
        description="Отбирайте задачи по фильтрам и откликайтесь моментально."
        sidebarLinks={sidebarLinks}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => mutate()}>
              Обновить
            </Button>
            <Button variant="outline">Настроить фильтры</Button>
          </div>
        }
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить кампании"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data && data.items.length ? (
          <Table
            columns={['Кампания', 'Бренд', 'Формат', 'Вознаграждение', 'Дедлайн']}
            data={data.items.map((item) => [
              item.title,
              item.brand,
              <Badge key={`${item.id}-format`}>{item.format}</Badge>,
              `${item.reward.toLocaleString('ru-RU')} ₽`,
              new Date(item.deadline).toLocaleDateString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState
            title="Кампаний не найдено"
            description="Попробуйте изменить фильтры поиска или зайдите позже."
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const creatorFeedFallback: CreatorFeedResponse = {
  items: [
    {
      id: 'cmp-feed-1',
      title: 'Видео-обзор смартфона',
      brand: 'TechLab',
      reward: 32000,
      deadline: new Date().toISOString(),
      format: 'Shorts'
    }
  ]
};
