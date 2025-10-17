'use client';

import { useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface FactoryTask {
  id: string;
  title: string;
  status: 'in_progress' | 'scheduled' | 'completed';
  due_date: string;
}

interface FactoryTasksResponse {
  items: FactoryTask[];
}

const sidebarLinks = [
  { href: '/factory', label: 'Обзор' },
  { href: '/factory/tasks', label: 'Задачи', exact: true },
  { href: '/factory/calendar', label: 'Календарь' }
];

const filters = [
  { value: 'all', label: 'Все' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'scheduled', label: 'Запланировано' },
  { value: 'completed', label: 'Завершено' }
];

export default function FactoryTasksPage() {
  const [filter, setFilter] = useState('all');
  const { data, isLoading, error, mutate } = useDashboardData<FactoryTasksResponse>('/api/factory/tasks', {
    fallbackData: factoryTasksFallback,
    revalidateOnFocus: true
  });

  const filtered = useMemo(() => {
    if (!data) return [];
    if (filter === 'all') return data.items;
    return data.items.filter((task) => task.status === filter);
  }, [data, filter]);

  return (
    <ProtectedRoute allowedRoles={['factory', 'admin']}>
      <LayoutShell
        title="Задачи"
        description="Следите за статусами задач и управляйте сроками производства."
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
            title="Не удалось загрузить задачи"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {filtered.length ? (
          <Table
            columns={['Название', 'Статус', 'Срок']}
            data={filtered.map((task) => [
              task.title,
              <Badge key={`${task.id}-status`} variant={badgeVariant(task.status)}>
                {statusLabel(task.status)}
              </Badge>,
              new Date(task.due_date).toLocaleString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState
            title="Задачи не найдены"
            description="Попробуйте выбрать другой фильтр или обновить данные."
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function statusLabel(status: FactoryTask['status']) {
  switch (status) {
    case 'in_progress':
      return 'В работе';
    case 'scheduled':
      return 'Запланировано';
    case 'completed':
      return 'Завершено';
    default:
      return status;
  }
}

function badgeVariant(status: FactoryTask['status']): 'default' | 'success' | 'warning' {
  switch (status) {
    case 'completed':
      return 'success';
    case 'scheduled':
      return 'warning';
    default:
      return 'default';
  }
}

const factoryTasksFallback: FactoryTasksResponse = {
  items: [
    {
      id: 'task-501',
      title: 'Монтаж ролика для кампании #42',
      status: 'in_progress',
      due_date: new Date().toISOString()
    },
    {
      id: 'task-502',
      title: 'Подготовка сценария для TikTok лайвов',
      status: 'scheduled',
      due_date: new Date(Date.now() + 86400000).toISOString()
    }
  ]
};
