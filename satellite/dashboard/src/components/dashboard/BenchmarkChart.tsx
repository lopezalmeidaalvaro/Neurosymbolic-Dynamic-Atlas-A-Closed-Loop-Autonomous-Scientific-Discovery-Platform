'use client';

import { motion } from 'framer-motion';
import type { BenchmarkResult, Language } from '@/types';

interface BenchmarkChartProps {
  results: BenchmarkResult[];
  lang: Language;
  metric: 'accuracy' | 'time';
}

export function BenchmarkChart({ results, lang, metric }: BenchmarkChartProps) {
  const values = results.map((r) => (metric === 'accuracy' ? r.accuracy : r.timeSeconds));
  const maxVal = Math.max(...values);
  const minVal = Math.min(...values);

  return (
    <div className="space-y-5">
      {results.map((result, index) => {
        const value = metric === 'accuracy' ? result.accuracy : result.timeSeconds;
        const barPct = metric === 'time' ? Math.max(8, (minVal / value) * 100) : (value / maxVal) * 100;
        const displayVal =
          metric === 'accuracy' ? `${(result.accuracy * 100).toFixed(2)}%` : `${result.timeSeconds.toFixed(3)}s`;
        const isBestTime = metric === 'time' && value === minVal;

        return (
          <motion.div
            key={result.id}
            initial={{ opacity: 0, x: -14, filter: 'blur(6px)' }}
            animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
            transition={{ delay: index * 0.08, duration: 0.58, ease: [0.22, 1, 0.36, 1] }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex min-w-0 items-center gap-2">
                <span className="truncate text-sm font-medium text-slate-200">{result.modelName}</span>
                {result.isOurs && (
                  <span className="rounded-full border border-cyan-100/20 bg-cyan-100/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-cyan-100/80">
                    {lang === 'es' ? 'Atlas' : 'Atlas'}
                  </span>
                )}
                {isBestTime && (
                  <span className="rounded-full border border-emerald-100/18 bg-emerald-100/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-100/80">
                    {lang === 'es' ? 'Mas rapido' : 'Fastest'}
                  </span>
                )}
              </div>
              <span className="font-mono text-sm font-semibold text-slate-100">{displayVal}</span>
            </div>
            <div className="relative h-2.5 overflow-hidden rounded-full border border-white/[0.06] bg-black/25">
              <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.04),transparent)]" />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${barPct}%` }}
                transition={{ duration: 1.0, delay: index * 0.08 + 0.16, ease: [0.22, 1, 0.36, 1] }}
                className="h-full rounded-full shadow-[0_0_24px_rgba(125,211,252,0.16)]"
                style={{
                  background: result.isOurs
                    ? 'linear-gradient(90deg, rgba(186,230,253,0.95), rgba(94,234,212,0.78))'
                    : `${result.color}aa`,
                }}
              />
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
