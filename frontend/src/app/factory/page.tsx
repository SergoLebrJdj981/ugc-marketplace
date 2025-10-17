'use client';

import Link from 'next/link';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
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
  { href: '/factory', label: 'Обзор', exact: true },
  { href: '/factory/tasks', label: 'Задачи' },
  { href: '/factory/calendar', label: 'Календарь' }
];

export default function FactoryDashboard() {
  const { data, isLoading, error } = useDashboardData<FactoryTasksResponse>('/api/factory/tasks', {
    fallbackData: factoryTasksFallback
  });

  const tasks = data?.items ?? [];

  return (
    <ProtectedRoute allowedRoles={['factory', 'admin']}>
      <LayoutShell
        title="Контент-завод"
        description="Управление задачами по созданию и публикации контента."
        sidebarLinks={sidebarLinks}
        actions={
          <Link href="/factory/tasks" className="text-sm text-slate-600 hover:text-slate-900">
            Все задачи
          </Link>
        }
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <Card title="Ошибка при загрузке">
            <EmptyState
              title="Не удалось загрузить"
              description={error.message || 'Попробуйте обновить страницу чуть позже.'}
            />
          </Card>
        ) : null}

        {tasks.length ? (
          <Card title="Активные задачи" description="Перечень задач, назначенных команде контент-завода.">
            <Table
              columns={['Название', 'Статус', 'Срок']}
              data={tasks.map((task) => [
                task.title,
                statusLabel(task.status),
                new Date(task.due_date).toLocaleDateString('ru-RU')
              ])}
            />
          </Card>
        ) : (
          <EmptyState
            title="Нет задач"
            description="Назначьте задачи контент-заводу, чтобы увидеть их в этом списке."
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
