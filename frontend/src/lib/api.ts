import axios, { AxiosError, AxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8002';

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

export interface ApiRequestOptions extends AxiosRequestConfig {
  token?: string | null;
}

export const client = axios.create({
  baseURL: API_URL,
  withCredentials: false,
  timeout: 10000
});

export async function apiRequest<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
  try {
    const { token, headers, ...rest } = options;
    const response = await client.request<T>({
      url: endpoint,
      headers: {
        ...(headers ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      ...rest
    });
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    const apiError: ApiError = {
      message:
        axiosError.response?.data?.detail || axiosError.response?.data?.message || axiosError.message,
      status: axiosError.response?.status,
      details: axiosError.response?.data
    };
    throw apiError;
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
