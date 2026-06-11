'use client';

import { Activity, Gauge, RadioTower } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAppStore } from '@/stores/appStore';
import type { Language } from '@/types';

interface ExperimentalDockProps {
  lang: Language;
}

export function ExperimentalDock({ lang }: ExperimentalDockProps) {
  const { systemStatus, activeExperimentStatus, focusModeEnabled } = useAppStore();
  const active = systemStatus === 'processing' || activeExperimentStatus === 'running';

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: focusModeEnabled ? 0 : 1, y: focusModeEnabled ? 18 : 0 }}
      transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
      className="pointer-events-none fixed bottom-5 left-1/2 z-20 hidden -translate-x-1/2 lg:block"
    >
      <div className="flex items-center gap-2 rounded-full border border-white/[0.09] bg-[rgba(5,8,16,0.66)] px-3 py-2 text-xs text-slate-300 shadow-[0_18px_60px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
        <span className="flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.035] px-3 py-1.5">
          <RadioTower size={13} className={active ? 'text-cyan-200' : 'text-slate-400'} />
          {active ? (lang === 'es' ? 'Actividad experimental' : 'Experimental activity') : (lang === 'es' ? 'Observatorio estable' : 'Stable observatory')}
        </span>
        <span className="flex items-center gap-2 px-2 py-1.5 text-slate-400">
          <Activity size={13} />
          {systemStatus}
        </span>
        <span className="flex items-center gap-2 px-2 py-1.5 text-slate-400">
          <Gauge size={13} />
          {activeExperimentStatus}
        </span>
      </div>
    </motion.div>
  );
}
