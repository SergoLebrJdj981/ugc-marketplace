'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface Crumb {
  href: string;
  label: string;
}

function buildCrumbs(pathname: string): Crumb[] {
  const segments = pathname.split('/').filter(Boolean);
  const crumbs: Crumb[] = [{ href: '/', label: 'Главная' }];
  let current = '';

  segments.forEach((segment) => {
    current += `/${segment}`;
    crumbs.push({ href: current, label: segment.charAt(0).toUpperCase() + segment.slice(1) });
  });

  return crumbs;
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const crumbs = buildCrumbs(pathname);

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-slate-500">
      {crumbs.map((crumb, index) => (
        <span key={crumb.href} className="inline-flex items-center gap-2">
          {index > 0 ? <span className="text-slate-400">/</span> : null}
          <Link href={crumb.href} className="hover:text-slate-900">
            {crumb.label}
          </Link>
        </span>
      ))}
    </nav>
  );
}
