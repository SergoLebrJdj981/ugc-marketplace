'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

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
  { href: '/brand', label: 'Кампании' },
  { href: '/brand/campaigns', label: 'Все кампании' },
  { href: '/brand/create', label: 'Создать кампанию' },
  { href: '/brand/analytics', label: 'Аналитика', exact: true },
  { href: '/brand/finance', label: 'Финансы' }
];

export default function BrandAnalyticsPage() {
  const { data, isLoading, error, mutate } = useDashboardData<BrandAnalyticsResponse>('/api/brand/analytics', {
    fallbackData: brandAnalyticsFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Аналитика кампаний"
        description="Следите за ключевыми метриками и сравнивайте эффективность креаторов."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить аналитику"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <>
            <div className="grid gap-4 sm:grid-cols-4">
              <MetricCard label="CTR" value={`${(data.metrics.ctr * 100).toFixed(1)}%`} />
              <MetricCard label="CPM" value={`${data.metrics.cpm.toLocaleString('ru-RU')} ₽`} />
              <MetricCard label="ROI" value={`${data.metrics.roi.toFixed(1)}x`} />
              <MetricCard label="Охват" value={data.metrics.reach.toLocaleString('ru-RU')} />
            </div>
            <Table
              columns={['Креатор', 'Заказы', 'Эффективность']}
              data={(data.top_creators ?? []).map((creator) => [
                creator.name,
                creator.orders,
                `${Math.round(creator.performance * 100)}%`
              ])}
            />
            <Table
              columns={['Кампания', 'Метрика', 'Период', 'Значение']}
              data={(data.recent ?? []).map((item) => [
                item.campaign_id,
                item.metric,
                item.period,
                item.value.toLocaleString('ru-RU')
              ])}
            />
          </>
        ) : (
          <EmptyState title="Нет данных" description="Аналитика появится после запуска кампаний." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold text-slate-900">{value}</p>
    </Card>
  );
}

const brandAnalyticsFallback: BrandAnalyticsResponse = {
  metrics: {
    ctr: 0.041,
    cpm: 290,
    roi: 2.1,
    reach: 1240000
  },
  top_creators: [
    { id: 'creator-1', name: 'Анна Петрова', orders: 8, performance: 0.91 },
    { id: 'creator-2', name: 'Иван Смирнов', orders: 5, performance: 0.87 }
  ],
  recent: [
    { campaign_id: 'camp-1', metric: 'views', value: 320000, period: '7d' },
    { campaign_id: 'camp-1', metric: 'conversions', value: 8200, period: '7d' }
  ]
};
