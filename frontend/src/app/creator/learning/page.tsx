'use client';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Badge, EmptyState, Loader, Table } from '@/components/ui';
import { useDashboardData } from '@/lib/useDashboardData';

interface CreatorLearningResponse {
  tracks: Array<{
    id: string;
    title: string;
    duration: number;
    level: string;
    status: string;
  }>;
}

const sidebarLinks = [
  { href: '/creator', label: 'Обзор' },
  { href: '/creator/feed', label: 'Лента' },
  { href: '/creator/orders', label: 'Заказы' },
  { href: '/creator/balance', label: 'Баланс' },
  { href: '/creator/rating', label: 'Рейтинг' },
  { href: '/creator/learning', label: 'Обучение', exact: true }
];

export default function CreatorLearningPage() {
  const { data, isLoading, error, mutate } = useDashboardData<CreatorLearningResponse>('/api/creator/learning', {
    fallbackData: creatorLearningFallback,
    revalidateOnFocus: true
  });

  return (
    <ProtectedRoute allowedRoles={['creator']}>
      <LayoutShell
        title="Обучение и треки развития"
        description="Развивайте навыки и повышайте уровень аккаунта."
        sidebarLinks={sidebarLinks}
      >
        {isLoading ? <Loader /> : null}
        {error ? (
          <EmptyState
            title="Не удалось загрузить обучающие треки"
            description={error.message}
            actionLabel="Повторить"
            onAction={() => mutate()}
          />
        ) : null}

        {data && data.tracks.length ? (
          <Table
            columns={['Название', 'Уровень', 'Статус', 'Длительность']}
            data={data.tracks.map((track) => [
              track.title,
              <Badge key={`${track.id}-level`} variant={track.level === 'pro_plus' ? 'success' : 'neutral'}>
                {levelLabel(track.level)}
              </Badge>,
              statusLabel(track.status),
              `${track.duration} мин`
            ])}
          />
        ) : (
          <EmptyState
            title="Обучение недоступно"
            description="Треки появятся после подключения подписки PRO или PRO+."
          />
        )}
      </LayoutShell>
    </ProtectedRoute>
  );
}

function levelLabel(level: string) {
  switch (level) {
    case 'pro':
      return 'PRO';
    case 'pro_plus':
      return 'PRO+';
    default:
      return level.toUpperCase();
  }
}

function statusLabel(status: string) {
  switch (status) {
    case 'in_progress':
      return 'В процессе';
    case 'completed':
      return 'Завершено';
    case 'available':
      return 'Доступно';
    default:
      return status;
  }
}

const creatorLearningFallback: CreatorLearningResponse = {
  tracks: [
    { id: 'lrn-1', title: 'Сторителлинг для шортов', duration: 90, level: 'pro', status: 'in_progress' },
    { id: 'lrn-2', title: 'Таргетинг и аналитика', duration: 120, level: 'pro_plus', status: 'available' }
  ]
};
