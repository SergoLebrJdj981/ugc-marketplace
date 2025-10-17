import { apiRequest } from './api';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  full_name: string;
  role: 'brand' | 'creator';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_role: string;
  user: {
    id: string;
    email: string;
    full_name?: string | null;
    role: string;
  };
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/login', {
    method: 'POST',
    data: payload
  });
}

export async function refresh(refresh_token: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/refresh', {
    method: 'POST',
    data: { refresh_token }
  });
}

export async function logout(refresh_token?: string): Promise<void> {
  await apiRequest('/api/auth/logout', {
    method: 'POST',
    data: refresh_token ? { refresh_token } : undefined
  });
}

export async function register(payload: RegisterPayload): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/register', {
    method: 'POST',
    data: payload
  });
}
