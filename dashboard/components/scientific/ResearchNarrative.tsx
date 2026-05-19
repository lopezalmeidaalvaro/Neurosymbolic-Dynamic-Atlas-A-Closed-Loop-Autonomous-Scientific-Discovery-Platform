'use client';

import { motion } from 'framer-motion';
import { ArrowRight, CircleDot } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, ScientificMemoryEntry } from '@/types';

interface ResearchNarrativeProps {
  entries: ScientificMemoryEntry[];
  lang: Language;
}

export function ResearchNarrative({ entries, lang }: ResearchNarrativeProps) {
  const { complexityMode } = useAppStore();

  return (
    <GlassPanel density="spacious">
      <div className="mb-7">
        <p className="metric-label">{lang === 'es' ? 'Viaje de investigacion' : 'Research journey'}</p>
        <h2 className="mt-2 text-2xl font-semibold text-white/90">
          {lang === 'es' ? 'De senales a memoria epistemologica' : 'From signals to epistemic memory'}
        </h2>
      </div>
      <div className="relative">
        {entries.map((entry, index) => {
          const isLast = index === entries.length - 1;
          return (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, x: -14, filter: 'blur(8px)' }}
              animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.58, delay: index * 0.06, ease: [0.22, 1, 0.36, 1] }}
              className="relative grid gap-4 pb-6 sm:grid-cols-[3rem_1fr]"
            >
              {!isLast && <div className="absolute bottom-0 left-6 top-12 w-px bg-gradient-to-b from-cyan-100/24 to-transparent" />}
              <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-100/16 bg-cyan-100/[0.06] text-cyan-100">
                <CircleDot size={16} />
              </div>
              <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-5">
                <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                  <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-2.5 py-1 text-[10px] uppercase tracking-[0.14em] text-slate-400">
                    {entry.type}
                  </span>
                  <span className="font-mono text-xs text-slate-500">{entry.date}</span>
                </div>
                <h3 className="text-lg font-semibold text-white/90">{entry.title[lang]}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-300/74">{entry.narrative[complexityMode][lang]}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {entry.linkedIds.map((id) => (
                    <span key={id} className="inline-flex items-center gap-1 rounded-full border border-white/[0.07] bg-white/[0.03] px-2 py-1 text-[10px] text-slate-500">
                      <ArrowRight size={10} />
                      {id}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </GlassPanel>
  );
}
