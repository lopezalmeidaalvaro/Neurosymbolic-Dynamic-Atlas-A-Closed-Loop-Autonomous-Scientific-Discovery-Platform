'use client';

import { ArrowUpRight, Library } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, ScientificReference } from '@/types';

interface RelatedResearchPanelProps {
  references: ScientificReference[];
  lang: Language;
}

export function RelatedResearchPanel({ references, lang }: RelatedResearchPanelProps) {
  const { complexityMode } = useAppStore();

  return (
    <GlassPanel density="spacious">
      <div className="mb-5 flex items-center gap-3">
        <Library size={17} className="text-violet-100" />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Related research' : 'Related research'}</p>
          <h2 className="mt-1 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Papers, datasets y linaje metodologico' : 'Papers, datasets, and methodology lineage'}
          </h2>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {references.map((ref) => (
          <a
            key={ref.id}
            href={ref.url}
            target="_blank"
            rel="noreferrer"
            className="group rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4 transition-colors hover:bg-white/[0.05]"
          >
            <div className="mb-3 flex items-start justify-between gap-3">
              <span className="rounded-full border border-cyan-100/16 bg-cyan-100/[0.06] px-2 py-1 text-[10px] uppercase tracking-[0.12em] text-cyan-100/75">
                {ref.category}
              </span>
              <ArrowUpRight size={14} className="shrink-0 text-slate-500 transition-colors group-hover:text-cyan-100" />
            </div>
            <h3 className="text-sm font-semibold leading-snug text-white/90">{ref.title}</h3>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              {ref.authors.slice(0, 4).join(', ')} · {ref.year} · {ref.venue}
            </p>
            <p className="mt-3 text-sm leading-7 text-slate-300/72">{ref.context[complexityMode][lang]}</p>
            {complexityMode === 'advanced' && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {ref.doi && <span className="rounded-full border border-white/[0.08] px-2 py-1 text-[10px] text-slate-400">DOI {ref.doi}</span>}
                {ref.arxiv && <span className="rounded-full border border-white/[0.08] px-2 py-1 text-[10px] text-slate-400">arXiv {ref.arxiv}</span>}
                {ref.tags.slice(0, 2).map((tag) => (
                  <span key={tag} className="rounded-full border border-white/[0.08] px-2 py-1 text-[10px] text-slate-500">{tag}</span>
                ))}
              </div>
            )}
          </a>
        ))}
      </div>
    </GlassPanel>
  );
}
