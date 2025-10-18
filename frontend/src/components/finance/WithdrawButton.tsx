'use client';

import { useMemo, useState } from 'react';

import { Button, Modal } from '@/components/ui';
import { apiRequest } from '@/lib/api';
import { notify } from '@/lib/toast';

interface PayoutItem {
  id: string;
  amount: number;
  status: string;
  created_at?: string | null;
  campaign_id?: string;
}

interface WithdrawButtonProps {
  payouts: PayoutItem[];
  onSuccess?: () => void;
}

export function WithdrawButton({ payouts, onSuccess }: WithdrawButtonProps) {
  const withdrawable = useMemo(() => payouts.filter((payout) => payout.status === 'released'), [payouts]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selected, setSelected] = useState<string | null>(withdrawable[0]?.id ?? null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const openModal = () => {
    if (!withdrawable.length) {
      notify.info('Нет выплат, доступных к выводу');
      return;
    }
    setSelected(withdrawable[0]?.id ?? null);
    setIsModalOpen(true);
  };

  const handleWithdraw = async () => {
    if (!selected) {
      notify.error('Выберите выплату для вывода');
      return;
    }
    setIsSubmitting(true);
    const response = await apiRequest('/api/payouts/withdraw', {
      method: 'POST',
      data: { payout_id: selected },
      successMessage: 'Заявка на вывод средств отправлена'
    });
    setIsSubmitting(false);
    if (!response.error) {
      setIsModalOpen(false);
      onSuccess?.();
    }
  };

  return (
    <>
      <Button onClick={openModal} variant="secondary" disabled={!withdrawable.length}>
        Вывести средства
      </Button>
      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Доступные выплаты"
        primaryAction={{ label: 'Вывести', onClick: handleWithdraw, loading: isSubmitting }}
      >
        {withdrawable.length ? (
          <div className="flex flex-col gap-3">
            {withdrawable.map((payout) => (
              <label key={payout.id} className="flex items-center justify-between gap-4 rounded-md border border-slate-200 px-4 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {payout.amount.toLocaleString('ru-RU')} ₽
                  </p>
                  <p className="text-xs text-slate-500">
                    {payout.created_at ? new Date(payout.created_at).toLocaleDateString('ru-RU') : 'Дата неизвестна'}
                    {payout.campaign_id ? ` · Кампания ${payout.campaign_id}` : ''}
                  </p>
                </div>
                <input
                  type="radio"
                  name="payout"
                  value={payout.id}
                  checked={selected === payout.id}
                  onChange={() => setSelected(payout.id)}
                  className="h-4 w-4"
                />
              </label>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Нет доступных выплат.</p>
        )}
      </Modal>
    </>
  );
}
