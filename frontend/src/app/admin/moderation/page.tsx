'use client';

import { ModerationPanel } from '@/components/admin/moderation/ModerationPanel';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';

const sidebarLinks = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/users', label: 'Пользователи' },
  { href: '/admin/campaigns', label: 'Кампании' },
  { href: '/admin/moderation', label: 'Модерация', exact: true },
  { href: '/admin/finance', label: 'Финансы' },
  { href: '/admin/analytics', label: 'Аналитика' }
];

export default function AdminModerationPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Модерация"
        description="Управление блокировками пользователей и кампаний, отправка предупреждений и контроль журналов действий."
        sidebarLinks={sidebarLinks}
      >
        <ModerationPanel />
      </LayoutShell>
    </ProtectedRoute>
  );
}
