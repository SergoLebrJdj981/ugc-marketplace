'use client';

import type { ModerationCampaign } from './types';
import { Badge, Button, Table } from '@/components/ui';

interface CampaignsTableProps {
  campaigns: ModerationCampaign[];
  loadingIds: string[];
  onToggleBlock: (campaign: ModerationCampaign, blocked: boolean) => void;
}

export function CampaignsTable({ campaigns, loadingIds, onToggleBlock }: CampaignsTableProps) {
  const loadingSet = new Set(loadingIds);

  const rows = campaigns.map((campaign) => {
    const blocked = campaign.is_blocked;
    return [
      <div key={`${campaign.id}-info`} className="space-y-1">
        <p className="font-medium text-slate-900">{campaign.title}</p>
        <p className="text-sm text-slate-500">
          {campaign.brand_name || '—'} · {formatDate(campaign.created_at)}
        </p>
      </div>,
      statusLabel(campaign.status),
      <Badge key={`${campaign.id}-moderation`} variant={badgeVariant(campaign.moderation_state)}>
        {moderationLabel(campaign.moderation_state)}
      </Badge>,
      <div key={`${campaign.id}-actions`} className="flex flex-wrap gap-2">
        <Button
          variant={blocked ? 'secondary' : 'danger'}
          onClick={() => onToggleBlock(campaign, !blocked)}
          disabled={loadingSet.has(campaign.id)}
          className="px-3 py-1 text-sm"
        >
          {blocked ? 'Разблокировать' : 'Заблокировать'}
        </Button>
      </div>
    ];
  });

  return (
    <Table
      columns={['Кампания', 'Статус', 'Модерация', 'Действия']}
      data={rows}
      emptyMessage="Кампании для модерации не найдены"
    />
  );
}

function formatDate(iso?: string | null) {
  if (!iso) return '—';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('ru-RU');
}

function statusLabel(status: string) {
  switch (status) {
    case 'draft':
      return 'Черновик';
    case 'active':
      return 'Активна';
    case 'paused':
      return 'Пауза';
    case 'completed':
      return 'Завершена';
    case 'archived':
      return 'Архив';
    default:
      return status;
  }
}

function moderationLabel(state: ModerationCampaign['moderation_state']) {
  switch (state) {
    case 'blocked':
      return 'Заблокирована';
    case 'under_review':
      return 'На проверке';
    default:
      return 'Активна';
  }
}

function badgeVariant(state: ModerationCampaign['moderation_state']) {
  switch (state) {
    case 'blocked':
      return 'danger';
    case 'under_review':
      return 'warning';
    default:
      return 'info';
  }
}
