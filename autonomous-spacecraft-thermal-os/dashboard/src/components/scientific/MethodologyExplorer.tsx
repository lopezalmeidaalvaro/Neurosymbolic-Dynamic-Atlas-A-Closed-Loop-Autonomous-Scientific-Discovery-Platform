'use client';

import { useState } from 'react';
import { FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { GuidedLearningStep, Language } from '@/types';

interface MethodologyExplorerProps {
  steps: GuidedLearningStep[];
  lang: Language;
}

export function MethodologyExplorer({ steps, lang }: MethodologyExplorerProps) {
  const [active, setActive] = useState(0);
  const { complexityMode } = useAppStore();
  const step = steps[active];

  if (!step) return null;

  return (
    <GlassPanel density="spacious" tone="success">
      <div className="mb-5 flex items-center gap-3">
        <FlaskConical size={17} className="text-emerald-100" />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Metodologia explorable' : 'Methodology explorer'}</p>
          <h2 className="mt-1 text-xl font-semibold text-white/90">
            {lang === 'es' ? 'Del dato al hallazgo' : 'From data to finding'}
          </h2>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {steps.map((item, index) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setActive(index)}
            className={cn(
              'rounded-full border px-3 py-1.5 text-xs transition-colors',
              active === index
                ? 'border-emerald-100/24 bg-emerald-100/10 text-emerald-50'
                : 'border-white/[0.08] bg-white/[0.03] text-slate-400 hover:text-slate-200'
            )}
          >
            {index + 1}. {item.title[lang]}
          </button>
        ))}
      </div>
      <div className="mt-5 rounded-2xl border border-white/[0.08] bg-black/20 p-5">
        <h3 className="text-lg font-semibold text-white/90">{step.title[lang]}</h3>
        <p className="mt-3 text-sm leading-7 text-slate-300/74">{step.body[complexityMode][lang]}</p>
        <p className="mt-4 text-sm leading-7 text-emerald-50/76">{step.outcome[complexityMode][lang]}</p>
      </div>
    </GlassPanel>
  );
}
