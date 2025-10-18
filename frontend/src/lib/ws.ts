'use client';

import { API_URL } from '@/lib/api';

export function buildWsUrl(path: string, token: string): string {
  const base = (API_URL ?? '').replace(/\/$/, '');
  const protocol = base.startsWith('https') ? 'wss' : 'ws';
  const suffix = path.startsWith('/') ? path : `/${path}`;
  const host = base.replace(/^https?:\/\//, '');
  const query = `token=${encodeURIComponent(token)}`;
  return `${protocol}://${host}${suffix}?${query}`;
}
