'use client';

import Link from 'next/link';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, Button, Card, EmptyState, ErrorState, Loader, Table } from '@/components/ui';
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

interface BrandAnalyticsResponse {
  metrics: {
    ctr: number;
    cpm: number;
    roi: number;
    reach: number;
  };
  top_creators: Array<{
    id: string;
    name: string;
    orders: number;
    performance: number;
  }>;
  recent: Array<{
    campaign_id: string;
    metric: string;
    value: number;
    period: string;
  }>;
}

const sidebarLinks = [
  { href: '/brand', label: 'Кампании', exact: true },
  { href: '/brand/campaigns', label: 'Все кампании' },
  { href: '/brand/create', label: 'Создать кампанию' },
  { href: '/brand/analytics', label: 'Аналитика' },
  { href: '/brand/finance', label: 'Финансы' }
];

export default function BrandDashboard() {
  const {
    data: campaignsData,
    isLoading: campaignsLoading,
    error: campaignsError
  } = useDashboardData<BrandCampaignsResponse>('/api/brand/campaigns', {
    fallbackData: brandCampaignsFallback
  });
  const {
    data: analyticsData,
    isLoading: analyticsLoading,
    error: analyticsError
  } = useDashboardData<BrandAnalyticsResponse>('/api/brand/analytics', {
    fallbackData: brandAnalyticsFallback
  });

  const isLoading = campaignsLoading || analyticsLoading;
  const hasError = Boolean(campaignsError || analyticsError);

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Панель бренда"
        description="Управляйте кампаниями, аналитикой и финансовыми потоками."
        sidebarLinks={sidebarLinks}
        actions={
          <Link href="/brand/create">
            <Button variant="primary">Новая кампания</Button>
          </Link>
        }
      >
        {isLoading ? <Loader /> : null}
        {hasError ? (
          <ErrorState
            message="Не удалось полностью загрузить данные. Показаны сохранённые значения."
            onRetry={() => window.location.reload()}
          />
        ) : null}

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Активные кампании</h2>
            <Link href="/brand/campaigns">
              <Button variant="secondary">Все кампании</Button>
            </Link>
          </div>
          {campaignsData && campaignsData.items.length ? (
            <Table
              columns={['Название', 'Статус', 'Бюджет', 'Отклики']}
              data={campaignsData.items.map((campaign) => [
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
              title="Добавьте первую кампанию"
              description="Создайте кампанию и приглашайте креаторов к сотрудничеству."
              actionLabel="Новая кампания"
              onAction={() => window.location.assign('/brand/create')}
            />
          )}
        </section>

        {analyticsData ? (
          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900">Ключевые метрики</h2>
            <div className="grid gap-4 sm:grid-cols-4">
              <MetricCard title="CTR" value={`${(analyticsData.metrics.ctr * 100).toFixed(1)}%`} />
              <MetricCard title="CPM" value={`${analyticsData.metrics.cpm.toLocaleString('ru-RU')} ₽`} />
              <MetricCard title="ROI" value={`${analyticsData.metrics.roi.toFixed(1)}x`} />
              <MetricCard title="Охват" value={analyticsData.metrics.reach.toLocaleString('ru-RU')} />
            </div>
          </section>
        ) : null}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
    </Card>
  );
}

const brandCampaignsFallback: BrandCampaignsResponse = {
  items: [
    { id: 'camp-1', title: 'Запуск коллекции Q4', status: 'active', budget: 150000, applications: 24 },
    { id: 'camp-2', title: 'UGC для TikTok', status: 'draft', budget: 90000, applications: 0 }
  ]
};

const brandAnalyticsFallback: BrandAnalyticsResponse = {
  metrics: {
    ctr: 0.041,
    cpm: 290,
    roi: 2.1,
    reach: 1240000
  },
  top_creators: [],
  recent: []
};
