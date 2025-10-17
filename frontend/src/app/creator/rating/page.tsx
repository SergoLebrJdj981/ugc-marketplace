'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Card, EmptyState, Loader, Progress } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface CreatorRatingResponse {
  score: number;
  position: number;
  total_creators: number;
  metrics: {
    completion_rate: number;
    avg_review_time: number;
    dispute_rate: number;
  };
  achievements: Array<{
    id: string;
    title: string;
    earned_at: string;
  }>;
}

const sidebarLinks = [
  { href: '/creator', label: 'Обзор' },
  { href: '/creator/feed', label: 'Лента' },
  { href: '/creator/orders', label: 'Заказы' },
  { href: '/creator/balance', label: 'Баланс' },
  { href: '/creator/rating', label: 'Рейтинг', exact: true },
  { href: '/creator/learning', label: 'Обучение' }
];

export default function CreatorRatingPage() {
  const { data, isLoading, error, mutate } = useDashboardData<CreatorRatingResponse>('/api/creator/rating', {
    fallbackData: creatorRatingFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Рейтинг и метрики"
        description="Анализируйте показатели вовлечённости и улучшайте позицию в общем рейтинге."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить рейтинг"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data ? (
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <p className="text-sm text-slate-500">Общий рейтинг</p>
              <p className="mt-2 text-5xl font-semibold text-slate-900">{data.score.toFixed(1)}</p>
              <p className="text-xs text-slate-500">Позиция в рейтинге: {data.position} из {data.total_creators}</p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Completion rate</p>
              <Progress value={Math.round((data.metrics.completion_rate ?? 0) * 100)} />
              <p className="mt-2 text-sm text-slate-500">
                {Math.round((data.metrics.completion_rate ?? 0) * 100)}% заказов завершено
              </p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Среднее время ревью</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {data.metrics.avg_review_time} часов
              </p>
              <p className="text-xs text-slate-500">Доля споров: {(data.metrics.dispute_rate * 100).toFixed(1)}%</p>
            </Card>
          </div>
        ) : null}

        {data && data.achievements.length ? (
          <div className="grid gap-4 md:grid-cols-2">
            {data.achievements.map((ach) => (
              <Card key={ach.id}>
                <p className="text-sm text-slate-500">Достижение</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">{ach.title}</p>
                <p className="text-xs text-slate-500">
                  Получено: {new Date(ach.earned_at).toLocaleDateString('ru-RU')}
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            title="Достижения отсутствуют"
            description="Выполняйте кампании без задержек и повышайте рейтинг, чтобы открыть награды."
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

const creatorRatingFallback: CreatorRatingResponse = {
  score: 4.6,
  position: 32,
  total_creators: 510,
  metrics: {
    completion_rate: 0.94,
    avg_review_time: 20,
    dispute_rate: 0.02
  },
  achievements: [
    { id: 'ach-1', title: 'PRO+ автор', earned_at: new Date().toISOString() },
    { id: 'ach-2', title: '50 успешных кампаний', earned_at: new Date().toISOString() }
  ]
};
