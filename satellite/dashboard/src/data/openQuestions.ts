import type { OpenQuestion } from '@/types';

export const openQuestions: OpenQuestion[] = [
  {
    id: 'scalability-vs-dtw',
    title: { en: 'Scalability vs DTW', es: 'Escalabilidad frente a DTW' },
    question: {
      simple: {
        en: 'How much faster does the fingerprint method stay when datasets become larger?',
        es: 'Cuanto mas rapido se mantiene el metodo de huella cuando los datasets crecen?',
      },
      advanced: {
        en: 'How does descriptor extraction plus classification scale against DTW alignment as sample count and sequence length increase?',
        es: 'Como escala extraccion de descriptores mas clasificacion frente a alineamiento DTW al aumentar muestras y longitud de secuencia?',
      },
    },
    whyOpen: {
      simple: {
        en: 'The current speed win is strong, but it was measured on a controlled benchmark.',
        es: 'La ventaja de velocidad actual es fuerte, pero se midio en un benchmark controlado.',
      },
      advanced: {
        en: 'Asymptotic and wall-clock scaling need measurement across sequence lengths and dataset sizes.',
        es: 'El escalado asintotico y wall-clock debe medirse en multiples longitudes y tamanos de dataset.',
      },
    },
    priority: 'high',
    relatedFindingIds: ['embedding-v2-speed-parity'],
  },
  {
    id: 'structural-noise',
    title: { en: 'Robustness under structural noise', es: 'Robustez bajo ruido estructural' },
    question: {
      simple: {
        en: 'Does the map still work when the rules of the system change, not just the measurements?',
        es: 'El mapa sigue funcionando cuando cambian las reglas del sistema, no solo las mediciones?',
      },
      advanced: {
        en: 'Which perturbation families preserve descriptor invariance, and which collapse latent separability?',
        es: 'Que familias de perturbacion preservan invariancia de descriptores y cuales colapsan separabilidad latente?',
      },
    },
    whyOpen: {
      simple: {
        en: 'Real systems change in deeper ways than random shake.',
        es: 'Los sistemas reales cambian de formas mas profundas que vibracion aleatoria.',
      },
      advanced: {
        en: 'Current memory lacks a systematic structural perturbation grid.',
        es: 'La memoria actual carece de una matriz sistematica de perturbacion estructural.',
      },
    },
    priority: 'high',
    relatedFindingIds: ['structural-noise-boundary', 'latent-geometry-separability'],
  },
  {
    id: 'ucr-generalization',
    title: { en: 'UCR generalization', es: 'Generalizacion UCR' },
    question: {
      simple: {
        en: 'Will the discovery method work on standard public time-series datasets?',
        es: 'Funcionara el metodo de descubrimiento en datasets publicos estandar de series temporales?',
      },
      advanced: {
        en: 'Can the descriptor set remain competitive on heterogeneous UCR tasks without domain-specific tuning?',
        es: 'Puede el conjunto de descriptores seguir siendo competitivo en tareas UCR heterogeneas sin ajuste especifico de dominio?',
      },
    },
    whyOpen: {
      simple: {
        en: 'External datasets are the next reality check.',
        es: 'Datasets externos son la siguiente prueba de realidad.',
      },
      advanced: {
        en: 'Synthetic performance does not imply transfer under heterogeneous sampling, class definitions, and noise processes.',
        es: 'Rendimiento sintetico no implica transferencia bajo muestreo, clases y procesos de ruido heterogeneos.',
      },
    },
    priority: 'high',
    relatedFindingIds: ['embedding-v2-speed-parity'],
  },
  {
    id: 'feature-ablation',
    title: { en: 'Feature ablation', es: 'Ablacion de features' },
    question: {
      simple: {
        en: 'Which fingerprint measurements are actually doing the work?',
        es: 'Que medidas de la huella hacen realmente el trabajo?',
      },
      advanced: {
        en: 'Which descriptors contribute most to class separability, runtime advantage, and robustness?',
        es: 'Que descriptores contribuyen mas a separabilidad, ventaja de runtime y robustez?',
      },
    },
    whyOpen: {
      simple: {
        en: 'A smaller fingerprint may be easier to trust and explain.',
        es: 'Una huella mas pequena puede ser mas facil de confiar y explicar.',
      },
      advanced: {
        en: 'Ablations are required to identify causal descriptor contributions rather than correlated feature bundles.',
        es: 'Las ablaciones son necesarias para identificar contribuciones causales y no paquetes de features correlacionadas.',
      },
    },
    priority: 'medium',
    relatedFindingIds: ['latent-geometry-separability', 'embedding-v2-speed-parity'],
  },
  {
    id: 'lyapunov-scaling',
    title: { en: 'Lyapunov scaling', es: 'Escalado de Lyapunov' },
    question: {
      simple: {
        en: 'Does stronger chaos create stronger geometric separation in the map?',
        es: 'Un caos mas fuerte crea separacion geometrica mas fuerte en el mapa?',
      },
      advanced: {
        en: 'Do Lyapunov estimates correlate with latent curvature, local expansion, or neighborhood instability?',
        es: 'Las estimaciones de Lyapunov correlacionan con curvatura latente, expansion local o inestabilidad de vecindario?',
      },
    },
    whyOpen: {
      simple: {
        en: 'This would connect a known chaos measure to the atlas geometry.',
        es: 'Esto conectaria una medida conocida de caos con la geometria del atlas.',
      },
      advanced: {
        en: 'The relationship is plausible but currently confounded by entropy, variance, and sampling effects.',
        es: 'La relacion es plausible pero actualmente esta confundida por entropia, varianza y efectos de muestreo.',
      },
    },
    priority: 'medium',
    relatedFindingIds: ['latent-geometry-separability', 'feigenbaum-structural-signal'],
  },
];
