'use client';

import { memo, useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { Layers, Play, SkipBack, TrendingUp } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { cn } from '@/lib/utils/cn';
import type { Language } from '@/types';

// ── Types ─────────────────────────────────────────────────────
interface EmbeddingPoint {
  t: number;
  x: number;
  y: number;
  curvature: number;
  cluster: number;
}

interface LatentEvolutionPlayerProps {
  lang: Language;
}

// ── Synthetic evolution trajectory ────────────────────────────
// Two basins of attraction in PCA space, point migrates over time (downscaled in development)
const EVOLUTION_LENGTH = process.env.NODE_ENV === 'development' ? 5 : 24;

const EVOLUTION: EmbeddingPoint[] = Array.from({ length: EVOLUTION_LENGTH }, (_, i) => {
  const t = i / (EVOLUTION_LENGTH - 1 || 1);
  const theta = t * Math.PI * 2.4;
  const radius = 0.92 - t * 0.26;
  return {
    t,
    x: Math.cos(theta) * radius * 38 + 50,
    y: Math.sin(theta) * radius * 28 + 50,
    curvature: 0.04 + t * 0.09 + Math.sin(theta) * 0.02,
    cluster: t < 0.45 ? 0 : t < 0.78 ? 1 : 2,
  };
});

const CLUSTERS = {
  en: ['Lorenz Basin A', 'Transition Manifold', 'Lorenz Basin B'],
  es: ['Cuenca Lorenz A', 'Variedad de Transición', 'Cuenca Lorenz B'],
};

const C_STROKE  = ['#22d3ee', '#8b5cf6', '#f59e0b'];
const C_FILL    = ['rgba(34,211,238,0.75)', 'rgba(139,92,246,0.75)', 'rgba(245,158,11,0.75)'];
const C_SHADOW  = ['rgba(34,211,238,0.25)', 'rgba(139,92,246,0.25)', 'rgba(245,158,11,0.25)'];

function LatentEvolutionPlayerComponent({ lang }: LatentEvolutionPlayerProps) {
  const [frame, setFrame] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const pt = useMemo(() => EVOLUTION[frame]!, [frame]);

  const stop = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    setPlaying(false);
  }, []);

  const play = useCallback(() => {
    if (timerRef.current) return;
    setPlaying(true);
    timerRef.current = setInterval(() => {
      setFrame(prev => {
        if (prev >= EVOLUTION.length - 1) { stop(); return prev; }
        return prev + 1;
      });
    }, 160);
  }, [stop]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, []);

  const toggle = useCallback(() => playing ? stop() : play(), [play, playing, stop]);
  const reset  = useCallback(() => { stop(); setFrame(0); }, [stop]);

  // ── Build trail with fading opacity ──────────────────────────
  const trail = useMemo(
    () => EVOLUTION.slice(0, frame + 1),
    [frame]
  );

  return (
    <GlassPanel data-testid="latent-evolution-player" density="normal" className="flex flex-col gap-5">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-amber-500/20 bg-amber-500/10">
            <Layers size={15} className="text-amber-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-mono">
              {lang === 'es' ? 'Espacio Latente' : 'Latent Space'}
            </p>
            <h3 className="text-sm font-semibold text-white/90">
              {lang === 'es' ? 'Evolución del Embedding' : 'Embedding Evolution'}
            </h3>
          </div>
        </div>
        <span className="font-mono text-xs text-slate-500">
          PCA · t = <span className="text-amber-300 font-bold">{pt.t.toFixed(2)}</span>
        </span>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_220px]">
        {/* ── Canvas ─────────────────────────────────────────── */}
        <div className="relative rounded-2xl border border-white/[0.07] bg-[#010409]/80 overflow-hidden p-2">
          <div className="absolute inset-0 scientific-grid opacity-[0.04] pointer-events-none" />

          <svg viewBox="0 0 100 100" className="h-60 w-full">
            {/* Axes */}
            <line x1="5" y1="95" x2="95" y2="95" stroke="rgba(255,255,255,0.06)" strokeWidth="0.4" />
            <line x1="5" y1="5"  x2="5"  y2="95" stroke="rgba(255,255,255,0.06)" strokeWidth="0.4" />

            {/* Ghost full path */}
            <path
              d={EVOLUTION.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')}
              fill="none"
              stroke="rgba(255,255,255,0.04)"
              strokeWidth="0.5"
            />

            {/* Cinematic trail with fade */}
            {trail.map((p, i) => {
              if (i === 0) return null;
              const alpha = (i / trail.length) * 0.9;
              const prev = trail[i - 1]!;
              return (
                <line
                  key={i}
                  x1={prev.x} y1={prev.y}
                  x2={p.x}            y2={p.y}
                  stroke={C_STROKE[p.cluster]}
                  strokeWidth="0.7"
                  opacity={alpha}
                />
              );
            })}

            {/* Historical ghost dots */}
            {trail.slice(0, -1).map((p, i) => (
              <circle
                key={`ghost-${i}`}
                cx={p.x} cy={p.y} r="0.8"
                fill={C_FILL[p.cluster]}
                opacity={0.12 + (i / trail.length) * 0.3}
              />
            ))}

            {/* Animated glow around current point */}
            <motion.circle
              cx={pt.x} cy={pt.y} r="5"
              fill={C_SHADOW[pt.cluster]}
              animate={{ r: [4.5, 6.5, 4.5] }}
              transition={{ repeat: Infinity, duration: 1.6, ease: 'easeInOut' }}
            />

            {/* Current point */}
            <motion.circle
              key={`main-${frame}`}
              cx={pt.x} cy={pt.y} r="2.8"
              fill={C_FILL[pt.cluster]}
              stroke={C_STROKE[pt.cluster]}
              strokeWidth="0.5"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.12 }}
            />
          </svg>

          {/* Axis labels */}
          <div className="absolute bottom-2 right-3 text-[8px] font-mono text-slate-600">PC₁</div>
          <div className="absolute top-2 left-3 text-[8px] font-mono text-slate-600">PC₂</div>

          {/* Cluster legend */}
          <div className="absolute bottom-2 left-2 flex flex-col gap-0.5">
            {[0, 1, 2].map(c => (
              <div key={c} className="flex items-center gap-1">
                <div className="h-1 w-1 rounded-full" style={{ background: C_STROKE[c] }} />
                <span className="text-[7px] font-mono" style={{ color: C_STROKE[c] }}>
                  {CLUSTERS[lang][c]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Right controls ──────────────────────────────────── */}
        <div className="flex flex-col gap-4">
          {/* Curvature metric */}
          <div className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
            <div className="flex items-center gap-1.5 mb-2">
              <TrendingUp size={11} className="text-amber-400" />
              <span className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">
                {lang === 'es' ? 'Curvatura Local' : 'Local Curvature'}
              </span>
            </div>
            <p className="font-mono text-2xl font-bold text-amber-300">{pt.curvature.toFixed(4)}</p>
            <p className="text-[9px] text-slate-500 mt-1">κ (geodesic)</p>
          </div>

          {/* Cluster badge */}
          <div className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
            <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono mb-2">
              {lang === 'es' ? 'Clúster Actual' : 'Active Cluster'}
            </p>
            <div className="flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full" style={{ background: C_STROKE[pt.cluster] }} />
              <span className="text-xs font-semibold text-white/80" style={{ color: C_STROKE[pt.cluster] }}>
                {CLUSTERS[lang][pt.cluster]}
              </span>
            </div>
          </div>

          {/* Scrubber */}
          <div className="space-y-1.5">
            <p className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">
              {lang === 'es' ? 'Posición' : 'Position'}
            </p>
            <input
              type="range"
              min={0}
              max={EVOLUTION.length - 1}
              step={1}
              value={frame}
              onChange={e => { stop(); setFrame(Number(e.target.value)); }}
              className="w-full accent-amber-500 cursor-pointer"
            />
          </div>

          {/* Transport */}
          <div className="flex gap-2">
            <button
              onClick={reset}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.03] text-slate-400 hover:text-white transition-colors"
            >
              <SkipBack size={13} />
            </button>
            <button
              onClick={toggle}
              className={cn(
                'flex flex-1 items-center justify-center gap-2 rounded-xl border py-2 text-xs font-semibold transition-colors',
                playing
                  ? 'border-amber-500/30 bg-amber-500/10 text-amber-300 hover:bg-amber-500/15'
                  : 'border-white/[0.08] bg-white/[0.03] text-slate-300 hover:bg-white/[0.06]'
              )}
            >
              <Play size={11} />
              {playing ? (lang === 'es' ? 'Pausar' : 'Pause') : (lang === 'es' ? 'Animar' : 'Animate')}
            </button>
          </div>

          {/* Progress */}
          <div className="h-1 rounded-full bg-white/[0.06] overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-amber-500 to-yellow-400"
              style={{ width: `${(frame / (EVOLUTION.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

export const LatentEvolutionPlayer = memo(LatentEvolutionPlayerComponent);
