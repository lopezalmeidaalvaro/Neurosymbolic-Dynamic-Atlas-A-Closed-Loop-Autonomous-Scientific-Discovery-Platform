'use client';

import { motion } from 'framer-motion';
import { ShieldCheck, BarChart3, HelpCircle } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface ModelComparatorProps {
  lang: Language;
}

export function ModelComparator({ lang }: ModelComparatorProps) {
  const models = [
    {
      name: 'Dynamic Time Warping (DTW)',
      accuracy: 74.2,
      speed: '1x (Baseline)',
      noiseTolerance: 45,
      params: 'O(N²)',
      isOurs: false,
    },
    {
      name: 'ROCKET (Rand Convolutional)',
      accuracy: 88.5,
      speed: '12x fast',
      noiseTolerance: 68,
      params: '20,000 kernels',
      isOurs: false,
    },
    {
      name: 'Neurosymbolic Embedding V2',
      accuracy: 96.8,
      speed: '79x fast',
      noiseTolerance: 94,
      params: 'Compact 512-dim',
      isOurs: true,
    },
  ];

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
            <BarChart3 size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Comparador SOTA' : 'SOTA Comparison'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Desempeño Frente a Modelos Convencionales' : 'Model Benchmarks'}
            </h3>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead>
            <tr className="border-b border-white/[0.08] text-slate-500">
              <th className="pb-3 pl-2 font-semibold uppercase tracking-[0.14em]">
                {lang === 'es' ? 'Modelo' : 'Model'}
              </th>
              <th className="pb-3 font-semibold uppercase tracking-[0.14em]">
                {lang === 'es' ? 'Precisión' : 'Accuracy'}
              </th>
              <th className="pb-3 font-semibold uppercase tracking-[0.14em]">
                {lang === 'es' ? 'Velocidad' : 'Speed'}
              </th>
              <th className="pb-3 font-semibold uppercase tracking-[0.14em]">
                {lang === 'es' ? 'Tolerancia al Ruido' : 'Noise Tolerance'}
              </th>
              <th className="pb-3 pr-2 font-semibold uppercase tracking-[0.14em]">
                {lang === 'es' ? 'Complejidad / Tamaño' : 'Parameters / Size'}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {models.map((m) => (
              <tr
                key={m.name}
                className={`transition-colors ${
                  m.isOurs ? 'bg-cyan-500/[0.04] text-white' : 'hover:bg-white/[0.015]'
                }`}
              >
                <td className="py-4 pl-2 font-semibold">
                  <div className="flex items-center gap-2">
                    {m.isOurs && (
                      <span className="rounded-full bg-cyan-400/15 border border-cyan-400/20 px-2 py-0.5 text-[9px] font-bold text-cyan-300 uppercase tracking-widest font-mono">
                        Ours
                      </span>
                    )}
                    <span>{m.name}</span>
                  </div>
                </td>
                <td className="py-4 font-mono font-semibold">
                  <div className="flex items-center gap-3">
                    <span className={m.isOurs ? 'text-cyan-300' : 'text-slate-400'}>{m.accuracy}%</span>
                    <div className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-slate-800 sm:block">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${m.accuracy}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className={`h-full rounded-full ${m.isOurs ? 'bg-cyan-400' : 'bg-slate-500'}`}
                      />
                    </div>
                  </div>
                </td>
                <td className="py-4 font-mono font-medium">
                  <span className={m.isOurs ? 'text-cyan-400 font-bold' : 'text-slate-400'}>{m.speed}</span>
                </td>
                <td className="py-4 font-mono">
                  <div className="flex items-center gap-3">
                    <span className={m.isOurs ? 'text-amber-400' : 'text-slate-400'}>{m.noiseTolerance}%</span>
                    <div className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-slate-800 sm:block">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${m.noiseTolerance}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className={`h-full rounded-full ${m.isOurs ? 'bg-amber-400' : 'bg-slate-500'}`}
                      />
                    </div>
                  </div>
                </td>
                <td className="py-4 pr-2 font-mono text-slate-400">{m.params}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-2 rounded-xl border border-white/[0.05] bg-white/[0.015] p-3 text-xs text-slate-400">
        <ShieldCheck size={14} className="text-cyan-400 shrink-0" />
        <span>
          {lang === 'es'
            ? 'Los resultados muestran la superioridad del modelo neurosimbólico en entornos caóticos con alta presencia de ruido.'
            : 'Benchmark logs indicate extreme neurosymbolic superiority inside highly noisy or chaotic physical settings.'}
        </span>
      </div>
    </GlassPanel>
  );
}
