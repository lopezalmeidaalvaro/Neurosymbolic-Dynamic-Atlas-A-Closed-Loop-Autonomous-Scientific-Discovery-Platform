'use client';

import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Sliders, RefreshCw, Zap } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface SignalPlaygroundProps {
  lang: Language;
}

export function SignalPlayground({ lang }: SignalPlaygroundProps) {
  const [amplitude, setAmplitude] = useState<number>(1.2);
  const [frequency, setFrequency] = useState<number>(2.0);
  const [noise, setNoise] = useState<number>(0.15);

  const steps = 100;
  const stableNoise = (index: number, amp: number, freq: number, sigma: number) => {
    if (sigma === 0) return 0;
    const seed = Math.sin(index * 12.9898 + amp * 78.233 + freq * 37.719 + sigma * 19.19) * 43758.5453;
    return (seed - Math.floor(seed) - 0.5) * sigma * 3;
  };

  const generateSignal = (amp: number, freq: number, noiseSigma: number) => {
    const points: Array<{ x: number; y1: number; y2: number }> = [];
    for (let i = 0; i < steps; i++) {
      const t = (i / steps) * Math.PI * 4;
      const clean = amp * Math.sin(freq * t);
      const randomNoise = stableNoise(i, amp, freq, noiseSigma);
      points.push({
        x: i,
        y1: clean,
        y2: clean + randomNoise,
      });
    }
    return points;
  };

  const signalData = useMemo(
    () => generateSignal(amplitude, frequency, noise),
    [amplitude, frequency, noise]
  );

  // Approximate alignment error (DTW-like calculation)
  const calculateDTWDistance = () => {
    let dist = 0;
    for (let i = 0; i < steps; i++) {
      const dataPoint = signalData[i];
      if (dataPoint) {
        dist += Math.abs(dataPoint.y1 - dataPoint.y2);
      }
    }
    return (dist / steps).toFixed(4);
  };

  const dtwDistance = useMemo(calculateDTWDistance, [signalData]);

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
            <Sliders size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Simulador de Señales' : 'Signal Playground'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Frecuencia y Amplitud Dinámica' : 'Dynamic Frequency & Amplitude'}
            </h3>
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.03] px-3 py-1.5 text-xs text-slate-400 font-mono">
          <Zap size={12} className="text-cyan-400" />
          <span>DTW Error: {dtwDistance}</span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <div className="space-y-5">
          <p className="text-xs text-slate-400 leading-relaxed">
            {lang === 'es'
              ? 'Manipula los parámetros para alterar la señal en tiempo real y observa cómo el algoritmo mide la distorsión matemática.'
              : 'Manipulate variables to alter the signal in real-time and witness how the algorithm measures the mathematical distortion.'}
          </p>

          <div className="space-y-4">
            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>{lang === 'es' ? 'Amplitud' : 'Amplitude'}</span>
                <span className="font-mono text-cyan-400">{amplitude.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.2"
                max="2.5"
                step="0.05"
                value={amplitude}
                onChange={(e) => setAmplitude(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>{lang === 'es' ? 'Frecuencia' : 'Frequency'}</span>
                <span className="font-mono text-cyan-400">{frequency.toFixed(2)} Hz</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="5.0"
                step="0.1"
                value={frequency}
                onChange={(e) => setFrequency(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>{lang === 'es' ? 'Ruido Blanco (σ)' : 'White Noise (σ)'}</span>
                <span className="font-mono text-amber-400">{noise.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.2"
                step="0.02"
                value={noise}
                onChange={(e) => setNoise(parseFloat(e.target.value))}
                className="w-full accent-amber-400"
              />
            </div>
          </div>

          <button
            onClick={() => {
              setAmplitude(1.2);
              setFrequency(2.0);
              setNoise(0.15);
            }}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.03] py-2 text-xs font-medium text-slate-300 transition-colors hover:bg-white/[0.07] hover:text-white"
          >
            <RefreshCw size={12} />
            <span>{lang === 'es' ? 'Restablecer' : 'Reset defaults'}</span>
          </button>
        </div>

        <div className="relative rounded-2xl border border-white/[0.08] bg-black/40 p-4">
          <div className="absolute top-4 right-4 flex items-center gap-4 text-[10px] font-semibold uppercase tracking-[0.14em]">
            <div className="flex items-center gap-1.5 text-cyan-400">
              <span className="h-2 w-2 rounded-full bg-current" />
              <span>{lang === 'es' ? 'Original' : 'Clean'}</span>
            </div>
            <div className="flex items-center gap-1.5 text-amber-400">
              <span className="h-2 w-2 rounded-full bg-current" />
              <span>{lang === 'es' ? 'Perturbada' : 'Distorted'}</span>
            </div>
          </div>

          {/* SVG Plotting */}
          <div className="mt-8 h-48 w-full">
            <svg viewBox={`0 -3 100 6`} preserveAspectRatio="none" className="h-full w-full overflow-visible">
              <line x1="0" y1="0" x2="100" y2="0" stroke="rgba(255,255,255,0.08)" strokeWidth="0.05" />

              {/* Clean signal path */}
              <motion.path
                key={`clean-${amplitude}-${frequency}`}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.5 }}
                d={signalData.map((d, i) => `${i === 0 ? 'M' : 'L'} ${(i / steps) * 100} ${d.y1}`).join(' ')}
                fill="none"
                stroke="#22d3ee"
                strokeWidth="0.12"
                strokeLinecap="round"
              />

              {/* Distorted signal path */}
              <motion.path
                key={`distorted-${amplitude}-${frequency}-${noise}`}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.4 }}
                d={signalData.map((d, i) => `${i === 0 ? 'M' : 'L'} ${(i / steps) * 100} ${d.y2}`).join(' ')}
                fill="none"
                stroke="#fbbf24"
                strokeWidth="0.08"
                strokeOpacity="0.8"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div className="mt-4 flex items-center justify-between text-[10px] uppercase tracking-[0.18em] text-slate-500 font-mono">
            <span>t = 0.00s</span>
            <span>{lang === 'es' ? 'Mapeo temporal continuo' : 'Continuous temporal mapping'}</span>
            <span>t = 1.00s</span>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
