'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Clock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { KaTeX } from '@/components/ui/KaTeX';
import type { TimelineEvent, Language } from '@/types';

interface TimelineProps {
  events: TimelineEvent[];
  lang: Language;
}

const STATUS_CONFIG = {
  completed: {
    icon: CheckCircle2,
    textColor: 'text-emerald-400',
    dot: 'border-emerald-500/30 bg-emerald-500/10 shadow-[0_0_24px_rgba(16,185,129,0.15)]',
    surface: 'border-emerald-500/10 bg-emerald-500/[0.015]',
    label: { en: 'Completed', es: 'Completado' },
  },
  active: {
    icon: Zap,
    textColor: 'text-cyan-400',
    dot: 'border-cyan-500/30 bg-cyan-500/10 shadow-[0_0_24px_rgba(34,211,238,0.25)]',
    surface: 'border-cyan-500/20 bg-cyan-500/[0.025]',
    label: { en: 'Active', es: 'Activo' },
  },
  planned: {
    icon: Clock,
    textColor: 'text-slate-500',
    dot: 'border-white/10 bg-white/[0.03]',
    surface: 'border-white/[0.05] bg-white/[0.005]',
    label: { en: 'Planned', es: 'Planificado' },
  },
};

const PHASE_FORMULAS: Record<string, string> = {
  'phase-1': 'P(x) = x^5 - 5x + 1 = 0 \\quad \\text{Sturm: } \\{+, -, +, -\\}',
  'phase-4': '\\min C_{\\text{latency}} \\implies \\text{SQLite Cache}',
  'phase-6': '\\delta = \\lim_{k\\to\\infty} \\frac{a_{k-1} - a_{k-2}}{a_k - a_{k-1}} \\approx 4.6692',
  'phase-7': '\\vec{v} = (\\lambda_{\\max}, H_s, f_d, \\sigma^2, \\tau, \\kappa, \\gamma, E)',
  'phase-11': '\\kappa_g = \\frac{e(v)}{\\text{Area}} \\quad \\lambda_g > 0',
  'phase-13': '\\text{Speedup} = \\frac{T_{\\text{ROCKET}}}{T_{\\text{Embedding V2}}} \\approx 79\\times',
  'phase-14': '\\text{Hydrate}(V, D) \\implies \\text{Next.js App Router}',
  'phase-15': '\\lim_{\\Delta t \\to 0} \\text{Lag}(t) = 0 \\quad \\text{WebSocket}',
};

function PhaseBlueprint({ phaseId }: { phaseId: string }) {
  if (phaseId === 'phase-1') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <path d="M 5,12 L 20,4 L 35,20 L 50,2 L 65,18 L 80,10 L 95,12" fill="none" stroke="#22d3ee" strokeWidth="0.8" />
        <line x1="0" y1="12" x2="100" y2="12" stroke="rgba(255,255,255,0.06)" strokeWidth="0.5" strokeDasharray="2 2" />
      </svg>
    );
  }
  if (phaseId === 'phase-4') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <rect x="35" y="2" width="30" height="6" rx="1.5" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
        <rect x="35" y="10" width="30" height="6" rx="1.5" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
      </svg>
    );
  }
  if (phaseId === 'phase-6') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <path d="M 5,12 L 30,12 M 30,12 L 60,6 M 30,12 L 60,18 M 60,6 L 90,3 M 60,6 L 90,9" stroke="#22d3ee" strokeWidth="0.8" fill="none" />
      </svg>
    );
  }
  if (phaseId === 'phase-7') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <rect x="5" y="6" width="14" height="12" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="24" y="6" width="14" height="12" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="43" y="6" width="14" height="12" fill="rgba(139,92,246,0.12)" stroke="#a78bfa" strokeWidth="0.5" />
        <rect x="62" y="6" width="14" height="12" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="81" y="6" width="14" height="12" fill="rgba(245,158,11,0.12)" stroke="#f59e0b" strokeWidth="0.5" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 100 24" className="w-full h-8 opacity-45">
      <path d="M 0,12 L 100,12" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" strokeDasharray="2 2" />
    </svg>
  );
}

export function Timeline({ events, lang }: TimelineProps) {
  const { complexityMode } = useAppStore();

  return (
    <div className="relative">
      {/* Central timeline line (waterfall view) */}
      <div className="absolute left-[20px] sm:left-1/2 top-4 bottom-10 w-[2px] bg-gradient-to-b from-cyan-500/50 via-violet-600/30 to-transparent -translate-x-1/2" />

      <div className="space-y-10">
        {events.map((event, index) => {
          const config = STATUS_CONFIG[event.status];
          const Icon = config.icon;
          const isEven = index % 2 === 0;
          const description = event.semanticDescription
            ? event.semanticDescription[complexityMode][lang]
            : event.description[lang];

          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: isEven ? -24 : 24 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className={cn(
                "relative grid grid-cols-1 sm:grid-cols-2 gap-6 items-center",
                isEven ? "sm:text-right" : "sm:text-left sm:flex-row-reverse"
              )}
            >
              {/* Central Node Dot */}
              <div className="absolute left-[20px] sm:left-1/2 top-[6px] -translate-x-1/2 z-20">
                <div className={cn(
                  "flex h-[24px] w-[24px] items-center justify-center rounded-full border bg-[#060a14] transition-all",
                  config.dot
                )}>
                  <Icon size={10} className={cn(config.textColor, event.status === 'active' && 'animate-pulse')} />
                </div>
              </div>

              {/* Timeline Card */}
              <div className={cn(
                "pl-10 sm:pl-0",
                isEven ? "sm:col-start-1 sm:pr-8" : "sm:col-start-2 sm:pl-8"
              )}>
                <div className={cn(
                  "rounded-2xl border p-4 transition-all duration-300 hover:bg-white/[0.015] group",
                  config.surface
                )}>
                  <div className={cn(
                    "flex flex-wrap items-center gap-1.5 mb-2 justify-start",
                    isEven ? "sm:justify-end" : "sm:justify-start"
                  )}>
                    {event.phaseName && (
                      <span className={cn(
                        "rounded border px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-[0.12em]",
                        config.textColor,
                        "bg-white/[0.02] border-white/[0.06]"
                      )}>
                        {event.phaseName[lang]}
                      </span>
                    )}
                    <span className="font-mono text-[9px] text-slate-500">{event.date}</span>
                  </div>

                  <h3 className="text-xs font-bold leading-snug text-white/90">
                    {event.title[lang]}
                  </h3>

                  <p className="mt-2 text-[11px] leading-relaxed text-slate-400">
                    {description}
                  </p>

                  {/* Mathematical formulas block */}
                  {PHASE_FORMULAS[event.id] && (
                    <div className="mt-3 py-1.5 border-y border-white/[0.04] bg-white/[0.005] rounded-lg flex items-center justify-center px-2 overflow-x-auto">
                      <KaTeX formula={PHASE_FORMULAS[event.id]!} className="text-[9px] text-cyan-200/70" />
                    </div>
                  )}

                  {/* SVG Blueprint */}
                  <div className="mt-3 border border-white/[0.05] rounded-xl bg-black/25 p-2">
                    <PhaseBlueprint phaseId={event.id} />
                  </div>
                </div>
              </div>

              {/* Spacer Column */}
              <div className="hidden sm:block" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
