'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, Table } from '@/components/ui';

const sidebarLinks = [
  { href: '/agent', label: 'Обзор', exact: true },
  { href: '/agent/creators', label: 'Креаторы' },
  { href: '/agent/reports', label: 'Отчёты' }
];

export default function AgentDashboard() {
  return (
    <ProtectedRoute allowedRoles={['agent', 'admin']}>
      <LayoutShell
        title="Панель агента"
        description="Управляйте креаторами и отслеживайте их активность."
        sidebarLinks={sidebarLinks}
      >
        <Card title="Активные креаторы" description="Краткая сводка по закреплённым креаторам.">
          <Table
            columns={['Имя', 'Кампании', 'Средний рейтинг']}
            data={[
              ['Анна Петрова', '3', '4.8'],
              ['Иван Смирнов', '2', '4.5']
            ]}
          />
        </Card>
      </LayoutShell>
    </ProtectedRoute>
  );
}
