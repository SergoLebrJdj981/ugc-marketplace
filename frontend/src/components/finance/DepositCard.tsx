'use client';

import { useState } from 'react';

import { Card, Input, Button } from '@/components/ui';
import { apiRequest } from '@/lib/api';
import { notify } from '@/lib/toast';

interface DepositCardProps {
  depositFee: number;
  onSuccess?: () => void;
}

export function DepositCard({ depositFee, onSuccess }: DepositCardProps) {
  const [amount, setAmount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDeposit = async () => {
    const normalisedAmount = amount.replace(',', '.');
    const value = Number(normalisedAmount);
    if (!Number.isFinite(value) || value <= 0) {
      notify.error('Введите сумму пополнения больше нуля');
      return;
    }
    setIsSubmitting(true);
    const response = await apiRequest('/api/payments/deposit', {
      method: 'POST',
      data: { amount: value },
      successMessage: 'Баланс успешно пополнен'
    });
    setIsSubmitting(false);
    if (!response.error) {
      setAmount('');
      onSuccess?.();
    }
  };

  return (
    <Card>
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Пополнить баланс</h3>
          <p className="mt-1 text-sm text-slate-500">
            Комиссия при депозите {Math.round(depositFee * 10000) / 100}% удерживается с суммы пополнения.
          </p>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <Input
            label="Сумма, ₽"
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            placeholder="Например, 15000"
          />
          <Button onClick={handleDeposit} loading={isSubmitting} className="sm:w-auto">
            Пополнить
          </Button>
        </div>
      </div>
    </Card>
  );
}
