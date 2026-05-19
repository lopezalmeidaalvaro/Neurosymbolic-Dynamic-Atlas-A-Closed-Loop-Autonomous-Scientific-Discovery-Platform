'use client';

import { FileCheck2, FlaskConical } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, ResearchFinding } from '@/types';

interface EvidencePanelProps {
  finding: ResearchFinding;
  lang: Language;
}

export function EvidencePanel({ finding, lang }: EvidencePanelProps) {
  const { complexityMode } = useAppStore();

  return (
    <GlassPanel density="normal">
      <div className="mb-5 flex items-center gap-3">
        <FileCheck2 size={17} className="text-cyan-100" />
        <div>
          <p className="metric-label">{lang === 'es' ? 'Evidencia' : 'Evidence'}</p>
          <h3 className="mt-1 text-lg font-semibold text-white/90">{finding.title[lang]}</h3>
        </div>
      </div>
      <div className="space-y-3">
        {finding.evidence.map((entry, index) => (
          <div key={`${finding.id}-evidence-${index}`} className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4">
            <p className="metric-label">{lang === 'es' ? 'Registro' : 'Record'} {index + 1}</p>
            <p className="mt-2 text-sm leading-7 text-slate-300/76">{entry[complexityMode][lang]}</p>
          </div>
        ))}
      </div>
      <div className="mt-4 rounded-2xl border border-emerald-100/14 bg-emerald-100/[0.045] p-4">
        <div className="mb-2 flex items-center gap-2 text-emerald-100">
          <FlaskConical size={14} />
          <p className="metric-label text-emerald-100/70">{lang === 'es' ? 'Metodologia' : 'Methodology'}</p>
        </div>
        <p className="text-sm leading-7 text-emerald-50/76">{finding.methodology[complexityMode][lang]}</p>
      </div>
    </GlassPanel>
  );
}
