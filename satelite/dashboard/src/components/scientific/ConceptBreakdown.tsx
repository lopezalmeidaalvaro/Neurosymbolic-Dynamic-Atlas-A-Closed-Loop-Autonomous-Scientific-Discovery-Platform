'use client';

import { Layers3 } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { EducationalConcept, Language } from '@/types';

interface ConceptBreakdownProps {
  concept: EducationalConcept;
  lang: Language;
}

export function ConceptBreakdown({ concept, lang }: ConceptBreakdownProps) {
  const { complexityMode } = useAppStore();
  const rows = [
    { label: lang === 'es' ? 'Intuicion' : 'Intuition', text: concept.analogy[complexityMode][lang] },
    { label: lang === 'es' ? 'Ejemplo' : 'Example', text: concept.example[complexityMode][lang] },
    { label: lang === 'es' ? 'Uso en el sistema' : 'Use in the system', text: concept.technical[complexityMode][lang] },
  ];

  return (
    <GlassPanel density="normal">
      <div className="mb-5 flex items-center gap-3">
        <Layers3 size={17} className="text-violet-100" />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Desglose conceptual' : 'Concept breakdown'}</p>
          <h3 className="mt-1 text-lg font-semibold text-white/90">{concept.title[lang]}</h3>
        </div>
      </div>
      <div className="space-y-3">
        {rows.map((row) => (
          <div key={row.label} className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4">
            <p className="metric-label">{row.label}</p>
            <p className="mt-2 text-sm leading-7 text-slate-300/74">{row.text}</p>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
