'use client';

import type { ModerationUser } from './types';
import { Badge, Button, Table } from '@/components/ui';

interface UsersTableProps {
  users: ModerationUser[];
  loadingIds: string[];
  onToggleBlock: (user: ModerationUser, blocked: boolean) => void;
  onSendWarning: (user: ModerationUser) => void;
}

export function UsersTable({ users, loadingIds, onToggleBlock, onSendWarning }: UsersTableProps) {
  const loadingSet = new Set(loadingIds);

  const rows = users.map((user) => {
    const blocked = user.status === 'blocked';
    return [
      <div key={`${user.id}-info`} className="space-y-1">
        <p className="font-medium text-slate-900">{user.email}</p>
        <p className="text-sm text-slate-500">{user.full_name || '—'}</p>
      </div>,
      roleLabel(user.role),
      <Badge key={`${user.id}-status`} variant={blocked ? 'danger' : 'success'}>
        {blocked ? 'Заблокирован' : 'Активен'}
      </Badge>,
      <span key={`${user.id}-level`} className="text-sm text-slate-600">
        {adminLevelLabel(user.admin_level)}
      </span>,
      <div key={`${user.id}-actions`} className="flex flex-wrap gap-2">
        <Button
          variant={blocked ? 'secondary' : 'danger'}
          onClick={() => onToggleBlock(user, !blocked)}
          disabled={loadingSet.has(user.id)}
          className="px-3 py-1 text-sm"
        >
          {blocked ? 'Разблокировать' : 'Заблокировать'}
        </Button>
        <Button
          variant="outline"
          onClick={() => onSendWarning(user)}
          disabled={loadingSet.has(user.id)}
          className="px-3 py-1 text-sm"
        >
          Предупреждение
        </Button>
      </div>
    ];
  });

  return (
    <Table
      columns={['Пользователь', 'Роль', 'Статус', 'Уровень', 'Действия']}
      data={rows}
      emptyMessage="Пользователи для модерации не найдены"
    />
  );
}

function roleLabel(role: string) {
  switch (role) {
    case 'creator':
      return 'Креатор';
    case 'brand':
      return 'Бренд';
    case 'agent':
      return 'Агент';
    case 'admin':
      return 'Администратор';
    default:
      return role;
  }
}

function adminLevelLabel(level: string) {
  switch (level) {
    case 'admin_level_1':
      return 'Модератор';
    case 'admin_level_2':
      return 'Финансы';
    case 'admin_level_3':
      return 'Руководитель';
    default:
      return '—';
  }
}
