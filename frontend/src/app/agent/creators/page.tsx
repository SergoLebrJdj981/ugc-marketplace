'use client';

import { useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Button, EmptyState, Loader, Table } from '@/components/ui';
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
  { href: '/agent', label: 'Обзор' },
  { href: '/agent/creators', label: 'Креаторы', exact: true },
  { href: '/agent/reports', label: 'Отчёты' }
];

const filters = [
  { value: 'all', label: 'Все' },
  { value: 'active', label: 'Активные' },
  { value: 'idle', label: 'Неактивные' }
];

export default function AgentCreatorsPage() {
  const [filter, setFilter] = useState('all');
  const { data, isLoading, error, mutate } = useDashboardData<AgentCreatorsResponse>('/api/agent/creators', {
    fallbackData: agentCreatorsFallback,
    revalidateOnFocus: true
  });

  const filtered = useMemo(() => {
    if (!data) return [];
    if (filter === 'all') return data.items;
    const now = Date.now();
    return data.items.filter((creator) => {
      const days = (now - new Date(creator.last_activity).getTime()) / (1000 * 60 * 60 * 24);
      return filter === 'active' ? days < 3 : days >= 3;
    });
  }, [data, filter]);

  return (
    <ProtectedRoute allowedRoles={['agent', 'admin']}>
      <LayoutShell
        title="Креаторы"
        description="Следите за активностью закреплённых креаторов и распределяйте задачи."
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
            title="Не удалось загрузить креаторов"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {filtered.length ? (
          <Table
            columns={['Креатор', 'Кампании', 'Средний рейтинг', 'Последняя активность']}
            data={filtered.map((creator) => [
              creator.name,
              creator.campaigns,
              creator.avg_rating.toFixed(1),
              new Date(creator.last_activity).toLocaleString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState
            title="Креаторы не найдены"
            description="Измените фильтры или пригласите новых креаторов."
            actionLabel="Обновить"
            onAction={() => mutate()}
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
      last_activity: new Date(Date.now() - 4 * 24 * 3600 * 1000).toISOString()
    }
  ]
};
