'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';
import type { Dictionary, Language } from '@/types';

interface BreadcrumbsProps {
  lang: Language;
  dict: Dictionary;
}

export function Breadcrumbs({ lang, dict }: BreadcrumbsProps) {
  const pathname = usePathname();
  const segments = pathname.replace(`/${lang}`, '').split('/').filter(Boolean);
  const labelForSegment = (seg: string) => {
    const labels: Record<string, string> = {
      dashboard: dict.breadcrumbs.dashboard,
      learn: dict.nav.learn,
      benchmark: dict.nav.benchmark,
      roadmap: dict.nav.roadmap,
      timeline: dict.nav.timeline,
      log: dict.nav.scientificLog,
      'scientific-log': dict.nav.scientificLog,
    };

    return labels[seg] ?? seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' ');
  };
  const crumbs = [
    { label: dict.breadcrumbs.home, href: `/${lang}/dashboard` },
    ...segments.map((seg, i) => ({
      label: labelForSegment(seg),
      href: `/${lang}/${segments.slice(0, i + 1).join('/')}`,
    })),
  ];

  return (
    <nav aria-label="breadcrumb" className="flex min-w-0 items-center gap-1.5 text-sm">
      <Link
        href={`/${lang}/dashboard`}
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/[0.07] bg-white/[0.03] text-slate-400 transition-colors hover:text-white"
      >
        <Home size={14} />
      </Link>
      {crumbs.slice(1).map((crumb, i) => (
        <span key={crumb.href} className="flex min-w-0 items-center gap-1.5">
          <ChevronRight size={12} className="shrink-0 text-white/20" />
          {i === crumbs.length - 2 ? (
            <span className="truncate text-xs font-medium uppercase tracking-[0.14em] text-slate-200">
              {crumb.label}
            </span>
          ) : (
            <Link href={crumb.href} className="truncate text-slate-500 transition-colors hover:text-slate-200">
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
