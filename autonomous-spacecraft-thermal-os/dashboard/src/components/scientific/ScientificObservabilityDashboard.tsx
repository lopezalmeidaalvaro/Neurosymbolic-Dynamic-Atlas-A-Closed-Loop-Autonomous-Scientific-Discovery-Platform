'use client';

import { AlertTriangle, BarChart3, Loader2 } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { useMassiveSweepReport } from '@/hooks/useMassiveSweepReport';
import { CertificationStatusCard } from '@/components/scientific/CertificationStatusCard';
import { ExperimentMetadataPanel } from '@/components/scientific/ExperimentMetadataPanel';
import { KinematicDerivativesChart } from '@/components/scientific/KinematicDerivativesChart';
import { ScientificTrendChart } from '@/components/scientific/ScientificTrendChart';
import { SweepComparisonPanel } from '@/components/scientific/SweepComparisonPanel';
import { ScientificRegressionPanel } from '@/components/scientific/ScientificRegressionPanel';
import { StabilityHeatmap } from '@/components/scientific/StabilityHeatmap';
import { ManifoldCollapsePlayer } from '@/components/scientific/ManifoldCollapsePlayer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

interface ScientificObservabilityDashboardProps {
  lang: Language;
}

const EXPLANATION = {
  simple: {
    en: 'The system is observing how behavior changes when noise increases.',
    es: 'El sistema observa como cambia el comportamiento cuando aumenta el ruido.',
  },
  advanced: {
    en: 'The dashboard visualizes Delta(sigma), its derivatives and statistically certified structural regions.',
    es: 'El dashboard visualiza Delta(sigma), sus derivadas y regiones estructurales certificadas estadisticamente.',
  },
} as const;

export function ScientificObservabilityDashboard({ lang }: ScientificObservabilityDashboardProps) {
  const { complexityMode } = useAppStore();
  const { report, isLoading, isError, isEmpty, error } = useMassiveSweepReport();

  if (isLoading) {
    return (
      <GlassPanel className="flex min-h-72 items-center justify-center border-white/[0.06] bg-slate-950/25">
        <div className="flex flex-col items-center gap-3 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-300" />
          <p className="font-mono text-sm text-slate-400">
            {lang === 'es' ? 'Cargando reporte certificado...' : 'Loading certified sweep report...'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  if (isError || !report) {
    return (
      <GlassPanel tone="warning" className="border-amber-500/20 bg-amber-950/10 p-8">
        <div className="flex flex-col items-center gap-3 text-center">
          <AlertTriangle className="h-10 w-10 text-amber-300" />
          <h3 className="text-lg font-semibold text-slate-100">
            {lang === 'es' ? 'Reporte no disponible' : 'Report unavailable'}
          </h3>
          <p className="max-w-xl text-sm leading-6 text-slate-400">
            {error?.message ??
              (lang === 'es'
                ? 'Ejecuta python run_massive_sweep.py --seeds 3 --noise-levels 10 para generar el artefacto.'
                : 'Run python run_massive_sweep.py --seeds 3 --noise-levels 10 to generate the artifact.')}
          </p>
        </div>
      </GlassPanel>
    );
  }

  if (isEmpty) {
    return (
      <GlassPanel className="border-white/[0.06] bg-slate-950/20 p-8">
        <div className="flex flex-col items-center gap-3 text-center">
          <BarChart3 className="h-10 w-10 text-slate-400" />
          <h3 className="text-lg font-semibold text-slate-100">
            {lang === 'es' ? 'Sin sistemas certificados' : 'No certified systems'}
          </h3>
          <p className="max-w-xl text-sm leading-6 text-slate-400">
            {lang === 'es'
              ? 'El JSON existe, pero certified_results esta vacio.'
              : 'The JSON exists, but certified_results is empty.'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  return (
    <div className="space-y-7">
      <ScientificSurface grid className="p-6 sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="research-kicker mb-4">
              <BarChart3 size={13} />
              {lang === 'es' ? 'OBSERVABILIDAD CIENTIFICA' : 'SCIENTIFIC OBSERVABILITY'}
            </span>
            <h2 className="cinematic-heading text-3xl sm:text-4xl">
              {lang === 'es' ? 'Panel de certificacion estructural' : 'Structural certification dashboard'}
            </h2>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300/78">
              {EXPLANATION[complexityMode][lang]}
            </p>
          </div>
          <div className="rounded-xl border border-white/[0.06] bg-slate-950/40 px-4 py-3 font-mono text-xs text-slate-300">
            source: /artifacts/discoveries/massive_sweep_report.json
          </div>
        </div>
      </ScientificSurface>

      <ExperimentMetadataPanel metadata={report.metadata} lang={lang} />

      <ScientificRegressionPanel lang={lang} />

      <StabilityHeatmap lang={lang} />

      <ManifoldCollapsePlayer lang={lang} />

      <SweepComparisonPanel lang={lang} />

      <ScientificTrendChart lang={lang} />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        {report.certified_results.map((result) => (
          <CertificationStatusCard key={result.system} result={result} lang={lang} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5">
        {report.certified_results.map((result) => (
          <KinematicDerivativesChart key={result.system} result={result} lang={lang} />
        ))}
      </div>
    </div>
  );
}
