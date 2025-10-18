'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AdminAnalyticsResponse {
  total_events: number;
  per_status: Record<string, number>;
  systems: Record<string, { incidents: number; uptime: number }>;
}

const sidebarLinks = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/users', label: 'Пользователи' },
  { href: '/admin/campaigns', label: 'Кампании' },
  { href: '/admin/moderation', label: 'Модерация' },
  { href: '/admin/finance', label: 'Финансы' },
  { href: '/admin/analytics', label: 'Аналитика', exact: true }
];

export default function AdminAnalyticsPage() {
  const { data, isLoading, error, mutate } = useDashboardData<AdminAnalyticsResponse>('/api/admin/analytics', {
    fallbackData: adminAnalyticsFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Аналитика системы"
        description="Следите за стабильностью сервисов и количеством событий."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить аналитику"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <>
            <div className="grid gap-4 sm:grid-cols-3">
              <Card>
                <p className="text-xs text-slate-500">Всего событий</p>
                <p className="mt-2 text-xl font-semibold text-slate-900">{data.total_events}</p>
              </Card>
              <Card>
                <p className="text-xs text-slate-500">Статусов событий</p>
                <p className="mt-2 text-xl font-semibold text-slate-900">
                  {Object.keys(data.per_status).length}
                </p>
              </Card>
              <Card>
                <p className="text-xs text-slate-500">Сервисов</p>
                <p className="mt-2 text-xl font-semibold text-slate-900">{Object.keys(data.systems).length}</p>
              </Card>
            </div>

            <Table
              columns={['Статус события', 'Количество']}
              data={Object.entries(data.per_status).map(([status, count]) => [status, count])}
            />
            <Table
              columns={['Система', 'Инцидентов', 'Uptime']}
              data={Object.entries(data.systems).map(([system, info]) => [
                system,
                info.incidents,
                `${(info.uptime * 100).toFixed(2)}%`
              ])}
            />
          </>
        ) : (
          <EmptyState title="Нет данных" description="Аналитика появится после накопления событий." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const adminAnalyticsFallback: AdminAnalyticsResponse = {
  total_events: 0,
  per_status: { processed: 0 },
  systems: {
    auth: { incidents: 0, uptime: 0.999 },
    api: { incidents: 1, uptime: 0.995 },
    notifications: { incidents: 0, uptime: 0.998 }
  }
};
