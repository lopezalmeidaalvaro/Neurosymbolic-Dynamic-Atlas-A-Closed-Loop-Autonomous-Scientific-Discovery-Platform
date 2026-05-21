'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRobustnessReport } from '@/hooks/useScientificArtifacts';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import type { Language } from '@/types';
import {
  ShieldAlert,
  ShieldCheck,
  Activity,
  LineChart,
  HelpCircle,
  Cpu,
  Brain,
  Network
} from 'lucide-react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

interface NoiseRobustnessObservatoryProps {
  lang: Language;
}

export function NoiseRobustnessObservatory({ lang }: NoiseRobustnessObservatoryProps) {
  const { report, isLoading, isError } = useRobustnessReport();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (isLoading) {
    return (
      <GlassPanel className="flex h-96 items-center justify-center border-white/[0.05] bg-slate-950/20">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          <p className="font-mono text-sm text-slate-400/80">
            {lang === 'es' ? 'Cargando metadatos de resistencia al ruido...' : 'Fetching noise robustness metadata...'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  if (isError || !report) {
    return (
      <GlassPanel className="border-red-500/20 bg-red-950/5 p-8" tone="neutral">
        <div className="flex flex-col items-center gap-4 text-center">
          <ShieldAlert className="h-12 w-12 text-amber-500/80" />
          <h3 className="text-lg font-semibold text-slate-100">
            {lang === 'es' ? 'Reporte no disponible' : 'Report Unavailable'}
          </h3>
          <p className="max-w-md text-sm leading-6 text-slate-400">
            {lang === 'es'
              ? 'El reporte de resistencia al ruido no está disponible. Ejecuta un barrido de ruido autónomo (python run_autonomous_sweep.py) en el backend para generar la telemetría.'
              : 'The noise robustness report is not available. Run an autonomous noise sweep (python run_autonomous_sweep.py) in the backend to generate the telemetry.'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  const chartData = report.analysis_results.runs.map((run) => ({
    noise: run.noise_level,
    'Embedding V2': Number((run.accuracy * 100).toFixed(1)),
    ROCKET: Number((run.rocket_accuracy * 100).toFixed(1)),
    DTW: Number((run.dtw_accuracy * 100).toFixed(1)),
    Drift: Number(run.average_drift.toFixed(4)),
  }));

  const formatStatus = (status: string) => {
    let label = '';
    let color = '';
    let tone: 'neutral' | 'active' | 'success' | 'warning' = 'neutral';
    let icon = ShieldCheck;

    if (status === 'VALIDATED') {
      label = lang === 'es' ? 'VALIDADA' : 'VALIDATED';
      color = 'text-emerald-400 bg-emerald-400/10 border-emerald-500/20';
      tone = 'success';
      icon = ShieldCheck;
    } else if (status === 'NO_COLLAPSE_OBSERVED') {
      label = lang === 'es' ? 'SIN COLAPSO' : 'NO COLLAPSE';
      color = 'text-cyan-400 bg-cyan-400/10 border-cyan-500/20';
      tone = 'active';
      icon = ShieldCheck;
    } else {
      label = lang === 'es' ? 'FALSIFICADA' : 'FALSIFIED';
      color = 'text-amber-400 bg-amber-400/10 border-amber-500/20';
      tone = 'warning';
      icon = ShieldAlert;
    }

    return { label, color, tone, icon };
  };

  return (
    <div className="space-y-8">
      {/* Header section */}
      <ScrollReveal>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <span className="research-kicker mb-3">
              <Activity size={13} />
              {lang === 'es' ? 'BARRIDO AUTÓNOMO DE RUIDO' : 'AUTONOMOUS NOISE SWEEP'}
            </span>
            <h2 className="cinematic-heading text-3xl sm:text-4xl">
              {lang === 'es'
                ? 'Observatorio de Resistencia al Ruido'
                : 'Noise Robustness Observatory'}
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              {lang === 'es'
                ? 'Análisis de la degradación del clasificador frente a la deformación de la variedad latente'
                : 'Analysis of classifier degradation vs latent manifold deformation'}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs font-mono">
            <div className="rounded-lg border border-white/[0.06] bg-slate-950/40 px-3 py-2">
              <span className="text-slate-500 mr-2">Base:</span>
              <span className="text-cyan-300 font-semibold uppercase">{report.analysis_results.baseline_session_id}</span>
            </div>
            <div className="rounded-lg border border-white/[0.06] bg-slate-950/40 px-3 py-2">
              <span className="text-slate-500 mr-2">Model:</span>
              <span className="text-slate-300">{report.metadata.pipeline_model}</span>
            </div>
          </div>
        </div>
      </ScrollReveal>

      {/* Grid of chart & hypotheses */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column: Composed dual-axis Chart */}
        <div className="lg:col-span-7">
          <ScrollReveal>
            <GlassPanel density="spacious" className="h-[480px] flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <LineChart className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-md font-semibold text-slate-100">
                    {lang === 'es' ? 'Degradación Topológica de Precisión & Deriva' : 'Topological Degradation of Accuracy & Drift'}
                  </h3>
                </div>
                <p className="text-xs text-slate-400 leading-normal mb-4">
                  {lang === 'es'
                    ? 'Eje Izquierdo: Accuracy (%). Eje Derecho: Deriva Geométrica Latente (Δ).'
                    : 'Left Axis: Accuracy (%). Right Axis: Latent Geometric Drift (Δ).'}
                </p>
              </div>

              <div className="w-full min-w-0 flex-1 min-h-[300px] overflow-x-auto">
                {isMounted ? (
                    <ComposedChart
                      width={760}
                      height={300}
                      data={chartData}
                      margin={{ top: 10, right: 10, bottom: 0, left: -20 }}
                    >
                      <defs>
                        <linearGradient id="driftGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.24} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                      <XAxis
                        dataKey="noise"
                        stroke="#94a3b8"
                        fontSize={11}
                        tickLine={false}
                        tickFormatter={(v) => `σ = ${v}`}
                      />
                      <YAxis
                        yAxisId="left"
                        domain={[0, 100]}
                        stroke="#22d3ee"
                        fontSize={11}
                        tickLine={false}
                        label={{
                          value: lang === 'es' ? 'Precisión (%)' : 'Accuracy (%)',
                          angle: -90,
                          position: 'insideLeft',
                          offset: 10,
                          fill: '#22d3ee',
                          fontSize: 10,
                          fontFamily: 'monospace',
                        }}
                      />
                      <YAxis
                        yAxisId="right"
                        orientation="right"
                        stroke="#3b82f6"
                        fontSize={11}
                        tickLine={false}
                        label={{
                          value: lang === 'es' ? 'Deriva (Δ)' : 'Geometric Drift (Δ)',
                          angle: 90,
                          position: 'insideRight',
                          offset: 10,
                          fill: '#3b82f6',
                          fontSize: 10,
                          fontFamily: 'monospace',
                        }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(10, 15, 30, 0.9)',
                          borderColor: 'rgba(255, 255, 255, 0.08)',
                          borderRadius: '10px',
                          color: '#f8fafc',
                          fontFamily: 'monospace',
                          fontSize: '12px',
                          backdropFilter: 'blur(8px)',
                        }}
                      />
                      <Legend
                        verticalAlign="top"
                        height={36}
                        iconSize={10}
                        iconType="circle"
                        wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }}
                      />
                      <Area
                        yAxisId="right"
                        type="monotone"
                        dataKey="Drift"
                        fill="url(#driftGradient)"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        name={lang === 'es' ? 'Deriva (Δ)' : 'Drift (Δ)'}
                      />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="Embedding V2"
                        stroke="#22d3ee"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        name="Embedding V2 (Atlas)"
                      />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="ROCKET"
                        stroke="#f59e0b"
                        strokeWidth={1.5}
                        strokeDasharray="4 4"
                        dot={{ r: 3 }}
                        name="ROCKET SOTA"
                      />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="DTW"
                        stroke="#8b5cf6"
                        strokeWidth={1.5}
                        strokeDasharray="4 4"
                        dot={{ r: 3 }}
                        name="DTW SOTA"
                      />
                    </ComposedChart>
                ) : (
                  <div className="h-full w-full bg-slate-950/20 animate-pulse rounded-lg" />
                )}
              </div>
            </GlassPanel>
          </ScrollReveal>
        </div>

        {/* Right Column: Hypotheses Status Container */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <ScrollReveal>
            <div className="mb-2">
              <h3 className="text-md font-semibold text-slate-100 flex items-center gap-2">
                <Brain className="h-4 w-4 text-violet-400" />
                {lang === 'es' ? 'Evaluación de Hipótesis Científicas' : 'Research Hypotheses Evaluation'}
              </h3>
              <p className="text-xs text-slate-400 leading-normal">
                {lang === 'es'
                  ? 'Contratos de validación lógica ejecutados sobre los resultados del barrido de perturbación.'
                  : 'Logical validation contracts executed over the perturbation sweep results.'}
              </p>
            </div>
          </ScrollReveal>

          {Object.entries(report.hypotheses_evaluation).map(([key, value], idx) => {
            const statusConfig = formatStatus(value.status);
            const StatusIcon = statusConfig.icon;

            return (
              <ScrollReveal key={key}>
                <GlassPanel tone={statusConfig.tone} className="transition-all duration-300 hover:border-white/15">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-slate-500">{key}</span>
                        <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[9px] font-semibold tracking-wider font-mono ${statusConfig.color}`}>
                          <StatusIcon size={9} />
                          {statusConfig.label}
                        </span>
                      </div>
                      <h4 className="text-sm font-semibold text-slate-100 mt-1">
                        {value.hypothesis}
                      </h4>
                      <p className="text-xs text-slate-400 leading-relaxed mt-2 bg-black/20 rounded-lg p-2.5 font-mono border border-white/[0.02]">
                        <span className="text-cyan-400 mr-1 font-semibold">{lang === 'es' ? 'Evidencia:' : 'Evidence:'}</span>
                        {value.evidence}
                      </p>
                    </div>
                  </div>
                </GlassPanel>
              </ScrollReveal>
            );
          })}
        </div>
      </div>

      {/* Bottom section: Manifold Meaning & Systems list */}
      <ScrollReveal>
        <ScientificSurface grid className="p-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-2">
                <HelpCircle className="h-4 w-4 text-cyan-400" />
                {lang === 'es' ? 'Interpretación Física de la Deriva Geométrica' : 'Physical Interpretation of Geometric Drift'}
              </h4>
              <p className="text-xs text-slate-300/80 leading-relaxed">
                {lang === 'es'
                  ? 'La Deriva Geométrica (Δ) cuantifica la distorsión del atractor continuo proyectado en el espacio latente. A diferencia del ruido blanco aditivo que perturba las variables temporales directamente, Δ monitorea la resiliencia estructural de la variedad de fase entera. Si Δ sube uniformemente mientras el Accuracy se mantiene al 100%, significa que el modelo es invariante y absorbe el ruido mediante adaptaciones ortogonales de frontera.'
                  : 'Geometric Drift (Δ) quantifies the distortion of the continuous attractor projected onto the latent manifold. Unlike additive white noise which directly corrupts the temporal variables, Δ tracks the structural resilience of the entire phase manifold. If Δ rises steadily while accuracy remains at 100%, it implies that the model is invariant, absorbing the noise through orthogonal boundary adaptations.'}
              </p>
            </div>
            <div className="flex flex-col justify-between">
              <div>
                <h4 className="text-sm font-semibold text-slate-100 flex items-center gap-2 mb-2">
                  <Network className="h-4 w-4 text-violet-400" />
                  {lang === 'es' ? 'Sistemas Dinámicos Analizados en Paralelo' : 'Dynamical Systems Analyzed in Parallel'}
                </h4>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {report.analysis_results.systems_analyzed.map((sys) => (
                    <span
                      key={sys}
                      className="rounded-md border border-white/[0.04] bg-slate-950/30 px-2 py-1 text-[10px] font-mono text-slate-300/90"
                    >
                      {sys.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between text-[11px] font-mono text-slate-500 border-t border-white/[0.05] pt-3">
                <span>{lang === 'es' ? 'Última actualización' : 'Last evaluated'}: {new Date(report.metadata.timestamp).toLocaleString()}</span>
                <span className="flex items-center gap-1">
                  <Cpu size={10} className="text-slate-600" />
                  Orchestrator v2.0
                </span>
              </div>
            </div>
          </div>
        </ScientificSurface>
      </ScrollReveal>
    </div>
  );
}
