'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface BrandFinanceResponse {
  balance: number;
  frozen: number;
  spent_this_month: number;
  expected: number;
  transactions: Array<{
    id: string;
    type: string;
    amount: number;
    date: string;
    status: string;
  }>;
}

const sidebarLinks = [
  { href: '/brand', label: 'Кампании' },
  { href: '/brand/campaigns', label: 'Все кампании' },
  { href: '/brand/create', label: 'Создать кампанию' },
  { href: '/brand/analytics', label: 'Аналитика' },
  { href: '/brand/finance', label: 'Финансы', exact: true }
];

export default function BrandFinancePage() {
  const { data, isLoading, error, mutate } = useDashboardData<BrandFinanceResponse>('/api/brand/finance', {
    fallbackData: brandFinanceFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Финансы"
        description="Контролируйте бюджеты кампаний и следите за транзакциями."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить финансы"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <div className="grid gap-4 md:grid-cols-4">
            <SummaryCard label="Баланс" value={`${data.balance.toLocaleString('ru-RU')} ₽`} />
            <SummaryCard label="Заморожено" value={`${data.frozen.toLocaleString('ru-RU')} ₽`} />
            <SummaryCard label="Расходы (месяц)" value={`${data.spent_this_month.toLocaleString('ru-RU')} ₽`} />
            <SummaryCard label="Ожидается" value={`${data.expected.toLocaleString('ru-RU')} ₽`} />
          </div>
        ) : null}

        {data && data.transactions.length ? (
          <Table
            columns={['ID', 'Тип', 'Дата', 'Сумма', 'Статус']}
            data={data.transactions.map((txn) => [
              txn.id,
              financeTypeLabel(txn.type),
              new Date(txn.date).toLocaleDateString('ru-RU'),
              `${txn.amount.toLocaleString('ru-RU')} ₽`,
              txn.status
            ])}
          />
        ) : (
          <EmptyState title="Нет транзакций" description="История появится после проведения платежей." />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold text-slate-900">{value}</p>
    </Card>
  );
}

function financeTypeLabel(type: string) {
  switch (type) {
    case 'payout':
      return 'Выплата';
    case 'escrow':
      return 'Эскроу';
    default:
      return type;
  }
}

const brandFinanceFallback: BrandFinanceResponse = {
  balance: 245000,
  frozen: 78000,
  spent_this_month: 96000,
  expected: 54000,
  transactions: [
    { id: 'txn-201', type: 'payout', amount: 42000, date: new Date().toISOString(), status: 'completed' },
    { id: 'txn-202', type: 'escrow', amount: 36000, date: new Date().toISOString(), status: 'processing' }
  ]
};
