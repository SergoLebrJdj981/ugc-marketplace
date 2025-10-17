'use client';

import Link from 'next/link';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, ErrorState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AgentCreatorsResponse {
  items: Array<{
    id: string;
    name: string;
    campaigns: number;
    avg_rating: number;
    last_activity: string;
  }>;
}

const sidebarLinks = [
  { href: '/agent', label: 'Обзор', exact: true },
  { href: '/agent/creators', label: 'Креаторы' },
  { href: '/agent/reports', label: 'Отчёты' }
];

export default function AgentDashboard() {
  const { data, isLoading, error } = useDashboardData<AgentCreatorsResponse>('/api/agent/creators', {
    fallbackData: agentCreatorsFallback
  });

  return (
    <ProtectedRoute allowedRoles={['agent', 'admin']}>
      <LayoutShell
        title="Панель агента"
        description="Управляйте креаторами и отслеживайте их активность."
        sidebarLinks={sidebarLinks}
        actions={
          <Link href="/agent/reports">
            <span className="text-sm text-slate-600 hover:text-slate-900">Перейти к отчётам</span>
          </Link>
        }
      >
        {isLoading ? <Loader /> : null}
        {error ? <ErrorState message={error.message} onRetry={() => window.location.reload()} /> : null}
        {data && data.items.length ? (
          <Card title="Активные креаторы" description="Краткая сводка по закреплённым креаторам.">
            <Table
              columns={['Имя', 'Кампании', 'Средний рейтинг', 'Активность']}
              data={data.items.map((creator) => [
                creator.name,
                creator.campaigns,
                creator.avg_rating.toFixed(1),
                new Date(creator.last_activity).toLocaleDateString('ru-RU')
              ])}
            />
          </Card>
        ) : (
          <EmptyState
            title="Нет закреплённых креаторов"
            description="Добавьте креаторов, чтобы отслеживать их активность и результаты."
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const agentCreatorsFallback: AgentCreatorsResponse = {
  items: [
    {
      id: 'creator-301',
      name: 'Анна Ким',
      campaigns: 4,
      avg_rating: 4.9,
      last_activity: new Date().toISOString()
    },
    {
      id: 'creator-302',
      name: 'Дмитрий Орлов',
      campaigns: 2,
      avg_rating: 4.6,
      last_activity: new Date().toISOString()
    }
  ]
};
