'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AdminCampaignsResponse {
  items: Array<{
    id: string;
    title: string;
    brand: string;
    status: string;
    budget: number;
    created_at: string;
  }>;
}

const sidebarLinks = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/users', label: 'Пользователи' },
  { href: '/admin/campaigns', label: 'Кампании', exact: true },
  { href: '/admin/finance', label: 'Финансы' },
  { href: '/admin/analytics', label: 'Аналитика' }
];

export default function AdminCampaignsPage() {
  const { data, isLoading, error, mutate } = useDashboardData<AdminCampaignsResponse>('/api/admin/campaigns', {
    fallbackData: adminCampaignsFallback,
    revalidateOnFocus: true
  });

  const items = data?.items ?? [];

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Кампании"
        description="Просматривайте кампании брендов и текущие бюджеты."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить кампании"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {items.length ? (
          <Table
            columns={['ID', 'Название', 'Бренд', 'Статус', 'Бюджет', 'Создана']}
            data={items.map((campaign) => [
              campaign.id,
              campaign.title,
              campaign.brand,
              campaign.status,
              `${campaign.budget.toLocaleString('ru-RU')} ₽`,
              new Date(campaign.created_at).toLocaleDateString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState title="Кампаний нет" description="Список будет заполнен после создания кампаний брендами." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const adminCampaignsFallback: AdminCampaignsResponse = {
  items: [
    {
      id: 'cmp-virtual-1',
      title: 'Demo Campaign',
      brand: 'Demo Brand',
      status: 'draft',
      budget: 50000,
      created_at: new Date().toISOString()
    }
  ]
};
