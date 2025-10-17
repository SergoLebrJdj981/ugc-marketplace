'use client';

import useSWR from 'swr';

import { useAuth } from '@/context';
import { apiRequest, type ApiResponse } from '@/lib/api';

interface UseDashboardOptions<T> {
  fallbackData?: T;
  revalidateOnFocus?: boolean;
}

async function fetchDashboardData<T>(
  endpoint: string,
  token: string | null,
  fallback?: T
): Promise<T> {
  const response: ApiResponse<T> = await apiRequest<T>(endpoint, {
    method: 'GET',
    token,
    showErrorToast: false
  });

  if (response.error) {
    const message = response.message ?? 'Не удалось загрузить данные';
    const error = new Error(message) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  if (!response.data) {
    if (fallback !== undefined) {
      return fallback;
    }
    throw new Error('Пустой ответ сервера');
  }

  return response.data;
}

export function useDashboardData<T>(endpoint: string, options: UseDashboardOptions<T> = {}) {
  const { accessToken, logout } = useAuth();
  const shouldFetch = Boolean(accessToken);

  const swr = useSWR<T>(shouldFetch ? [endpoint, accessToken] : null, {
    fetcher: async ([url, token]) => {
      try {
        return await fetchDashboardData<T>(url, token ?? null, options.fallbackData);
      } catch (error) {
        const err = error as Error & { status?: number };
        if (err.status === 401) {
          logout();
        }
        if (options.fallbackData !== undefined) {
          return options.fallbackData;
        }
        throw err;
      }
    },
    keepPreviousData: true,
    fallbackData: options.fallbackData,
    revalidateOnFocus: options.revalidateOnFocus ?? false
  });

  return {
    data: swr.data,
    isLoading: swr.isLoading,
    isValidating: swr.isValidating,
    error: swr.error,
    mutate: swr.mutate
  };
}
