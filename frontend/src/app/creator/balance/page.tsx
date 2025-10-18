'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';
import { WithdrawButton } from '@/components/finance/WithdrawButton';
import { TransactionsTable } from '@/components/finance/TransactionsTable';

interface CreatorBalanceResponse {
  available: number;
  pending: number;
  total_earned: number;
  last_payout: {
    amount: number;
    date: string;
    method: string;
  };
  transactions: Array<{
    id: string;
    type: string;
    amount: number;
    date: string | null;
    status: string;
    description?: string | null;
  }>;
  payouts: Array<{
    id: string;
    amount: number;
    status: string;
    created_at: string | null;
    updated_at: string | null;
    campaign_id?: string;
    payment_id?: string | null;
  }>;
  withdrawable: string[];
  retained_fee_total: number;
  platform_fee: number;
}

const sidebarLinks = [
  { href: '/creator', label: 'Обзор' },
  { href: '/creator/feed', label: 'Лента' },
  { href: '/creator/orders', label: 'Заказы' },
  { href: '/creator/balance', label: 'Баланс', exact: true },
  { href: '/creator/rating', label: 'Рейтинг' },
  { href: '/creator/learning', label: 'Обучение' }
];

export default function CreatorBalancePage() {
  const { data, isLoading, error, mutate } = useDashboardData<CreatorBalanceResponse>('/api/creator/balance', {
    fallbackData: creatorBalanceFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Баланс и выплаты"
        description="Проверяйте доступные средства и историю транзакций."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить баланс"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <p className="text-sm text-slate-500">Доступно к выводу</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {data.available.toLocaleString('ru-RU')} ₽
              </p>
              <div className="mt-4">
                <WithdrawButton payouts={data.payouts} onSuccess={() => mutate()} />
              </div>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Ожидает подтверждения</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {data.pending.toLocaleString('ru-RU')} ₽
              </p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Всего заработано</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {data.total_earned.toLocaleString('ru-RU')} ₽
              </p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Удержанная комиссия</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {data.retained_fee_total.toLocaleString('ru-RU')} ₽
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Текущая комиссия платформы {Math.round(data.platform_fee * 10000) / 100}%.
              </p>
            </Card>
          </div>
        ) : null}

        {data ? (
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <p className="text-sm text-slate-500">Последняя выплата</p>
              <p className="mt-2 text-slate-900">
                {data.last_payout.amount.toLocaleString('ru-RU')} ₽ ·{' '}
                {data.last_payout.date ? new Date(data.last_payout.date).toLocaleDateString('ru-RU') : '—'}
              </p>
              <p className="text-xs text-slate-500">Метод: {methodLabel(data.last_payout.method)}</p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Доступно к выводу</p>
              <p className="mt-2 text-slate-900">
                {data.withdrawable.length ? `${data.withdrawable.length} выплат(ы)` : 'нет доступных выплат'}
              </p>
            </Card>
          </div>
        ) : null}

        {data ? (
          <div className="mt-6">
            <TransactionsTable items={data.transactions} />
          </div>
        ) : (
          <EmptyState title="Транзакции отсутствуют" description="История выплат появится после поступления средств." />
        )}

        {data && data.payouts.length ? (
          <Card>
            <h3 className="text-base font-semibold text-slate-900">Выплаты</h3>
            <p className="mt-1 text-sm text-slate-500">
              Список последних выплат и их статусы.
            </p>
            <div className="mt-4">
              <Table
                columns={['ID', 'Кампания', 'Сумма', 'Статус', 'Создана']}
                data={data.payouts.map((payout) => [
                  payout.id,
                  payout.campaign_id ?? '—',
                  `${payout.amount.toLocaleString('ru-RU')} ₽`,
                  payout.status,
                  payout.created_at ? new Date(payout.created_at).toLocaleDateString('ru-RU') : '—'
                ])}
              />
            </div>
          </Card>
        ) : null}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function methodLabel(method: string) {
  switch (method) {
    case 'bank_transfer':
      return 'Банковский перевод';
    case 'card':
      return 'Банковская карта';
    default:
      return method;
  }
}

function transactionTypeLabel(type: string) {
  switch (type) {
    case 'payout':
      return 'Выплата';
    case 'escrow':
      return 'Эскроу';
    default:
      return type;
  }
}

const creatorBalanceFallback: CreatorBalanceResponse = {
  available: 62000,
  pending: 21000,
  total_earned: 398000,
  last_payout: {
    amount: 34000,
    date: new Date().toISOString(),
    method: 'bank_transfer'
  },
  transactions: [
    { id: 'txn-1', type: 'withdraw', amount: 34000, date: new Date().toISOString(), status: 'completed', description: null },
    { id: 'txn-2', type: 'release', amount: 21000, date: new Date().toISOString(), status: 'processed', description: null }
  ],
  payouts: [
    {
      id: 'payout-1',
      amount: 34000,
      status: 'withdrawn',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      campaign_id: 'cmp-demo',
      payment_id: 'pay-1'
    },
    {
      id: 'payout-2',
      amount: 21000,
      status: 'released',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      campaign_id: 'cmp-demo-2',
      payment_id: 'pay-2'
    }
  ],
  withdrawable: ['payout-2'],
  retained_fee_total: 12000,
  platform_fee: 0.1
};
