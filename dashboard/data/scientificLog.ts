// ═══════════════════════════════════════════════════════════════
// data/scientificLog.ts — Pipeline execution log entries
// ═══════════════════════════════════════════════════════════════
import type { ScientificLogEntry } from '@/types';

export const scientificLog: ScientificLogEntry[] = [
  {
    id: 'log-001',
    timestamp: '2026-05-18T14:27:49Z',
    severity: 'info',
    phase: 'Phase 13',
    message: {
      en: 'Pipeline initiated: continuous attractor integration started.',
      es: 'Pipeline iniciado: integración de atractores continuos iniciada.',
    },
  },
  {
    id: 'log-002',
    timestamp: '2026-05-18T14:28:20Z',
    severity: 'success',
    phase: 'Phase 13',
    message: {
      en: 'Lorenz, Rössler, Chua integrated and embedding v2 computed.',
      es: 'Lorenz, Rössler, Chua integrados y embedding v2 calculado.',
    },
    details: 'lyapunov_max: Lorenz=0.9012, Rössler=0.0712, Chua=0.1403',
  },
  {
    id: 'log-003',
    timestamp: '2026-05-18T14:29:09Z',
    severity: 'success',
    phase: 'Phase 13',
    message: {
      en: 'Universality test completed. Lorenz–Rössler cosine similarity: 0.9670.',
      es: 'Test de universalidad completado. Similitud coseno Lorenz–Rössler: 0.9670.',
    },
    details: 'sim_lorenz_rossler=0.9670 > 0.80 → universality confirmed',
  },
  {
    id: 'log-004',
    timestamp: '2026-05-18T14:29:09Z',
    severity: 'insight',
    phase: 'Phase 13',
    message: {
      en: 'Meta-insight registered: continuous_discrete_universality (confidence 0.96).',
      es: 'Meta-insight registrado: continuous_discrete_universality (confianza 0.96).',
    },
  },
  {
    id: 'log-005',
    timestamp: '2026-05-18T15:27:19Z',
    severity: 'success',
    phase: 'Benchmark',
    message: {
      en: 'ROCKET evaluated: Accuracy=100.00%, Time=9.950s.',
      es: 'ROCKET evaluado: Precisión=100.00%, Tiempo=9.950s.',
    },
  },
  {
    id: 'log-006',
    timestamp: '2026-05-18T15:27:19Z',
    severity: 'success',
    phase: 'Benchmark',
    message: {
      en: 'DTW (1-NN) evaluated: Accuracy=100.00%, Time=1.615s.',
      es: 'DTW (1-NN) evaluado: Precisión=100.00%, Tiempo=1.615s.',
    },
  },
  {
    id: 'log-007',
    timestamp: '2026-05-18T15:27:19Z',
    severity: 'insight',
    phase: 'Benchmark',
    message: {
      en: 'Embedding V2 wins: Accuracy=100.00%, Time=0.127s — 79x faster than ROCKET.',
      es: 'Embedding V2 gana: Precisión=100.00%, Tiempo=0.127s — 79x más rápido que ROCKET.',
    },
    details: 'pattern_type: sota_baseline_comparison | confidence: 0.97',
  },
];
