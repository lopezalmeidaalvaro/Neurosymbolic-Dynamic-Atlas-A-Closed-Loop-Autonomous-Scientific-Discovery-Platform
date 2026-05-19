'use client';

import { motion } from 'framer-motion';
import { BookOpen, Sparkles } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ConceptVisualizer } from './ConceptVisualizer';
import { LearningTooltip } from './LearningTooltip';
import type { EducationalConcept, Language } from '@/types';

interface GuidedConceptFlowProps {
  concepts: EducationalConcept[];
  lang: Language;
}

export function GuidedConceptFlow({ concepts, lang }: GuidedConceptFlowProps) {
  const { complexityMode } = useAppStore();

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {concepts.map((concept, index) => (
        <motion.div
          key={concept.id}
          initial={{ opacity: 0, y: 18, filter: 'blur(8px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{ duration: 0.65, delay: index * 0.045, ease: [0.22, 1, 0.36, 1] }}
        >
          <GlassPanel density="normal" className="h-full">
            <ConceptVisualizer type={concept.visualType} className="mb-5 h-44" />
            <div className="mb-3 flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="metric-label">{lang === 'es' ? 'Concepto' : 'Concept'}</p>
                <h3 className="mt-1 text-xl font-semibold text-white/90">{concept.title[lang]}</h3>
              </div>
              <LearningTooltip label={`${concept.title[lang]} help`}>
                <div className="mb-2 flex items-center gap-2 text-cyan-100">
                  <Sparkles size={13} />
                  <span className="font-semibold">{lang === 'es' ? 'Intuicion' : 'Intuition'}</span>
                </div>
                <p>{concept.analogy[complexityMode][lang]}</p>
              </LearningTooltip>
            </div>
            <p className="text-sm leading-7 text-slate-300/74">{concept.short[complexityMode][lang]}</p>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {concept.keywords.map((keyword) => (
                <span key={keyword} className="rounded-full border border-white/[0.07] bg-white/[0.03] px-2 py-1 text-[10px] text-slate-400">
                  {keyword}
                </span>
              ))}
            </div>
            <div className="mt-5 flex items-center gap-2 text-xs text-slate-500">
              <BookOpen size={13} />
              {lang === 'es' ? 'Lee simple, cambia a avanzado cuando quieras.' : 'Read simple, switch to advanced anytime.'}
            </div>
          </GlassPanel>
        </motion.div>
      ))}
    </div>
  );
}
