'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AgentReportsResponse {
  items: Array<{
    id: string;
    title: string;
    status: string;
    updated_at: string;
  }>;
}

const sidebarLinks = [
  { href: '/agent', label: 'Обзор' },
  { href: '/agent/creators', label: 'Креаторы' },
  { href: '/agent/reports', label: 'Отчёты', exact: true }
];

export default function AgentReportsPage() {
  const { data, isLoading, error, mutate } = useDashboardData<AgentReportsResponse>('/api/agent/reports', {
    fallbackData: agentReportsFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['agent', 'admin']}>
      <LayoutShell
        title="Отчёты"
        description="Готовьте ежемесячные отчёты и отслеживайте статус их согласования."
        sidebarLinks={sidebarLinks}
        actions={<Button variant="primary">Создать отчёт</Button>}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить отчёты"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data && data.items.length ? (
          <Table
            columns={['Название', 'Статус', 'Обновлён']}
            data={data.items.map((report) => [
              report.title,
              <Badge key={`${report.id}-status`} variant={report.status === 'submitted' ? 'success' : 'warning'}>
                {statusLabel(report.status)}
              </Badge>,
              new Date(report.updated_at).toLocaleDateString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState
            title="Отчёты отсутствуют"
            description="Создайте первый отчёт, чтобы поделиться результатами с брендом."
            actionLabel="Создать"
            onAction={() => mutate()}
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function statusLabel(status: string) {
  switch (status) {
    case 'draft':
      return 'Черновик';
    case 'submitted':
      return 'Отправлен';
    default:
      return status;
  }
}

const agentReportsFallback: AgentReportsResponse = {
  items: [
    { id: 'report-71', title: 'Месячный отчёт: октябрь', status: 'draft', updated_at: new Date().toISOString() },
    { id: 'report-72', title: 'Финальный отчёт по Holiday drop', status: 'submitted', updated_at: new Date().toISOString() }
  ]
};
