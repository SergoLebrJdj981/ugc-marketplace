'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

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
    date: string;
    status: string;
  }>;
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
              <p className="text-sm text-slate-500">Последняя выплата</p>
              <p className="mt-2 text-slate-900">
                {data.last_payout.amount.toLocaleString('ru-RU')} ₽ ·{' '}
                {new Date(data.last_payout.date).toLocaleDateString('ru-RU')}
              </p>
              <p className="text-xs text-slate-500">Метод: {methodLabel(data.last_payout.method)}</p>
            </Card>
          </div>
        ) : null}

        {data && data.transactions.length ? (
          <Table
            columns={['ID', 'Тип', 'Дата', 'Сумма', 'Статус']}
            data={data.transactions.map((txn) => [
              txn.id,
              transactionTypeLabel(txn.type),
              new Date(txn.date).toLocaleDateString('ru-RU'),
              `${txn.amount.toLocaleString('ru-RU')} ₽`,
              txn.status
            ])}
          />
        ) : (
          <EmptyState title="Транзакции отсутствуют" description="История выплат появится после поступления средств." />
        )}
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
    { id: 'txn-1', type: 'payout', amount: 34000, date: new Date().toISOString(), status: 'completed' },
    { id: 'txn-2', type: 'escrow', amount: 21000, date: new Date().toISOString(), status: 'pending' }
  ]
};
