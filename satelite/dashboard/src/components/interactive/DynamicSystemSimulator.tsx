'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, Orbit, RefreshCw } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface DynamicSystemSimulatorProps {
  lang: Language;
}

export function DynamicSystemSimulator({ lang }: DynamicSystemSimulatorProps) {
  const [rho, setRho] = useState<number>(28); // Standard chaotic rho
  const [sigma, setSigma] = useState<number>(10);
  const [beta, setBeta] = useState<number>(2.666); // 8/3 standard beta

  const generateLorenzAttractor = (s: number, r: number, b: number) => {
    let x = 0.1;
    let y = 0.0;
    let z = 0.0;
    const dt = 0.01;
    const points: Array<{ x: number; y: number }> = [];

    // Solve equations iteratively using Euler method (downscaled to 10% in development for CPU safety)
    const iterations = process.env.NODE_ENV === 'development' ? 32 : 320;
    for (let i = 0; i < iterations; i++) {
      const dx = s * (y - x) * dt;
      const dy = (x * (r - z) - y) * dt;
      const dz = (x * y - b * z) * dt;
      x += dx;
      y += dy;
      z += dz;

      // Project 3D coordinate (x, z) to 2D SVG bounds
      points.push({
        x: 50 + x * 1.6,
        y: 90 - z * 1.6,
      });
    }
    return points;
  };

  const attractorPoints = generateLorenzAttractor(sigma, rho, beta);

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
            <Orbit size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Simulador de Caos' : 'Chaos Simulator'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Fase del Atractor de Lorenz' : 'Lorenz Attractor Evolution'}
            </h3>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <div className="space-y-5">
          <p className="text-xs text-slate-400 leading-relaxed">
            {lang === 'es'
              ? 'Ajusta los parámetros físicos clásicos para desencadenar bifurcaciones o estabilizar el caos en órbitas periódicas.'
              : 'Adjust physical system parameters to trigger bifurcations or stabilize the chaotic orbits into periodic cycles.'}
          </p>

          <div className="space-y-4">
            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>{lang === 'es' ? 'Número de Rayleigh (ρ)' : 'Rayleigh number (ρ)'}</span>
                <span className="font-mono text-cyan-400">{rho.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="10"
                max="40"
                step="0.5"
                value={rho}
                onChange={(e) => setRho(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>{lang === 'es' ? 'Prandtl number (σ)' : 'Prandtl number (σ)'}</span>
                <span className="font-mono text-cyan-400">{sigma.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="4"
                max="18"
                step="0.5"
                value={sigma}
                onChange={(e) => setSigma(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
                <span>Beta (β)</span>
                <span className="font-mono text-cyan-400">{beta.toFixed(3)}</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="4.0"
                step="0.1"
                value={beta}
                onChange={(e) => setBeta(parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>
          </div>

          <button
            onClick={() => {
              setRho(28);
              setSigma(10);
              setBeta(2.666);
            }}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.03] py-2 text-xs font-medium text-slate-300 transition-colors hover:bg-white/[0.07] hover:text-white"
          >
            <RefreshCw size={12} />
            <span>{lang === 'es' ? 'Restablecer Atractor' : 'Reset attractor'}</span>
          </button>
        </div>

        <div className="relative rounded-2xl border border-white/[0.08] bg-black/40 p-4">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(6,182,212,0.03),transparent_74%)] pointer-events-none" />
          <div className="absolute inset-0 scientific-grid opacity-[0.04] pointer-events-none" />

          {/* Attractor Plot */}
          <div className="h-64 w-full">
            <svg viewBox="0 0 100 100" className="h-full w-full overflow-visible">
              <motion.path
                key={`lorenz-${rho}-${sigma}-${beta}`}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.2, ease: 'linear' }}
                d={attractorPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')}
                fill="none"
                stroke="#22d3ee"
                strokeWidth="0.4"
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity="0.85"
              />
            </svg>
          </div>

          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-slate-500 font-mono">
            <span>x-axis (attractor coordinate x)</span>
            <span>z-axis (attractor coordinate z)</span>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
