'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';
import { DepositCard } from '@/components/finance/DepositCard';
import { TransactionsTable } from '@/components/finance/TransactionsTable';

interface BrandFinanceResponse {
  balance: number;
  frozen: number;
  spent_this_month: number;
  expected: number;
  transactions: Array<{
    id: string;
    type: string;
    amount: number;
    date: string | null;
    status: string;
    description?: string | null;
  }>;
  platform_fee: number;
  platform_fee_deposit: number;
  platform_fee_payout: number;
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
          <>
            <div className="grid gap-4 md:grid-cols-4">
              <SummaryCard label="Баланс" value={`${data.balance.toLocaleString('ru-RU')} ₽`} />
              <SummaryCard label="Заморожено" value={`${data.frozen.toLocaleString('ru-RU')} ₽`} />
              <SummaryCard label="Расходы (месяц)" value={`${data.spent_this_month.toLocaleString('ru-RU')} ₽`} />
              <SummaryCard label="Ожидается" value={`${data.expected.toLocaleString('ru-RU')} ₽`} />
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <DepositCard depositFee={data.platform_fee_deposit} onSuccess={() => mutate()} />
              <Card>
                <h3 className="text-base font-semibold text-slate-900">Финансовые условия</h3>
                <p className="mt-2 text-sm text-slate-500">
                  Базовая комиссия: {Math.round(data.platform_fee * 10000) / 100}%.
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Комиссия при депозите: {Math.round(data.platform_fee_deposit * 10000) / 100}%.
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Комиссия при выплате: {Math.round(data.platform_fee_payout * 10000) / 100}%.
                </p>
              </Card>
            </div>
          </>
        ) : null}

        {data ? (
          <div className="mt-6">
            <TransactionsTable items={data.transactions} />
          </div>
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

const brandFinanceFallback: BrandFinanceResponse = {
  balance: 245000,
  frozen: 78000,
  spent_this_month: 96000,
  expected: 54000,
  transactions: [
    { id: 'txn-201', type: 'payout', amount: 42000, date: new Date().toISOString(), status: 'completed', description: null },
    { id: 'txn-202', type: 'deposit', amount: 36000, date: new Date().toISOString(), status: 'reserved', description: null }
  ],
  platform_fee: 0.1,
  platform_fee_deposit: 0.1,
  platform_fee_payout: 0.1
};
