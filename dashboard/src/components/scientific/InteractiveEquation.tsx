'use client';

import { useState } from 'react';
import { Sigma } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { KaTeX } from '@/components/ui/KaTeX';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, MultilingualText } from '@/types';

interface EquationTerm {
  symbol: string;
  label: MultilingualText;
  explanation: MultilingualText;
}

interface InteractiveEquationProps {
  title: MultilingualText;
  formula: string;
  terms: EquationTerm[];
  lang: Language;
}

export function InteractiveEquation({ title, formula, terms, lang }: InteractiveEquationProps) {
  const [active, setActive] = useState(terms[0]?.symbol ?? '');
  const activeTerm = terms.find((term) => term.symbol === active) ?? terms[0];

  return (
    <GlassPanel density="spacious">
      <div className="mb-5 flex items-center gap-3">
        <Sigma size={17} className="text-cyan-100" />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Ecuacion interactiva' : 'Interactive equation'}</p>
          <h2 className="mt-1 text-xl font-semibold text-white/90">{title[lang]}</h2>
        </div>
      </div>
      <div className="equation-surface rounded-2xl border border-white/[0.08] bg-black/25 p-4">
        <KaTeX formula={formula} block />
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        {terms.map((term) => (
          <button
            key={term.symbol}
            type="button"
            onClick={() => setActive(term.symbol)}
            className={cn(
              'rounded-full border px-3 py-1.5 font-mono text-xs transition-colors',
              active === term.symbol
                ? 'border-cyan-100/22 bg-cyan-100/10 text-cyan-50'
                : 'border-white/[0.08] bg-white/[0.03] text-slate-400 hover:text-slate-200'
            )}
          >
            {term.symbol}
          </button>
        ))}
      </div>
      {activeTerm && (
        <div className="mt-4 rounded-2xl border border-white/[0.08] bg-white/[0.035] p-4">
          <p className="text-sm font-semibold text-white/90">{activeTerm.label[lang]}</p>
          <p className="mt-2 text-sm leading-7 text-slate-300/72">{activeTerm.explanation[lang]}</p>
        </div>
      )}
    </GlassPanel>
  );
}
