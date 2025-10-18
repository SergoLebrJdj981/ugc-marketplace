'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import { ActionLogTable } from './ActionLogTable';
import { CampaignsTable } from './CampaignsTable';
import { UsersTable } from './UsersTable';
import { WarningModal } from './WarningModal';
import type { AdminActionLog, ModerationCampaign, ModerationUser } from './types';
import { Button, Card, ErrorState, Loader } from '@/components/ui';
import { useAuth } from '@/context';
import { apiRequest, buildQuery } from '@/lib/api';
import { notify } from '@/lib/toast';

interface ModerationUsersResponse {
  total: number;
  items: ModerationUser[];
}

interface ModerationCampaignsResponse {
  total: number;
  items: ModerationCampaign[];
}

interface ModerationLogsResponse {
  total: number;
  items: AdminActionLog[];
}

interface ModerationUserActionResponse {
  user: ModerationUser;
}

interface ModerationCampaignActionResponse {
  campaign: ModerationCampaign;
}

interface ModerationWarningResponse {
  user: ModerationUser;
}

type UserFilters = {
  role: string;
  status: 'all' | 'active' | 'blocked';
  activity: 'all' | 'active' | 'inactive';
};

type CampaignFilters = {
  status: string;
  blocked: 'all' | 'blocked' | 'unblocked';
};

export function ModerationPanel() {
  const { accessToken } = useAuth();
  const [users, setUsers] = useState<ModerationUser[]>([]);
  const [campaigns, setCampaigns] = useState<ModerationCampaign[]>([]);
  const [logs, setLogs] = useState<AdminActionLog[]>([]);
  const [userFilters, setUserFilters] = useState<UserFilters>({
    role: 'all',
    status: 'all',
    activity: 'all'
  });
  const [campaignFilters, setCampaignFilters] = useState<CampaignFilters>({
    status: 'all',
    blocked: 'all'
  });
  const [loading, setLoading] = useState({ users: false, campaigns: false, logs: false });
  const [initialLoading, setInitialLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string[]>([]);
  const [warningModalOpen, setWarningModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<ModerationUser | null>(null);
  const [warningMessage, setWarningMessage] = useState('');
  const [warningLoading, setWarningLoading] = useState(false);

  const setActionPending = useCallback((key: string, pending: boolean) => {
    setActionLoading((prev) => {
      if (pending) {
        if (prev.includes(key)) {
          return prev;
        }
        return [...prev, key];
      }
      return prev.filter((item) => item !== key);
    });
  }, []);

  const fetchUsers = useCallback(
    async (filters: UserFilters) => {
      if (!accessToken) return;
      setLoading((prev) => ({ ...prev, users: true }));
      const query = buildQuery({
        role: filters.role !== 'all' ? filters.role : undefined,
        status: filters.status !== 'all' ? filters.status : undefined,
        active:
          filters.activity === 'active' ? true : filters.activity === 'inactive' ? false : undefined
      });
      const response = await apiRequest<ModerationUsersResponse>(
        `/api/admin/moderation/users${query}`,
        { token: accessToken }
      );
      if (response.error) {
        setError(response.error.message);
      } else if (response.data) {
        setUsers(response.data.items);
        setError(null);
      }
      setLoading((prev) => ({ ...prev, users: false }));
    },
    [accessToken]
  );

  const fetchCampaigns = useCallback(
    async (filters: CampaignFilters) => {
      if (!accessToken) return;
      setLoading((prev) => ({ ...prev, campaigns: true }));
      const query = buildQuery({
        status: filters.status !== 'all' ? filters.status : undefined,
        blocked:
          filters.blocked === 'blocked'
            ? true
            : filters.blocked === 'unblocked'
            ? false
            : undefined
      });
      const response = await apiRequest<ModerationCampaignsResponse>(
        `/api/admin/moderation/campaigns${query}`,
        { token: accessToken }
      );
      if (response.error) {
        setError(response.error.message);
      } else if (response.data) {
        setCampaigns(response.data.items);
        setError(null);
      }
      setLoading((prev) => ({ ...prev, campaigns: false }));
    },
    [accessToken]
  );

  const fetchLogs = useCallback(async () => {
    if (!accessToken) return;
    setLoading((prev) => ({ ...prev, logs: true }));
    const response = await apiRequest<ModerationLogsResponse>('/api/admin/moderation/logs', {
      token: accessToken
    });
    if (response.error) {
      setError(response.error.message);
    } else if (response.data) {
      setLogs(response.data.items);
      setError(null);
    }
    setLoading((prev) => ({ ...prev, logs: false }));
  }, [accessToken]);

  const refreshAll = useCallback(async () => {
    if (!accessToken) return;
    setInitialLoading(true);
    await Promise.all([
      fetchUsers(userFilters),
      fetchCampaigns(campaignFilters),
      fetchLogs()
    ]);
    setInitialLoading(false);
  }, [accessToken, fetchUsers, fetchCampaigns, fetchLogs, userFilters, campaignFilters]);

  useEffect(() => {
    if (!accessToken) return;
    void refreshAll();
  }, [accessToken, refreshAll]);

  const handleUserFilterChange = async (key: keyof UserFilters, value: string) => {
    const nextFilters = { ...userFilters, [key]: value };
    setUserFilters(nextFilters);
    await fetchUsers(nextFilters);
  };

  const handleCampaignFilterChange = async (key: keyof CampaignFilters, value: string) => {
    const nextFilters = { ...campaignFilters, [key]: value };
    setCampaignFilters(nextFilters);
    await fetchCampaigns(nextFilters);
  };

  const onToggleUserBlock = async (user: ModerationUser, blocked: boolean) => {
    if (!accessToken) return;

    let reason: string | undefined;
    if (blocked) {
      const input = window.prompt('Укажите причину блокировки', '');
      if (input === null) {
        return;
      }
      reason = input.trim() || undefined;
    }

    const key = `user-${user.id}`;
    setActionPending(key, true);
    const response = await apiRequest<ModerationUserActionResponse>(
      `/api/admin/moderation/user/${user.id}/block`,
      {
        method: 'PATCH',
        token: accessToken,
        data: { blocked, reason },
        successMessage: blocked ? 'Пользователь заблокирован' : 'Пользователь разблокирован'
      }
    );
    if (!response.error && response.data) {
      setUsers((prev) =>
        prev.map((item) => (item.id === response.data!.user.id ? response.data!.user : item))
      );
      await fetchLogs();
    }
    setActionPending(key, false);
  };

  const onToggleCampaignBlock = async (campaign: ModerationCampaign, blocked: boolean) => {
    if (!accessToken) return;

    let reason: string | undefined;
    if (blocked) {
      const input = window.prompt('Укажите причину блокировки кампании', '');
      if (input === null) {
        return;
      }
      reason = input.trim() || undefined;
    }

    const key = `campaign-${campaign.id}`;
    setActionPending(key, true);
    const response = await apiRequest<ModerationCampaignActionResponse>(
      `/api/admin/moderation/campaign/${campaign.id}/block`,
      {
        method: 'PATCH',
        token: accessToken,
        data: { blocked, reason },
        successMessage: blocked ? 'Кампания заблокирована' : 'Кампания разблокирована'
      }
    );
    if (!response.error && response.data) {
      setCampaigns((prev) =>
        prev.map((item) =>
          item.id === response.data!.campaign.id ? response.data!.campaign : item
        )
      );
      await fetchLogs();
    }
    setActionPending(key, false);
  };

  const openWarningModal = (user: ModerationUser) => {
    setSelectedUser(user);
    setWarningMessage('');
    setWarningModalOpen(true);
  };

  const handleWarningSubmit = async () => {
    if (!accessToken || !selectedUser) return;
    const message = warningMessage.trim();
    if (!message) {
      notify.error('Введите текст предупреждения');
      return;
    }

    setWarningLoading(true);
    const response = await apiRequest<ModerationWarningResponse>(
      '/api/admin/moderation/warning',
      {
        method: 'POST',
        token: accessToken,
        data: { user_id: selectedUser.id, message },
        successMessage: 'Предупреждение отправлено'
      }
    );
    if (!response.error && response.data) {
      setUsers((prev) =>
        prev.map((user) => (user.id === response.data!.user.id ? response.data!.user : user))
      );
      await fetchLogs();
      setWarningModalOpen(false);
      setSelectedUser(null);
      setWarningMessage('');
    }
    setWarningLoading(false);
  };

  const blockedUsersCount = useMemo(
    () => users.filter((user) => user.status === 'blocked').length,
    [users]
  );
  const blockedCampaignsCount = useMemo(
    () => campaigns.filter((campaign) => campaign.is_blocked).length,
    [campaigns]
  );
  const totalActions = logs.length;

  const userLoadingIds = actionLoading
    .filter((key) => key.startsWith('user-'))
    .map((key) => key.replace('user-', ''));
  const campaignLoadingIds = actionLoading
    .filter((key) => key.startsWith('campaign-'))
    .map((key) => key.replace('campaign-', ''));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-slate-900">Инструменты модерации</h2>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => refreshAll()} disabled={initialLoading}>
            Обновить данные
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card title="Заблокированные пользователи">
          <p className="text-3xl font-semibold text-rose-600">{blockedUsersCount}</p>
          <p className="mt-1 text-sm text-slate-500">Всего пользователей: {users.length}</p>
        </Card>
        <Card title="Заблокированные кампании">
          <p className="text-3xl font-semibold text-rose-600">{blockedCampaignsCount}</p>
          <p className="mt-1 text-sm text-slate-500">Всего кампаний: {campaigns.length}</p>
        </Card>
        <Card title="Действия администраторов">
          <p className="text-3xl font-semibold text-slate-900">{totalActions}</p>
          <p className="mt-1 text-sm text-slate-500">Количество записей в журнале</p>
        </Card>
      </div>

      {initialLoading ? <Loader /> : null}
      {error ? (
        <ErrorState message={error} onRetry={() => refreshAll()} />
      ) : (
        <>
          <Card
            title="Пользователи"
            description="Управляйте блокировками и отправляйте предупреждения. Фильтры применяются моментально."
          >
            <div className="space-y-4">
              <div className="flex flex-wrap gap-3">
                <select
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                  value={userFilters.role}
                  onChange={(event) => handleUserFilterChange('role', event.target.value)}
                >
                  <option value="all">Все роли</option>
                  <option value="creator">Креаторы</option>
                  <option value="brand">Бренды</option>
                  <option value="agent">Агенты</option>
                  <option value="admin">Администраторы</option>
                </select>
                <select
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                  value={userFilters.activity}
                  onChange={(event) => handleUserFilterChange('activity', event.target.value)}
                >
                  <option value="all">Активность: любая</option>
                  <option value="active">Только активные</option>
                  <option value="inactive">Отключенные</option>
                </select>
                <select
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                  value={userFilters.status}
                  onChange={(event) => handleUserFilterChange('status', event.target.value as UserFilters['status'])}
                >
                  <option value="all">Статус: все</option>
                  <option value="active">Активные</option>
                  <option value="blocked">Заблокированные</option>
                </select>
              </div>
              {loading.users ? <Loader /> : null}
              <UsersTable
                users={users}
                loadingIds={userLoadingIds}
                onToggleBlock={onToggleUserBlock}
                onSendWarning={openWarningModal}
              />
            </div>
          </Card>

          <Card
            title="Кампании"
            description="Контролируйте блокировки кампаний брендов и следите за статусами модерации."
          >
            <div className="space-y-4">
              <div className="flex flex-wrap gap-3">
                <select
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                  value={campaignFilters.status}
                  onChange={(event) =>
                    handleCampaignFilterChange('status', event.target.value as CampaignFilters['status'])
                  }
                >
                  <option value="all">Все статусы</option>
                  <option value="draft">Черновики</option>
                  <option value="active">Активные</option>
                  <option value="paused">На проверке</option>
                  <option value="completed">Завершённые</option>
                  <option value="archived">Архив</option>
                </select>
                <select
                  className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand"
                  value={campaignFilters.blocked}
                  onChange={(event) =>
                    handleCampaignFilterChange(
                      'blocked',
                      event.target.value as CampaignFilters['blocked']
                    )
                  }
                >
                  <option value="all">Все кампании</option>
                  <option value="blocked">Только заблокированные</option>
                  <option value="unblocked">Без блокировки</option>
                </select>
              </div>
              {loading.campaigns ? <Loader /> : null}
              <CampaignsTable
                campaigns={campaigns}
                loadingIds={campaignLoadingIds}
                onToggleBlock={onToggleCampaignBlock}
              />
            </div>
          </Card>

          <Card
            title="Журнал действий"
            description="История действий администраторов и модераторов. Отображаются последние 200 записей."
          >
            <div className="space-y-4">
              <div className="flex justify-end">
                <Button variant="ghost" onClick={() => fetchLogs()} disabled={loading.logs}>
                  Обновить журнал
                </Button>
              </div>
              {loading.logs ? <Loader /> : null}
              <ActionLogTable logs={logs} />
            </div>
          </Card>
        </>
      )}

      <WarningModal
        open={warningModalOpen}
        user={selectedUser}
        message={warningMessage}
        loading={warningLoading}
        onChange={setWarningMessage}
        onClose={() => {
          setWarningModalOpen(false);
          setSelectedUser(null);
        }}
        onSubmit={() => void handleWarningSubmit()}
      />
    </div>
  );
}
