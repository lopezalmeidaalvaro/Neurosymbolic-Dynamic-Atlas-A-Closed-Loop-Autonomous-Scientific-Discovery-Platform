// ═══════════════════════════════════════════════════════════════
// data/roadmapData.ts — Future development roadmap
// ═══════════════════════════════════════════════════════════════
import type { RoadmapItem } from '@/types';

export const roadmapItems: RoadmapItem[] = [
  {
    id: 'rm-1',
    title: { en: 'Real-Time Pipeline Monitor', es: 'Monitor de Pipeline en Tiempo Real' },
    description: {
      en: 'WebSocket integration to stream live experiment telemetry from the Python backend.',
      es: 'Integración WebSocket para transmitir telemetría de experimentos en vivo desde el backend Python.',
    },
    status: 'in-progress',
    priority: 'high',
    eta: 'Phase 2',
  },
  {
    id: 'rm-2',
    title: { en: 'Interactive Latent Space Viewer', es: 'Visualizador del Espacio Latente Interactivo' },
    description: {
      en: '3D scatter plot of PCA projections with cluster coloring and system annotations.',
      es: 'Gráfico de dispersión 3D de proyecciones PCA con coloreado de clústeres y anotaciones de sistemas.',
    },
    status: 'planned',
    priority: 'high',
    eta: 'Phase 2',
  },
  {
    id: 'rm-3',
    title: { en: 'Benchmark Chart Component', es: 'Componente de Gráfico Benchmark' },
    description: {
      en: 'Interactive dual-axis bar+line chart for Accuracy vs Time comparisons.',
      es: 'Gráfico interactivo de doble eje barra+línea para comparaciones Precisión vs Tiempo.',
    },
    status: 'in-progress',
    priority: 'high',
    eta: 'Phase 2',
  },
  {
    id: 'rm-4',
    title: { en: 'KaTeX Scientific Rendering', es: 'Renderizado Científico KaTeX' },
    description: {
      en: 'Render mathematical expressions (λg, κ, Feigenbaum δ) natively in the UI.',
      es: 'Renderizar expresiones matemáticas (λg, κ, δ de Feigenbaum) nativamente en la UI.',
    },
    status: 'planned',
    priority: 'medium',
    eta: 'Phase 3',
  },
  {
    id: 'rm-5',
    title: { en: 'TDA (Persistent Homology) Viewer', es: 'Visor TDA (Homología Persistente)' },
    description: {
      en: 'Replace heuristic geometry proxies with rigorous Betti numbers and persistence diagrams.',
      es: 'Reemplazar proxies geométricos heurísticos con números de Betti y diagramas de persistencia rigurosos.',
    },
    status: 'planned',
    priority: 'medium',
    eta: 'Phase 4',
  },
  {
    id: 'rm-6',
    title: { en: 'Paper Export Mode', es: 'Modo Exportación Paper' },
    description: {
      en: 'One-click export of all findings, charts, and insights into a LaTeX/PDF research report.',
      es: 'Exportación con un clic de todos los hallazgos, gráficos e insights en un informe de investigación LaTeX/PDF.',
    },
    status: 'planned',
    priority: 'low',
    eta: 'Phase 5',
  },
];
