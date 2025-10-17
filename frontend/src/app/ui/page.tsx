'use client';

import { useState } from 'react';

import { Button, EmptyState, ErrorState, Loader, Modal, Table } from '@/components/ui';

export default function UiShowcase() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-12">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">UI Kit</h1>
        <p className="text-sm text-slate-600">Витрина базовых компонентов интерфейса проекта.</p>
      </header>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-900">Кнопки</h2>
        <div className="flex flex-wrap gap-4">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button loading>Loading</Button>
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
