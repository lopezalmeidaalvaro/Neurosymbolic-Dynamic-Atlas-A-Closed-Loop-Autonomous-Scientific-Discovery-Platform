import type { ScientificMemoryEntry } from '@/types';

export const scientificMemory: ScientificMemoryEntry[] = [
  {
    id: 'memory-generate-systems',
    date: '2026-05-13',
    type: 'experiment',
    title: {
      en: 'Generated controlled dynamical systems',
      es: 'Generacion de sistemas dinamicos controlados',
    },
    narrative: {
      simple: {
        en: 'The lab started by creating signals whose behavior we could inspect and label.',
        es: 'El laboratorio empezo creando senales cuyo comportamiento podiamos inspeccionar y etiquetar.',
      },
      advanced: {
        en: 'Controlled synthetic systems provided known regimes for early validation of descriptors and classifiers.',
        es: 'Sistemas sinteticos controlados proporcionaron regimenes conocidos para validacion temprana de descriptores y clasificadores.',
      },
    },
    linkedIds: ['phase-1', 'phase-6'],
  },
  {
    id: 'memory-perturbation',
    date: '2026-05-17',
    type: 'experiment',
    title: {
      en: 'Introduced perturbations and deformation flows',
      es: 'Introduccion de perturbaciones y flujos de deformacion',
    },
    narrative: {
      simple: {
        en: 'The system began asking whether patterns survive when the data becomes less clean.',
        es: 'El sistema empezo a preguntar si los patrones sobreviven cuando los datos son menos limpios.',
      },
      advanced: {
        en: 'Perturbation scripts established the need for explicit robustness and falsification checks.',
        es: 'Los scripts de perturbacion establecieron la necesidad de robustez explicita y comprobaciones de falsacion.',
      },
    },
    linkedIds: ['deformation_flow.py', 'falsification_001.py', 'structural-noise-boundary'],
  },
  {
    id: 'memory-benchmark',
    date: '2026-05-18',
    type: 'finding',
    title: {
      en: 'Compared Embedding V2 against DTW and ROCKET',
      es: 'Comparacion de Embedding V2 contra DTW y ROCKET',
    },
    narrative: {
      simple: {
        en: 'The fingerprint approach matched the benchmark accuracy while using far less time.',
        es: 'El enfoque de huella igualo la precision del benchmark usando mucho menos tiempo.',
      },
      advanced: {
        en: 'Benchmark evidence supports a strong accuracy-cost tradeoff for descriptor-based classification.',
        es: 'La evidencia de benchmark apoya un fuerte compromiso precision-coste para clasificacion basada en descriptores.',
      },
    },
    linkedIds: ['embedding-v2-speed-parity', 'rocket', 'dtw-sakoe-chiba'],
  },
  {
    id: 'memory-invariance',
    date: '2026-05-18',
    type: 'hypothesis',
    title: {
      en: 'Observed geometric invariance in latent neighborhoods',
      es: 'Observacion de invariancia geometrica en vecindarios latentes',
    },
    narrative: {
      simple: {
        en: 'Similar behaviors appeared to gather together after signals were converted into fingerprints.',
        es: 'Comportamientos similares parecieron agruparse tras convertir senales en huellas.',
      },
      advanced: {
        en: 'Neighborhood organization suggests, but does not yet prove, descriptor-level invariance.',
        es: 'La organizacion de vecindario sugiere, pero aun no prueba, invariancia a nivel de descriptores.',
      },
    },
    linkedIds: ['latent-geometry-separability', 'lyapunov-scaling'],
  },
  {
    id: 'memory-next-frontier',
    date: '2026-05-19',
    type: 'question',
    title: {
      en: 'Defined the next uncertainty frontier',
      es: 'Definicion de la siguiente frontera de incertidumbre',
    },
    narrative: {
      simple: {
        en: 'The next phase is to learn where the discovery map breaks.',
        es: 'La siguiente fase es aprender donde se rompe el mapa de descubrimiento.',
      },
      advanced: {
        en: 'Open questions now center on UCR transfer, structural noise, descriptor ablation, and Lyapunov scaling.',
        es: 'Las preguntas abiertas se centran en transferencia UCR, ruido estructural, ablacion de descriptores y escalado de Lyapunov.',
      },
    },
    linkedIds: ['ucr-generalization', 'structural-noise', 'feature-ablation', 'lyapunov-scaling'],
  },
];
