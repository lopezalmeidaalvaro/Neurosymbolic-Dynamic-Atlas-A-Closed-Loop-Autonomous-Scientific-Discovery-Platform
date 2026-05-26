'use client';

import dynamic from 'next/dynamic';
import { useMassiveSweepReport } from '@/hooks/useMassiveSweepReport';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { AlertCircle, Activity } from 'lucide-react';
import type { Language } from '@/types';

// Dynamically import Plotly with SSR disabled to prevent 'window is not defined' error on Next.js server
const Plot = dynamic(
  () => import('react-plotly.js').then((mod) => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-80 items-center justify-center font-mono text-xs text-slate-400">
        <Activity className="mr-2 h-4 w-4 animate-spin text-cyan-400" />
        Initializing WebGL Heatmap...
      </div>
    ),
  }
);

interface StabilityHeatmapProps {
  lang: Language;
}

export function StabilityHeatmap({ lang }: StabilityHeatmapProps) {
  const { report, isLoading, isError } = useMassiveSweepReport();

  if (isLoading) {
    return (
      <GlassPanel className="p-6">
        <div className="flex h-80 items-center justify-center font-mono text-xs text-slate-400">
          Loading sweep report data...
        </div>
      </GlassPanel>
    );
  }

  if (isError || !report || !report.certified_results || report.certified_results.length === 0) {
    return (
      <GlassPanel tone="warning" className="p-6">
        <div className="flex flex-col items-center justify-center gap-2 py-8 text-center">
          <AlertCircle className="h-8 w-8 text-amber-400" />
          <p className="font-mono text-sm text-slate-300">
            {lang === 'es'
              ? 'Datos de barrido no disponibles para el mapa de estabilidad.'
              : 'Sweep data unavailable for stability heatmap.'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  // 1. Identify priority metric: acceleration -> mean_drift -> (fallback to first available)
  const firstResult = report.certified_results[0];
  if (!firstResult) {
    return null;
  }
  let metricKey: 'acceleration' | 'mean_drift' | 'velocity' = 'acceleration';
  let metricLabel = lang === 'es' ? 'Aceleración' : 'Acceleration';

  if (Array.isArray(firstResult.acceleration) && firstResult.acceleration.length > 0) {
    metricKey = 'acceleration';
    metricLabel = lang === 'es' ? 'Aceleración' : 'Acceleration';
  } else if (Array.isArray(firstResult.mean_drift) && firstResult.mean_drift.length > 0) {
    metricKey = 'mean_drift';
    metricLabel = lang === 'es' ? 'Deriva Media' : 'Mean Drift';
  } else if (Array.isArray(firstResult.velocity) && firstResult.velocity.length > 0) {
    metricKey = 'velocity';
    metricLabel = lang === 'es' ? 'Velocidad' : 'Velocity';
  }

  // 2. Prepare X axis (noise levels)
  const xData = firstResult.noise;

  // 3. Prepare Y axis (system names)
  const yData = report.certified_results.map((r) => r.system);

  // 4. Prepare Z axis (matrix of values)
  // zData[y_index][x_index] -> zData[system_index][noise_index]
  const zData = report.certified_results.map((r) => r[metricKey]);

  return (
    <GlassPanel density="spacious" tone="active">
      <div className="mb-4">
        <p className="metric-label">
          {lang === 'es' ? 'Estabilidad del Sistema' : 'System Stability'}
        </p>
        <h3 className="mt-2 text-2xl font-semibold text-white/90">
          {lang === 'es' ? 'Mapa Térmico de Estabilidad Estructural' : 'Structural Stability Heatmap'}
        </h3>
        <p className="mt-2 font-mono text-xs text-slate-400">
          {lang === 'es'
            ? `Eje Z: Métrica de atractor [${metricKey}] sin recalcular`
            : `Z-Axis: Attractor metric [${metricKey}] mapped from backend`}
        </p>
      </div>

      <div className="h-80 w-full overflow-hidden rounded-xl border border-white/[0.06] bg-slate-950/40 p-2">
        <Plot
          data={[
            {
              x: xData,
              y: yData,
              z: zData,
              type: 'heatmap',
              colorscale: [
                [0.0, '#030712'],   // deep black-slate
                [0.2, '#1e1b4b'],   // dark indigo
                [0.4, '#4c1d95'],   // dark violet
                [0.6, '#0ea5e9'],   // bright cyan
                [0.8, '#f43f5e'],   // bright rose
                [1.0, '#f59e0b'],   // amber gold
              ],
              hovertemplate:
                '<b>System</b>: %{y}<br>' +
                '<b>Noise σ</b>: %{x:.4f}<br>' +
                `<b>${metricLabel}</b>: %{z:.4f}<extra></extra>`,
              showscale: true,
              colorbar: {
                tickfont: { color: '#94a3b8', family: 'monospace', size: 10 },
                title: {
                  text: metricLabel,
                  font: { color: '#e2e8f0', family: 'monospace', size: 11 },
                },
              },
            },
          ]}
          layout={{
            autosize: true,
            margin: { t: 20, r: 10, b: 50, l: 120 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: {
              title: {
                text: lang === 'es' ? 'Nivel de Ruido (σ)' : 'Noise Level (σ)',
                font: { color: '#64748b', family: 'monospace', size: 11 },
              },
              tickfont: { color: '#94a3b8', family: 'monospace', size: 10 },
              gridcolor: 'rgba(255,255,255,0.04)',
            },
            yaxis: {
              tickfont: { color: '#94a3b8', family: 'monospace', size: 11 },
              gridcolor: 'rgba(255,255,255,0.04)',
            },
          }}
          config={{
            responsive: true,
            displayModeBar: false,
          }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler
        />
      </div>
    </GlassPanel>
  );
}
