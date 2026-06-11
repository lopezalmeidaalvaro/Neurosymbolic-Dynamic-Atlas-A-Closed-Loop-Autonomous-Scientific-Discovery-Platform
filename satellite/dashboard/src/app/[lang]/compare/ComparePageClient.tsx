'use client';

import { memo, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { GitCompare, Activity, Zap, BarChart3, AlertCircle } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { ExportExperimentButton } from '@/components/scientific/ExportExperimentButton';
import { ExperimentReplayTimeline } from '@/components/scientific/ExperimentReplayTimeline';
import { LatentEvolutionPlayer } from '@/components/scientific/LatentEvolutionPlayer';
import { LiveTelemetryConsole } from '@/components/scientific/LiveTelemetryConsole';
import { cn } from '@/lib/utils/cn';
import { useSessionBenchmark, useSessionMetadata } from '@/hooks/useSessionData';
import type { Language, Dictionary } from '@/types';

interface ComparePageClientProps {
  lang: Language;
  dict: Dictionary;
}

// ── Static session registry (extend as sessions grow) ─────────
const SESSIONS = [
  { id: 'experiment_001', label: { en: 'Exp 001 — Baseline (No Noise)', es: 'Exp 001 — Base (Sin Ruido)' } },
  { id: 'experiment_002', label: { en: 'Exp 002 — High-Noise Run',      es: 'Exp 002 — Ejecución Ruidosa' } },
];

const MODEL_COLORS: Record<string, string> = {
  'NODE (Ours)': '#22d3ee',
  'Sakoe-Chiba DTW': '#3b82f6',
  'ROCKET Classifier': '#8b5cf6',
};

// ── Accuracy bar ────────────────────────────────────────────────
const AccuracyBar = memo(function AccuracyBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = (value / max) * 100;
  return (
    <div className="h-1.5 w-full rounded-full bg-white/[0.06] overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="h-full rounded-full"
        style={{ background: color }}
      />
    </div>
  );
});

// ── Single session column ───────────────────────────────────────
const SessionColumn = memo(function SessionColumn({ sessionId, lang }: { sessionId: string; lang: Language }) {
  const { session, isLoading: metaLoad } = useSessionMetadata(sessionId);
  const { benchmarks, isLoading: benchLoad } = useSessionBenchmark(sessionId);

  const isLoading = metaLoad || benchLoad;

  const maxAcc = Math.max(...benchmarks.map(b => b.accuracy), 0.01);

  if (isLoading) {
    return (
      <div className="flex-1 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5 animate-pulse min-h-[320px]" />
    );
  }

  if (!session) {
    return (
      <div className="flex-1 rounded-2xl border border-rose-500/20 bg-rose-500/5 p-5 flex items-center justify-center gap-2 text-rose-400 text-sm min-h-[320px]">
        <AlertCircle size={15} />
        {lang === 'es' ? 'Sesión no encontrada' : 'Session not found'}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex-1 rounded-2xl border border-white/[0.08] bg-[rgba(9,13,24,0.62)] backdrop-blur-xl p-5 flex flex-col gap-4"
    >
      {/* Session header */}
      <div className="border-b border-white/[0.07] pb-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-slate-500">{session.id}</p>
            <h3 className="text-sm font-semibold text-white/90 mt-0.5 leading-snug">
              {lang === 'es' ? session.description?.es : session.description?.en ?? session.id}
            </h3>
          </div>
          <span className={cn(
            'shrink-0 rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest',
            session.status === 'completed'
              ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
              : session.status === 'running'
              ? 'border-amber-500/30 bg-amber-500/10 text-amber-300'
              : 'border-rose-500/30 bg-rose-500/10 text-rose-300'
          )}>
            {session.status}
          </span>
        </div>
      </div>

      {/* Meta grid */}
      <div className="grid grid-cols-2 gap-2">
        {[
          {
            icon: Activity,
            label: lang === 'es' ? 'Nivel de ruido' : 'Noise level',
            value: `${(session.noiseLevel * 100).toFixed(0)}%`,
            color: session.noiseLevel > 0.2 ? 'text-amber-300' : 'text-emerald-300',
          },
          {
            icon: Zap,
            label: lang === 'es' ? 'Modelos' : 'Models',
            value: `${session.models.length}`,
            color: 'text-cyan-300',
          },
        ].map(m => (
          <div key={m.label} className="rounded-xl border border-white/[0.06] bg-white/[0.025] p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <m.icon size={10} className={m.color} />
              <span className="text-[8px] uppercase tracking-widest text-slate-500 font-mono">{m.label}</span>
            </div>
            <p className={cn('font-mono text-lg font-bold', m.color)}>{m.value}</p>
          </div>
        ))}
      </div>

      {/* Benchmark table */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 size={11} className="text-slate-500" />
          <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">
            {lang === 'es' ? 'Resultados de Benchmark' : 'Benchmark Results'}
          </p>
        </div>
        <div className="space-y-3">
          {benchmarks.map(b => (
            <div key={b.id} className="space-y-1.5">
              <div className="flex items-center justify-between text-[10px]">
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-1.5 rounded-full" style={{ background: MODEL_COLORS[b.modelName] ?? '#888' }} />
                  <span className={cn('font-medium', b.isOurs ? 'text-white/90' : 'text-slate-400')}>
                    {b.modelName}
                    {b.isOurs && (
                      <span className="ml-1.5 text-[8px] font-bold uppercase tracking-wider text-cyan-400 font-mono">(ours)</span>
                    )}
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-white/80 font-bold">{(b.accuracy * 100).toFixed(1)}%</span>
                  <span className="text-slate-600">{b.timeSeconds.toFixed(3)}s</span>
                </div>
              </div>
              <AccuracyBar value={b.accuracy} max={maxAcc} color={MODEL_COLORS[b.modelName] ?? '#888'} />
            </div>
          ))}
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5 mt-auto pt-3 border-t border-white/[0.06]">
        {session.tags.map(t => (
          <span key={t} className="rounded-full border border-white/[0.07] bg-white/[0.03] px-2 py-0.5 text-[9px] font-mono text-slate-500">
            {t}
          </span>
        ))}
      </div>
    </motion.div>
  );
});

// ── Main compare view ───────────────────────────────────────────
export function ComparePageClient({ lang }: ComparePageClientProps) {
  const [selectedA, setSelectedA] = useState(SESSIONS[0]!.id);
  const [selectedB, setSelectedB] = useState(SESSIONS[1]!.id);

  // Both sessions loaded at top level — no hook-in-callback violation
  const { benchmarks: benchA } = useSessionBenchmark(selectedA);
  const { benchmarks: benchB } = useSessionBenchmark(selectedB);
  const { session: sessionA }  = useSessionMetadata(selectedA);

  // Compute accuracy delta between sessions for same model
  const deltas = useMemo(() => {
    return benchA.map(a => {
      const b = benchB.find(x => x.id === a.id);
      const diff = b ? a.accuracy - b.accuracy : null;
      return { id: a.id, name: a.modelName, accA: a.accuracy, accB: b?.accuracy ?? null, diff };
    });
  }, [benchA, benchB]);

  return (
    <FocusContainer data-testid="compare-engine">
      <div className="mx-auto max-w-6xl px-4 py-8 space-y-8">
        {/* ── Page header ──────────────────────────────────── */}
        <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
                <GitCompare size={16} className="text-cyan-400" />
              </div>
              <h1 className="text-xl font-bold text-white/95">
                {lang === 'es' ? 'Motor de Comparación' : 'Experiment Comparison Engine'}
              </h1>
            </div>
            <p className="text-sm text-slate-400 max-w-xl">
              {lang === 'es'
                ? 'Compara sesiones de experimentos en paralelo: robustez frente al ruido, precisión comparativa y geometría de embeddings.'
                : 'Compare experiment sessions side by side — noise robustness, accuracy differentials and embedding geometry evolution.'}
            </p>
          </div>

          {sessionA && (
            <ExportExperimentButton
              lang={lang}
              sessionId={selectedA}
              sessionData={sessionA}
              benchmarkData={benchA}
            />
          )}
        </div>

        {/* ── Session selectors ─────────────────────────────── */}
        <GlassPanel density="compact">
          <div className="flex flex-wrap items-center gap-4">
            {/* Left selector */}
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <div className="h-2 w-2 rounded-full bg-cyan-400 shrink-0" />
              <div className="flex-1">
                <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono mb-1">
                  {lang === 'es' ? 'Sesión A' : 'Session A'}
                </p>
                <select
                  value={selectedA}
                  onChange={e => setSelectedA(e.target.value)}
                  className="w-full rounded-lg border border-white/[0.08] bg-black/40 px-2.5 py-1.5 text-xs text-white/80 focus:outline-none focus:border-cyan-500/40"
                >
                  {SESSIONS.map(s => <option key={s.id} value={s.id}>{s.label[lang]}</option>)}
                </select>
              </div>
            </div>

            {/* VS badge */}
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/[0.08] bg-white/[0.03] text-[10px] font-bold text-slate-500">
              VS
            </div>

            {/* Right selector */}
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <div className="h-2 w-2 rounded-full bg-violet-400 shrink-0" />
              <div className="flex-1">
                <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono mb-1">
                  {lang === 'es' ? 'Sesión B' : 'Session B'}
                </p>
                <select
                  value={selectedB}
                  onChange={e => setSelectedB(e.target.value)}
                  className="w-full rounded-lg border border-white/[0.08] bg-black/40 px-2.5 py-1.5 text-xs text-white/80 focus:outline-none focus:border-violet-500/40"
                >
                  {SESSIONS.map(s => <option key={s.id} value={s.id}>{s.label[lang]}</option>)}
                </select>
              </div>
            </div>
          </div>
        </GlassPanel>

        {/* ── Split comparison columns ──────────────────────── */}
        <div className="flex flex-col gap-4 sm:flex-row">
          {/* Left border accent */}
          <div className="w-1 shrink-0 rounded-full bg-gradient-to-b from-cyan-500/30 via-cyan-500/10 to-transparent hidden sm:block" />

          <SessionColumn sessionId={selectedA} lang={lang} />

          {/* VS divider */}
          <div className="flex items-center justify-center sm:flex-col sm:gap-2">
            <div className="h-px flex-1 bg-white/[0.06] sm:h-full sm:w-px" />
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/[0.08] bg-[#030712] text-[9px] font-bold text-slate-600">
              VS
            </div>
            <div className="h-px flex-1 bg-white/[0.06] sm:h-full sm:w-px" />
          </div>

          <SessionColumn sessionId={selectedB} lang={lang} />

          {/* Right border accent */}
          <div className="w-1 shrink-0 rounded-full bg-gradient-to-b from-violet-500/30 via-violet-500/10 to-transparent hidden sm:block" />
        </div>

        {/* ── Live delta table ──────────────────────────────── */}
        {deltas.length > 0 && (
          <div id="compare-deltas" data-testid="compare-deltas">
          <GlassPanel density="compact" tone="active">
            <div className="flex items-center gap-2 mb-4">
              <Activity size={13} className="text-cyan-400" />
              <p className="text-xs font-semibold text-white/80">
                {lang === 'es' ? 'Δ Diferencial de Precisión (A − B)' : 'Δ Accuracy Differential (A − B)'}
              </p>
            </div>
            <div className="space-y-2">
              {deltas.map(d => {
                const pct = d.diff !== null ? d.diff * 100 : null;
                const positive = pct !== null && pct >= 0;
                return (
                  <div key={d.id} className="flex items-center justify-between text-[11px] gap-3">
                    <span className="text-slate-400 truncate">{d.name}</span>
                    <div className="flex items-center gap-2 font-mono shrink-0">
                      <span className="text-slate-500">{d.accA !== null ? `${(d.accA * 100).toFixed(1)}%` : '—'}</span>
                      <span className="text-slate-700">→</span>
                      <span className="text-slate-500">{d.accB !== null ? `${(d.accB * 100).toFixed(1)}%` : '—'}</span>
                      {pct !== null && (
                        <span className={`font-bold ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {positive ? '+' : ''}{pct.toFixed(1)} pp
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="mt-4 text-[10px] text-slate-500 leading-relaxed">
              {lang === 'es'
                ? 'Δ positivo indica que la sesión A supera a B. El clasificador NODE muestra mayor invarianza estructural frente al ruido gaussiano que las baselines clásicas.'
                : 'Positive Δ means session A outperforms session B. The NODE classifier shows superior structural invariance under Gaussian noise vs. classical baselines.'}
            </p>
          </GlassPanel>
          </div>
        )}

        <div className="grid gap-4 xl:grid-cols-2">
          <ExperimentReplayTimeline lang={lang} sessionId={selectedA} />
          <LatentEvolutionPlayer lang={lang} />
        </div>

        <LiveTelemetryConsole lang={lang} sessionId={selectedA} />
      </div>
    </FocusContainer>
  );
}
