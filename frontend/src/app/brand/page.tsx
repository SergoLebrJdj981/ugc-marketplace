'use client';

import { useEffect } from 'react';

import { Button, EmptyState, Table } from '@/components/ui';
import { useAuth } from '@/context';
import { useCampaignStore } from '@/store';

export default function BrandDashboard() {
  const { user } = useAuth();
  const { campaigns, setCampaigns, addCampaign } = useCampaignStore();

  useEffect(() => {
    setCampaigns([
      { id: 'camp-1', title: 'Запуск коллекции Q4', status: 'active', budget: 150000 },
      { id: 'camp-2', title: 'UGC для TikTok', status: 'draft', budget: 90000 }
    ]);
  }, [setCampaigns]);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-slate-900">Привет, {user?.full_name ?? user?.email}</h1>
        <p className="text-sm text-slate-600">Управляйте кампаниями и следите за аналитикой в реальном времени.</p>
      </header>

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
    </main>
  );
}
