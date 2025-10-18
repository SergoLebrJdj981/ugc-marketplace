'use client';

import type { AdminActionLog } from './types';
import { Badge, Table } from '@/components/ui';

interface ActionLogTableProps {
  logs: AdminActionLog[];
}

export function ActionLogTable({ logs }: ActionLogTableProps) {
  const rows = logs.map((log) => [
    formatDateTime(log.created_at),
    <span key={`${log.id}-admin`} className="font-mono text-sm text-slate-700">
      {log.admin_id}
    </span>,
    <span key={`${log.id}-target`} className="font-mono text-sm text-slate-700">
      {log.target_id}
    </span>,
    <Badge key={`${log.id}-type`} variant={badgeVariant(log.action_type)}>
      {actionLabel(log.action_type)}
    </Badge>,
    <span key={`${log.id}-desc`} className="text-sm text-slate-600">
      {log.description || '—'}
    </span>
  ]);

  return (
    <Table
      columns={['Дата', 'Администратор', 'Цель', 'Действие', 'Комментарий']}
      data={rows}
      emptyMessage="Записей действий пока нет"
    />
  );
}

function formatDateTime(iso?: string | null) {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString('ru-RU');
}

function actionLabel(action: string) {
  switch (action) {
    case 'block_user':
      return 'Блокировка пользователя';
    case 'unblock_user':
      return 'Разблокировка пользователя';
    case 'block_campaign':
      return 'Блокировка кампании';
    case 'unblock_campaign':
      return 'Разблокировка кампании';
    case 'warning':
      return 'Предупреждение';
    default:
      return action;
  }
}

function badgeVariant(action: string) {
  switch (action) {
    case 'warning':
      return 'warning';
    case 'block_user':
    case 'block_campaign':
      return 'danger';
    case 'unblock_user':
    case 'unblock_campaign':
      return 'success';
    default:
      return 'neutral';
  }
}
