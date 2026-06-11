'use client';

import { memo, useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Play, SkipBack, SkipForward, Gauge, Activity } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { cn } from '@/lib/utils/cn';
import type { Language } from '@/types';

// ── Types ─────────────────────────────────────────────────────
interface ReplayFrame {
  t: number;
  x: number;
  y: number;
  z: number;
  lyapunov: number;
  entropy: number;
  clusterLabel: number;
}

interface ExperimentReplayTimelineProps {
  lang: Language;
  sessionId?: string;
}

// ── Pre-computed synthetic replay trajectory ──────────────────
const REPLAY_FRAMES: ReplayFrame[] = Array.from({ length: 20 }, (_, i) => {
  const t = i / 19;
  const angle = t * Math.PI * 3.8;
  return {
    t,
    x: Math.cos(angle) * (1 - t * 0.18) * 42 + 50,
    y: Math.sin(angle) * (1 - t * 0.12) * 34 + 50,
    z: t * 82,
    lyapunov: 0.72 + t * 0.19 + Math.sin(angle * 2) * 0.06,
    entropy: 3.4 + t * 1.1 + Math.cos(angle) * 0.15,
    clusterLabel: t < 0.5 ? 0 : t < 0.82 ? 1 : 2,
  };
});

const CLUSTER_COLORS = ['text-cyan-400', 'text-violet-400', 'text-amber-400'];
const CLUSTER_DOTS   = ['bg-cyan-400',   'bg-violet-400',   'bg-amber-400'];
const CLUSTER_NAMES  = {
  en: ['Attractor A (Lorenz Wing)', 'Transition Zone', 'Attractor B (Divergent)'],
  es: ['Atractor A (Ala de Lorenz)', 'Zona de Transición', 'Atractor B (Divergente)'],
};

const MARKER_INDICES = [0, 5, 10, 14, 19];

function ExperimentReplayTimelineComponent({ lang }: ExperimentReplayTimelineProps) {
  const [frameIdx, setFrameIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const playRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const frame = useMemo(() => REPLAY_FRAMES[frameIdx]!, [frameIdx]);

  // ── Play / Pause ───────────────────────────────────────────
  const stopPlay = useCallback(() => {
    if (playRef.current) clearInterval(playRef.current);
    playRef.current = null;
    setPlaying(false);
  }, []);

  const startPlay = useCallback(() => {
    if (playRef.current) return;
    setPlaying(true);
    playRef.current = setInterval(() => {
      setFrameIdx(prev => {
        if (prev >= REPLAY_FRAMES.length - 1) {
          if (playRef.current) clearInterval(playRef.current);
          playRef.current = null;
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 180);
  }, []);

  useEffect(() => {
    return () => {
      if (playRef.current) clearInterval(playRef.current);
      playRef.current = null;
    };
  }, []);

  const toggle = useCallback(() => (playing ? stopPlay() : startPlay()), [playing, startPlay, stopPlay]);

  const seek = useCallback((idx: number) => {
    stopPlay();
    setFrameIdx(Math.max(0, Math.min(REPLAY_FRAMES.length - 1, idx)));
  }, [stopPlay]);

  // ── Attractor SVG trail ────────────────────────────────────
  const trailPath = useMemo(() => {
    const pts = REPLAY_FRAMES.slice(0, frameIdx + 1);
    return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  }, [frameIdx]);

  return (
    <GlassPanel data-testid="replay-timeline" density="normal" className="flex flex-col gap-5">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-500/10">
            <Clock size={15} className="text-violet-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-mono">
              {lang === 'es' ? 'Motor de Replay' : 'Replay Engine'}
            </p>
            <h3 className="text-sm font-semibold text-white/90">
              {lang === 'es' ? 'Línea Temporal del Experimento' : 'Experiment Timeline Replay'}
            </h3>
          </div>
        </div>

        {/* Frame counter */}
        <span className="font-mono text-xs text-slate-500">
          t = <span className="text-violet-300 font-bold">{frame.t.toFixed(2)}</span>
          &nbsp;/&nbsp;1.00
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_280px]">
        {/* ── Attractor canvas ─────────────────────────────── */}
        <div className="relative rounded-2xl border border-white/[0.07] bg-black/50 p-2 overflow-hidden">
          {/* Grid overlay */}
          <div className="absolute inset-0 scientific-grid opacity-[0.04] pointer-events-none" />
          {/* Radial glow */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(139,92,246,0.04),transparent_70%)] pointer-events-none" />

          <svg viewBox="0 0 100 100" className="h-56 w-full overflow-visible">
            {/* Ghost full trail */}
            <path
              d={REPLAY_FRAMES.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')}
              fill="none"
              stroke="rgba(139,92,246,0.08)"
              strokeWidth="0.6"
            />

            {/* Active replay trail */}
            <motion.path
              key={frameIdx}
              d={trailPath}
              fill="none"
              stroke="#8b5cf6"
              strokeWidth="0.7"
              strokeLinecap="round"
              opacity={0.9}
            />

            {/* Timeline markers */}
            {MARKER_INDICES.map(mi => {
              const mf = REPLAY_FRAMES[mi]!;
              return (
              <circle
                key={mi}
                cx={mf.x}
                cy={mf.y}
                r="1.2"
                fill={mi <= frameIdx ? '#8b5cf6' : 'rgba(255,255,255,0.08)'}
                stroke={mi <= frameIdx ? '#c4b5fd' : 'rgba(255,255,255,0.12)'}
                strokeWidth="0.4"
              />
              );
            })}

            {/* Current position dot */}
            <motion.circle
              key={`dot-${frameIdx}`}
              cx={frame.x}
              cy={frame.y}
              r="2.2"
              fill="#c4b5fd"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.12 }}
            />
          </svg>

          {/* Cluster label */}
          <div className="absolute bottom-3 left-3 flex items-center gap-1.5">
            <div className={cn('h-1.5 w-1.5 rounded-full', CLUSTER_DOTS[frame.clusterLabel])} />
            <span className={cn('text-[9px] font-semibold uppercase tracking-wider font-mono', CLUSTER_COLORS[frame.clusterLabel])}>
              {CLUSTER_NAMES[lang][frame.clusterLabel]}
            </span>
          </div>
        </div>

        {/* ── Right panel: metrics + controls ──────────────── */}
        <div className="flex flex-col gap-4">
          {/* Metrics */}
          <div className="grid grid-cols-2 gap-2">
            {[
              { icon: Activity, label: 'λ_max', value: frame.lyapunov.toFixed(3), color: 'text-cyan-400', sub: frame.lyapunov > 0 ? (lang === 'es' ? 'Caótico' : 'Chaotic') : (lang === 'es' ? 'Estable' : 'Stable') },
              { icon: Gauge, label: lang === 'es' ? 'Entropía' : 'Entropy', value: frame.entropy.toFixed(2), color: 'text-violet-400', sub: 'Shannon' },
            ].map(m => (
              <div key={m.label} className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <m.icon size={11} className={m.color} />
                  <span className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">{m.label}</span>
                </div>
                <p className={cn('font-mono text-xl font-bold', m.color)}>{m.value}</p>
                <p className="text-[9px] text-slate-500 mt-0.5">{m.sub}</p>
              </div>
            ))}
          </div>

          {/* Scrubber */}
          <div className="space-y-2">
            <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">
              {lang === 'es' ? 'Posición temporal' : 'Temporal position'}
            </p>
            <input
              type="range"
              min={0}
              max={REPLAY_FRAMES.length - 1}
              step={1}
              value={frameIdx}
              onChange={e => seek(Number(e.target.value))}
              className="w-full accent-violet-500 cursor-pointer"
            />
            <div className="flex justify-between text-[9px] font-mono text-slate-600">
              <span>t=0.00</span>
              <span>t=0.50</span>
              <span>t=1.00</span>
            </div>
          </div>

          {/* Transport controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => seek(0)}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-slate-400 hover:text-white transition-colors"
            >
              <SkipBack size={13} />
            </button>

            <button
              onClick={toggle}
              className={cn(
                'flex flex-1 items-center justify-center gap-2 rounded-xl border py-2 text-xs font-semibold transition-colors',
                playing
                  ? 'border-violet-500/30 bg-violet-500/10 text-violet-300 hover:bg-violet-500/15'
                  : 'border-white/[0.08] bg-white/[0.03] text-slate-300 hover:bg-white/[0.06] hover:text-white'
              )}
            >
              <Play size={12} />
              {playing
                ? (lang === 'es' ? 'Pausar Replay' : 'Pause Replay')
                : (lang === 'es' ? 'Iniciar Replay' : 'Play Replay')}
            </button>

            <button
              onClick={() => seek(REPLAY_FRAMES.length - 1)}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-slate-400 hover:text-white transition-colors"
            >
              <SkipForward size={13} />
            </button>
          </div>

          {/* Progress bar */}
          <div className="h-1 rounded-full bg-white/[0.06] overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-violet-500 to-purple-400"
              style={{ width: `${(frameIdx / (REPLAY_FRAMES.length - 1)) * 100}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

export const ExperimentReplayTimeline = memo(ExperimentReplayTimelineComponent);
