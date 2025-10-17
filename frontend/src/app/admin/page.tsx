'use client';

import { useEffect, useState } from 'react';

import { Button, ErrorState, Loader, Table } from '@/components/ui';
import { useAuth, useNotifications } from '@/context';
import { apiRequest } from '@/lib/api';

interface MetricsResponse {
  total_events: number;
  events_by_type: Record<string, number>;
  recent_events: Array<{ id: number; event_type: string; status: string; created_at: string | null }>;
}

export default function AdminDashboard() {
  const { user, accessToken } = useAuth();
  const { unreadCount } = useNotifications();
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<MetricsResponse>('/api/system/metrics', {
        token: accessToken
      });
      setMetrics(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [accessToken]);

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold text-slate-900">Админ-панель</h1>
        <p className="text-sm text-slate-600">
          {user?.email} · Новые уведомления: <span className="font-semibold">{unreadCount}</span>
        </p>
        <div>
          <Button variant="secondary" onClick={fetchMetrics} disabled={loading}>
            Обновить метрики
          </Button>
        </div>
      </header>

      {loading ? <Loader /> : null}
      {error ? <ErrorState message={error} onRetry={fetchMetrics} /> : null}

      {metrics ? (
        <section className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Всего событий</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{metrics.total_events}</p>
            </div>
            <div className="rounded-xl bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Типов событий</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">
                {Object.keys(metrics.events_by_type).length}
              </p>
            </div>
            <div className="rounded-xl bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">Непрочитанные уведомления</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{unreadCount}</p>
            </div>
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
    </main>
  );
}
