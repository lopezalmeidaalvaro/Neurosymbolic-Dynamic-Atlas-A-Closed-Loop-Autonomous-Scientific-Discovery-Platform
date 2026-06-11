'use client';

import { useMemo, useState } from 'react';
import { GitCompareArrows } from 'lucide-react';
import { useHistoricalSweeps } from '@/hooks/useHistoricalSweeps';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { CertifiedSystemResult, Language } from '@/types';

interface SweepComparisonPanelProps {
  lang: Language;
}

function bySystem(results: CertifiedSystemResult[]) {
  return new Map(results.map((result) => [result.system, result]));
}

function signed(value: number) {
  return value > 0 ? `+${value.toFixed(6)}` : value.toFixed(6);
}

export function SweepComparisonPanel({ lang }: SweepComparisonPanelProps) {
  const { snapshots, loading, isError, error } = useHistoricalSweeps();
  const [baselineFile, setBaselineFile] = useState<string>('');
  const [comparisonFile, setComparisonFile] = useState<string>('');

  const baseline = snapshots.find((snapshot) => snapshot.index.file === baselineFile) ?? snapshots[0];
  const comparison =
    snapshots.find((snapshot) => snapshot.index.file === comparisonFile) ??
    snapshots[snapshots.length - 1];

  const rows = useMemo(() => {
    if (!baseline || !comparison) {
      return [];
    }

    const baselineSystems = bySystem(baseline.report.certified_results);
    const comparisonSystems = bySystem(comparison.report.certified_results);

    return [...baselineSystems.entries()]
      .filter(([system]) => comparisonSystems.has(system))
      .map(([system, baselineResult]) => {
        const comparisonResult = comparisonSystems.get(system);

        if (!comparisonResult) {
          return null;
        }

        return {
          system,
          criticalScoreDelta:
            comparisonResult.certification.critical_score - baselineResult.certification.critical_score,
          confidenceScoreDelta:
            comparisonResult.certification.confidence_score - baselineResult.certification.confidence_score,
          baselineReproducibility: baselineResult.certification.reproducibility_status,
          comparisonReproducibility: comparisonResult.certification.reproducibility_status,
        };
      })
      .filter((row): row is NonNullable<typeof row> => row !== null);
  }, [baseline, comparison]);

  if (loading) {
    return (
      <GlassPanel className="p-6">
        <p className="font-mono text-sm text-slate-400">
          {lang === 'es' ? 'Cargando historial de sweeps...' : 'Loading sweep history...'}
        </p>
      </GlassPanel>
    );
  }

  if (isError) {
    return (
      <GlassPanel tone="warning" className="p-6">
        <p className="text-sm text-amber-200">
          {error?.message ?? (lang === 'es' ? 'Historial no disponible.' : 'History unavailable.')}
        </p>
      </GlassPanel>
    );
  }

  if (snapshots.length < 2) {
    return (
      <GlassPanel className="p-6">
        <p className="metric-label">{lang === 'es' ? 'Comparacion historica' : 'Historical comparison'}</p>
        <p className="mt-3 text-sm leading-6 text-slate-400">
          {lang === 'es'
            ? 'Se necesitan al menos dos snapshots historicos para comparar sweeps.'
            : 'At least two historical snapshots are required to compare sweeps.'}
        </p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel density="spacious" tone="active">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="metric-label">{lang === 'es' ? 'Comparacion historica' : 'Historical comparison'}</p>
          <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold text-white/90">
            <GitCompareArrows size={18} className="text-cyan-300" />
            {lang === 'es' ? 'Evolucion entre sweeps' : 'Sweep-to-sweep evolution'}
          </h3>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <label className="space-y-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
              baseline sweep
            </span>
            <select
              value={baseline?.index.file ?? ''}
              onChange={(event) => setBaselineFile(event.target.value)}
              className="w-full rounded-lg border border-white/[0.08] bg-slate-950/80 px-3 py-2 font-mono text-xs text-slate-100"
            >
              {snapshots.map((snapshot) => (
                <option key={snapshot.index.file} value={snapshot.index.file}>
                  {snapshot.index.timestamp}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
              comparison sweep
            </span>
            <select
              value={comparison?.index.file ?? ''}
              onChange={(event) => setComparisonFile(event.target.value)}
              className="w-full rounded-lg border border-white/[0.08] bg-slate-950/80 px-3 py-2 font-mono text-xs text-slate-100"
            >
              {snapshots.map((snapshot) => (
                <option key={snapshot.index.file} value={snapshot.index.file}>
                  {snapshot.index.timestamp}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-separate border-spacing-y-2 text-left">
          <thead className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate-500">
            <tr>
              <th className="px-3 py-2">system</th>
              <th className="px-3 py-2">critical_score delta</th>
              <th className="px-3 py-2">confidence_score delta</th>
              <th className="px-3 py-2">reproducibility changes</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.system} className="rounded-xl bg-slate-950/35 font-mono text-sm text-slate-200">
                <td className="rounded-l-xl px-3 py-3 capitalize">{row.system.replaceAll('_', ' ')}</td>
                <td className="px-3 py-3">{signed(row.criticalScoreDelta)}</td>
                <td className="px-3 py-3">{signed(row.confidenceScoreDelta)}</td>
                <td className="rounded-r-xl px-3 py-3">
                  {row.baselineReproducibility}{' -> '}{row.comparisonReproducibility}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassPanel>
  );
}
