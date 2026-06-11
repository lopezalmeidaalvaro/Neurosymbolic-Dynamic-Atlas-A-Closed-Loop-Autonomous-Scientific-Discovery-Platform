'use client';

import { FlaskConical, HelpCircle } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ConfidenceBadge } from './ConfidenceBadge';
import type { Language, OpenQuestion, ResearchHypothesis } from '@/types';

interface HypothesisTrackerProps {
  hypotheses: ResearchHypothesis[];
  openQuestions: OpenQuestion[];
  lang: Language;
}

const PRIORITY_STYLE = {
  high: 'border-red-100/16 bg-red-100/[0.055] text-red-100/80',
  medium: 'border-amber-100/18 bg-amber-100/[0.07] text-amber-100/80',
  low: 'border-white/[0.08] bg-white/[0.03] text-slate-400',
};

export function HypothesisTracker({ hypotheses, openQuestions, lang }: HypothesisTrackerProps) {
  const { complexityMode } = useAppStore();

  return (
    <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
      <GlassPanel density="spacious" tone="active">
        <div className="mb-6 flex items-center gap-3">
          <FlaskConical size={17} className="text-violet-100" />
          <div>
            <p className="metric-label">{lang === 'es' ? 'Hipotesis vivas' : 'Live hypotheses'}</p>
            <h2 className="mt-1 text-2xl font-semibold text-white/90">
              {lang === 'es' ? 'Lo que el sistema cree, pero aun debe probar' : 'What the system believes, but still must test'}
            </h2>
          </div>
        </div>
        <div className="space-y-4">
          {hypotheses.map((hypothesis) => (
            <div key={hypothesis.id} className="rounded-2xl border border-violet-100/14 bg-violet-100/[0.045] p-5">
              <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
                <h3 className="text-base font-semibold text-white/90">{hypothesis.title[lang]}</h3>
                <ConfidenceBadge state={hypothesis.state} confidence={hypothesis.confidence} lang={lang} />
              </div>
              <p className="text-sm leading-7 text-slate-300/76">{hypothesis.claim[complexityMode][lang]}</p>
              <div className="mt-4 rounded-2xl border border-white/[0.08] bg-black/20 p-4">
                <p className="metric-label">{lang === 'es' ? 'Siguiente experimento' : 'Next experiment'}</p>
                <p className="mt-2 text-sm leading-7 text-slate-300/74">{hypothesis.nextExperiment[complexityMode][lang]}</p>
              </div>
            </div>
          ))}
        </div>
      </GlassPanel>

      <GlassPanel density="spacious" tone="warning">
        <div className="mb-6 flex items-center gap-3">
          <HelpCircle size={17} className="text-amber-100" />
          <div>
            <p className="metric-label">{lang === 'es' ? 'Preguntas abiertas' : 'Open questions'}</p>
            <h2 className="mt-1 text-2xl font-semibold text-white/90">
              {lang === 'es' ? 'Fronteras de incertidumbre' : 'Uncertainty frontiers'}
            </h2>
          </div>
        </div>
        <div className="space-y-3">
          {openQuestions.map((question) => (
            <div key={question.id} className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4">
              <div className="mb-3 flex items-start justify-between gap-3">
                <h3 className="text-sm font-semibold text-white/90">{question.title[lang]}</h3>
                <span className={`rounded-full border px-2 py-1 text-[10px] uppercase tracking-[0.12em] ${PRIORITY_STYLE[question.priority]}`}>
                  {question.priority}
                </span>
              </div>
              <p className="text-sm leading-7 text-slate-300/74">{question.question[complexityMode][lang]}</p>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );
}
