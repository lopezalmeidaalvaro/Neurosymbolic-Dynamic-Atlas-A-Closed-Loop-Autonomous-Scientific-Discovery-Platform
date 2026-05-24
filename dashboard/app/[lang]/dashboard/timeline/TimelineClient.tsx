'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, Clock, Zap, Cpu, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { KaTeX } from '@/components/ui/KaTeX';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { TimelineEvent, Language } from '@/types';

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

// SVG blueprinted visualizer components
function PhaseBlueprint({ phaseId }: { phaseId: string }) {
  if (phaseId === 'phase-1') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <path d="M 5,12 L 20,4 L 35,20 L 50,2 L 65,18 L 80,10 L 95,12" fill="none" stroke="#22d3ee" strokeWidth="0.8" />
        <line x1="0" y1="12" x2="100" y2="12" stroke="rgba(255,255,255,0.06)" strokeWidth="0.5" strokeDasharray="2 2" />
        <circle cx="50" cy="2" r="1.5" fill="#f59e0b" />
        <circle cx="35" cy="20" r="1.5" fill="#a78bfa" />
      </svg>
    );
  }
  if (phaseId === 'phase-4') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <rect x="35" y="2" width="30" height="6" rx="1.5" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
        <rect x="35" y="10" width="30" height="6" rx="1.5" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
        <rect x="35" y="18" width="30" height="6" rx="1.5" fill="none" stroke="#a78bfa" strokeWidth="0.8" />
        <path d="M 20,5 L 35,5 M 20,13 L 35,13 M 20,21 L 35,21" stroke="#22d3ee" strokeWidth="0.8" strokeDasharray="1 1" />
      </svg>
    );
  }
  if (phaseId === 'phase-6') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <path d="M 5,12 L 30,12 M 30,12 L 60,6 M 30,12 L 60,18 M 60,6 L 90,3 M 60,6 L 90,9 M 60,18 L 90,15 M 60,18 L 90,21" stroke="#22d3ee" strokeWidth="0.8" fill="none" />
      </svg>
    );
  }
  if (phaseId === 'phase-7') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <rect x="5" y="4" width="10" height="16" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="17" y="4" width="10" height="16" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="29" y="4" width="10" height="16" fill="rgba(139,92,246,0.12)" stroke="#a78bfa" strokeWidth="0.5" />
        <rect x="41" y="4" width="10" height="16" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="53" y="4" width="10" height="16" fill="rgba(245,158,11,0.12)" stroke="#f59e0b" strokeWidth="0.5" />
        <rect x="65" y="4" width="10" height="16" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
        <rect x="77" y="4" width="10" height="16" fill="rgba(139,92,246,0.12)" stroke="#a78bfa" strokeWidth="0.5" />
        <rect x="89" y="4" width="6" height="16" fill="rgba(34,211,238,0.12)" stroke="#22d3ee" strokeWidth="0.5" />
      </svg>
    );
  }
  if (phaseId === 'phase-11') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <circle cx="15" cy="6" r="2" fill="#22d3ee" />
        <circle cx="35" cy="18" r="2" fill="#22d3ee" />
        <circle cx="55" cy="8" r="2" fill="#a78bfa" />
        <circle cx="85" cy="15" r="2" fill="#a78bfa" />
        <line x1="15" y1="6" x2="35" y2="18" stroke="#22d3ee" strokeWidth="0.5" />
        <line x1="35" y1="18" x2="55" y2="8" stroke="#a78bfa" strokeWidth="0.5" strokeDasharray="1 1" />
        <line x1="55" y1="8" x2="85" y2="15" stroke="#a78bfa" strokeWidth="0.5" />
      </svg>
    );
  }
  if (phaseId === 'phase-13') {
    return (
      <svg viewBox="0 0 100 24" className="w-full h-8 opacity-65">
        <rect x="5" y="3" width="90" height="5" rx="1" fill="rgba(255,255,255,0.06)" />
        <rect x="5" y="3" width="90" height="5" rx="1" fill="#22d3ee" className="animate-pulse" style={{ width: '95%' }} />
        
        <rect x="5" y="13" width="90" height="5" rx="1" fill="rgba(255,255,255,0.06)" />
        <rect x="5" y="13" width="90" height="5" rx="1" fill="#ef4444" style={{ width: '8%' }} />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 100 24" className="w-full h-8 opacity-45">
      <path d="M 0,12 L 100,12" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" strokeDasharray="2 2" />
      <motion.circle
        cx="50" cy="12" r="3" fill="#22d3ee"
        animate={{ scale: [1, 1.4, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />
    </svg>
  );
}

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
      {/* 1. Milestone Counters */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { icon: CheckCircle2, count: completed, label: labels.completed, tone: 'success' as const, color: 'text-emerald-400' },
          { icon: Zap, count: active, label: labels.active, tone: 'active' as const, color: 'text-cyan-400' },
          { icon: Clock, count: planned, label: labels.planned, tone: 'neutral' as const, color: 'text-slate-400' },
        ].map(({ icon: Icon, count, label, tone, color }, index) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            transition={{ duration: 0.65, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
          >
            <GlassPanel density="compact" tone={tone} className="rounded-2xl border border-white/[0.08]">
              <Icon size={16} className={color} />
              <p className="metric-label mt-4">{label}</p>
              <p className="mt-2 text-3xl font-semibold tabular-nums text-white">
                <AnimatedCounter value={count} />
              </p>
            </GlassPanel>
          </motion.div>
        ))}
      </div>

      {/* 2. Central Waterfall Timeline with Scroll Reveal */}
      <GlassPanel density="spacious" className="relative overflow-hidden border border-white/[0.08]">
        {/* Decorative elements */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(139,92,246,0.035),transparent_65%)] pointer-events-none" />
        <div className="absolute inset-0 scientific-grid opacity-[0.03] pointer-events-none" />

        <div className="mb-10 flex items-center justify-between gap-4 border-b border-white/[0.06] pb-5">
          <div>
            <p className="metric-label">{lang === 'es' ? 'Secuencia experimental' : 'Experimental sequence'}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white/90">
              {lang === 'es' ? 'Hitos del Pipeline Científico' : 'Scientific Pipeline Milestones'}
            </h2>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.035] px-3 py-1.5 text-xs text-slate-400 sm:flex">
            <Cpu size={13} className="text-cyan-400" />
            <span className="font-mono">{complexityMode}</span>
          </div>
        </div>

        {/* Central timeline line */}
        <div className="relative">
          {/* Main vertical line for waterfall view (centered on desktop, left on mobile) */}
          <div className="absolute left-[23px] sm:left-1/2 top-4 bottom-10 w-[2px] bg-gradient-to-b from-cyan-500 via-violet-600 to-transparent -translate-x-1/2" />

          <div className="space-y-12">
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
                  initial={{ opacity: 0, x: isEven ? -40 : 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                  className={cn(
                    "relative grid grid-cols-1 sm:grid-cols-2 gap-8 items-center",
                    isEven ? "sm:text-right" : "sm:text-left sm:flex-row-reverse"
                  )}
                >
                  {/* Central Node Dot */}
                  <div className="absolute left-[23px] sm:left-1/2 top-[6px] -translate-x-1/2 z-20">
                    <div className={cn(
                      "flex h-[26px] w-[26px] items-center justify-center rounded-full border bg-[#060a14] transition-all",
                      config.dot
                    )}>
                      <Icon size={11} className={cn(config.textColor, event.status === 'active' && 'animate-pulse')} />
                    </div>
                  </div>

                  {/* Timeline Card */}
                  <div className={cn(
                    "pl-12 sm:pl-0",
                    isEven ? "sm:col-start-1 sm:pr-10" : "sm:col-start-2 sm:pl-10"
                  )}>
                    <div className={cn(
                      "rounded-3xl border p-5 relative overflow-hidden transition-all duration-300 hover:bg-white/[0.025] group shadow-2xl",
                      config.surface
                    )}>
                      {/* Floating overlay gradients */}
                      <div className="absolute inset-0 bg-[radial-gradient(circle_at_16%_0%,rgba(255,255,255,0.015),transparent_38%)] pointer-events-none" />

                      <div className={cn(
                        "flex flex-wrap items-center gap-2 mb-3 justify-start",
                        isEven ? "sm:justify-end" : "sm:justify-start"
                      )}>
                        {event.phaseName && (
                          <span className={cn(
                            "rounded-full border border-white/[0.08] bg-white/[0.035] px-2.5 py-0.5 text-[9px] font-bold uppercase tracking-[0.12em]",
                            config.textColor
                          )}>
                            {event.phaseName[lang]}
                          </span>
                        )}
                        <span className={cn("text-[9px] font-bold uppercase tracking-[0.14em]", config.textColor)}>
                          {config.label[lang]}
                        </span>
                        <span className="font-mono text-[10px] text-slate-500 ml-auto sm:ml-0">{event.date}</span>
                      </div>

                      <h3 className="text-base font-bold leading-snug text-white group-hover:text-cyan-300 transition-colors">
                        {event.title[lang]}
                      </h3>

                      <p className="mt-3 text-xs leading-relaxed text-slate-400 group-hover:text-slate-300 transition-colors">
                        {description}
                      </p>

                      {/* Mathematical rigor in the timeline */}
                      {PHASE_FORMULAS[event.id] && (
                        <div className="mt-4 py-2 border-y border-white/[0.05] bg-white/[0.01] rounded-xl flex items-center justify-center px-3 overflow-x-auto">
                          <KaTeX formula={PHASE_FORMULAS[event.id]!} className="text-[10px] text-cyan-200/80" />
                        </div>
                      )}

                      {/* Graphical visual blueprint illustration */}
                      <div className="mt-4 border border-white/[0.06] rounded-2xl bg-black/30 p-2.5 flex items-center justify-center">
                        <PhaseBlueprint phaseId={event.id} />
                      </div>

                      {/* Milestone Tags */}
                      {event.tags.length > 0 && (
                        <div className={cn(
                          "mt-4 flex flex-wrap gap-1.5",
                          isEven ? "sm:justify-end" : "sm:justify-start"
                        )}>
                          {event.tags.map((tag) => (
                            <span
                              key={tag}
                              className="rounded-full border border-white/[0.07] bg-white/[0.03] px-2.5 py-0.5 text-[9px] text-slate-500 font-mono"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Empty placeholder Column (Desktop only) */}
                  <div className="hidden sm:block" />
                </motion.div>
              );
            })}
          </div>
        </div>
      </GlassPanel>
    </>
  );
}
