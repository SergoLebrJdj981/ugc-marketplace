'use client';

import Link from 'next/link';

import { ThemeSwitcher } from '@/components/ui';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/context';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur">
      <Link href="/" className="text-lg font-semibold text-slate-900">
        UGC Marketplace
      </Link>
      <div className="flex items-center gap-4">
        <ThemeSwitcher />
        {user ? (
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="hidden sm:inline">{user.full_name ?? user.email}</span>
            <Button variant="outline" onClick={logout}>
              Выйти
            </Button>
          </div>
        ) : null}
      </div>
    </header>
  );
}
