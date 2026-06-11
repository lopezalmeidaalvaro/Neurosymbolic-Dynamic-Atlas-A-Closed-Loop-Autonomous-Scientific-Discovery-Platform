'use client';

import { useMemo } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import { useHistoricalSweeps } from '@/hooks/useHistoricalSweeps';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface ScientificTrendChartProps {
  lang: Language;
}

interface TrendPoint {
  timestamp: string;
  [system: string]: string | number | null;
}

const COLORS = ['#22d3ee', '#a78bfa', '#f97316', '#34d399', '#f43f5e', '#facc15'];

export function ScientificTrendChart({ lang }: ScientificTrendChartProps) {
  const { snapshots, loading, isError, error } = useHistoricalSweeps();

  const systems = useMemo(() => {
    const names = new Set<string>();
    snapshots.forEach((snapshot) => {
      snapshot.report.certified_results.forEach((result) => names.add(result.system));
    });
    return [...names];
  }, [snapshots]);

  const chartData = useMemo<TrendPoint[]>(
    () =>
      snapshots.map((snapshot) => {
        const point: TrendPoint = {
          timestamp: snapshot.index.timestamp,
        };

        snapshot.report.certified_results.forEach((result) => {
          point[result.system] = result.certification.confidence_score;
        });

        return point;
      }),
    [snapshots]
  );

  if (loading) {
    return (
      <GlassPanel className="p-6">
        <p className="font-mono text-sm text-slate-400">
          {lang === 'es' ? 'Cargando tendencia historica...' : 'Loading historical trend...'}
        </p>
      </GlassPanel>
    );
  }

  if (isError) {
    return (
      <GlassPanel tone="warning" className="p-6">
        <p className="text-sm text-amber-200">
          {error?.message ?? (lang === 'es' ? 'Tendencia no disponible.' : 'Trend unavailable.')}
        </p>
      </GlassPanel>
    );
  }

  if (snapshots.length === 0) {
    return (
      <GlassPanel className="p-6">
        <p className="text-sm text-slate-400">
          {lang === 'es' ? 'No hay snapshots historicos.' : 'No historical snapshots available.'}
        </p>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel density="spacious" tone="success">
      <div className="mb-5">
        <p className="metric-label">{lang === 'es' ? 'Tendencia cientifica' : 'Scientific trend'}</p>
        <h3 className="mt-2 flex items-center gap-2 text-2xl font-semibold text-white/90">
          <TrendingUp size={18} className="text-emerald-300" />
          {lang === 'es' ? 'Evolucion de confidence_score' : 'confidence_score over time'}
        </h3>
      </div>

      <div className="h-[340px] overflow-x-auto">
        <LineChart width={920} height={320} data={chartData} margin={{ top: 10, right: 22, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis
            dataKey="timestamp"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            minTickGap={24}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            width={56}
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
          />
          <Legend
            verticalAlign="top"
            height={32}
            iconType="circle"
            wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
          />
          {systems.map((system, index) => (
            <Line
              key={system}
              type="monotone"
              dataKey={system}
              name={system}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2.5}
              dot={{ r: 3 }}
              connectNulls
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </div>
    </GlassPanel>
  );
}
