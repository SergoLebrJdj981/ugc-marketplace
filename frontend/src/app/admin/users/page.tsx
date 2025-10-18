'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

const sidebarLinks = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/users', label: 'Пользователи', exact: true },
  { href: '/admin/campaigns', label: 'Кампании' },
  { href: '/admin/moderation', label: 'Модерация' },
  { href: '/admin/finance', label: 'Финансы' },
  { href: '/admin/analytics', label: 'Аналитика' }
];

export default function AdminUsersPage() {
  const { data, isLoading, error, mutate } = useDashboardData<AdminUser[]>('/api/admin/users', {
    fallbackData: adminUsersFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Пользователи"
        description="Список зарегистрированных пользователей и их роли."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить пользователей"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data && data.length ? (
          <Table
            columns={['ID', 'Email', 'Имя', 'Роль']}
            data={data.map((user) => [user.id, user.email, user.full_name ?? '—', roleLabel(user.role)])}
          />
        ) : (
          <EmptyState title="Пользователи отсутствуют" description="Список пользователей появится после регистрации." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function roleLabel(role: string) {
  switch (role) {
    case 'creator':
      return 'Креатор';
    case 'brand':
      return 'Бренд';
    case 'agent':
      return 'Агент';
    case 'admin':
      return 'Администратор';
    default:
      return role;
  }
}

const adminUsersFallback: AdminUser[] = [
  { id: 'user-1', email: 'admin@ugc.local', full_name: 'Главный администратор', role: 'admin' },
  { id: 'user-2', email: 'brand@ugc.local', full_name: 'Brand Manager', role: 'brand' }
];
