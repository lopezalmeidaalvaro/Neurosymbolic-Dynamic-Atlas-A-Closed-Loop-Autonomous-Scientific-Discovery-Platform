'use client';

import { ArrowUpRight, BookMarked } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ConfidenceBadge } from './ConfidenceBadge';
import type { Language, LiteratureReference, ResearchFinding } from '@/types';

interface InsightCardProps {
  finding: ResearchFinding;
  references: LiteratureReference[];
  lang: Language;
}

export function InsightCard({ finding, references, lang }: InsightCardProps) {
  const { complexityMode } = useAppStore();
  const linkedRefs = references.filter((ref) => finding.literatureRefs.includes(ref.id));

  return (
    <GlassPanel density="normal" tone={finding.state === 'validated' ? 'active' : 'neutral'}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="metric-label">{lang === 'es' ? 'Insight cientifico' : 'Scientific insight'}</p>
          <h3 className="mt-2 text-xl font-semibold leading-tight text-white/92">{finding.title[lang]}</h3>
        </div>
        <ConfidenceBadge state={finding.state} confidence={finding.metrics.confidence} lang={lang} />
      </div>
      <p className="text-sm leading-7 text-slate-300/76">{finding.whyItMatters[complexityMode][lang]}</p>
      {linkedRefs.length > 0 && (
        <div className="mt-5 space-y-2">
          <p className="metric-label">{lang === 'es' ? 'Literatura conectada' : 'Linked literature'}</p>
          {linkedRefs.map((ref) => (
            <a
              key={ref.id}
              href={ref.url}
              target="_blank"
              rel="noreferrer"
              className="flex items-start justify-between gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.03] p-3 text-sm text-slate-300 transition-colors hover:bg-white/[0.05]"
            >
              <span className="min-w-0">
                <span className="flex items-center gap-2 text-slate-100">
                  <BookMarked size={13} className="shrink-0 text-cyan-100" />
                  <span className="line-clamp-1">{ref.title}</span>
                </span>
                <span className="mt-1 block text-xs text-slate-500">{ref.authors.slice(0, 3).join(', ')} · {ref.year}</span>
              </span>
              <ArrowUpRight size={14} className="shrink-0 text-slate-500" />
            </a>
          ))}
        </div>
      )}
    </GlassPanel>
  );
}
