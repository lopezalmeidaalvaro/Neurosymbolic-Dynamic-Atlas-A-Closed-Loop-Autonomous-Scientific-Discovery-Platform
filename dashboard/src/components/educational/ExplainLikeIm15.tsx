'use client';

import { motion } from 'framer-motion';
import { GraduationCap } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, MultilingualText, SemanticText } from '@/types';

interface ExplainLikeIm15Props {
  title: MultilingualText;
  text: SemanticText;
  lang: Language;
  example?: SemanticText;
}

export function ExplainLikeIm15({ title, text, lang, example }: ExplainLikeIm15Props) {
  const { complexityMode } = useAppStore();
  const simple = complexityMode === 'simple';

  return (
    <GlassPanel density="spacious" tone={simple ? 'active' : 'neutral'}>
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-100/18 bg-cyan-100/[0.07] text-cyan-100">
          <GraduationCap size={17} />
        </div>
        <div>
          <p className="metric-label">{simple ? 'Explain like I am 15' : 'Technical frame'}</p>
          <h2 className="mt-1 text-xl font-semibold text-white/90">{title[lang]}</h2>
        </div>
      </div>

      <motion.p
        key={`${complexityMode}-${lang}-${title.en}`}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className={simple ? 'text-lg leading-8 text-slate-200/86' : 'text-sm leading-7 text-slate-300/72'}
      >
        {text[complexityMode][lang]}
      </motion.p>

      {example && (
        <div className="mt-5 rounded-2xl border border-white/[0.08] bg-white/[0.035] p-4">
          <p className="metric-label mb-2">{lang === 'es' ? 'Ejemplo' : 'Example'}</p>
          <p className="text-sm leading-7 text-slate-300/75">{example[complexityMode][lang]}</p>
        </div>
      )}
    </GlassPanel>
  );
}
