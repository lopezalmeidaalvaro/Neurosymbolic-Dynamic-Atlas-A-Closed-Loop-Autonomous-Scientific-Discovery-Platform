'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, BookOpen, GitBranch, BarChart3, ScrollText,
  Map, ChevronLeft, ChevronRight, Zap, ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { NAV_ITEMS, APP_NAME, SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH, GITHUB_URL } from '@/constants';
import type { Language } from '@/types';

const ICON_MAP: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  LayoutDashboard, BookOpen, GitBranch, BarChart3, ScrollText, Map,
};

interface SidebarProps {
  lang: Language;
}

export function Sidebar({ lang }: SidebarProps) {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();
  const pathname = usePathname();

  const isActive = (href: string) => {
    const full = `/${lang}${href}`;
    return href === '/dashboard'
      ? pathname === full
      : pathname.startsWith(full);
  };

  return (
    <motion.aside
      animate={{ width: sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="relative flex flex-col h-screen border-r border-white/[0.06] bg-[#030712]/90 backdrop-blur-xl shrink-0 z-30"
    >
      {/* ── Logo / Brand ─────────────────────────────────────── */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-white/[0.06]">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 shrink-0">
          <Zap size={16} className="text-cyan-400" />
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.2 }}
              className="text-sm font-semibold text-white/90 whitespace-nowrap truncate"
            >
              {APP_NAME}
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* ── Navigation ───────────────────────────────────────── */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = ICON_MAP[item.icon];
          const active = isActive(item.href);
          return (
            <Link
              key={item.id}
              href={`/${lang}${item.href}`}
              title={item.label[lang]}
            >
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors duration-150 relative group',
                  active
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    : 'text-white/50 hover:text-white/80 hover:bg-white/[0.04]'
                )}
              >
                {Icon && <Icon size={16} className="shrink-0" />}
                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="flex-1 whitespace-nowrap truncate"
                    >
                      {item.label[lang]}
                    </motion.span>
                  )}
                </AnimatePresence>
                {/* Badge */}
                {item.badge && !sidebarCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/20 font-medium">
                    {item.badge}
                  </span>
                )}
                {/* Active indicator */}
                {active && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 rounded-r bg-cyan-400"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* ── Footer ───────────────────────────────────────────── */}
      <div className="p-2 border-t border-white/[0.06]">
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-white/40 hover:text-white/70 hover:bg-white/[0.04] transition-colors"
          title="GitHub"
        >
          <ExternalLink size={16} className="shrink-0" />
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="text-xs whitespace-nowrap"
              >
                View on GitHub
              </motion.span>
            )}
          </AnimatePresence>
        </a>
      </div>

      {/* ── Collapse toggle ──────────────────────────────────── */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 z-40 flex items-center justify-center w-6 h-6 rounded-full bg-[#0d1117] border border-white/10 text-white/50 hover:text-white/90 hover:border-white/20 transition-all"
        aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {sidebarCollapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </motion.aside>
  );
}
