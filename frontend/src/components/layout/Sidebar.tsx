'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { twMerge } from 'tailwind-merge';

export interface SidebarLink {
  href: string;
  label: string;
  exact?: boolean;
}

interface SidebarProps {
  links: SidebarLink[];
}

export function Sidebar({ links }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white/80 px-4 py-6 backdrop-blur sm:block">
      <nav className="flex flex-col gap-1 text-sm text-slate-700">
        {links.map((link) => {
          const isActive = link.exact ? pathname === link.href : pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={twMerge(
                'rounded-lg px-3 py-2 transition hover:bg-slate-100',
                isActive ? 'bg-slate-900 text-white shadow-sm hover:bg-slate-800' : 'text-slate-700'
              )}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
