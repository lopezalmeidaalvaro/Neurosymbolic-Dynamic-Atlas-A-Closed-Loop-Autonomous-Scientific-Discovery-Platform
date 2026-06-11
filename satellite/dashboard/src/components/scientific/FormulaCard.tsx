'use client';

import { motion } from 'framer-motion';
import { KaTeX } from '@/components/ui/KaTeX';
import { useAppStore } from '@/stores/appStore';
import { cn } from '@/lib/utils/cn';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { TheoryBlock, Language } from '@/types';

interface FormulaCardProps {
  block: TheoryBlock;
  lang: Language;
  index?: number;
}

const COLOR_MAP = {
  cyan: { accent: 'text-cyan-100', tag: 'border-cyan-100/20 bg-cyan-100/10 text-cyan-100/80' },
  blue: { accent: 'text-sky-100', tag: 'border-sky-100/20 bg-sky-100/10 text-sky-100/80' },
  violet: { accent: 'text-violet-100', tag: 'border-violet-100/20 bg-violet-100/10 text-violet-100/80' },
  emerald: { accent: 'text-emerald-100', tag: 'border-emerald-100/20 bg-emerald-100/10 text-emerald-100/80' },
};

export function FormulaCard({ block, lang, index = 0 }: FormulaCardProps) {
  const { complexityMode } = useAppStore();
  const colors = COLOR_MAP[block.color ?? 'cyan'];
  const content = block.content[complexityMode][lang];

  return (
    <motion.div
      initial={{ opacity: 0, y: 18, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.68, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      <GlassPanel className="h-full" density="normal">
        <div className="mb-5 flex items-start justify-between gap-3">
          <h3 className={cn('text-base font-semibold leading-tight', colors.accent)}>{block.title[lang]}</h3>
          {block.tag && (
            <span className={cn('shrink-0 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em]', colors.tag)}>
              {block.tag}
            </span>
          )}
        </div>

        <motion.p
          key={`${complexityMode}-${lang}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="mb-5 text-sm leading-7 text-slate-300/70"
        >
          {content}
        </motion.p>

        {block.formula && (
          <div className="equation-surface rounded-2xl border border-white/[0.08] bg-black/25 p-4 shadow-inner">
            {block.formulaLabel && <p className="metric-label mb-3">{block.formulaLabel[lang]}</p>}
            <div className="overflow-x-auto">
              <KaTeX formula={block.formula} block />
            </div>
          </div>
        )}
      </GlassPanel>
    </motion.div>
  );
}
