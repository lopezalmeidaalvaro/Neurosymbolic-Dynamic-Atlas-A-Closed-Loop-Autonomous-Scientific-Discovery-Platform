'use client';

import { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Play, Pause, SkipForward, SkipBack, Info, Database, Activity, RefreshCw } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { useManifoldSnapshots } from '@/hooks/useManifoldSnapshots';
import type { Language } from '@/types';

// Dynamically import Plotly with SSR disabled to prevent 'window is not defined' error on Next.js server
const Plot = dynamic(
  () => import('react-plotly.js').then((mod) => mod.default),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[320px] items-center justify-center font-mono text-xs text-slate-400">
        <Activity className="mr-2 h-4 w-4 animate-spin text-cyan-400" />
        Initializing WebGL Projection Map...
      </div>
    ),
  }
);

interface ManifoldCollapsePlayerProps {
  lang: Language;
}

const SEED_COLORS: Record<number, string> = {
  42: '#22d3ee',   // cyan
  1337: '#a78bfa', // purple/violet
  9001: '#34d399', // emerald/green
  2024: '#f97316', // orange
  777: '#f43f5e',  // rose
  314: '#facc15',  // yellow
};

export function ManifoldCollapsePlayer({ lang }: ManifoldCollapsePlayerProps) {
  const { snapshotsReport, isLoading, isError, isEmpty, error } = useManifoldSnapshots();

  // Control States
  const [selectedSystem, setSelectedSystem] = useState<string>('');
  const [selectedSeed, setSelectedSeed] = useState<string>('all');
  const [noiseIndex, setNoiseIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(400); // ms per step

  // 1. Get unique systems list from backend report
  const systemsList = useMemo(() => {
    if (!snapshotsReport?.systems) return [];
    return snapshotsReport.systems.map((s) => s.system);
  }, [snapshotsReport]);

  useEffect(() => {
    if (systemsList.length > 0 && !selectedSystem) {
      // Find 'lorenz' or default to the first system
      const defaultSys = systemsList.includes('lorenz') ? 'lorenz' : systemsList[0];
      if (defaultSys) {
        setSelectedSystem(defaultSys);
      }
    }
  }, [systemsList, selectedSystem]);

  // 2. Get unique seeds for selected system
  const availableSeeds = useMemo(() => {
    const sysData = snapshotsReport?.systems.find((s) => s.system === selectedSystem);
    if (!sysData) return [];
    const seedsSet = new Set<number>();
    sysData.snapshots.forEach((s) => seedsSet.add(s.seed));
    return Array.from(seedsSet).sort((a, b) => a - b);
  }, [snapshotsReport, selectedSystem]);

  // Validate selected seed when system changes
  useEffect(() => {
    if (availableSeeds.length > 0) {
      if (selectedSeed !== 'all' && !availableSeeds.includes(Number(selectedSeed))) {
        setSelectedSeed('all');
      }
    }
  }, [selectedSystem, availableSeeds, selectedSeed]);

  // 3. Get sorted unique noise levels for selected system
  const noiseLevels = useMemo(() => {
    const sysData = snapshotsReport?.systems.find((s) => s.system === selectedSystem);
    if (!sysData) return [];
    const levelsSet = new Set<number>();
    sysData.snapshots.forEach((s) => levelsSet.add(s.noise));
    return Array.from(levelsSet).sort((a, b) => a - b);
  }, [snapshotsReport, selectedSystem]);

  const maxNoiseVal = useMemo(() => {
    if (noiseLevels.length === 0) return 0;
    return noiseLevels[noiseLevels.length - 1] ?? 0;
  }, [noiseLevels]);

  // Adjust noise index when noise levels list changes
  useEffect(() => {
    if (noiseLevels.length > 0 && noiseIndex >= noiseLevels.length) {
      setNoiseIndex(Math.max(0, noiseLevels.length - 1));
    }
  }, [noiseLevels, noiseIndex]);

  // Playback timer loop
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    if (isPlaying && noiseLevels.length > 0) {
      intervalId = setInterval(() => {
        setNoiseIndex((prev) => {
          if (prev >= noiseLevels.length - 1) {
            return 0; // wrap around
          }
          return prev + 1;
        });
      }, playbackSpeed);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isPlaying, noiseLevels, playbackSpeed]);

  const activeNoise = noiseLevels[noiseIndex];

  // 4. Filter snapshots matching selected system, noise level, and seed
  const activeSnapshots = useMemo(() => {
    const sysData = snapshotsReport?.systems.find((s) => s.system === selectedSystem);
    if (!sysData || activeNoise === undefined) return [];
    return sysData.snapshots.filter((s) => {
      const isNoiseMatch = Math.abs(s.noise - activeNoise) < 1e-5;
      const isSeedMatch = selectedSeed === 'all' || s.seed === Number(selectedSeed);
      return isNoiseMatch && isSeedMatch;
    });
  }, [snapshotsReport, selectedSystem, activeNoise, selectedSeed]);

  // Gather projected points to render
  const activePoints = useMemo(() => {
    const pointsList: { x: number; y: number; seed: number }[] = [];
    activeSnapshots.forEach((snap) => {
      snap.points.forEach((p) => {
        pointsList.push({ x: p.x, y: p.y, seed: snap.seed });
      });
    });
    return pointsList;
  }, [activeSnapshots]);

  // Compute fixed coordinate boundaries across all snapshots for this system
  // This keeps scales constant across noise levels, making the shrinkage/collapse visible!
  const { minX, maxX, minY, maxY } = useMemo(() => {
    const sysData = snapshotsReport?.systems.find((s) => s.system === selectedSystem);
    if (!sysData) return { minX: -1, maxX: 1, minY: -1, maxY: 1 };
    
    let localMinX = Infinity;
    let localMaxX = -Infinity;
    let localMinY = Infinity;
    let localMaxY = -Infinity;
    
    sysData.snapshots.forEach((snap) => {
      snap.points.forEach((p) => {
        if (p.x < localMinX) localMinX = p.x;
        if (p.x > localMaxX) localMaxX = p.x;
        if (p.y < localMinY) localMinY = p.y;
        if (p.y > localMaxY) localMaxY = p.y;
      });
    });
    
    if (localMinX === Infinity) {
      return { minX: -1, maxX: 1, minY: -1, maxY: 1 };
    }
    
    // Add 10% padding
    const spanX = localMaxX - localMinX;
    const spanY = localMaxY - localMinY;
    const padX = spanX * 0.1 || 0.5;
    const padY = spanY * 0.1 || 0.5;
    
    return {
      minX: localMinX - padX,
      maxX: localMaxX + padX,
      minY: localMinY - padY,
      maxY: localMaxY + padY,
    };
  }, [snapshotsReport, selectedSystem]);

  // Group active points by seed for color mapping and legend traces
  const plotlyTraces = useMemo(() => {
    const grouped: Record<number, { x: number[]; y: number[] }> = {};
    activePoints.forEach((pt) => {
      if (!grouped[pt.seed]) {
        grouped[pt.seed] = { x: [], y: [] };
      }
      const grp = grouped[pt.seed];
      if (grp) {
        grp.x.push(pt.x);
        grp.y.push(pt.y);
      }
    });

    return Object.entries(grouped).map(([seedStr, group]) => {
      const seedNum = Number(seedStr);
      const color = SEED_COLORS[seedNum] || '#38bdf8';
      return {
        x: group.x,
        y: group.y,
        mode: 'markers' as const,
        type: 'scattergl' as const,
        name: `Seed ${seedNum}`,
        marker: {
          color: color,
          size: selectedSystem === 'logistic_sweep' ? 6 : 10,
          opacity: 0.85,
          line: {
            color: 'rgba(255, 255, 255, 0.25)',
            width: 1,
          },
        },
        hovertemplate: `<b>Seed ${seedNum}</b><br>X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>`,
      };
    });
  }, [activePoints, selectedSystem]);

  // Compute centroid displacement and point count metrics (direct read from active snapshots)
  const metricCentroidDisplacement = useMemo(() => {
    if (activeSnapshots.length === 0) return 0;
    const sum = activeSnapshots.reduce((acc, snap) => acc + snap.quantitative_metrics.centroid_displacement, 0);
    return sum / activeSnapshots.length;
  }, [activeSnapshots]);

  const metricPointCount = useMemo(() => {
    return activePoints.length;
  }, [activePoints]);

  const metricClusterCount = useMemo(() => {
    if (activeSnapshots.length === 0) return 1;
    const sum = activeSnapshots.reduce((acc, snap) => acc + (snap.quantitative_metrics.cluster_count ?? 1), 0);
    return sum / activeSnapshots.length;
  }, [activeSnapshots]);

  const metricCovarianceDeterminant = useMemo(() => {
    if (activeSnapshots.length === 0) return 0;
    const sum = activeSnapshots.reduce((acc, snap) => acc + (snap.quantitative_metrics.covariance_determinant ?? 0), 0);
    return sum / activeSnapshots.length;
  }, [activeSnapshots]);

  const metricNNDistStd = useMemo(() => {
    if (activeSnapshots.length === 0) return 0;
    const sum = activeSnapshots.reduce((acc, snap) => acc + (snap.quantitative_metrics.nearest_neighbor_distance_std ?? 0), 0);
    return sum / activeSnapshots.length;
  }, [activeSnapshots]);

  const explainedVariance = useMemo(() => {
    if (!snapshotsReport?.metadata?.explained_variance_ratio) return null;
    return snapshotsReport.metadata.explained_variance_ratio;
  }, [snapshotsReport]);

  // Handlers
  const handlePrev = () => {
    setIsPlaying(false);
    setNoiseIndex((prev) => (prev > 0 ? prev - 1 : noiseLevels.length - 1));
  };

  const handleNext = () => {
    setIsPlaying(false);
    setNoiseIndex((prev) => (prev < noiseLevels.length - 1 ? prev + 1 : 0));
  };

  // State checks
  if (isLoading) {
    return (
      <GlassPanel className="p-8 border-white/[0.06] bg-slate-950/25">
        <div className="flex h-[400px] flex-col items-center justify-center gap-3 font-mono text-xs text-slate-400">
          <Activity className="h-8 w-8 animate-spin text-cyan-400" />
          <span>{lang === 'es' ? 'Cargando snapshots de colector...' : 'Loading manifold snapshots...'}</span>
        </div>
      </GlassPanel>
    );
  }

  if (isError || isEmpty || !snapshotsReport) {
    return (
      <GlassPanel tone="warning" className="p-8 border-amber-500/20 bg-amber-950/10">
        <div className="flex flex-col items-center justify-center gap-2 text-center">
          <Info className="h-8 w-8 text-amber-400" />
          <h4 className="font-semibold text-slate-100">
            {lang === 'es' ? 'Snapshots no disponibles' : 'Snapshots unavailable'}
          </h4>
          <p className="max-w-md text-xs leading-5 text-slate-400 font-mono">
            {error?.message ?? (lang === 'es' 
              ? 'Ejecuta python core/autonomous/latent_snapshot_exporter.py para exportar.'
              : 'Execute python core/autonomous/latent_snapshot_exporter.py to export snapshots.')}
          </p>
        </div>
      </GlassPanel>
    );
  }

  return (
    <GlassPanel density="spacious" tone="active">
      {/* Header */}
      <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="metric-label text-slate-500 uppercase tracking-widest text-[10px]">
            {lang === 'es' ? 'Simulador de Espacio Latente' : 'Latent Space Simulator'}
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Reproductor de Colapso de Colector' : 'Manifold Collapse Player'}
          </h3>
        </div>
        <div className="flex items-center gap-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 font-mono text-[10px] text-cyan-400">
          <Database size={12} />
          {lang === 'es' ? 'Alineación Global PCA' : 'PCA Global Fit Aligned'}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Controls Column */}
        <div className="lg:col-span-4 flex flex-col justify-between rounded-xl border border-white/[0.04] bg-slate-950/45 p-5">
          <div className="space-y-5">
            {/* System selector */}
            <div>
              <label className="mb-1.5 block font-mono text-[10px] uppercase text-slate-400">
                {lang === 'es' ? 'Sistema Dinámico' : 'Dynamical System'}
              </label>
              <select
                value={selectedSystem}
                onChange={(e) => {
                  setSelectedSystem(e.target.value);
                  setIsPlaying(false);
                  setNoiseIndex(0);
                }}
                className="w-full rounded-lg border border-white/[0.08] bg-slate-900 px-3 py-2 font-mono text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                {systemsList.map((sys) => (
                  <option key={sys} value={sys}>
                    {sys.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Seed selector */}
            <div>
              <label className="mb-1.5 block font-mono text-[10px] uppercase text-slate-400">
                {lang === 'es' ? 'Semilla Científica' : 'Scientific Seed'}
              </label>
              <div className="flex flex-wrap gap-1.5">
                <button
                  onClick={() => setSelectedSeed('all')}
                  className={`rounded px-2.5 py-1 font-mono text-[11px] transition ${
                    selectedSeed === 'all'
                      ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-900 border border-white/[0.05] text-slate-400 hover:border-white/[0.12]'
                  }`}
                >
                  {lang === 'es' ? 'TODAS' : 'ALL'}
                </button>
                {availableSeeds.map((seed) => (
                  <button
                    key={seed}
                    onClick={() => setSelectedSeed(String(seed))}
                    className={`rounded px-2.5 py-1 font-mono text-[11px] transition ${
                      selectedSeed === String(seed)
                        ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-300'
                        : 'bg-slate-900 border border-white/[0.05] text-slate-400 hover:border-white/[0.12]'
                    }`}
                  >
                    S-{seed}
                  </button>
                ))}
              </div>
            </div>

            {/* Playback rate */}
            <div>
              <label className="mb-1.5 block font-mono text-[10px] uppercase text-slate-400">
                {lang === 'es' ? 'Velocidad de Animación' : 'Animation Speed'}
              </label>
              <select
                value={playbackSpeed}
                onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                className="w-full rounded-lg border border-white/[0.08] bg-slate-900 px-3 py-1.5 font-mono text-xs text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value={800}>{lang === 'es' ? 'Lento (800ms)' : 'Slow (800ms)'}</option>
                <option value={400}>{lang === 'es' ? 'Normal (400ms)' : 'Normal (400ms)'}</option>
                <option value={150}>{lang === 'es' ? 'Rápido (150ms)' : 'Fast (150ms)'}</option>
              </select>
            </div>

            <hr className="border-white/[0.04]" />

            {/* Playback buttons */}
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <button
                  onClick={handlePrev}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.08] bg-slate-900/60 text-slate-400 transition hover:border-white/[0.15] hover:text-slate-200"
                  title={lang === 'es' ? 'Retroceder paso' : 'Step back'}
                >
                  <SkipBack size={14} />
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className={`flex h-11 w-11 items-center justify-center rounded-full border transition ${
                    isPlaying
                      ? 'border-cyan-500/30 bg-cyan-950/40 text-cyan-300 hover:bg-cyan-950/60'
                      : 'border-white/[0.12] bg-slate-900/80 text-slate-200 hover:border-white/[0.2] hover:bg-slate-800'
                  }`}
                >
                  {isPlaying ? (
                    <Pause size={16} fill="currentColor" />
                  ) : (
                    <Play size={16} fill="currentColor" className="ml-0.5" />
                  )}
                </button>
                <button
                  onClick={handleNext}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/[0.08] bg-slate-900/60 text-slate-400 transition hover:border-white/[0.15] hover:text-slate-200"
                  title={lang === 'es' ? 'Avanzar paso' : 'Step forward'}
                >
                  <SkipForward size={14} />
                </button>
              </div>

              {/* Slider */}
              <div>
                <div className="mb-2 flex items-center justify-between font-mono text-[11px] text-slate-500">
                  <span>{lang === 'es' ? 'Nivel de Ruido σ' : 'Noise Level σ'}</span>
                  <span className="font-bold text-cyan-400">
                    {activeNoise !== undefined ? activeNoise.toFixed(4) : 'N/A'}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max={noiseLevels.length > 0 ? noiseLevels.length - 1 : 0}
                  step="1"
                  value={noiseIndex}
                  onChange={(e) => {
                    setIsPlaying(false);
                    setNoiseIndex(Number(e.target.value));
                  }}
                  className="h-1.5 w-full cursor-pointer rounded-lg bg-slate-800 accent-cyan-400 hover:accent-cyan-300"
                />
                <div className="mt-1 flex justify-between font-mono text-[9px] text-slate-600">
                  <span>Min: 0.0</span>
                  <span>
                    Max: {maxNoiseVal.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Validation Metrics Panel */}
          <div className="mt-6 space-y-3 rounded-lg border border-white/[0.04] bg-slate-950/60 p-4">
            <h4 className="flex items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-wider text-slate-400">
              <Info size={11} className="text-cyan-400" />
              {lang === 'es' ? 'Métricas de Proyección' : 'Projection Metrics'}
            </h4>
            
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <span className="block font-mono text-[9px] text-slate-500 uppercase">
                  {lang === 'es' ? 'Desplazamiento' : 'Displacement'}
                </span>
                <span className="font-mono text-xs font-semibold text-slate-200">
                  {metricCentroidDisplacement.toFixed(5)}
                </span>
              </div>
              <div>
                <span className="block font-mono text-[9px] text-slate-500 uppercase">
                  {lang === 'es' ? 'Puntos de Colector' : 'Manifold Points'}
                </span>
                <span className="font-mono text-xs font-semibold text-slate-200">
                  {metricPointCount}
                </span>
              </div>
              <div>
                <span className="block font-mono text-[9px] text-slate-500 uppercase">
                  {lang === 'es' ? 'Islas DBSCAN' : 'DBSCAN Clusters'}
                </span>
                <span className="font-mono text-xs font-semibold text-cyan-400">
                  {metricClusterCount.toFixed(0)}
                </span>
              </div>
              <div>
                <span className="block font-mono text-[9px] text-slate-500 uppercase">
                  {lang === 'es' ? 'Volumen Efectivo' : 'Effective Volume'}
                </span>
                <span className="font-mono text-xs font-semibold text-violet-400">
                  {metricCovarianceDeterminant.toExponential(4)}
                </span>
              </div>
              <div className="col-span-2">
                <span className="block font-mono text-[9px] text-slate-500 uppercase">
                  {lang === 'es' ? 'Dispersión Vecino Cercano (NN Std)' : 'Nearest Neighbor Distance Std'}
                </span>
                <span className="font-mono text-xs font-semibold text-emerald-400">
                  {metricNNDistStd.toFixed(5)}
                </span>
              </div>
            </div>

            {explainedVariance && explainedVariance.length >= 2 && (
              <div className="border-t border-white/[0.04] pt-2.5">
                <span className="block font-mono text-[9px] text-slate-500 uppercase mb-1">
                  {lang === 'es' ? 'Varianza Explicada Global' : 'Global Explained Variance'}
                </span>
                <div className="flex items-center justify-between font-mono text-[10px] text-slate-400">
                  <span>PC-1: {((explainedVariance[0] ?? 0) * 100).toFixed(2)}%</span>
                  <span>PC-2: {((explainedVariance[1] ?? 0) * 100).toFixed(2)}%</span>
                </div>
                <div className="mt-1.5 flex h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="bg-cyan-500"
                    style={{ width: `${(explainedVariance[0] ?? 0) * 100}%` }}
                    title={`PC1: ${((explainedVariance[0] ?? 0) * 100).toFixed(1)}%`}
                  />
                  <div
                    className="bg-violet-500"
                    style={{ width: `${(explainedVariance[1] ?? 0) * 100}%` }}
                    title={`PC2: ${((explainedVariance[1] ?? 0) * 100).toFixed(1)}%`}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Visualization Column */}
        <div className="lg:col-span-8 flex flex-col justify-center rounded-xl border border-white/[0.04] bg-slate-950/45 p-2 min-h-[350px]">
          <div className="relative h-[320px] w-full overflow-hidden rounded-lg">
            {activePoints.length > 0 ? (
              <Plot
                data={plotlyTraces}
                layout={{
                  autosize: true,
                  margin: { t: 20, r: 20, b: 35, l: 35 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  showlegend: selectedSeed === 'all',
                  legend: {
                    font: { color: '#94a3b8', family: 'monospace', size: 9 },
                    x: 0.02,
                    y: 0.98,
                    xanchor: 'left',
                    yanchor: 'top',
                    bgcolor: 'rgba(10, 15, 30, 0.7)',
                    bordercolor: 'rgba(255, 255, 255, 0.06)',
                    borderwidth: 1,
                  },
                  xaxis: {
                    range: [minX, maxX],
                    gridcolor: 'rgba(255, 255, 255, 0.03)',
                    zerolinecolor: 'rgba(255, 255, 255, 0.08)',
                    tickfont: { color: '#64748b', family: 'monospace', size: 9 },
                  },
                  yaxis: {
                    range: [minY, maxY],
                    gridcolor: 'rgba(255, 255, 255, 0.03)',
                    zerolinecolor: 'rgba(255, 255, 255, 0.08)',
                    tickfont: { color: '#64748b', family: 'monospace', size: 9 },
                  },
                }}
                config={{
                  responsive: true,
                  displayModeBar: false,
                }}
                style={{ width: '100%', height: '100%' }}
                useResizeHandler
              />
            ) : (
              <div className="flex h-full items-center justify-center font-mono text-xs text-slate-500">
                {lang === 'es'
                  ? 'No hay puntos proyectados para esta selección.'
                  : 'No projected points for this selection.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}
