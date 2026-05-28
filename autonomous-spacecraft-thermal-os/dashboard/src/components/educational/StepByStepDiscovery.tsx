'use client';

import { useState } from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { GuidedLearningStep, Language } from '@/types';

interface StepByStepDiscoveryProps {
  steps: GuidedLearningStep[];
  lang: Language;
}

export function StepByStepDiscovery({ steps, lang }: StepByStepDiscoveryProps) {
  const [active, setActive] = useState(0);
  const { complexityMode } = useAppStore();
  const step = steps[active];

  if (!step) return null;

  return (
    <GlassPanel density="spacious" tone="active">
      <div className="mb-6">
        <p className="metric-label">{lang === 'es' ? 'Ruta guiada' : 'Guided path'}</p>
        <h2 className="mt-2 text-2xl font-semibold text-white/90">
          {lang === 'es' ? 'Como piensa el experimento' : 'How the experiment thinks'}
        </h2>
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="space-y-2">
          {steps.map((item, index) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActive(index)}
              className={cn(
                'flex w-full items-center justify-between gap-3 rounded-2xl border p-4 text-left transition-colors',
                active === index
                  ? 'border-cyan-100/22 bg-cyan-100/[0.07] text-cyan-50'
                  : 'border-white/[0.07] bg-white/[0.025] text-slate-400 hover:bg-white/[0.045] hover:text-slate-200'
              )}
            >
              <span className="text-sm font-medium">{item.title[lang]}</span>
              {active === index ? <CheckCircle2 size={15} /> : <ArrowRight size={15} />}
            </button>
          ))}
        </div>

        <div className="rounded-2xl border border-white/[0.08] bg-black/20 p-5">
          <p className="metric-label">{lang === 'es' ? 'Paso' : 'Step'} {active + 1}</p>
          <h3 className="mt-2 text-xl font-semibold text-white/90">{step.title[lang]}</h3>
          <p className="mt-4 text-base leading-8 text-slate-300/78">{step.body[complexityMode][lang]}</p>
          <div className="mt-5 rounded-2xl border border-emerald-100/14 bg-emerald-100/[0.055] p-4">
            <p className="metric-label text-emerald-100/70">{lang === 'es' ? 'Resultado cognitivo' : 'Learning outcome'}</p>
            <p className="mt-2 text-sm leading-7 text-emerald-50/78">{step.outcome[complexityMode][lang]}</p>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
