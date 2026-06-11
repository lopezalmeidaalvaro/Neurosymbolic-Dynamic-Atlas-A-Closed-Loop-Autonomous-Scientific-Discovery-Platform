'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Orbit, Compass, Plus, Minus } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface GeometryVisualizerProps {
  lang: Language;
}

export function GeometryVisualizer({ lang }: GeometryVisualizerProps) {
  const [separability, setSeparability] = useState<number>(85);
  const [selectedCluster, setSelectedCluster] = useState<string | null>(null);

  const clusters = [
    {
      id: 'lorenz',
      name: { en: 'Lorenz Attractor', es: 'Atractor de Lorenz' },
      color: 'text-cyan-400',
      fill: 'rgba(34,211,238,0.22)',
      stroke: '#22d3ee',
      nodes: [
        { x: 22, y: 35 },
        { x: 30, y: 24 },
        { x: 18, y: 15 },
        { x: 38, y: 32 },
        { x: 28, y: 44 },
      ],
    },
    {
      id: 'rossler',
      name: { en: 'Rössler System', es: 'Sistema Rössler' },
      color: 'text-violet-400',
      fill: 'rgba(167,139,250,0.22)',
      stroke: '#a78bfa',
      nodes: [
        { x: 68, y: 22 },
        { x: 74, y: 36 },
        { x: 58, y: 18 },
        { x: 80, y: 14 },
        { x: 84, y: 28 },
      ],
    },
    {
      id: 'duffing',
      name: { en: 'Duffing Oscillator', es: 'Oscilador Duffing' },
      color: 'text-emerald-400',
      fill: 'rgba(52,211,153,0.22)',
      stroke: '#34d399',
      nodes: [
        { x: 44, y: 72 },
        { x: 54, y: 82 },
        { x: 36, y: 62 },
        { x: 48, y: 55 },
        { x: 30, y: 80 },
      ],
    },
  ];

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-500/10 text-violet-400">
            <Compass size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Separabilidad Geométrica' : 'Geometric Separability'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Mapa de Embeddings Latentes' : 'Latent Embeddings Space'}
            </h3>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <div className="space-y-4">
          <p className="text-xs text-slate-400 leading-relaxed">
            {lang === 'es'
              ? 'Los descriptores neuronales agrupan sistemas caóticos de la misma familia topológica de forma compacta y geométrica.'
              : 'Neural descriptors group chaotic systems of the same topological family in a compact, geometric manner.'}
          </p>

          <div className="space-y-2">
            <p className="metric-label">{lang === 'es' ? 'Sistemas Detectados' : 'Detected Systems'}</p>
            <div className="space-y-2">
              {clusters.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCluster(selectedCluster === c.id ? null : c.id)}
                  className={`flex w-full items-center justify-between rounded-xl border p-2.5 text-xs transition-all ${
                    selectedCluster === c.id
                      ? 'border-white/20 bg-white/[0.08] text-white'
                      : 'border-white/[0.06] bg-white/[0.02] text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${c.color} bg-current shadow-[0_0_12px_currentColor]`} />
                    <span>{c.name[lang]}</span>
                  </div>
                  <span className="font-mono opacity-60">{c.nodes.length} pts</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="mb-2 flex justify-between text-xs font-semibold text-slate-300">
              <span>{lang === 'es' ? 'Métrica de Agrupamiento' : 'Clustering Separability'}</span>
              <span className="font-mono text-cyan-400">{separability}%</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setSeparability(Math.max(60, separability - 5))}
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.02] text-slate-400 hover:bg-white/[0.06] hover:text-white"
              >
                <Minus size={14} />
              </button>
              <button
                onClick={() => setSeparability(Math.min(100, separability + 5))}
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.02] text-slate-400 hover:bg-white/[0.06] hover:text-white"
              >
                <Plus size={14} />
              </button>
            </div>
          </div>
        </div>

        <div className="relative rounded-2xl border border-white/[0.08] bg-black/40 p-4">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(139,92,246,0.045),transparent_68%)] pointer-events-none" />
          <div className="absolute inset-0 scientific-grid opacity-[0.06] pointer-events-none" />

          {/* SVG Map representing 2D projections */}
          <div className="h-64 w-full">
            <svg viewBox="0 0 100 100" className="h-full w-full overflow-visible">
              {clusters.map((cluster) => {
                const isFocused = selectedCluster === null || selectedCluster === cluster.id;
                const center = cluster.nodes.reduce(
                  (acc, curr) => ({ x: acc.x + curr.x, y: acc.y + curr.y }),
                  { x: 0, y: 0 }
                );
                center.x /= cluster.nodes.length;
                center.y /= cluster.nodes.length;

                // Adjust spread based on separability slider
                const spreadRatio = (100 - separability) / 15 + 0.8;

                return (
                  <g key={cluster.id} className="transition-opacity duration-300" style={{ opacity: isFocused ? 1 : 0.25 }}>
                    {/* Shadow envelope polygon for nodes */}
                    <polygon
                      points={cluster.nodes
                        .map((n) => {
                          const px = center.x + (n.x - center.x) * spreadRatio;
                          const py = center.y + (n.y - center.y) * spreadRatio;
                          return `${px},${py}`;
                        })
                        .join(' ')}
                      fill={cluster.fill}
                      stroke={cluster.stroke}
                      strokeWidth="0.3"
                      strokeDasharray="2 2"
                      className="transition-all duration-300"
                    />

                    {/* Neighborhood connecting lines */}
                    {cluster.nodes.map((n, i) => {
                      const px = center.x + (n.x - center.x) * spreadRatio;
                      const py = center.y + (n.y - center.y) * spreadRatio;
                      return (
                        <line
                          key={i}
                          x1={center.x}
                          y1={center.y}
                          x2={px}
                          y2={py}
                          stroke={cluster.stroke}
                          strokeWidth="0.25"
                          opacity="0.4"
                        />
                      );
                    })}

                    {/* Cluster center */}
                    <circle cx={center.x} cy={center.y} r="1.5" fill={cluster.stroke} opacity="0.9" />

                    {/* Data Points */}
                    {cluster.nodes.map((n, i) => {
                      const px = center.x + (n.x - center.x) * spreadRatio;
                      const py = center.y + (n.y - center.y) * spreadRatio;

                      return (
                        <g key={i}>
                          <circle
                            cx={px}
                            cy={py}
                            r="1"
                            fill={cluster.stroke}
                            className="cursor-pointer transition-transform duration-200 hover:scale-150"
                          />
                          <circle cx={px} cy={py} r="2.5" stroke={cluster.stroke} strokeWidth="0.1" fill="none" opacity="0.15" />
                        </g>
                      );
                    })}
                  </g>
                );
              })}
            </svg>
          </div>

          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-slate-500 font-mono">
            <span>manifold dimension x</span>
            <span>manifold dimension y</span>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
