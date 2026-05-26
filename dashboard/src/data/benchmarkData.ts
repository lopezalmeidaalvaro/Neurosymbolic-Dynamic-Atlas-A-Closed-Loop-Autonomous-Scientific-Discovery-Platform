// ═══════════════════════════════════════════════════════════════
// data/benchmarkData.ts — SOTA benchmark results
// ═══════════════════════════════════════════════════════════════
import type { BenchmarkResult, KPIEntry } from '@/types';

export const benchmarkResults: BenchmarkResult[] = [
  {
    id: 'rocket',
    modelName: 'ROCKET',
    accuracy: 1.0,
    timeSeconds: 9.95,
    isOurs: false,
    color: '#3b82f6',
  },
  {
    id: 'dtw',
    modelName: 'DTW (1-NN)',
    accuracy: 1.0,
    timeSeconds: 1.615,
    isOurs: false,
    color: '#8b5cf6',
  },
  {
    id: 'embedding_v2',
    modelName: 'Embedding V2',
    accuracy: 1.0,
    timeSeconds: 0.127,
    isOurs: true,
    color: '#22d3ee',
  },
];

export const kpiEntries: KPIEntry[] = [
  {
    id: 'total_experiments',
    label: { en: 'Total Experiments', es: 'Experimentos Totales' },
    value: 16,
    trend: 'up',
    trendValue: '+3 this session',
    color: 'cyan',
  },
  {
    id: 'completed_phases',
    label: { en: 'Completed Phases', es: 'Fases Completadas' },
    value: '13 / 13',
    trend: 'stable',
    color: 'emerald',
  },
  {
    id: 'avg_accuracy',
    label: { en: 'Benchmark Accuracy', es: 'Precisión Benchmark' },
    value: '100.00',
    unit: '%',
    trend: 'stable',
    description: {
      en: 'Matches ROCKET and DTW on synthetic dynamical classes.',
      es: 'Iguala a ROCKET y DTW en clases dinámicas sintéticas.',
    },
    color: 'blue',
  },
  {
    id: 'speed_advantage',
    label: { en: 'Speed vs ROCKET', es: 'Velocidad vs ROCKET' },
    value: '79',
    unit: 'x faster',
    trend: 'up',
    description: {
      en: '0.127s vs 9.95s — same accuracy at a fraction of the cost.',
      es: '0.127s vs 9.95s — misma precisión a una fracción del coste.',
    },
    color: 'violet',
  },
];
