'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useForm } from 'react-hook-form';

import { Button, Input } from '@/components/ui';
import { Modal } from '@/components/ui/Modal';
import { useAuth } from '@/context';

interface LoginFormValues {
  email: string;
  password: string;
}

const ROLE_LABELS: Record<string, string> = {
  creator: 'Кабинет креатора',
  brand: 'Кабинет бренда',
  admin: 'Админ-панель'
};

const roleHints: Record<string, LoginFormValues> = {
  creator: { email: 'creator@example.com', password: 'Secret123!' },
  brand: { email: 'slebronov@mail.ru', password: '12322828' },
  admin: { email: 'admin@example.com', password: 'Secret123!' }
};

export default function HomePage() {
  const { login, loading } = useAuth();
  const [loginRole, setLoginRole] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<LoginFormValues>({
    defaultValues: { email: '', password: '' }
  });

  const closeModal = () => {
    setLoginRole(null);
    reset();
  };

  const onSubmit = async (data: LoginFormValues) => {
    await login(data);
    closeModal();
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 py-16 text-center">
      <header className="max-w-2xl space-y-4">
        <span className="inline-flex items-center rounded-full bg-brand/10 px-3 py-1 text-sm font-semibold text-brand">
          UGC Marketplace · v0.4
        </span>
        <h1 className="text-4xl font-bold text-slate-900 sm:text-5xl">
          Платформа для брендов и креаторов с единым контролем кампаний
        </h1>
        <p className="text-base text-slate-600">
          Управляйте кампаниями, отслеживайте результаты и выстраивайте коммуникации в одной системе.
          Используйте демо-вход или зарегистрируйте новый бренд/креатора.
        </p>
      </header>

      <div className="mt-10 flex flex-col gap-4 sm:flex-row">
        {Object.entries(ROLE_LABELS).map(([role, label]) => (
          <Button
            key={role}
            variant="primary"
            onClick={() => {
              setLoginRole(role);
              const hint = roleHints[role];
              if (hint) {
                reset(hint);
              }
            }}
          >
            Войти как {label.split(' ')[1] ?? label}
          </Button>
        ))}
        <Link
          href="/register"
          className="inline-flex items-center justify-center rounded-md border border-brand bg-white px-4 py-2 text-sm font-medium text-brand shadow-sm transition hover:bg-brand/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
        >
          Регистрация
        </Link>
      </div>

      <section className="mt-16 grid w-full gap-6 rounded-3xl bg-white p-8 shadow-xl sm:grid-cols-3">
        <div className="space-y-2 text-left">
          <h2 className="text-lg font-semibold text-slate-900">Креаторы</h2>
          <p className="text-sm text-slate-600">
            Управляйте заказами, отслеживайте баланс и улучшайте рейтинг качества.
          </p>
        </div>
        <div className="space-y-2 text-left">
          <h2 className="text-lg font-semibold text-slate-900">Бренды</h2>
          <p className="text-sm text-slate-600">
            Создавайте кампании, анализируйте результаты и контролируйте бюджет.
          </p>
        </div>
        <div className="space-y-2 text-left">
          <h2 className="text-lg font-semibold text-slate-900">Администраторы</h2>
          <p className="text-sm text-slate-600">
            Следите за метриками платформы, событиями и безопасностью.
          </p>
        </div>
      </section>

      <Modal
        open={Boolean(loginRole)}
        onClose={closeModal}
        title={loginRole ? `Вход — ${ROLE_LABELS[loginRole]}` : 'Вход'}
        primaryAction={{
          label: 'Войти',
          onClick: handleSubmit(onSubmit),
          loading
        }}
      >
        <form className="mt-4 space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            {...register('email', { required: 'Укажите email' })}
            error={errors.email?.message}
          />
          <Input
            label="Пароль"
            type="password"
            autoComplete="current-password"
            {...register('password', { required: 'Введите пароль' })}
            error={errors.password?.message}
          />
        </form>
        <p className="mt-3 text-xs text-slate-400">
          Используйте демо-данные или свои учетные данные.
        </p>
      </Modal>
    </main>
  );
}
