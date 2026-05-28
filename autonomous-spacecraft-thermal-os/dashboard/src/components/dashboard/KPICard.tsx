'use client';

import { motion } from 'framer-motion';
import { TrendingDown, TrendingUp, Minus } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { PremiumCard } from '@/components/ui/PremiumCard';
import type { KPIEntry, Language } from '@/types';

interface KPICardProps {
  kpi: KPIEntry;
  lang: Language;
  index?: number;
}

const COLOR_MAP = {
  cyan: {
    accent: 'text-cyan-100',
    wash: 'from-cyan-300/12',
    line: 'bg-cyan-200/50',
  },
  blue: {
    accent: 'text-sky-100',
    wash: 'from-sky-300/12',
    line: 'bg-sky-200/50',
  },
  violet: {
    accent: 'text-violet-100',
    wash: 'from-violet-300/12',
    line: 'bg-violet-200/50',
  },
  emerald: {
    accent: 'text-emerald-100',
    wash: 'from-emerald-300/12',
    line: 'bg-emerald-200/50',
  },
  amber: {
    accent: 'text-amber-100',
    wash: 'from-amber-300/12',
    line: 'bg-amber-200/50',
  },
};

const TREND_ICON = {
  up: TrendingUp,
  down: TrendingDown,
  stable: Minus,
};

function numericValue(value: string | number) {
  if (typeof value === 'number') return value;
  if (!/^[\d.,]+\s*%?$/.test(value)) return null;
  const parsed = Number.parseFloat(value.replace(/[^\d.-]/g, ''));
  return Number.isFinite(parsed) ? parsed : null;
}

export function KPICard({ kpi, lang, index = 0 }: KPICardProps) {
  const colors = COLOR_MAP[kpi.color ?? 'cyan'];
  const TrendIcon = TREND_ICON[kpi.trend ?? 'stable'];
  const numeric = numericValue(kpi.value);
  const suffix = typeof kpi.value === 'string' && kpi.value.includes('%') ? '%' : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.65, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
    >
      <PremiumCard className="h-full p-5">
        <div className={cn('pointer-events-none absolute inset-0 bg-gradient-to-br via-transparent to-transparent', colors.wash)} />
        <div className={cn('mb-5 h-px w-10', colors.line)} />

        <p className="metric-label mb-3">{kpi.label[lang]}</p>

        <div className="flex items-end gap-2">
          <span className={cn('text-3xl font-semibold tabular-nums leading-none tracking-normal', colors.accent)}>
            {numeric !== null && String(kpi.value).length < 8 ? (
              <AnimatedCounter value={numeric} decimals={String(kpi.value).includes('.') ? 2 : 0} suffix={suffix} />
            ) : (
              kpi.value
            )}
          </span>
          {kpi.unit && <span className="pb-1 text-sm font-medium text-slate-400">{kpi.unit}</span>}
        </div>

        {kpi.trend && (
          <div className="mt-4 flex items-center gap-2 text-xs text-slate-400">
            <TrendIcon
              size={13}
              className={cn(
                kpi.trend === 'up' ? 'text-emerald-200' : kpi.trend === 'down' ? 'text-red-300' : 'text-slate-500'
              )}
            />
            <span>{kpi.trendValue ?? (lang === 'es' ? 'estable' : 'stable')}</span>
          </div>
        )}

        {kpi.description && (
          <p className="mt-3 text-xs leading-relaxed text-slate-400/80">{kpi.description[lang]}</p>
        )}
      </PremiumCard>
    </motion.div>
  );
}
