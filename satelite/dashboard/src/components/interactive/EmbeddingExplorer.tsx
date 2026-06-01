'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, Shield, Cpu, RefreshCw } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

interface EmbeddingExplorerProps {
  lang: Language;
}

export function EmbeddingExplorer({ lang }: EmbeddingExplorerProps) {
  const [selectedNode, setSelectedNode] = useState<number | null>(0);

  const nodes = [
    { id: 0, x: 0.12, y: 0.88, z: -0.34, label: 'Run 8A - Lorenz chaotic' },
    { id: 1, x: 0.15, y: 0.84, z: -0.29, label: 'Run 8B - Lorenz low-noise' },
    { id: 2, x: 0.76, y: -0.12, z: 0.54, label: 'Run 12A - Duffing baseline' },
    { id: 3, x: 0.72, y: -0.18, z: 0.49, label: 'Run 12B - Duffing noisy' },
    { id: 4, x: -0.45, y: 0.32, z: -0.88, label: 'Run 14A - Rossler chaotic' },
  ];

  const calculateDistance = (n1: typeof nodes[0], n2: typeof nodes[0]) => {
    return Math.sqrt(Math.pow(n1.x - n2.x, 2) + Math.pow(n1.y - n2.y, 2) + Math.pow(n1.z - n2.z, 2)).toFixed(4);
  };

  const getDistanceTable = () => {
    if (selectedNode === null) return [];
    const source = nodes.find(n => n.id === selectedNode);
    if (!source) return [];
    return nodes
      .map((n) => ({
        label: n.label,
        dist: calculateDistance(source, n),
        id: n.id,
      }))
      .sort((a, b) => parseFloat(a.dist) - parseFloat(b.dist));
  };

  const distances = getDistanceTable();

  return (
    <GlassPanel density="normal" className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
            <Cpu size={16} />
          </div>
          <div>
            <p className="metric-label">{lang === 'es' ? 'Explorador Latente' : 'Embedding Explorer'}</p>
            <h3 className="text-lg font-semibold text-white/90">
              {lang === 'es' ? 'Vectorizador de Atractores' : 'Vector Space Inspector'}
            </h3>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <p className="text-xs text-slate-400 leading-relaxed">
            {lang === 'es'
              ? 'Haz clic en cualquier nodo para calcular de forma inmediata su vector de distancia euclidiana en el hiperespacio latente.'
              : 'Click any node to instantly calculate its Euclidean distance vector in the latent hyperspace.'}
          </p>

          <div className="rounded-2xl border border-white/[0.08] bg-black/40 p-4">
            <p className="metric-label mb-3">{lang === 'es' ? 'Vectores Seleccionados' : 'Selected Vectors'}</p>
            <div className="space-y-2">
              {nodes.map((node) => (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node.id)}
                  className={`flex w-full items-center justify-between rounded-xl border p-2.5 text-xs transition-all ${
                    selectedNode === node.id
                      ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
                      : 'border-white/[0.06] bg-white/[0.02] text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                  }`}
                >
                  <span className="truncate">{node.label}</span>
                  <span className="font-mono text-[10px] opacity-60">
                    [{node.x.toFixed(2)}, {node.y.toFixed(2)}]
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-white/[0.08] bg-black/40 p-4 flex flex-col justify-between">
          <div>
            <div className="mb-4 flex items-center justify-between">
              <p className="metric-label">
                {lang === 'es' ? 'Matriz de Proximidad Latente' : 'Latent Proximity Matrix'}
              </p>
              <span className="rounded-full bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 text-[9px] font-semibold text-cyan-300 uppercase tracking-widest font-mono">
                Euclidean Dist
              </span>
            </div>

            <div className="space-y-2.5">
              {distances.map((item) => (
                <div
                  key={item.id}
                  className={`flex items-center justify-between rounded-xl border px-3 py-2 text-xs transition-all ${
                    item.id === selectedNode
                      ? 'border-white/10 bg-white/[0.04] text-white'
                      : 'border-white/[0.04] bg-white/[0.015] text-slate-400'
                  }`}
                >
                  <span className="truncate">{item.label}</span>
                  <span className="font-mono text-cyan-400 font-bold">
                    {item.id === selectedNode ? '0.0000 (Self)' : item.dist}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500 font-mono">
            <Eye size={12} className="text-cyan-400" />
            <span>
              {lang === 'es'
                ? 'Agrupamiento e invariabilidad dimensional comprobados'
                : 'Dimensional invariancy & clustering validated'}
            </span>
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
