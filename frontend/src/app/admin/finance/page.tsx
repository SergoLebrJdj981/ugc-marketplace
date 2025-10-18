'use client';

import { useEffect, useState } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Input, Button } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';
import { TransactionsTable } from '@/components/finance/TransactionsTable';
import { apiRequest } from '@/lib/api';
import { notify } from '@/lib/toast';

interface AdminFinanceResponse {
  metrics: {
    total_payouts: number;
    escrow_balance: number;
    processing: number;
    fees_collected: number;
    platform_fee: number;
    platform_fee_deposit: number;
    platform_fee_payout: number;
  };
  recent: Array<{
    id: string;
    type: string;
    amount: number;
    status: string;
    date: string;
  }>;
}

interface PlatformFeeSettingsItemResponse {
  value: number;
  description?: string | null;
  updated_at?: string | null;
}

interface PlatformFeeSettingsResponse {
  platform_fee: PlatformFeeSettingsItemResponse;
  platform_fee_deposit: PlatformFeeSettingsItemResponse;
  platform_fee_payout: PlatformFeeSettingsItemResponse;
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
  const [feeValue, setFeeValue] = useState('0.1');
  const [depositFeeValue, setDepositFeeValue] = useState('0.1');
  const [payoutFeeValue, setPayoutFeeValue] = useState('0.1');
  const [isSaving, setIsSaving] = useState(false);
  const [isSavingDeposit, setIsSavingDeposit] = useState(false);
  const [isSavingPayout, setIsSavingPayout] = useState(false);

  const fetchSettings = async () => {
    const response = await apiRequest<PlatformFeeSettingsResponse>('/api/admin/settings', {
      method: 'GET',
      showErrorToast: false
    });
    if (!response.error && response.data) {
      setFeeValue(String(response.data.platform_fee.value));
      setDepositFeeValue(String(response.data.platform_fee_deposit.value));
      setPayoutFeeValue(String(response.data.platform_fee_payout.value));
    }
  };

  useEffect(() => {
    if (data?.metrics.platform_fee !== undefined) {
      setFeeValue(String(data.metrics.platform_fee));
    }
    if (data?.metrics.platform_fee_deposit !== undefined) {
      setDepositFeeValue(String(data.metrics.platform_fee_deposit));
    }
    if (data?.metrics.platform_fee_payout !== undefined) {
      setPayoutFeeValue(String(data.metrics.platform_fee_payout));
    }
  }, [data?.metrics.platform_fee, data?.metrics.platform_fee_deposit, data?.metrics.platform_fee_payout]);

  useEffect(() => {
    void fetchSettings();
  }, []);

  const handleFeeSave = async () => {
    const normalised = feeValue.replace(',', '.');
    const value = Number(normalised);
    if (!Number.isFinite(value) || value <= 0 || value >= 1) {
      notify.error('Комиссия должна быть числом от 0 до 1 (пример: 0.12)');
      return;
    }
    setIsSaving(true);
    const response = await apiRequest('/api/admin/settings/platform_fee', {
      method: 'PATCH',
      data: { value },
      successMessage: 'Комиссия платформы обновлена'
    });
    setIsSaving(false);
    if (!response.error) {
      mutate();
      fetchSettings();
    }
  };

  const handleDepositFeeSave = async () => {
    const normalised = depositFeeValue.replace(',', '.');
    const value = Number(normalised);
    if (!Number.isFinite(value) || value <= 0 || value >= 1) {
      notify.error('Комиссия должна быть числом от 0 до 1 (пример: 0.12)');
      return;
    }
    setIsSavingDeposit(true);
    const response = await apiRequest('/api/admin/settings/platform_fee_deposit', {
      method: 'PATCH',
      data: { value },
      successMessage: 'Комиссия обновлена'
    });
    setIsSavingDeposit(false);
    if (!response.error) {
      mutate();
      fetchSettings();
    }
  };

  const handlePayoutFeeSave = async () => {
    const normalised = payoutFeeValue.replace(',', '.');
    const value = Number(normalised);
    if (!Number.isFinite(value) || value <= 0 || value >= 1) {
      notify.error('Комиссия должна быть числом от 0 до 1 (пример: 0.12)');
      return;
    }
    setIsSavingPayout(true);
    const response = await apiRequest('/api/admin/settings/platform_fee_payout', {
      method: 'PATCH',
      data: { value },
      successMessage: 'Комиссия обновлена'
    });
    setIsSavingPayout(false);
    if (!response.error) {
      mutate();
      fetchSettings();
    }
  };

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
          <>
            <div className="grid gap-4 md:grid-cols-4">
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
              <Card>
                <p className="text-xs text-slate-500">Собрано комиссии</p>
                <p className="mt-2 text-xl font-semibold text-slate-900">
                  {data.metrics.fees_collected.toLocaleString('ru-RU')} ₽
                </p>
              </Card>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-2">
              <Card>
                <h3 className="text-base font-semibold text-slate-900">Комиссия платформы</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Текущие ставки: депозиты — {Math.round(data.metrics.platform_fee_deposit * 10000) / 100}% · выплаты —{' '}
                  {Math.round(data.metrics.platform_fee_payout * 10000) / 100}%.
                </p>
                <div className="mt-4 flex flex-col gap-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <Input
                      label="Базовая комиссия (0-1)"
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={feeValue}
                      onChange={(event) => setFeeValue(event.target.value)}
                    />
                    <Button onClick={handleFeeSave} loading={isSaving} className="sm:w-auto">
                      Сохранить
                    </Button>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <Input
                      label="Комиссия при депозите (0-1)"
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={depositFeeValue}
                      onChange={(event) => setDepositFeeValue(event.target.value)}
                    />
                    <Button onClick={handleDepositFeeSave} loading={isSavingDeposit} className="sm:w-auto">
                      Сохранить
                    </Button>
                  </div>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <Input
                      label="Комиссия при выплате (0-1)"
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={payoutFeeValue}
                      onChange={(event) => setPayoutFeeValue(event.target.value)}
                    />
                    <Button onClick={handlePayoutFeeSave} loading={isSavingPayout} className="sm:w-auto">
                      Сохранить
                    </Button>
                  </div>
                </div>
              </Card>
            </div>

            <div className="mt-6">
              {data.recent.length ? (
                <TransactionsTable items={data.recent} />
              ) : (
                <EmptyState title="Нет транзакций" description="История появится после проведения операций." />
              )}
            </div>
          </>
        ) : null}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const adminFinanceFallback: AdminFinanceResponse = {
  metrics: {
    total_payouts: 420000,
    escrow_balance: 520000,
    processing: 74000,
    fees_collected: 120000,
    platform_fee: 0.1
  },
  recent: [
    { id: 'adm-txn-1', type: 'payout', amount: 42000, status: 'completed', date: new Date().toISOString() },
    { id: 'adm-txn-2', type: 'release', amount: 18000, status: 'processed', date: new Date().toISOString() }
  ]
};
