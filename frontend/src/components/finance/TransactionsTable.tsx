'use client';

import { Card, EmptyState, Table } from '@/components/ui';

interface TransactionItem {
  id: string;
  type: string;
  amount: number;
  date: string | null;
  status: string;
  description?: string | null;
}

interface TransactionsTableProps {
  title?: string;
  items: TransactionItem[];
}

function typeLabel(type: string) {
  switch (type) {
    case 'deposit':
      return 'Пополнение';
    case 'release':
      return 'Релиз';
    case 'withdraw':
      return 'Вывод';
    case 'fee':
      return 'Комиссия';
    case 'reserve':
      return 'Резерв';
    default:
      return type;
  }
}

function statusLabel(status: string) {
  switch (status) {
    case 'hold':
      return 'Холд';
    case 'reserved':
      return 'В резерве';
    case 'released':
      return 'Релиз';
    case 'paid':
      return 'Оплачено';
    case 'refunded':
      return 'Возврат';
    default:
      return status;
  }
}

export function TransactionsTable({ title = 'История транзакций', items }: TransactionsTableProps) {
  if (!items.length) {
    return <EmptyState title={title} description="Записей пока нет." />;
  }

  return (
    <Card>
      <div className="flex flex-col gap-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">{title}</h3>
          <p className="mt-1 text-sm text-slate-500">Отображаются последние операции с эскроу-счётом.</p>
        </div>
        <Table
          columns={['ID', 'Тип', 'Дата', 'Сумма', 'Статус']}
          data={items.map((txn) => [
            txn.id,
            typeLabel(txn.type),
            txn.date ? new Date(txn.date).toLocaleString('ru-RU') : '—',
            `${txn.amount.toLocaleString('ru-RU')} ₽`,
            statusLabel(txn.status)
          ])}
        />
      </div>
    </Card>
  );
}
