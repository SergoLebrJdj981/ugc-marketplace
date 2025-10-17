'use client';

import { useEffect } from 'react';

import { Button, EmptyState, Table } from '@/components/ui';
import { useAuth } from '@/context';
import { useCampaignStore, useOrderStore } from '@/store';

export default function CreatorDashboard() {
  const { user } = useAuth();
  const { orders, setOrders } = useOrderStore();
  const { campaigns, setCampaigns } = useCampaignStore();

  useEffect(() => {
    setOrders([
      { id: 'order-1', status: 'in_progress', amount: 45000 },
      { id: 'order-2', status: 'approved', amount: 32000 }
    ]);
    setCampaigns([
      { id: 'cmp-1', title: 'UGC для бренда X', status: 'active', budget: 75000 }
    ]);
  }, [setCampaigns, setOrders]);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-slate-900">Привет, {user?.full_name ?? user?.email}</h1>
        <p className="text-sm text-slate-600">Следите за заказами, балансом и рейтингом качества.</p>
      </header>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Активные заказы</h2>
          <Button variant="secondary">Загрузить результаты</Button>
        </div>
        {orders.length ? (
          <Table
            columns={['ID заказа', 'Статус', 'Сумма']}
            data={orders.map((order) => [order.id, order.status, `${order.amount.toLocaleString('ru-RU')} ₽`])}
          />
        ) : (
          <EmptyState
            title="Заказы пока отсутствуют"
            description="Откликайтесь на кампании и отслеживайте статус исполнения заказа здесь."
          />
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Избранные кампании</h2>
        {campaigns.length ? (
          <Table
            columns={['Кампания', 'Статус', 'Бюджет']}
            data={campaigns.map((campaign) => [campaign.title, campaign.status, `${campaign.budget.toLocaleString('ru-RU')} ₽`])}
          />
        ) : (
          <EmptyState
            title="Ещё ничего не выбрано"
            description="Найдите кампанию бренда и отправьте предложение, чтобы попасть в список."
          />
        )}
      </section>
    </main>
  );
}
