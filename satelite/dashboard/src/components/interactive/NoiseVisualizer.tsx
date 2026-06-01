'use client';

import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, ShieldAlert, Sparkles } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface NoiseVisualizerProps {
  lang: Language;
}

export function NoiseVisualizer({ lang }: NoiseVisualizerProps) {
  const [selectedSigma, setSelectedSigma] = useState<number>(0.1);

  const sigmas = [0.0, 0.1, 0.5, 1.0];

  const generateNoiseWave = (sigma: number) => {
    const points: Array<{ x: number; y: number }> = [];
    const steps = 60;
    for (let i = 0; i < steps; i++) {
      const t = (i / steps) * Math.PI * 4;
      const baseSignal = Math.sin(t) * 1.0;
      const seed = Math.sin(i * 12.9898 + sigma * 78.233) * 43758.5453;
      const noise = sigma === 0 ? 0 : (seed - Math.floor(seed) - 0.5) * sigma * 3;
      points.push({ x: (i / steps) * 100, y: baseSignal + noise });
    }
    return points;
  };

  const wavePoints = useMemo(() => generateNoiseWave(selectedSigma), [selectedSigma]);

  const getSigmaDescription = (sigma: number) => {
    if (sigma === 0.0) {
      return lang === 'es'
        ? 'Señal perfecta y determinista sin perturbaciones ambientales.'
        : 'Perfect, deterministic signal without environmental perturbations.';
    }
    if (sigma === 0.1) {
      return lang === 'es'
        ? 'Ruido estructural leve de medición. Patrones fácilmente identificables.'
        : 'Mild measurement structural noise. Patterns easily identifiable.';
    }
    if (sigma === 0.5) {
      return lang === 'es'
        ? 'Caos significativo y atenuación de picos. Requiere algoritmos de embedding para filtrado.'
        : 'Significant chaos and peak attenuation. Requires embedding algorithms for filtering.';
    }
    return lang === 'es'
      ? 'Señal severamente corrompida. El ruido supera la amplitud. Imposible de alinear con DTW convencional.'
      : 'Severely corrupted signal. Noise overrides amplitude. Conventional DTW alignment fails.';
  };

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-amber-500/20 bg-amber-500/10 text-amber-400">
            <ShieldAlert size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Observador de Ruido' : 'Noise Observatory'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Degradación por Sigma' : 'Sigma Degradation Simulator'}
            </h3>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {sigmas.map((sig) => (
            <button
              key={sig}
              onClick={() => setSelectedSigma(sig)}
              className={`rounded-xl border px-4 py-2 text-xs font-semibold tracking-wider transition-all ${
                selectedSigma === sig
                  ? 'border-amber-400/30 bg-amber-500/15 text-amber-300'
                  : 'border-white/[0.08] bg-white/[0.02] text-slate-400 hover:bg-white/[0.06] hover:text-white'
              }`}
            >
              σ = {sig.toFixed(1)}
            </button>
          ))}
        </div>

        <p className="text-sm text-slate-300/80 leading-relaxed min-h-[40px]">
          {getSigmaDescription(selectedSigma)}
        </p>

        <div className="relative rounded-2xl border border-white/[0.08] bg-black/50 p-4">
          <div className="h-44 w-full">
            <svg viewBox="0 -2.5 100 5" preserveAspectRatio="none" className="h-full w-full overflow-visible">
              {/* Reference Grid lines */}
              <line x1="0" y1="-1" x2="100" y2="-1" stroke="rgba(255,255,255,0.04)" strokeWidth="0.04" />
              <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,255,255,0.08)" strokeWidth="0.06" />
              <line x1="0" y1="1" x2="100" y2="1" stroke="rgba(255,255,255,0.04)" strokeWidth="0.04" />

              <motion.path
                key={`noise-wave-${selectedSigma}`}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                d={wavePoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')}
                fill="none"
                stroke="#fbbf24"
                strokeWidth="0.10"
                strokeLinecap="round"
              />
            </svg>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-xl border border-white/[0.05] bg-white/[0.015] p-3 text-xs text-slate-400">
          <Sparkles size={14} className="text-cyan-400 shrink-0" />
          <span>
            {lang === 'es'
              ? 'Con σ = 1.0, el caos es total, pero nuestro modelo neurosimbólico logra extraer descriptores invariantes.'
              : 'At σ = 1.0, chaos is total, but our neurosymbolic model successfully extracts invariant descriptors.'}
          </span>
        </div>
      </div>
    </GlassPanel>
  );
}
