'use client';

import { Fragment, type ReactNode } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Button } from './Button';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void;
    loading?: boolean;
  };
}

export function Modal({ open, onClose, title, children, primaryAction }: ModalProps) {
  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-slate-900/40" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center px-4 py-8">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 translate-y-1"
              enterTo="opacity-100 translate-y-0"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 translate-y-0"
              leaveTo="opacity-0 translate-y-1"
            >
              <Dialog.Panel className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
                <Dialog.Title className="text-lg font-semibold text-slate-900">{title}</Dialog.Title>
                <div className="mt-4 text-sm text-slate-600">{children}</div>
                <div className="mt-6 flex justify-end gap-3">
                  <Button variant="secondary" onClick={onClose}>
                    Закрыть
                  </Button>
                  {primaryAction ? (
                    <Button onClick={primaryAction.onClick} loading={primaryAction.loading}>
                      {primaryAction.label}
                    </Button>
                  ) : null}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
