'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import {
  BarChart3,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  GitBranch,
  LayoutDashboard,
  Map,
  Orbit,
  ScrollText,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { APP_NAME, GITHUB_URL, NAV_ITEMS, SIDEBAR_COLLAPSED_WIDTH, SIDEBAR_WIDTH } from '@/constants';
import { useAppStore } from '@/stores/appStore';
import type { Language } from '@/types';

const ICON_MAP: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  LayoutDashboard,
  BookOpen,
  Sparkles,
  GitBranch,
  BarChart3,
  ScrollText,
  Map,
};

interface AdaptiveSidebarProps {
  lang: Language;
}

export function AdaptiveSidebar({ lang }: AdaptiveSidebarProps) {
  const { sidebarCollapsed, focusModeEnabled, toggleSidebar } = useAppStore();
  const pathname = usePathname();

  const isActive = (href: string) => {
    const full = `/${lang}${href}`;
    return href === '/dashboard' ? pathname === full : pathname.startsWith(full);
  };

  return (
    <motion.aside
      animate={{
        width: focusModeEnabled ? 0 : sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
        opacity: focusModeEnabled ? 0 : 1,
      }}
      transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        'relative z-30 hidden h-screen shrink-0 flex-col overflow-hidden border-r border-white/[0.08] bg-[rgba(3,6,14,0.72)] backdrop-blur-2xl md:flex',
        focusModeEnabled && 'pointer-events-none'
      )}
    >
      <div aria-hidden className="absolute inset-0 scientific-grid opacity-[0.06]" />
      <div aria-hidden className="absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-cyan-100/18 to-transparent" />

      <div className="relative flex h-20 items-center gap-3 px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-cyan-100/20 bg-white/[0.045] shadow-[0_0_34px_rgba(125,211,252,0.10)]">
          <Orbit size={17} className="text-cyan-100/85" />
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.22 }}
              className="min-w-0"
            >
              <p className="truncate text-sm font-semibold text-white/90">{APP_NAME}</p>
              <p className="truncate text-[10px] uppercase tracking-[0.18em] text-cyan-100/40">
                Research OS
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <nav className="relative flex-1 space-y-1 overflow-y-auto px-2 py-3">
        {NAV_ITEMS.map((item, index) => {
          const Icon = ICON_MAP[item.icon];
          const active = isActive(item.href);

          return (
            <Link key={item.id} href={`/${lang}${item.href}`} title={item.label[lang]}>
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.035, duration: 0.45 }}
                whileHover={{ x: 2 }}
                className={cn(
                  'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors duration-300',
                  active
                    ? 'text-white'
                    : 'text-slate-400 hover:bg-white/[0.045] hover:text-slate-100'
                )}
              >
                {active && (
                  <motion.div
                    layoutId="sidebar-active-surface"
                    className="absolute inset-0 rounded-xl border border-cyan-100/18 bg-cyan-100/[0.055] shadow-[0_16px_50px_rgba(56,189,248,0.08)]"
                    transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                  />
                )}
                <span
                  className={cn(
                    'relative flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border transition-colors',
                    active
                      ? 'border-cyan-100/20 bg-cyan-100/10 text-cyan-100'
                      : 'border-white/[0.06] bg-white/[0.025] text-slate-400 group-hover:text-slate-100'
                  )}
                >
                  {Icon && <Icon size={15} />}
                </span>
                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="relative flex-1 truncate"
                    >
                      {item.label[lang]}
                    </motion.span>
                  )}
                </AnimatePresence>
                {item.badge && !sidebarCollapsed && (
                  <span className="relative rounded-full border border-amber-100/20 bg-amber-100/10 px-2 py-0.5 text-[10px] font-semibold text-amber-100/80">
                    {item.badge}
                  </span>
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      <div className="relative p-2">
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-slate-500 transition-colors hover:bg-white/[0.04] hover:text-slate-200"
          title="GitHub"
        >
          <ExternalLink size={15} className="shrink-0" />
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-xs">
                Research repository
              </motion.span>
            )}
          </AnimatePresence>
        </a>
      </div>

      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-24 z-40 flex h-6 w-6 items-center justify-center rounded-full border border-white/12 bg-[#080c16] text-white/55 shadow-lg transition-all hover:border-cyan-100/25 hover:text-white"
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {sidebarCollapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </motion.aside>
  );
}
