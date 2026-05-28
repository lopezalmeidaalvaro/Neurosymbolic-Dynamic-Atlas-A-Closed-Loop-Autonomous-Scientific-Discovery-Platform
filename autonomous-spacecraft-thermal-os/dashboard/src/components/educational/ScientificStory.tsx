'use client';

import { motion } from 'framer-motion';
import { RadioTower } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import type { Language, ScientificStoryStep } from '@/types';

interface ScientificStoryProps {
  steps: ScientificStoryStep[];
  lang: Language;
}

export function ScientificStory({ steps, lang }: ScientificStoryProps) {
  const { complexityMode } = useAppStore();

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {steps.map((step, index) => (
        <motion.div
          key={step.id}
          initial={{ opacity: 0, y: 16, filter: 'blur(8px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{ duration: 0.62, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
          className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.035] p-5"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_0%,rgba(125,211,252,0.08),transparent_34%)]" />
          <div className="relative">
            <div className="mb-5 flex items-center justify-between gap-3">
              <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-2.5 py-1 text-[10px] uppercase tracking-[0.14em] text-slate-400">
                {step.signal[lang]}
              </span>
              <RadioTower size={14} className="text-cyan-100/60" />
            </div>
            <h3 className="text-lg font-semibold text-white/90">{step.title[lang]}</h3>
            <p className="mt-3 text-sm leading-7 text-slate-300/70">{step.body[complexityMode][lang]}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
