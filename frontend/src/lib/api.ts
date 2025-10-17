import axios, { AxiosError, AxiosRequestConfig } from 'axios';

import { notify } from '@/lib/toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8002';
const ACCESS_TOKEN_KEY = 'ugc_access_token';

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
  url?: string;
  method?: string;
  unauthorized?: boolean;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  message?: string;
  status?: number;
}

export interface ApiRequestOptions extends AxiosRequestConfig {
  token?: string | null;
  showErrorToast?: boolean;
  successMessage?: string;
  onUnauthorized?: () => void;
}

export const client = axios.create({
  baseURL: API_URL,
  withCredentials: false,
  timeout: 10000
});

function getStoredAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export async function apiRequest<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<ApiResponse<T>> {
  const {
    token,
    headers,
    method = 'GET',
    data,
    showErrorToast = true,
    successMessage,
    onUnauthorized,
    ...rest
  } = options;

  const authToken = token ?? getStoredAccessToken();

  try {
    const response = await client.request<T>({
      url: endpoint,
      method,
      data,
      headers: {
        ...(headers ?? {}),
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
      },
      ...rest
    });

    if (successMessage) {
      notify.success(successMessage);
    }

    return { data: response.data, status: response.status };
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    const message =
      axiosError.response?.data?.detail || axiosError.response?.data?.message || axiosError.message;
    const apiError: ApiError = {
      message,
      status: axiosError.response?.status,
      details: axiosError.response?.data,
      url: axiosError.config?.url,
      method: axiosError.config?.method?.toUpperCase(),
      unauthorized: axiosError.response?.status === 401
    };

    if (apiError.unauthorized && onUnauthorized) {
      onUnauthorized();
    }

    if (showErrorToast && message) {
      notify.error(message);
    }

    return { error: apiError, message, status: apiError.status };
  }
}

export function buildQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    search.append(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}
