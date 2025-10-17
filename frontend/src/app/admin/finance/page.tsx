'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface AdminFinanceResponse {
  metrics: {
    total_payouts: number;
    escrow_balance: number;
    processing: number;
  };
  recent: Array<{
    id: string;
    type: string;
    amount: number;
    status: string;
    date: string;
  }>;
}

const sidebarLinks = [
  { href: '/admin', label: 'Обзор' },
  { href: '/admin/users', label: 'Пользователи' },
  { href: '/admin/campaigns', label: 'Кампании' },
  { href: '/admin/finance', label: 'Финансы', exact: true },
  { href: '/admin/analytics', label: 'Аналитика' }
];

export default function AdminFinancePage() {
  const { data, isLoading, error, mutate } = useDashboardData<AdminFinanceResponse>('/api/admin/finance', {
    fallbackData: adminFinanceFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Финансы платформы"
        description="Контролируйте суммы выплат, баланс эскроу и ожидающие транзакции."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить финансовые данные"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <p className="text-xs text-slate-500">Выплачено всего</p>
              <p className="mt-2 text-xl font-semibold text-slate-900">
                {data.metrics.total_payouts.toLocaleString('ru-RU')} ₽
              </p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500">Баланс эскроу</p>
              <p className="mt-2 text-xl font-semibold text-slate-900">
                {data.metrics.escrow_balance.toLocaleString('ru-RU')} ₽
              </p>
            </Card>
            <Card>
              <p className="text-xs text-slate-500">В обработке</p>
              <p className="mt-2 text-xl font-semibold text-slate-900">
                {data.metrics.processing.toLocaleString('ru-RU')} ₽
              </p>
            </Card>
          </div>
        ) : null}

        {data && data.recent.length ? (
          <Table
            columns={['ID', 'Тип', 'Сумма', 'Статус', 'Дата']}
            data={data.recent.map((txn) => [
              txn.id,
              transactionTypeLabel(txn.type),
              `${txn.amount.toLocaleString('ru-RU')} ₽`,
              txn.status,
              new Date(txn.date).toLocaleDateString('ru-RU')
            ])}
          />
        ) : (
          <EmptyState title="Нет транзакций" description="История появится после проведения операций." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
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

const adminFinanceFallback: AdminFinanceResponse = {
  metrics: {
    total_payouts: 420000,
    escrow_balance: 520000,
    processing: 74000
  },
  recent: [
    { id: 'adm-txn-1', type: 'payout', amount: 42000, status: 'completed', date: new Date().toISOString() },
    { id: 'adm-txn-2', type: 'escrow', amount: 18000, status: 'pending', date: new Date().toISOString() }
  ]
};
