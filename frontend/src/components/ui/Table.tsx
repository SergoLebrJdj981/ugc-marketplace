'use client';

import type { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface TableProps {
  columns: string[];
  data: ReactNode[][];
  emptyMessage?: string;
}

export function Table({ columns, data, emptyMessage = 'Нет данных для отображения' }: TableProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column}
                scope="col"
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-6 text-center text-sm text-slate-500">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr key={rowIndex} className={twMerge(rowIndex % 2 === 0 ? 'bg-white' : 'bg-slate-50/50')}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="px-4 py-3 text-sm text-slate-700">
                    {cell}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
