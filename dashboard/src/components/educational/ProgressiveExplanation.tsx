'use client';

import { ChevronDown } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ConceptVisualizer } from './ConceptVisualizer';
import type { EducationalConcept, Language } from '@/types';

interface ProgressiveExplanationProps {
  concept: EducationalConcept;
  lang: Language;
}

export function ProgressiveExplanation({ concept, lang }: ProgressiveExplanationProps) {
  const { complexityMode } = useAppStore();

  const rows = [
    { label: lang === 'es' ? '1. Idea simple' : '1. Simple idea', body: concept.short[complexityMode][lang] },
    { label: lang === 'es' ? '2. Lectura visual' : '2. Visual reading', body: concept.visual[complexityMode][lang] },
    { label: lang === 'es' ? '3. Explicacion tecnica' : '3. Technical explanation', body: concept.technical[complexityMode][lang] },
    concept.methodology && {
      label: lang === 'es' ? '4. Metodologia' : '4. Methodology',
      body: concept.methodology[complexityMode][lang],
    },
  ].filter(Boolean) as Array<{ label: string; body: string }>;

  return (
    <GlassPanel density="spacious">
      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <ConceptVisualizer type={concept.visualType} />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Disclosure progresivo' : 'Progressive disclosure'}</p>
          <h2 className="mt-2 text-2xl font-semibold text-white/90">{concept.title[lang]}</h2>
          <div className="mt-5 space-y-3">
            {rows.map((row, index) => (
              <div key={row.label} className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4">
                <div className="flex items-center gap-2">
                  <ChevronDown size={14} className="text-cyan-100/70" />
                  <p className="metric-label">{row.label}</p>
                </div>
                <p className="mt-2 text-sm leading-7 text-slate-300/74">{row.body}</p>
                {index < rows.length - 1 && (
                  <div className="mt-3 h-px w-16 bg-gradient-to-r from-cyan-100/28 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
