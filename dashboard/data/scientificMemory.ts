import type { LiteratureReference, ScientificMemoryEntry } from '@/types';

export const literatureReferences: LiteratureReference[] = [
  {
    id: 'rocket-2020',
    title: 'ROCKET: exceptionally fast and accurate time series classification using random convolutional kernels',
    authors: ['Angus Dempster', 'Francois Petitjean', 'Geoffrey I. Webb'],
    year: 2020,
    venue: 'Data Mining and Knowledge Discovery',
    url: 'https://arxiv.org/abs/1910.13051',
    note: {
      en: 'Reference baseline for fast random convolutional kernels in time-series classification.',
      es: 'Baseline de referencia para kernels convolucionales aleatorios rapidos en clasificacion de series temporales.',
    },
  },
  {
    id: 'dtw-1978',
    title: 'Dynamic programming algorithm optimization for spoken word recognition',
    authors: ['Hiroaki Sakoe', 'Seibi Chiba'],
    year: 1978,
    venue: 'IEEE Transactions on Acoustics, Speech, and Signal Processing',
    url: 'https://jeffe.cs.illinois.edu/teaching/compgeom/2022/refs/Sakoe-Chiba-DTW.pdf',
    note: {
      en: 'Classical source for dynamic time warping style sequence alignment.',
      es: 'Fuente clasica para alineamiento de secuencias tipo dynamic time warping.',
    },
  },
  {
    id: 'ucr-2019',
    title: 'The UCR Time Series Archive',
    authors: ['Hoang Anh Dau', 'Anthony Bagnall', 'Kaveh Kamgar', 'Chin-Chia Michael Yeh', 'Yan Zhu', 'Shaghayegh Gharghabi', 'Chotirat Ann Ratanamahatana', 'Eamonn Keogh'],
    year: 2019,
    venue: 'IEEE/CAA Journal of Automatica Sinica',
    url: 'https://arxiv.org/abs/1810.07758',
    note: {
      en: 'External validation target for time-series classification generalization.',
      es: 'Objetivo de validacion externa para generalizacion en clasificacion de series temporales.',
    },
  },
];

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
    linkedIds: ['embedding-v2-speed-parity', 'rocket-2020', 'dtw-1978'],
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
