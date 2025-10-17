'use client';

import { useState } from 'react';

import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorState,
  Input,
  Loader,
  Modal,
  Table,
  ThemeSwitcher
} from '@/components/ui';

export default function UiShowcase() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-12">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">UI Kit</h1>
        <p className="text-sm text-slate-600">Витрина базовых компонентов интерфейса проекта.</p>
      </header>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Темы и кнопки</h2>
          <ThemeSwitcher />
        </div>
        <div className="flex flex-wrap gap-4">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="danger">Danger</Button>
          <Button loading>Loading…</Button>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Формы</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Email" placeholder="you@example.com" type="email" />
          <Input label="Пароль" placeholder="••••••••" type="password" />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Бейджи</h2>
        <div className="flex flex-wrap gap-3">
          <Badge>Neutral</Badge>
          <Badge variant="info">Info</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Карточки</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <Card title="Карточка" description="Базовый контейнер с тенью">
            Используйте карточки для группировки информации. Внутри можно размещать формы, списки или диаграммы.
          </Card>
          <Card
            title="Состояние"
            description="Карточка с дополнительным футером"
            footer="Последнее обновление: сегодня"
          >
            Контент карточки может быть любым. Например, описание кампании или статистика.
          </Card>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Модальные окна</h2>
        <Button onClick={() => setModalOpen(true)}>Открыть модалку</Button>
        <Modal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          title="Пример модального окна"
          primaryAction={{ label: 'Подтвердить', onClick: () => setModalOpen(false) }}
        >
          Используйте модальные окна для подтверждения действий или отображения дополнительной информации.
        </Modal>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Таблица</h2>
        <Table
          columns={['Кампания', 'Статус', 'Бюджет']}
          data={[
            ['UGC для бренда X', 'active', '75 000 ₽'],
            ['Витрина продукта', 'draft', '90 000 ₽']
          ]}
        />
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Состояния</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <EmptyState
            title="Пусто"
            description="Компонент для отображения пустых состояний списков и таблиц."
            actionLabel="Добавить"
            onAction={() => setModalOpen(true)}
          />
          <ErrorState message="Не удалось загрузить данные" onRetry={() => window.location.reload()} />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Loader</h2>
        <Loader />
      </section>
    </main>
  );
}
