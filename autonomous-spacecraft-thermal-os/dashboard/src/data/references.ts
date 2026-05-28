import type { ScientificReference } from '@/types';

export const scientificReferences: ScientificReference[] = [
  {
    id: 'rocket',
    title: 'ROCKET: exceptionally fast and accurate time series classification using random convolutional kernels',
    authors: ['Angus Dempster', 'Francois Petitjean', 'Geoffrey I. Webb'],
    year: 2020,
    venue: 'Data Mining and Knowledge Discovery',
    doi: '10.1007/s10618-020-00701-z',
    arxiv: '1910.13051',
    url: 'https://arxiv.org/abs/1910.13051',
    tags: ['time-series classification', 'random convolutional kernels', 'benchmark'],
    category: 'benchmark',
    context: {
      simple: {
        en: 'ROCKET is a strong fast baseline: it throws many random filters at a signal and learns from the responses.',
        es: 'ROCKET es un baseline rapido y fuerte: lanza muchos filtros aleatorios a una senal y aprende de sus respuestas.',
      },
      advanced: {
        en: 'Canonical benchmark method for random convolutional kernel transforms in time-series classification; DOI 10.1007/s10618-020-00701-z.',
        es: 'Metodo benchmark canonico para transformadas con kernels convolucionales aleatorios en clasificacion de series temporales; DOI 10.1007/s10618-020-00701-z.',
      },
    },
  },
  {
    id: 'ucr-archive',
    title: 'The UCR Time Series Archive',
    authors: [
      'Hoang Anh Dau',
      'Anthony Bagnall',
      'Kaveh Kamgar',
      'Chin-Chia Michael Yeh',
      'Yan Zhu',
      'Shaghayegh Gharghabi',
      'Chotirat Ann Ratanamahatana',
      'Eamonn Keogh',
    ],
    year: 2019,
    venue: 'IEEE/CAA Journal of Automatica Sinica',
    doi: '10.1109/JAS.2019.1911747',
    arxiv: '1810.07758',
    url: 'https://arxiv.org/abs/1810.07758',
    tags: ['dataset archive', 'external validation', 'time-series classification'],
    category: 'dataset',
    context: {
      simple: {
        en: 'UCR is the external test arena: many public time-series datasets used to check whether a method works beyond a toy lab setup.',
        es: 'UCR es el campo de prueba externo: muchos datasets publicos de series temporales usados para comprobar si un metodo funciona fuera del laboratorio controlado.',
      },
      advanced: {
        en: 'Canonical archive paper for broad time-series classification validation; DOI 10.1109/JAS.2019.1911747.',
        es: 'Paper canonico del archivo para validacion amplia en clasificacion de series temporales; DOI 10.1109/JAS.2019.1911747.',
      },
    },
  },
  {
    id: 'dtw-sakoe-chiba',
    title: 'Dynamic programming algorithm optimization for spoken word recognition',
    authors: ['Hiroaki Sakoe', 'Seibi Chiba'],
    year: 1978,
    venue: 'IEEE Transactions on Acoustics, Speech, and Signal Processing',
    doi: '10.1109/TASSP.1978.1163055',
    arxiv: null,
    url: 'https://ieeexplore.ieee.org/document/1163055',
    tags: ['dynamic time warping', 'sequence alignment', 'methodology'],
    category: 'methodology',
    context: {
      simple: {
        en: 'DTW is the historical alignment idea: it compares signals even when one is stretched or delayed in time.',
        es: 'DTW es la idea historica de alineamiento: compara senales aunque una este estirada o retrasada en el tiempo.',
      },
      advanced: {
        en: 'Canonical IEEE source for dynamic-programming time normalization and DTW lineage; DOI 10.1109/TASSP.1978.1163055.',
        es: 'Fuente IEEE canonica para normalizacion temporal por programacion dinamica y linaje DTW; DOI 10.1109/TASSP.1978.1163055.',
      },
    },
  },
  {
    id: 'distill',
    title: 'Distill',
    authors: ['Distill Editorial Team'],
    year: 2016,
    venue: 'Distill',
    doi: null,
    arxiv: null,
    url: 'https://distill.pub/',
    tags: ['scientific communication', 'visual explanation', 'interactive articles'],
    category: 'methodology',
    context: {
      simple: {
        en: 'Distill is a reference for explaining complex machine-learning ideas with visual, inspectable narratives.',
        es: 'Distill es una referencia para explicar ideas complejas de machine learning con narrativas visuales e inspeccionables.',
      },
      advanced: {
        en: 'Canonical source for interactive scientific communication patterns; used here as methodology lineage, not as experimental evidence.',
        es: 'Fuente canonica para patrones de comunicacion cientifica interactiva; aqui se usa como linaje metodologico, no como evidencia experimental.',
      },
    },
  },
  {
    id: 'three-blue-one-brown',
    title: '3Blue1Brown',
    authors: ['Grant Sanderson'],
    year: 2015,
    venue: '3Blue1Brown',
    doi: null,
    arxiv: null,
    url: 'https://www.3blue1brown.com/',
    tags: ['mathematical visualization', 'pedagogy', 'intuition'],
    category: 'methodology',
    context: {
      simple: {
        en: '3Blue1Brown is a reference for making abstract math feel visual and intuitive.',
        es: '3Blue1Brown es una referencia para hacer que la matematica abstracta se sienta visual e intuitiva.',
      },
      advanced: {
        en: 'Canonical educational reference for visual mathematical pedagogy; used here to guide explanation style.',
        es: 'Referencia educativa canonica para pedagogia matematica visual; se usa aqui para guiar el estilo explicativo.',
      },
    },
  },
  {
    id: 'ucr-official-repository',
    title: 'UCR Time Series Classification Archive',
    authors: ['University of California, Riverside Time Series Classification Group'],
    year: 2021,
    venue: 'Official Benchmark Repository',
    doi: null,
    arxiv: null,
    url: 'https://www.timeseriesclassification.com/',
    tags: ['official repository', 'benchmark datasets', 'reproducibility'],
    category: 'dataset',
    context: {
      simple: {
        en: 'The official archive is where benchmark datasets can be obtained for future validation.',
        es: 'El archivo oficial es donde pueden obtenerse datasets benchmark para validacion futura.',
      },
      advanced: {
        en: 'Official dataset access point for reproducibility workflows and external validation runs.',
        es: 'Punto oficial de acceso a datasets para workflows de reproducibilidad y validacion externa.',
      },
    },
  },
];
