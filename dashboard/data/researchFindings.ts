import type { ResearchFinding } from '@/types';

export const researchFindings: ResearchFinding[] = [
  {
    id: 'embedding-v2-speed-parity',
    state: 'validated',
    title: {
      en: 'Embedding V2 matched benchmark accuracy at lower runtime',
      es: 'Embedding V2 igualo la precision del benchmark con menor runtime',
    },
    summary: {
      simple: {
        en: 'The compact fingerprint method reached the same classification accuracy as stronger baselines while running much faster.',
        es: 'El metodo de huella compacta alcanzo la misma precision de clasificacion que baselines fuertes ejecutandose mucho mas rapido.',
      },
      advanced: {
        en: 'Descriptor-based classification reached 100% accuracy on the synthetic benchmark while reducing inference time relative to ROCKET and DTW.',
        es: 'La clasificacion basada en descriptores alcanzo 100% de precision en el benchmark sintetico reduciendo el tiempo de inferencia frente a ROCKET y DTW.',
      },
    },
    whyItMatters: {
      simple: {
        en: 'If the lab can classify faster without losing accuracy, it can test more systems, more noise levels, and more hypotheses.',
        es: 'Si el laboratorio clasifica mas rapido sin perder precision, puede probar mas sistemas, mas niveles de ruido y mas hipotesis.',
      },
      advanced: {
        en: 'Lower compute cost increases experimental throughput and makes perturbation sweeps, ablations, and repeated validation more practical.',
        es: 'Menor coste computacional aumenta el throughput experimental y hace mas practicos barridos de perturbacion, ablaciones y validacion repetida.',
      },
    },
    methodology: {
      simple: {
        en: 'We generated labeled time series, converted each one into a compact fingerprint, and compared classification accuracy and runtime against DTW and ROCKET.',
        es: 'Generamos series temporales etiquetadas, convertimos cada una en una huella compacta y comparamos precision y runtime contra DTW y ROCKET.',
      },
      advanced: {
        en: 'A controlled synthetic dataset was split into train/test subsets; Embedding V2 descriptors were classified and compared with DTW 1-NN and ROCKET using accuracy and wall-clock runtime.',
        es: 'Un dataset sintetico controlado se dividio en train/test; los descriptores de Embedding V2 se clasificaron y compararon con DTW 1-NN y ROCKET usando precision y runtime.',
      },
    },
    evidence: [
      {
        simple: {
          en: 'Embedding V2, DTW, and ROCKET all reached perfect accuracy on the current benchmark.',
          es: 'Embedding V2, DTW y ROCKET alcanzaron precision perfecta en el benchmark actual.',
        },
        advanced: {
          en: 'Current benchmark records show 1.0 accuracy for all three evaluated methods.',
          es: 'Los registros actuales del benchmark muestran 1.0 de precision para los tres metodos evaluados.',
        },
      },
      {
        simple: {
          en: 'Embedding V2 completed the comparison in 0.127 seconds, while ROCKET took 9.95 seconds.',
          es: 'Embedding V2 completo la comparacion en 0.127 segundos, mientras ROCKET tardo 9.95 segundos.',
        },
        advanced: {
          en: 'Measured runtime: Embedding V2 0.127s, DTW 1.615s, ROCKET 9.95s.',
          es: 'Runtime medido: Embedding V2 0.127s, DTW 1.615s, ROCKET 9.95s.',
        },
      },
    ],
    linkedExperiments: ['phase-13', 'baseline_benchmark.py', 'benchmark_results.json'],
    metrics: {
      significance: 94,
      confidence: 88,
      reproducibility: 82,
    },
    quantitativeSignals: [
      { label: { en: 'Accuracy', es: 'Precision' }, value: 100, unit: '%' },
      { label: { en: 'Runtime', es: 'Runtime' }, value: 0.127, unit: 's' },
      { label: { en: 'Speedup vs ROCKET', es: 'Aceleracion vs ROCKET' }, value: 79, unit: 'x' },
    ],
    literatureRefs: ['rocket-2020', 'dtw-1978', 'ucr-2019'],
    nextStep: {
      simple: {
        en: 'Test the same idea on broader public datasets, not only controlled synthetic signals.',
        es: 'Probar la misma idea en datasets publicos mas amplios, no solo en senales sinteticas controladas.',
      },
      advanced: {
        en: 'Validate on UCR-style datasets and run feature ablations to isolate which descriptors carry the runtime-accuracy advantage.',
        es: 'Validar en datasets tipo UCR y ejecutar ablaciones para aislar que descriptores explican la ventaja runtime-precision.',
      },
    },
  },
  {
    id: 'latent-geometry-separability',
    state: 'observed',
    title: {
      en: 'Latent neighborhoods suggest geometric separability',
      es: 'Los vecindarios latentes sugieren separabilidad geometrica',
    },
    summary: {
      simple: {
        en: 'When signals become fingerprints, similar dynamical behaviors tend to land near each other on the map.',
        es: 'Cuando las senales se convierten en huellas, comportamientos dinamicos similares tienden a caer cerca en el mapa.',
      },
      advanced: {
        en: 'Feature-space projections show neighborhood organization consistent with separable dynamical regimes.',
        es: 'Las proyecciones del espacio de caracteristicas muestran organizacion de vecindario compatible con regimenes dinamicos separables.',
      },
    },
    whyItMatters: {
      simple: {
        en: 'This means the system may be learning structure, not only memorizing labels.',
        es: 'Esto significa que el sistema podria estar aprendiendo estructura, no solo memorizando etiquetas.',
      },
      advanced: {
        en: 'Class-conditioned geometry can become evidence for representation quality and support interpretable classification.',
        es: 'La geometria condicionada por clase puede convertirse en evidencia de calidad representacional y apoyar clasificacion interpretable.',
      },
    },
    methodology: {
      simple: {
        en: 'We placed fingerprints in a low-dimensional map and inspected whether related systems formed neighborhoods.',
        es: 'Colocamos huellas en un mapa de baja dimension e inspeccionamos si sistemas relacionados formaban vecindarios.',
      },
      advanced: {
        en: 'Descriptor vectors were projected and analyzed through neighborhood structure, clustering behavior, and curvature-inspired diagnostics.',
        es: 'Los vectores descriptores se proyectaron y analizaron mediante estructura de vecindario, clustering y diagnosticos inspirados en curvatura.',
      },
    },
    evidence: [
      {
        simple: {
          en: 'Chaotic systems appear closer to other chaotic systems than to random noise.',
          es: 'Los sistemas caoticos aparecen mas cerca de otros sistemas caoticos que del ruido aleatorio.',
        },
        advanced: {
          en: 'Observed projections and nearest-neighbor diagnostics indicate non-random grouping by dynamical behavior.',
          es: 'Las proyecciones observadas y diagnosticos de vecinos indican agrupamiento no aleatorio por comportamiento dinamico.',
        },
      },
    ],
    linkedExperiments: ['phase-7', 'phase-11', 'universal_atlas_pca.png', 'curvature_clusters.png'],
    metrics: {
      significance: 89,
      confidence: 74,
      reproducibility: 70,
    },
    quantitativeSignals: [
      { label: { en: 'Embedding dimensions', es: 'Dimensiones del embedding' }, value: 8 },
      { label: { en: 'Atlas systems', es: 'Sistemas del atlas' }, value: 6 },
    ],
    literatureRefs: ['ucr-2019'],
    nextStep: {
      simple: {
        en: 'Check whether the same map stays organized when the systems get noisier or structurally different.',
        es: 'Comprobar si el mapa sigue organizado cuando los sistemas tienen mas ruido o cambian estructuralmente.',
      },
      advanced: {
        en: 'Quantify margins, neighborhood purity, and robustness under structural perturbation.',
        es: 'Cuantificar margenes, pureza de vecindario y robustez bajo perturbacion estructural.',
      },
    },
  },
  {
    id: 'feigenbaum-structural-signal',
    state: 'validated',
    title: {
      en: 'Period-doubling ratios recovered a known universality signal',
      es: 'Las razones de duplicacion de periodo recuperaron una senal de universalidad conocida',
    },
    summary: {
      simple: {
        en: 'The system reproduced a famous pattern: systems can become chaotic through repeated period doubling.',
        es: 'El sistema reprodujo un patron famoso: los sistemas pueden volverse caoticos mediante duplicacion repetida de periodo.',
      },
      advanced: {
        en: 'Numerical experiments recovered period-doubling ratios consistent with Feigenbaum-style universality.',
        es: 'Los experimentos numericos recuperaron razones de duplicacion de periodo compatibles con universalidad tipo Feigenbaum.',
      },
    },
    whyItMatters: {
      simple: {
        en: 'Recovering a known scientific pattern is a sanity check that the laboratory is measuring meaningful structure.',
        es: 'Recuperar un patron cientifico conocido valida que el laboratorio mide estructura significativa.',
      },
      advanced: {
        en: 'Known invariants provide calibration targets before claiming new representational discoveries.',
        es: 'Invariantes conocidos aportan objetivos de calibracion antes de afirmar descubrimientos representacionales nuevos.',
      },
    },
    methodology: {
      simple: {
        en: 'We watched simple maps change behavior as a parameter moved and measured how the changes compressed together.',
        es: 'Observamos mapas simples cambiar de comportamiento al mover un parametro y medimos como los cambios se comprimian.',
      },
      advanced: {
        en: 'Bifurcation transitions were estimated numerically across logistic and sine maps and compared through period-doubling ratios.',
        es: 'Transiciones de bifurcacion se estimaron numericamente en mapas logistico y seno y se compararon mediante razones de duplicacion de periodo.',
      },
    },
    evidence: [
      {
        simple: {
          en: 'The measured ratios approached the expected constant near 4.669.',
          es: 'Las razones medidas se acercaron a la constante esperada cerca de 4.669.',
        },
        advanced: {
          en: 'Period-doubling estimates converged toward delta approximately 4.669 across tested maps.',
          es: 'Las estimaciones de duplicacion de periodo convergieron hacia delta aproximadamente 4.669 en los mapas probados.',
        },
      },
    ],
    linkedExperiments: ['phase-6', 'feigenbaum_hunt.py', 'logistic_delta_d.png'],
    metrics: {
      significance: 78,
      confidence: 86,
      reproducibility: 84,
    },
    quantitativeSignals: [
      { label: { en: 'Expected delta', es: 'Delta esperada' }, value: 4.669 },
      { label: { en: 'Map families', es: 'Familias de mapas' }, value: 2 },
    ],
    literatureRefs: [],
    nextStep: {
      simple: {
        en: 'Use this as a calibration checkpoint for harder discoveries.',
        es: 'Usar esto como punto de calibracion para descubrimientos mas dificiles.',
      },
      advanced: {
        en: 'Connect bifurcation diagnostics to descriptor-space trajectories and instability features.',
        es: 'Conectar diagnosticos de bifurcacion con trayectorias en espacio de descriptores y features de inestabilidad.',
      },
    },
  },
  {
    id: 'structural-noise-boundary',
    state: 'uncertain',
    title: {
      en: 'Robustness under structural noise is not yet established',
      es: 'La robustez bajo ruido estructural aun no esta establecida',
    },
    summary: {
      simple: {
        en: 'The fingerprint method handles the current benchmark, but we do not yet know how it behaves when the system itself changes shape.',
        es: 'El metodo de huella funciona en el benchmark actual, pero aun no sabemos como se comporta cuando el propio sistema cambia de forma.',
      },
      advanced: {
        en: 'Current evidence covers controlled synthetic classes; structural perturbations may alter the invariant descriptors more severely than additive noise.',
        es: 'La evidencia actual cubre clases sinteticas controladas; perturbaciones estructurales pueden alterar descriptores invariantes mas severamente que ruido aditivo.',
      },
    },
    whyItMatters: {
      simple: {
        en: 'A real discovery system must know where its own confidence stops.',
        es: 'Un sistema real de descubrimiento debe saber donde termina su propia confianza.',
      },
      advanced: {
        en: 'Explicit uncertainty prevents overclaiming and defines the next validation frontier.',
        es: 'La incertidumbre explicita evita sobreafirmaciones y define la siguiente frontera de validacion.',
      },
    },
    methodology: {
      simple: {
        en: 'We need experiments that deform equations, not only add random shake to their outputs.',
        es: 'Necesitamos experimentos que deformen ecuaciones, no solo anadan vibracion aleatoria a sus salidas.',
      },
      advanced: {
        en: 'Future tests should vary parameters, coupling terms, sampling regimes, and observation noise independently.',
        es: 'Pruebas futuras deben variar parametros, terminos de acoplamiento, regimenes de muestreo y ruido de observacion de forma independiente.',
      },
    },
    evidence: [
      {
        simple: {
          en: 'The current records do not yet include a full structural-noise sweep.',
          es: 'Los registros actuales aun no incluyen un barrido completo de ruido estructural.',
        },
        advanced: {
          en: 'Scientific memory lacks a systematic matrix crossing structural perturbation with feature ablation.',
          es: 'La memoria cientifica carece de una matriz sistematica que cruce perturbacion estructural con ablacion de features.',
        },
      },
    ],
    linkedExperiments: ['deformation_flow.py', 'falsification_001.py', 'falsification_002.py'],
    metrics: {
      significance: 83,
      confidence: 46,
      reproducibility: 40,
    },
    quantitativeSignals: [
      { label: { en: 'Known gap', es: 'Brecha conocida' }, value: 1 },
      { label: { en: 'Required sweeps', es: 'Barridos requeridos' }, value: 5 },
    ],
    literatureRefs: ['ucr-2019'],
    nextStep: {
      simple: {
        en: 'Run targeted tests that change the rules of the system and measure when the map breaks.',
        es: 'Ejecutar pruebas dirigidas que cambien las reglas del sistema y medir cuando se rompe el mapa.',
      },
      advanced: {
        en: 'Design a perturbation grid for parameter drift, topology shifts, sensor noise, and descriptor ablations.',
        es: 'Disenar una matriz de perturbacion para deriva parametrica, cambios topologicos, ruido de sensor y ablaciones de descriptores.',
      },
    },
  },
];
