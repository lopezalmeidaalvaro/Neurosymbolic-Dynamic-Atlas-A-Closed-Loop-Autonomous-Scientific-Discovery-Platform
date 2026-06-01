'use client';

import { Activity, Gauge, ShieldCheck } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { CertifiedSystemResult, CriticalLevel, Language, ReproducibilityStatus } from '@/types';

interface CertificationStatusCardProps {
  result: CertifiedSystemResult;
  lang: Language;
}

const LEVEL_STYLE: Record<CriticalLevel, string> = {
  strong: 'border-red-400/30 bg-red-500/10 text-red-200',
  moderate: 'border-amber-400/30 bg-amber-500/10 text-amber-200',
  none: 'border-slate-400/20 bg-slate-500/10 text-slate-200',
};

const REPRO_STYLE: Record<ReproducibilityStatus, string> = {
  validated: 'text-emerald-200',
  replicated: 'text-cyan-200',
  preliminary: 'text-amber-200',
  uncertain: 'text-slate-300',
};

export function CertificationStatusCard({ result, lang }: CertificationStatusCardProps) {
  const { certification } = result;
  const evidence = certification.evidence;

  return (
    <GlassPanel density="normal" tone={certification.critical_level === 'none' ? 'neutral' : 'warning'}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="metric-label">{lang === 'es' ? 'Sistema certificado' : 'Certified system'}</p>
          <h3 className="mt-2 text-2xl font-semibold capitalize text-white/90">
            {result.system.replaceAll('_', ' ')}
          </h3>
        </div>
        <span className={`rounded-full border px-3 py-1 font-mono text-xs uppercase ${LEVEL_STYLE[certification.critical_level]}`}>
          {certification.critical_level}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
          <div className="mb-2 flex items-center gap-2 text-cyan-200">
            <Gauge size={14} />
            <span className="metric-label">critical_score</span>
          </div>
          <p className="font-mono text-lg text-slate-100">{certification.critical_score}</p>
        </div>

        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
          <div className="mb-2 flex items-center gap-2 text-cyan-200">
            <Activity size={14} />
            <span className="metric-label">confidence_score</span>
          </div>
          <p className="font-mono text-lg text-slate-100">{certification.confidence_score}</p>
        </div>

        <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
          <div className="mb-2 flex items-center gap-2 text-cyan-200">
            <ShieldCheck size={14} />
            <span className="metric-label">reproducibility</span>
          </div>
          <p className={`font-mono text-lg ${REPRO_STYLE[certification.reproducibility_status]}`}>
            {certification.reproducibility_status}
          </p>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-white/[0.06] bg-slate-950/35 p-4">
        <p className="metric-label">{lang === 'es' ? 'Evidencia backend' : 'Backend evidence'}</p>
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div>
            <span className="block text-xs text-slate-500">acceleration</span>
            <span className="font-mono text-sm text-slate-100">{evidence.acceleration}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500">acceleration_std</span>
            <span className="font-mono text-sm text-slate-100">{evidence.acceleration_std}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500">seed_count</span>
            <span className="font-mono text-sm text-slate-100">{evidence.seed_count}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 font-mono text-[11px] text-slate-400">
        <span>version: {certification.version}</span>
        <span>method: {certification.confidence_method}</span>
      </div>
    </GlassPanel>
  );
}
