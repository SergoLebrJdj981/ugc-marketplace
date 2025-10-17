'use client';

import Link from 'next/link';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface BrandCampaignsResponse {
  items: Array<{
    id: string;
    title: string;
    status: string;
    budget: number;
    applications?: number;
  }>;
}

const sidebarLinks = [
  { href: '/brand', label: 'Кампании' },
  { href: '/brand/campaigns', label: 'Все кампании', exact: true },
  { href: '/brand/create', label: 'Создать кампанию' },
  { href: '/brand/analytics', label: 'Аналитика' },
  { href: '/brand/finance', label: 'Финансы' }
];

export default function BrandCampaignsPage() {
  const { data, isLoading, error, mutate } = useDashboardData<BrandCampaignsResponse>('/api/brand/campaigns', {
    fallbackData: brandCampaignsFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Кампании бренда"
        description="Управляйте активными, черновыми и завершёнными кампаниями."
        sidebarLinks={sidebarLinks}
        actions={
          <Link href="/brand/create">
            <Button variant="primary">Новая кампания</Button>
          </Link>
        }
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

        {data && data.items.length ? (
          <Table
            columns={['Название', 'Статус', 'Бюджет', 'Отклики']}
            data={data.items.map((campaign) => [
              campaign.title,
              <Badge key={`${campaign.id}-status`} variant={campaign.status === 'active' ? 'success' : 'warning'}>
                {campaign.status === 'active' ? 'Активна' : 'Черновик'}
              </Badge>,
              `${campaign.budget.toLocaleString('ru-RU')} ₽`,
              campaign.applications ?? 0
            ])}
          />
        ) : (
          <EmptyState
            title="Кампаний нет"
            description="Создайте кампанию, чтобы начать сотрудничество с креаторами."
            actionLabel="Создать кампанию"
            onAction={() => window.location.assign('/brand/create')}
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const brandCampaignsFallback: BrandCampaignsResponse = {
  items: [
    { id: 'camp-1', title: 'Запуск коллекции Q4', status: 'active', budget: 150000, applications: 24 },
    { id: 'camp-2', title: 'UGC для TikTok', status: 'draft', budget: 90000, applications: 0 }
  ]
};
