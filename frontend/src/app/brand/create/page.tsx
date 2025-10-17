'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Button, Card, EmptyState, Input, Loader } from '@/components/ui';
import { useAuth } from '@/context';
import { apiRequest } from '@/lib/api';

interface CampaignFormValues {
  title: string;
  goals: string;
  budget: number;
  brief: string;
}

const sidebarLinks = [
  { href: '/brand', label: 'Кампании' },
  { href: '/brand/campaigns', label: 'Все кампании' },
  { href: '/brand/create', label: 'Создать кампанию', exact: true },
  { href: '/brand/analytics', label: 'Аналитика' },
  { href: '/brand/finance', label: 'Финансы' }
];

export default function BrandCreateCampaignPage() {
  const { accessToken } = useAuth();
  const { register, handleSubmit, reset } = useForm<CampaignFormValues>({
    defaultValues: {
      title: '',
      goals: '',
      budget: 50000,
      brief: ''
    }
  });
  const [isSubmitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onSubmit = handleSubmit(async (values) => {
    if (!accessToken) return;
    setSubmitting(true);
    setError(null);
    setSuccess(false);

    const response = await apiRequest('/api/brand/campaigns', {
      method: 'POST',
      token: accessToken,
      data: values,
      successMessage: 'Кампания создана'
    });

    if (response.error) {
      setError(response.message ?? 'Не удалось создать кампанию');
    } else {
      setSuccess(true);
      reset();
    }
    setSubmitting(false);
  });

  return (
    <ProtectedRoute allowedRoles={['brand']}>
      <LayoutShell
        title="Создание кампании"
        description="Укажите цели, бюджет и подготовьте техническое задание."
        sidebarLinks={sidebarLinks}
      >
        {isSubmitting ? <Loader /> : null}
        {error ? <EmptyState title="Ошибка" description={error} /> : null}
        {success ? <Card>Кампания сохранена как черновик. Перейдите в раздел «Все кампании», чтобы продолжить.</Card> : null}

        <form onSubmit={onSubmit} className="grid gap-6 md:grid-cols-2">
          <Card>
            <label className="block text-sm font-medium text-slate-700">
              Название кампании
              <Input placeholder="Например, Holiday drop 2025" {...register('title', { required: true })} />
            </label>
            <label className="mt-4 block text-sm font-medium text-slate-700">
              Цели
              <Input placeholder="Повышение узнаваемости, продажи..." {...register('goals', { required: true })} />
            </label>
            <label className="mt-4 block text-sm font-medium text-slate-700">
              Бюджет (₽)
              <Input type="number" min={0} step={1000} {...register('budget', { valueAsNumber: true })} />
            </label>
          </Card>
          <Card>
            <label className="block text-sm font-medium text-slate-700">
              Техническое задание
              <textarea
                className="mt-2 h-48 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none"
                placeholder="Опишите формат контента, сроки, ключевые сообщения."
                {...register('brief')}
              />
            </label>
            <div className="mt-6 flex justify-end">
              <Button type="submit" disabled={isSubmitting}>
                Сохранить кампанию
              </Button>
            </div>
          </Card>
        </form>
      </LayoutShell>
    </ProtectedRoute>
  );
}
