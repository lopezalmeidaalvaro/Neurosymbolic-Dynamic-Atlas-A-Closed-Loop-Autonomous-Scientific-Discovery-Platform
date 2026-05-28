'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  Tooltip,
  XAxis,
  YAxis,
  ComposedChart,
} from 'recharts';
import { Activity } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { CriticalRegionDetector } from '@/components/scientific/CriticalRegionDetector';
import type { CertifiedSystemResult, Language } from '@/types';

interface KinematicDerivativesChartProps {
  result: CertifiedSystemResult;
  lang: Language;
}

interface KinematicChartPoint {
  noise: number;
  mean_drift: number | null;
  velocity: number | null;
  acceleration: number | null;
}

export function KinematicDerivativesChart({ result, lang }: KinematicDerivativesChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const chartData = useMemo<KinematicChartPoint[]>(
    () =>
      result.noise.map((noise, index) => ({
        noise,
        mean_drift: result.mean_drift[index] ?? null,
        velocity: result.velocity[index] ?? null,
        acceleration: result.acceleration[index] ?? null,
      })),
    [result]
  );

  return (
    <GlassPanel density="spacious" tone="active" className="min-h-[460px]">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="metric-label">{lang === 'es' ? 'Derivadas cinematicas' : 'Kinematic derivatives'}</p>
          <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold capitalize text-white/90">
            <Activity size={18} className="text-cyan-300" />
            {result.system.replaceAll('_', ' ')}
          </h3>
        </div>
        <span className="rounded-full border border-white/[0.08] bg-slate-950/40 px-3 py-1 font-mono text-xs text-slate-300">
          critical_level: {result.certification.critical_level}
        </span>
      </div>

      <div className="h-[340px] min-w-0 w-full overflow-x-auto">
        {mounted ? (
            <ComposedChart width={920} height={320} data={chartData} margin={{ top: 10, right: 20, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="noise"
                type="number"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                tickFormatter={(value) => `sigma ${value}`}
              />
              <YAxis
                yAxisId="values"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                width={52}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(10, 15, 30, 0.94)',
                  borderColor: 'rgba(255,255,255,0.10)',
                  borderRadius: '12px',
                  color: '#f8fafc',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                }}
                labelFormatter={(value) => `noise sigma: ${value}`}
              />
              <Legend
                verticalAlign="top"
                height={32}
                iconType="circle"
                wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
              />
              <CriticalRegionDetector result={result} />
              <Line
                yAxisId="values"
                type="monotone"
                dataKey="mean_drift"
                name="mean_drift"
                stroke="#22d3ee"
                strokeWidth={2.5}
                dot={{ r: 3 }}
                isAnimationActive={false}
              />
              <Line
                yAxisId="values"
                type="monotone"
                dataKey="velocity"
                name="velocity"
                stroke="#a78bfa"
                strokeWidth={2}
                dot={{ r: 3 }}
                isAnimationActive={false}
              />
              <Line
                yAxisId="values"
                type="monotone"
                dataKey="acceleration"
                name="acceleration"
                stroke="#f97316"
                strokeWidth={2}
                dot={{ r: 3 }}
                isAnimationActive={false}
              />
            </ComposedChart>
        ) : (
          <div className="h-full rounded-xl border border-white/[0.05] bg-slate-950/25" />
        )}
      </div>
    </GlassPanel>
  );
}
