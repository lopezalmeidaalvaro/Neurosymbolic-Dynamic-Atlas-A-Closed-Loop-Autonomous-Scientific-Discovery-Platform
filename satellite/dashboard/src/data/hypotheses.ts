import type { ResearchHypothesis } from '@/types';

export const hypotheses: ResearchHypothesis[] = [
  {
    id: 'ucr-generalization',
    state: 'hypothesis',
    title: {
      en: 'Embedding descriptors may generalize beyond synthetic systems',
      es: 'Los descriptores de embedding podrian generalizar mas alla de sistemas sinteticos',
    },
    claim: {
      simple: {
        en: 'If the fingerprint captures real shape, it should work on public time-series datasets too.',
        es: 'Si la huella captura forma real, tambien deberia funcionar en datasets publicos de series temporales.',
      },
      advanced: {
        en: 'Descriptor invariance should transfer to selected UCR-style classification tasks when class structure depends on dynamics rather than domain-specific artifacts.',
        es: 'La invariancia de descriptores deberia transferir a tareas tipo UCR cuando la estructura de clase depende de dinamica y no de artefactos de dominio.',
      },
    },
    rationale: {
      simple: {
        en: 'The current benchmark is controlled; public datasets will test whether the idea survives outside the lab.',
        es: 'El benchmark actual es controlado; datasets publicos probaran si la idea sobrevive fuera del laboratorio.',
      },
      advanced: {
        en: 'External validation is required to separate representation quality from synthetic-data overfitting.',
        es: 'La validacion externa es necesaria para separar calidad representacional de sobreajuste a datos sinteticos.',
      },
    },
    evidenceIds: ['embedding-v2-speed-parity', 'latent-geometry-separability'],
    blocker: {
      simple: {
        en: 'We have not run the full public benchmark yet.',
        es: 'Aun no hemos ejecutado el benchmark publico completo.',
      },
      advanced: {
        en: 'Dataset heterogeneity, unequal lengths, and domain-specific noise may require normalization and descriptor adaptation.',
        es: 'Heterogeneidad de datasets, longitudes desiguales y ruido especifico de dominio pueden requerir normalizacion y adaptacion de descriptores.',
      },
    },
    nextExperiment: {
      simple: {
        en: 'Select a small UCR subset and compare fingerprint accuracy against standard baselines.',
        es: 'Seleccionar un subconjunto UCR pequeno y comparar precision de huella contra baselines estandar.',
      },
      advanced: {
        en: 'Run a stratified UCR pilot with length normalization, feature scaling, and per-dataset error analysis.',
        es: 'Ejecutar un piloto UCR estratificado con normalizacion de longitud, escalado de features y analisis de error por dataset.',
      },
    },
    confidence: 58,
  },
  {
    id: 'lyapunov-scaling',
    state: 'hypothesis',
    title: {
      en: 'Lyapunov-related descriptors may scale with latent curvature',
      es: 'Descriptores ligados a Lyapunov podrian escalar con curvatura latente',
    },
    claim: {
      simple: {
        en: 'Systems that separate quickly may also create stronger bends in the discovery map.',
        es: 'Sistemas que se separan rapido tambien podrian crear curvaturas mas fuertes en el mapa de descubrimiento.',
      },
      advanced: {
        en: 'Instability descriptors may correlate with local metric expansion and curvature proxies in the induced feature manifold.',
        es: 'Descriptores de inestabilidad podrian correlacionar con expansion metrica local y proxies de curvatura en la variedad inducida.',
      },
    },
    rationale: {
      simple: {
        en: 'Chaos changes how nearby paths move apart; the map may preserve part of that geometry.',
        es: 'El caos cambia como se separan caminos cercanos; el mapa podria preservar parte de esa geometria.',
      },
      advanced: {
        en: 'Prior atlas diagnostics suggest curvature-like structure around chaotic regimes, but the descriptor-level driver is not isolated.',
        es: 'Diagnosticos previos del atlas sugieren estructura tipo curvatura alrededor de regimenes caoticos, pero el descriptor causal no esta aislado.',
      },
    },
    evidenceIds: ['latent-geometry-separability', 'feigenbaum-structural-signal'],
    blocker: {
      simple: {
        en: 'We need ablations to know which feature is responsible.',
        es: 'Necesitamos ablaciones para saber que feature es responsable.',
      },
      advanced: {
        en: 'Current evidence mixes Lyapunov, entropy, variance, and autocorrelation effects.',
        es: 'La evidencia actual mezcla efectos de Lyapunov, entropia, varianza y autocorrelacion.',
      },
    },
    nextExperiment: {
      simple: {
        en: 'Remove one feature at a time and see when the map loses its shape.',
        es: 'Quitar una feature cada vez y observar cuando el mapa pierde su forma.',
      },
      advanced: {
        en: 'Run descriptor ablations and correlate neighborhood distortion with Lyapunov estimates.',
        es: 'Ejecutar ablaciones de descriptores y correlacionar distorsion de vecindario con estimaciones de Lyapunov.',
      },
    },
    confidence: 52,
  },
  {
    id: 'structural-noise-threshold',
    state: 'uncertain',
    title: {
      en: 'There may be a measurable structural-noise breaking point',
      es: 'Podria existir un punto de ruptura medible bajo ruido estructural',
    },
    claim: {
      simple: {
        en: 'The map may stay useful until the system is changed too much, then its neighborhoods break.',
        es: 'El mapa podria seguir siendo util hasta que el sistema cambie demasiado y sus vecindarios se rompan.',
      },
      advanced: {
        en: 'Feature-space separability may degrade nonlinearly under structural perturbations, exposing a threshold for descriptor invariance.',
        es: 'La separabilidad en espacio de features podria degradarse de forma no lineal bajo perturbaciones estructurales, exponiendo un umbral de invariancia.',
      },
    },
    rationale: {
      simple: {
        en: 'A good lab should know not only what works, but when it stops working.',
        es: 'Un buen laboratorio debe saber no solo que funciona, sino cuando deja de funcionar.',
      },
      advanced: {
        en: 'Threshold behavior would provide a falsifiable boundary for the representation.',
        es: 'Un comportamiento umbral aportaria una frontera falsable para la representacion.',
      },
    },
    evidenceIds: ['structural-noise-boundary'],
    blocker: {
      simple: {
        en: 'The required perturbation matrix has not been executed.',
        es: 'La matriz de perturbacion requerida no se ha ejecutado.',
      },
      advanced: {
        en: 'We need controlled parameter sweeps with repeated seeds and calibrated noise families.',
        es: 'Necesitamos barridos parametrizados con semillas repetidas y familias de ruido calibradas.',
      },
    },
    nextExperiment: {
      simple: {
        en: 'Increase structural noise step by step and watch when classification starts failing.',
        es: 'Aumentar ruido estructural paso a paso y observar cuando empieza a fallar la clasificacion.',
      },
      advanced: {
        en: 'Estimate degradation curves for additive, parametric, and topology-altering perturbations.',
        es: 'Estimar curvas de degradacion para perturbaciones aditivas, parametricas y de cambio topologico.',
      },
    },
    confidence: 41,
  },
];
