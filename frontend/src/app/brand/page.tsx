'use client';

import { useEffect } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Button, EmptyState, Table } from '@/components/ui';
import { useCampaignStore } from '@/store';

const sidebarLinks = [
  { href: '/brand', label: 'Кампании', exact: true },
  { href: '/brand/analytics', label: 'Аналитика' },
  { href: '/brand/finance', label: 'Финансы' }
];

export default function BrandDashboard() {
  const { campaigns, setCampaigns, addCampaign } = useCampaignStore();

  useEffect(() => {
    setCampaigns([
      { id: 'camp-1', title: 'Запуск коллекции Q4', status: 'active', budget: 150000 },
      { id: 'camp-2', title: 'UGC для TikTok', status: 'draft', budget: 90000 }
    ]);
  }, [setCampaigns]);

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Панель бренда"
        description="Управляйте кампаниями, анализируйте результаты и контролируйте бюджет."
        sidebarLinks={sidebarLinks}
      >
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Ваши кампании</h2>
            <Button
              onClick={() =>
                addCampaign({ id: crypto.randomUUID(), title: 'Новая кампания', status: 'draft', budget: 50000 })
              }
            >
              Создать кампанию
            </Button>
          </div>
          {campaigns.length ? (
            <Table
              columns={['Название', 'Статус', 'Бюджет']}
              data={campaigns.map((campaign) => [campaign.title, campaign.status, `${campaign.budget.toLocaleString('ru-RU')} ₽`])}
            />
          ) : (
            <EmptyState
              title="Добавьте первую кампанию"
              description="Создайте кампанию и приглашайте креаторов к сотрудничеству."
              actionLabel="Новая кампания"
              onAction={() =>
                addCampaign({ id: crypto.randomUUID(), title: 'Новая кампания', status: 'draft', budget: 75000 })
              }
            />
          )}
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-slate-900">Финансовые метрики</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              { label: 'Общий бюджет', value: '240 000 ₽' },
              { label: 'Активные кампании', value: '2' },
              { label: 'Исполненные заказы', value: '5' }
            ].map((metric) => (
              <div key={metric.label} className="rounded-xl bg-white p-5 text-left shadow-sm">
                <p className="text-sm text-slate-500">{metric.label}</p>
                <p className="mt-2 text-2xl font-semibold text-slate-900">{metric.value}</p>
              </div>
            ))}
          </div>
        </section>
      </LayoutShell>
    </ProtectedRoute>
  );
}
