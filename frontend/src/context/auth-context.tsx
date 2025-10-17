'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from 'react';
import { useRouter } from 'next/navigation';

import {
  login as loginRequest,
  logout as logoutRequest,
  refresh as refreshRequest,
  register as registerRequest,
  type AuthResponse,
  type LoginPayload,
  type RegisterPayload
} from '@/lib/auth';
import { notify } from '@/lib/toast';
import { resolveDashboardRoute } from '@/lib/routes';
import type { UserProfile } from '@/types/auth';

interface AuthContextValue {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_KEYS = {
  access: 'ugc_access_token',
  refresh: 'ugc_refresh_token',
  user: 'ugc_user'
};

function persistAuth(response: AuthResponse | null) {
  if (typeof window === 'undefined') return;
  if (!response) {
    window.localStorage.removeItem(STORAGE_KEYS.access);
    window.localStorage.removeItem(STORAGE_KEYS.refresh);
    window.localStorage.removeItem(STORAGE_KEYS.user);
    return;
  }
  window.localStorage.setItem(STORAGE_KEYS.access, response.access_token);
  window.localStorage.setItem(STORAGE_KEYS.refresh, response.refresh_token);
  window.localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(response.user));
}

function loadPersistedAuth(): {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
} {
  if (typeof window === 'undefined') {
    return { accessToken: null, refreshToken: null, user: null };
  }
  try {
    const accessToken = window.localStorage.getItem(STORAGE_KEYS.access);
    const refreshToken = window.localStorage.getItem(STORAGE_KEYS.refresh);
    const userRaw = window.localStorage.getItem(STORAGE_KEYS.user);
    const user = userRaw ? (JSON.parse(userRaw) as UserProfile) : null;
    return { accessToken, refreshToken, user };
  } catch (error) {
    console.warn('Failed to load auth state from storage', error);
    return { accessToken: null, refreshToken: null, user: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [{ accessToken, refreshToken, user }, setAuthState] = useState(() => loadPersistedAuth());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!accessToken || !refreshToken || !user) return;
    persistAuth({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      user_role: user.role,
      user
    } as AuthResponse);
  }, [accessToken, refreshToken, user]);

  const handleAuthSuccess = useCallback(
    (response: AuthResponse, redirect = true) => {
      persistAuth(response);
      setAuthState({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        user: response.user
      });
      if (redirect) {
        router.push(resolveDashboardRoute(response.user?.role));
      }
    },
    [router]
  );

  const login = useCallback(
    async (payload: LoginPayload) => {
      setLoading(true);
      try {
        const response = await loginRequest(payload);
        handleAuthSuccess(response);
        notify.success('Добро пожаловать обратно!');
      } catch (error) {
        notify.error((error as Error).message || 'Не удалось войти');
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [handleAuthSuccess]
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      setLoading(true);
      try {
        const response = await registerRequest(payload);
        handleAuthSuccess(response);
        notify.success('Регистрация прошла успешно!');
      } catch (error) {
        notify.error((error as Error).message || 'Ошибка регистрации');
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [handleAuthSuccess]
  );

  const logout = useCallback(async () => {
    try {
      if (refreshToken) {
        await logoutRequest(refreshToken);
      }
    } catch (error) {
      console.warn('Logout request failed', error);
    } finally {
      persistAuth(null);
      setAuthState({ accessToken: null, refreshToken: null, user: null });
      router.push('/');
    }
  }, [refreshToken, router]);

  const refresh = useCallback(async () => {
    if (!refreshToken) return;
    try {
      const response = await refreshRequest(refreshToken);
      handleAuthSuccess(response, false);
    } catch (error) {
      console.warn('Token refresh failed', error);
      await logout();
    }
  }, [handleAuthSuccess, logout, refreshToken]);

  useEffect(() => {
    const { accessToken: storedAccess, refreshToken: storedRefresh, user: storedUser } =
      loadPersistedAuth();
    if (storedAccess && storedRefresh && storedUser) {
      setAuthState({ accessToken: storedAccess, refreshToken: storedRefresh, user: storedUser });
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      refreshToken,
      loading,
      login,
      register,
      logout,
      refresh
    }),
    [user, accessToken, refreshToken, loading, login, register, logout, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
