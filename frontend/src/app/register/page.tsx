'use client';

import Link from 'next/link';
import { useForm } from 'react-hook-form';

import { Button, Input } from '@/components/ui';
import { useAuth } from '@/context';
import type { RegisterPayload } from '@/lib/auth';

interface RegisterFormValues extends RegisterPayload {
  confirmPassword: string;
}

const ROLE_OPTIONS: RegisterPayload['role'][] = ['brand', 'creator'];

export default function RegisterPage() {
  const { register: registerUser, loading } = useAuth();
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<RegisterFormValues>({
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      full_name: '',
      role: 'brand'
    }
  });

  const passwordValue = watch('password');

  const onSubmit = async ({ confirmPassword, ...payload }: RegisterFormValues) => {
    if (confirmPassword !== payload.password) {
      throw new Error('Пароли не совпадают');
    }
    await registerUser(payload);
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center px-6 py-16">
      <div className="rounded-3xl bg-white p-10 shadow-xl">
        <h1 className="text-3xl font-semibold text-slate-900">Регистрация бренда или креатора</h1>
        <p className="mt-2 text-sm text-slate-600">
          После регистрации вы будете перенаправлены в личный кабинет выбранной роли.
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Полное имя"
            placeholder="Имя и фамилия"
            {...register('full_name', { required: 'Введите имя' })}
            error={errors.full_name?.message}
          />
          <Input
            label="Email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            {...register('email', { required: 'Укажите email' })}
            error={errors.email?.message}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label="Пароль"
              type="password"
              autoComplete="new-password"
              {...register('password', {
                required: 'Введите пароль',
                minLength: { value: 8, message: 'Минимум 8 символов' }
              })}
              error={errors.password?.message}
            />
            <Input
              label="Повторите пароль"
              type="password"
              autoComplete="new-password"
              {...register('confirmPassword', {
                required: 'Подтвердите пароль',
                validate: (value) => value === passwordValue || 'Пароли не совпадают'
              })}
              error={errors.confirmPassword?.message}
            />
          </div>

          <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
            Тип учётной записи
            <select
              className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-brand focus:ring-2 focus:ring-brand/20"
              {...register('role')}
            >
              {ROLE_OPTIONS.map((role) => (
                <option key={role} value={role}>
                  {role === 'brand' ? 'Бренд' : 'Креатор'}
                </option>
              ))}
            </select>
          </label>

          <div className="flex items-center justify-between pt-4">
            <Link href="/" className="text-sm text-brand hover:text-brand-dark">
              Уже есть аккаунт? Вернуться на главную
            </Link>
            <Button type="submit" loading={loading}>
              Зарегистрироваться
            </Button>
          </div>
        </form>
      </div>
    </main>
  );
}
