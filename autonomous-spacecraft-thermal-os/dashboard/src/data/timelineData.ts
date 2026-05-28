// ═══════════════════════════════════════════════════════════════
// data/timelineData.ts — Research phase timeline events
// ═══════════════════════════════════════════════════════════════
import type { TimelineEvent } from '@/types';

export const timelineEvents: TimelineEvent[] = [
  {
    id: 'phase-1',
    date: '2026-05-13',
    title: { en: 'Mathematical Foundation', es: 'Fundamentos Matemáticos' },
    description: {
      en: 'Quintic polynomial roots, Galois solvability, and Sturm sequences implemented as first symbolic search experiments.',
      es: 'Raíces de polinomios quínticos, solubilidad de Galois y secuencias de Sturm implementadas como primeros experimentos de búsqueda simbólica.',
    },
    status: 'completed',
    tags: ['sympy', 'algebra', 'numerical'],
    phaseName: { en: 'Phase 1-3', es: 'Fase 1-3' },
  },
  {
    id: 'phase-4',
    date: '2026-05-14',
    title: { en: 'Local SQLite Memory Layer', es: 'Capa de Memoria SQLite Local' },
    description: {
      en: 'evaluator_db.py deployed: hybrid telemetry tracking execution cost, redundancy, and semantic insights in a persistent database.',
      es: 'evaluator_db.py desplegado: telemetría híbrida que rastrea coste de ejecución, redundancia e insights semánticos en base de datos persistente.',
    },
    status: 'completed',
    tags: ['sqlite', 'memory', 'evaluator'],
    phaseName: { en: 'Phase 4-5', es: 'Fase 4-5' },
  },
  {
    id: 'phase-6',
    date: '2026-05-17',
    title: { en: 'Feigenbaum Universality Hunt', es: 'Caza de Universalidad de Feigenbaum' },
    description: {
      en: 'Numerically verified period-doubling bifurcation ratios (δ ≈ 4.669) across logistic and sine maps, confirming structural universality.',
      es: 'Verificación numérica de razones de bifurcación de duplicación de período (δ ≈ 4.669) en mapas logístico y seno, confirmando universalidad estructural.',
    },
    status: 'completed',
    tags: ['feigenbaum', 'bifurcation', 'universality'],
    phaseName: { en: 'Phase 6', es: 'Fase 6' },
  },
  {
    id: 'phase-7',
    date: '2026-05-17',
    title: { en: 'Latent Geometry Embedding V2', es: 'Embedding de Geometría Latente V2' },
    description: {
      en: 'Topology Miner V2: 8-dimensional feature vectors (Lyapunov, Spectral Entropy, Dominant Frequency, Variance, Autocorr, Kurtosis, Skewness, Energy) extracted for Lorenz, Rössler, Chua, Duffing, Van der Pol, Kuramoto.',
      es: 'Topology Miner V2: vectores de características 8-dimensionales extraídos para Lorenz, Rössler, Chua, Duffing, Van der Pol, Kuramoto.',
    },
    status: 'completed',
    tags: ['embedding', 'lyapunov', 'pca', 'topology'],
    phaseName: { en: 'Phase 7-10', es: 'Fase 7-10' },
  },
  {
    id: 'phase-11',
    date: '2026-05-17',
    title: { en: 'Geodesic Flow & Curvature Atlas', es: 'Flujo Geodésico y Atlas de Curvatura' },
    description: {
      en: 'k-NN graph analysis revealed that chaotic regimes exhibit negative curvature and high local metric expansion (λg > 0), while periodic systems cluster tightly.',
      es: 'El análisis de grafo k-NN reveló que los regímenes caóticos exhiben curvatura negativa y alta expansión métrica local (λg > 0), mientras los sistemas periódicos se agrupan densamente.',
    },
    status: 'completed',
    tags: ['geodesic', 'curvature', 'knn', 'atlas'],
    phaseName: { en: 'Phase 11-12', es: 'Fase 11-12' },
  },
  {
    id: 'phase-13',
    date: '2026-05-18',
    title: { en: 'SOTA Benchmark: 79x Speed Win', es: 'Benchmark SOTA: 79x más Rápido' },
    description: {
      en: 'Formal comparison vs ROCKET and DTW: Embedding V2 matches 100% accuracy while being 79x faster than ROCKET and 12x faster than DTW. Computational superiority confirmed.',
      es: 'Comparación formal vs ROCKET y DTW: Embedding V2 iguala 100% de precisión siendo 79x más rápido que ROCKET y 12x más que DTW. Superioridad computacional confirmada.',
    },
    status: 'completed',
    tags: ['benchmark', 'sota', 'rocket', 'dtw', 'classification'],
    phaseName: { en: 'Phase 13', es: 'Fase 13' },
  },
  {
    id: 'phase-14',
    date: '2026-05-18',
    title: { en: 'Scientific Dashboard (This)', es: 'Dashboard Científico (Este)' },
    description: {
      en: 'Next.js 14 + TypeScript frontend with i18n, global state, and cinematic dark theme to visualize the research pipeline.',
      es: 'Frontend Next.js 14 + TypeScript con i18n, estado global y tema oscuro cinematográfico para visualizar el pipeline de investigación.',
    },
    status: 'active',
    tags: ['frontend', 'nextjs', 'typescript', 'dashboard'],
    phaseName: { en: 'Phase 14', es: 'Fase 14' },
  },
  {
    id: 'phase-15',
    date: 'TBD',
    title: { en: 'Real-Time Pipeline Monitor', es: 'Monitor de Pipeline en Tiempo Real' },
    description: {
      en: 'WebSocket integration to stream live experiment results from the Python backend directly into the dashboard.',
      es: 'Integración WebSocket para transmitir resultados de experimentos en vivo desde el backend Python directamente al dashboard.',
    },
    status: 'planned',
    tags: ['websocket', 'realtime', 'streaming'],
    phaseName: { en: 'Phase 15', es: 'Fase 15' },
  },
];
