'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Clock, FlaskConical, Zap } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { TimelineEvent, Language } from '@/types';

const STATUS_CONFIG = {
  completed: {
    icon: CheckCircle2,
    textColor: 'text-emerald-100',
    rail: 'from-emerald-200/35 via-white/10 to-transparent',
    surface: 'border-emerald-100/14 bg-emerald-100/[0.035]',
    dot: 'border-emerald-100/22 bg-emerald-100/10 shadow-[0_0_30px_rgba(167,243,208,0.14)]',
    label: { en: 'Completed', es: 'Completado' },
  },
  active: {
    icon: Zap,
    textColor: 'text-cyan-100',
    rail: 'from-cyan-200/45 via-cyan-100/16 to-transparent',
    surface: 'border-cyan-100/18 bg-cyan-100/[0.055] shadow-[0_20px_70px_rgba(56,189,248,0.08)]',
    dot: 'border-cyan-100/28 bg-cyan-100/12 shadow-[0_0_34px_rgba(125,211,252,0.22)]',
    label: { en: 'Active', es: 'Activo' },
  },
  planned: {
    icon: Clock,
    textColor: 'text-slate-500',
    rail: 'from-white/10 via-white/[0.04] to-transparent',
    surface: 'border-white/[0.07] bg-white/[0.025]',
    dot: 'border-white/10 bg-white/[0.035]',
    label: { en: 'Planned', es: 'Planificado' },
  },
};

interface TimelineClientProps {
  events: TimelineEvent[];
  lang: Language;
  labels: { completed: string; active: string; planned: string };
}

export function TimelineClient({ events, lang, labels }: TimelineClientProps) {
  const { complexityMode } = useAppStore();

  const completed = events.filter((e) => e.status === 'completed').length;
  const active = events.filter((e) => e.status === 'active').length;
  const planned = events.filter((e) => e.status === 'planned').length;

  return (
    <>
      <ScrollReveal className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { icon: CheckCircle2, count: completed, label: labels.completed, tone: 'success' as const, color: 'text-emerald-100' },
          { icon: Zap, count: active, label: labels.active, tone: 'active' as const, color: 'text-cyan-100' },
          { icon: Clock, count: planned, label: labels.planned, tone: 'neutral' as const, color: 'text-slate-400' },
        ].map(({ icon: Icon, count, label, tone, color }, index) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            transition={{ duration: 0.65, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
          >
            <GlassPanel density="compact" tone={tone} className="rounded-2xl">
              <Icon size={16} className={color} />
              <p className="metric-label mt-4">{label}</p>
              <p className="mt-2 text-3xl font-semibold tabular-nums text-white">
                <AnimatedCounter value={count} />
              </p>
            </GlassPanel>
          </motion.div>
        ))}
      </ScrollReveal>

      <ScrollReveal>
        <GlassPanel density="spacious">
          <div className="mb-7 flex items-center justify-between gap-4">
            <div>
              <p className="metric-label">{lang === 'es' ? 'Secuencia experimental' : 'Experimental sequence'}</p>
              <h2 className="mt-2 text-2xl font-semibold text-white/90">
                {lang === 'es' ? 'Hitos de investigacion' : 'Research milestones'}
              </h2>
            </div>
            <div className="hidden items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.035] px-3 py-1.5 text-xs text-slate-400 sm:flex">
              <FlaskConical size={13} />
              {complexityMode}
            </div>
          </div>

          <div className="relative">
            {events.map((event, index) => {
              const config = STATUS_CONFIG[event.status];
              const Icon = config.icon;
              const isLast = index === events.length - 1;
              const description = event.semanticDescription
                ? event.semanticDescription[complexityMode][lang]
                : event.description[lang];

              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -14, filter: 'blur(8px)' }}
                  animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                  transition={{ duration: 0.58, delay: index * 0.055, ease: [0.22, 1, 0.36, 1] }}
                  className="relative grid gap-4 pb-6 sm:grid-cols-[3rem_1fr]"
                >
                  {!isLast && (
                    <div className={cn('absolute bottom-0 left-6 top-12 w-px bg-gradient-to-b', config.rail)} />
                  )}

                  <div className="relative z-10 flex justify-start sm:justify-center">
                    <div className={cn('flex h-12 w-12 items-center justify-center rounded-2xl border backdrop-blur-xl', config.dot)}>
                      <Icon size={16} className={cn(config.textColor, event.status === 'active' && 'animate-pulse')} />
                    </div>
                  </div>

                  <div className={cn('rounded-2xl border p-5 transition-colors hover:bg-white/[0.045]', config.surface)}>
                    <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap items-center gap-2">
                        {event.phaseName && (
                          <span className={cn('rounded-full border border-white/[0.08] bg-white/[0.035] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em]', config.textColor)}>
                            {event.phaseName[lang]}
                          </span>
                        )}
                        <span className={cn('text-[10px] font-semibold uppercase tracking-[0.14em]', config.textColor)}>
                          {config.label[lang]}
                        </span>
                      </div>
                      <span className="font-mono text-xs text-slate-500">{event.date}</span>
                    </div>

                    <h3 className="text-base font-semibold leading-snug text-white/90">
                      {event.title[lang]}
                    </h3>

                    <motion.p
                      key={`${complexityMode}-${lang}-${event.id}`}
                      initial={{ opacity: 0, y: 3 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.25 }}
                      className={cn(
                        'mt-3 text-sm leading-7',
                        event.status === 'planned' ? 'text-slate-500' : 'text-slate-300/72'
                      )}
                    >
                      {description}
                    </motion.p>

                    {event.tags.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-1.5">
                        {event.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded-full border border-white/[0.07] bg-white/[0.03] px-2 py-1 text-[10px] text-slate-400"
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
        </GlassPanel>
      </ScrollReveal>
    </>
  );
}
