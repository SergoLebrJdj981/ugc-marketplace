'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface FactoryCalendarItem {
  id: string;
  title: string;
  date: string;
  campaign: string;
}

interface FactoryCalendarResponse {
  items: FactoryCalendarItem[];
}

const sidebarLinks = [
  { href: '/factory', label: 'Обзор' },
  { href: '/factory/tasks', label: 'Задачи' },
  { href: '/factory/calendar', label: 'Календарь', exact: true }
];

export default function FactoryCalendarPage() {
  const { data, isLoading, error, mutate } = useDashboardData<FactoryCalendarResponse>('/api/factory/calendar', {
    fallbackData: factoryCalendarFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['factory', 'admin']}>
      <LayoutShell
        title="Календарь публикаций"
        description="Следите за датами выкладок и съёмок."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить календарь"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data && data.items.length ? (
          <Table
            columns={['Дата', 'Событие', 'Кампания']}
            data={data.items.map((item) => [
              new Date(item.date).toLocaleDateString('ru-RU'),
              item.title,
              item.campaign
            ])}
          />
        ) : (
          <EmptyState title="Событий нет" description="Запланируйте публикации, чтобы увидеть их в календаре." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const factoryCalendarFallback: FactoryCalendarResponse = {
  items: [
    {
      id: 'cal-301',
      title: 'Публикация ролика в Instagram',
      date: new Date().toISOString(),
      campaign: 'Holiday drop 2025'
    },
    {
      id: 'cal-302',
      title: 'Съёмка для TechLab',
      date: new Date(Date.now() + 2 * 24 * 3600 * 1000).toISOString(),
      campaign: 'TechLab gadgets'
    }
  ]
};
