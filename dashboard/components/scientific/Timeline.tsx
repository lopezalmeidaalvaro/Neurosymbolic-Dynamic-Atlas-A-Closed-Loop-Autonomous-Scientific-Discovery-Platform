'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Clock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import type { TimelineEvent, Language } from '@/types';

interface TimelineProps {
  events: TimelineEvent[];
  lang: Language;
}

const STATUS_CONFIG = {
  completed: {
    icon: CheckCircle2,
    dotColor: 'bg-emerald-400',
    lineColor: 'bg-emerald-400/30',
    textColor: 'text-emerald-400',
    cardBorder: 'border-white/[0.06]',
    label: 'Completed',
  },
  active: {
    icon: Zap,
    dotColor: 'bg-cyan-400',
    lineColor: 'bg-cyan-400/30',
    textColor: 'text-cyan-400',
    cardBorder: 'border-cyan-500/30',
    label: 'Active',
  },
  planned: {
    icon: Clock,
    dotColor: 'bg-white/20',
    lineColor: 'bg-white/10',
    textColor: 'text-white/30',
    cardBorder: 'border-white/[0.04]',
    label: 'Planned',
  },
};

export function Timeline({ events, lang }: TimelineProps) {
  const { complexityMode } = useAppStore();

  return (
    <div className="relative">
      {events.map((event, index) => {
        const config = STATUS_CONFIG[event.status];
        const Icon = config.icon;
        const isLast = index === events.length - 1;

        // Prefer semantic description if available for active mode
        const description =
          event.semanticDescription
            ? event.semanticDescription[complexityMode][lang]
            : event.description[lang];

        return (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.06 }}
            className="relative flex gap-5 pb-8"
          >
            {/* ── Connector line ──────────────────────── */}
            {!isLast && (
              <div className="absolute left-[18px] top-10 bottom-0 w-px bg-white/[0.06]" />
            )}

            {/* ── Dot ─────────────────────────────────── */}
            <div className="relative z-10 shrink-0 mt-1">
              <div
                className={cn(
                  'w-9 h-9 rounded-full flex items-center justify-center border',
                  event.status === 'active'
                    ? 'bg-cyan-500/10 border-cyan-500/30'
                    : event.status === 'completed'
                    ? 'bg-emerald-500/10 border-emerald-500/20'
                    : 'bg-white/[0.03] border-white/10'
                )}
              >
                <Icon
                  size={15}
                  className={cn(
                    config.textColor,
                    event.status === 'active' && 'animate-pulse'
                  )}
                />
              </div>
            </div>

            {/* ── Card ─────────────────────────────────── */}
            <div
              className={cn(
                'flex-1 rounded-xl border p-4 bg-white/[0.02] backdrop-blur-sm transition-colors',
                config.cardBorder,
                event.status === 'active' && 'bg-cyan-500/[0.03]'
              )}
            >
              {/* Phase badge + Date */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  {event.phaseName && (
                    <span className={cn('text-[10px] font-semibold uppercase tracking-widest px-1.5 py-0.5 rounded border', config.textColor,
                      event.status === 'active'
                        ? 'bg-cyan-500/10 border-cyan-500/20'
                        : event.status === 'completed'
                        ? 'bg-emerald-500/10 border-emerald-500/20'
                        : 'bg-white/[0.03] border-white/10 text-white/25'
                    )}>
                      {event.phaseName[lang]}
                    </span>
                  )}
                  <span className={cn('text-[10px] font-medium', config.textColor)}>
                    {config.label}
                  </span>
                </div>
                <span className="text-xs text-white/25">{event.date}</span>
              </div>

              {/* Title */}
              <h3 className="text-sm font-semibold text-white/85 mb-1.5">
                {event.title[lang]}
              </h3>

              {/* Description (semantic) */}
              <motion.p
                key={`${complexityMode}-${lang}-${event.id}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
                className={cn(
                  'text-xs leading-relaxed',
                  event.status === 'planned' ? 'text-white/25' : 'text-white/50'
                )}
              >
                {description}
              </motion.p>

              {/* Tags */}
              {event.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {event.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.04] text-white/30 border border-white/[0.06]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
