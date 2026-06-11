'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { ScientificLogEntry, Language } from '@/types';

interface ScientificLogProps {
  entries: ScientificLogEntry[];
  lang: Language;
}

const SEVERITY_CONFIG = {
  info: { color: 'text-sky-200', bg: 'bg-sky-300/[0.055]', border: 'border-sky-200/14', dot: 'bg-sky-200', label: 'INFO' },
  success: { color: 'text-emerald-200', bg: 'bg-emerald-300/[0.055]', border: 'border-emerald-200/14', dot: 'bg-emerald-200', label: 'OK' },
  warning: { color: 'text-amber-200', bg: 'bg-amber-300/[0.055]', border: 'border-amber-200/14', dot: 'bg-amber-200', label: 'WARN' },
  error: { color: 'text-red-200', bg: 'bg-red-300/[0.055]', border: 'border-red-200/14', dot: 'bg-red-200', label: 'ERR' },
  insight: { color: 'text-violet-200', bg: 'bg-violet-300/[0.055]', border: 'border-violet-200/14', dot: 'bg-violet-200', label: 'INSIGHT' },
};

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return `${d.toISOString().replace('T', ' ').slice(0, 19)} UTC`;
}

export function ScientificLog({ entries, lang }: ScientificLogProps) {
  return (
    <GlassPanel density="compact" className="font-mono">
      <div className="mb-4 flex items-center justify-between gap-4 border-b border-white/[0.07] pb-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex gap-1.5">
            <div className="h-2.5 w-2.5 rounded-full bg-red-300/55" />
            <div className="h-2.5 w-2.5 rounded-full bg-amber-200/55" />
            <div className="h-2.5 w-2.5 rounded-full bg-emerald-200/55" />
          </div>
          <span className="truncate text-xs text-slate-400">
            neurosymbolic-atlas / scientific.log
          </span>
        </div>
        <span className="hidden text-[10px] uppercase tracking-[0.16em] text-slate-500 sm:inline">
          {lang === 'es' ? 'registro experimental' : 'experimental record'}
        </span>
      </div>

      <div className="space-y-2 text-xs">
        {entries.map((entry, index) => {
          const cfg = SEVERITY_CONFIG[entry.severity];
          return (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: 10, filter: 'blur(6px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.45, delay: index * 0.035, ease: [0.22, 1, 0.36, 1] }}
              className={cn(
                'grid gap-3 rounded-2xl border px-4 py-3 transition-colors hover:bg-white/[0.045] sm:grid-cols-[4.5rem_1fr_auto]',
                cfg.bg,
                cfg.border
              )}
            >
              <span className={cn('font-bold tracking-[0.10em]', cfg.color)}>[{cfg.label}]</span>
              <div className="min-w-0 space-y-1">
                <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500">
                  <span>{formatTimestamp(entry.timestamp)}</span>
                  <span>/</span>
                  <span className="text-slate-400">{entry.phase}</span>
                </div>
                <p className="leading-relaxed text-slate-200/85">{entry.message[lang]}</p>
                {entry.details && (
                  <p className="border-l border-white/10 pl-3 text-[11px] leading-relaxed text-slate-400">
                    {entry.details}
                  </p>
                )}
              </div>
              <div className="hidden items-start pt-1 sm:flex">
                <div className={cn('h-1.5 w-1.5 rounded-full shadow-[0_0_18px_currentColor]', cfg.dot)} />
              </div>
            </motion.div>
          );
        })}
      </div>
    </GlassPanel>
  );
}
