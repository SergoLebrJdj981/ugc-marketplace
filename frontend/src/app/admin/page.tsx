'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { LayoutShell } from '@/components/layout/LayoutShell';
import { Button, Card, ErrorState, Loader, Table } from '@/components/ui';
import { useAuth, useNotifications } from '@/context';
import { apiRequest } from '@/lib/api';

interface MetricsResponse {
  total_events: number;
  events_by_type: Record<string, number>;
  recent_events: Array<{ id: number; event_type: string; status: string; created_at: string | null }>;
}

const sidebarLinks = [
  { href: '/admin', label: 'Обзор', exact: true },
  { href: '/admin/users', label: 'Пользователи' },
  { href: '/admin/campaigns', label: 'Кампании' },
  { href: '/admin/finance', label: 'Финансы' },
  { href: '/admin/analytics', label: 'Аналитика' }
];

export default function AdminDashboard() {
  const { accessToken } = useAuth();
  const { unreadCount } = useNotifications();
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    const response = await apiRequest<MetricsResponse>('/api/system/metrics', {
      token: accessToken
    });
    if (response.error) {
      setError(response.message || 'Не удалось загрузить метрики');
    } else {
      setMetrics(response.data ?? null);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMetrics();
  }, [accessToken]);

  const eventTypeRows = useMemo(() => {
    if (!metrics) return [];
    return Object.entries(metrics.events_by_type).map(([type, count]) => [type, count]);
  }, [metrics]);

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <LayoutShell
        title="Админ-панель"
        description="Управление системой, пользователями и финансами."
        sidebarLinks={sidebarLinks}
        actions={
          <div className="flex items-center gap-3">
            <Link href="/admin/users">
              <Button variant="outline">Пользователи</Button>
            </Link>
            <Button variant="secondary" onClick={fetchMetrics} disabled={loading}>
              Обновить метрики
            </Button>
          </div>
        }
      >
        <section className="grid gap-4 sm:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-500">Непрочитанные уведомления</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">{unreadCount}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Всего событий</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">{metrics?.total_events ?? '—'}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Типов событий</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {metrics ? Object.keys(metrics.events_by_type).length : '—'}
            </p>
          </Card>
        </section>

        {loading ? <Loader /> : null}
        {error ? <ErrorState message={error} onRetry={fetchMetrics} /> : null}

        {metrics ? (
          <section className="space-y-6">
            <div className="space-y-3">
              <h2 className="text-xl font-semibold text-slate-900">Распределение событий</h2>
              <Table columns={['Тип события', 'Кол-во']} data={eventTypeRows} />
            </div>
            <div className="space-y-3">
              <h2 className="text-xl font-semibold text-slate-900">Последние события</h2>
              <Table
                columns={['ID', 'Тип', 'Статус', 'Создано']}
                data={metrics.recent_events.map((event) => [
                  event.id,
                  event.event_type,
                  event.status,
                  event.created_at ? new Date(event.created_at).toLocaleString('ru-RU') : '—'
                ])}
              />
            </div>
          </section>
        ) : null}
      </LayoutShell>
    </ProtectedRoute>
  );
}
