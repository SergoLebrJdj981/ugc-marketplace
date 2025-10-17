import Link from 'next/link';

import { Button } from '@/components/ui';

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-100 px-6">
      <div className="rounded-3xl bg-white p-12 text-center shadow-xl">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand">404</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">Страница не найдена</h1>
        <p className="mt-3 text-sm text-slate-600">
          Похоже, вы попали в раздел, которого ещё нет. Вернитесь на главную и продолжите работу.
        </p>
        <div className="mt-6">
          <Link href="/">
            <Button>На главную</Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
