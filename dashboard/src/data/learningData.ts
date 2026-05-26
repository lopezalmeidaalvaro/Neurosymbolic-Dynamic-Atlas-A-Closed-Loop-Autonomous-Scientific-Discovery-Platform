import type { EducationalConcept, GuidedLearningStep, ScientificStoryStep } from '@/types';

export const educationalConcepts: EducationalConcept[] = [
  {
    id: 'time-series',
    title: { en: 'Time series', es: 'Serie temporal' },
    short: {
      simple: {
        en: 'A time series is a measurement written down step by step, like the temperature every minute or the position of a pendulum over time.',
        es: 'Una serie temporal es una medicion escrita paso a paso, como la temperatura cada minuto o la posicion de un pendulo en el tiempo.',
      },
      advanced: {
        en: 'A time series is an ordered sequence x(t) sampled from a dynamical process, preserving temporal structure and short-range dependencies.',
        es: 'Una serie temporal es una secuencia ordenada x(t) muestreada desde un proceso dinamico, conservando estructura temporal y dependencias locales.',
      },
    },
    visual: {
      simple: {
        en: 'Imagine a line that moves as the system changes. Smooth lines often mean regular behavior; jagged lines can mean instability or noise.',
        es: 'Imagina una linea que se mueve cuando el sistema cambia. Lineas suaves suelen indicar comportamiento regular; lineas irregulares pueden indicar inestabilidad o ruido.',
      },
      advanced: {
        en: 'The visual trace exposes amplitude, frequency, drift, local smoothness, and recurrence patterns before any model sees the data.',
        es: 'La traza visual muestra amplitud, frecuencia, deriva, suavidad local y patrones recurrentes antes de que cualquier modelo vea los datos.',
      },
    },
    technical: {
      simple: {
        en: 'We use these sequences as the raw material for every experiment.',
        es: 'Usamos estas secuencias como materia prima de cada experimento.',
      },
      advanced: {
        en: 'The pipeline receives sampled trajectories and converts them into descriptors that are more stable for classification.',
        es: 'El pipeline recibe trayectorias muestreadas y las convierte en descriptores mas estables para clasificacion.',
      },
    },
    analogy: {
      simple: {
        en: 'It is like a heartbeat trace: the shape over time tells you more than one isolated number.',
        es: 'Es como una traza cardiaca: la forma en el tiempo cuenta mas que un numero aislado.',
      },
      advanced: {
        en: 'Temporal order is part of the signal, so permutation destroys information used by autocorrelation and frequency descriptors.',
        es: 'El orden temporal es parte de la senal, asi que permutarlo destruye informacion usada por autocorrelacion y frecuencia.',
      },
    },
    example: {
      simple: {
        en: 'A sine wave repeats. Noise shakes randomly. Chaos looks irregular but still has hidden structure.',
        es: 'Una onda seno se repite. El ruido tiembla al azar. El caos parece irregular pero conserva estructura oculta.',
      },
      advanced: {
        en: 'Periodic, stochastic, and chaotic regimes can share amplitudes while differing in entropy, recurrence, and sensitivity to initial conditions.',
        es: 'Regimenes periodicos, estocasticos y caoticos pueden compartir amplitudes pero diferir en entropia, recurrencia y sensibilidad a condiciones iniciales.',
      },
    },
    keywords: ['signal', 'trajectory', 'time'],
    visualType: 'wave',
    color: 'cyan',
  },
  {
    id: 'chaos',
    title: { en: 'Chaos', es: 'Caos' },
    short: {
      simple: {
        en: 'Chaos is not pure randomness. It is a system with rules that becomes hard to predict because tiny changes grow fast.',
        es: 'El caos no es azar puro. Es un sistema con reglas que se vuelve dificil de predecir porque cambios pequenos crecen rapido.',
      },
      advanced: {
        en: 'Chaos is deterministic dynamics with sensitive dependence on initial conditions, often indicated by positive Lyapunov exponents.',
        es: 'El caos es dinamica determinista con dependencia sensible de condiciones iniciales, a menudo indicada por exponentes de Lyapunov positivos.',
      },
    },
    visual: {
      simple: {
        en: 'Two almost identical starting points separate like two paths that begin together and then drift apart.',
        es: 'Dos puntos iniciales casi iguales se separan como dos caminos que empiezan juntos y luego se alejan.',
      },
      advanced: {
        en: 'Divergence in phase space creates geometric signatures that can remain visible after feature extraction.',
        es: 'La divergencia en espacio de fases crea firmas geometricas que pueden seguir visibles tras extraer caracteristicas.',
      },
    },
    technical: {
      simple: {
        en: 'We try to recognize chaos by measuring its fingerprint rather than forecasting every future point.',
        es: 'Intentamos reconocer el caos midiendo su huella en vez de predecir cada punto futuro.',
      },
      advanced: {
        en: 'The classifier uses descriptors related to instability, entropy, spread, and recurrence instead of direct long-horizon prediction.',
        es: 'El clasificador usa descriptores ligados a inestabilidad, entropia, dispersion y recurrencia en lugar de prediccion directa a largo plazo.',
      },
    },
    analogy: {
      simple: {
        en: 'Like stirring cream into coffee: the motion follows physics, but the exact swirls quickly become impossible to track.',
        es: 'Como remover leche en cafe: el movimiento sigue fisica, pero los remolinos exactos se vuelven imposibles de seguir.',
      },
      advanced: {
        en: 'Deterministic equations can produce trajectories that are locally governed but globally unstable under perturbation.',
        es: 'Ecuaciones deterministas pueden producir trayectorias localmente gobernadas pero globalmente inestables ante perturbaciones.',
      },
    },
    example: {
      simple: {
        en: 'Lorenz and logistic systems can look different, but both can carry the same chaos signature.',
        es: 'Lorenz y el sistema logistico pueden verse distintos, pero ambos pueden portar la misma firma de caos.',
      },
      advanced: {
        en: 'Embedding similarity between Lorenz and other strange attractors suggests a shared geometric regime.',
        es: 'La similitud de embeddings entre Lorenz y otros atractores extranos sugiere un regimen geometrico compartido.',
      },
    },
    formula: '\\lambda_{\\max} > 0',
    formulaLabel: { en: 'Chaos criterion', es: 'Criterio de caos' },
    keywords: ['lyapunov', 'instability', 'deterministic'],
    visualType: 'comparison',
    color: 'violet',
  },
  {
    id: 'noise',
    title: { en: 'Noise', es: 'Ruido' },
    short: {
      simple: {
        en: 'Noise is random disturbance added to a signal. It can hide the pattern we want to recognize.',
        es: 'El ruido es una perturbacion aleatoria anadida a una senal. Puede ocultar el patron que queremos reconocer.',
      },
      advanced: {
        en: 'Noise is stochastic perturbation that degrades observability and can reduce separability between dynamical classes.',
        es: 'El ruido es perturbacion estocastica que degrada la observabilidad y puede reducir la separabilidad entre clases dinamicas.',
      },
    },
    visual: {
      simple: {
        en: 'The same curve becomes fuzzy. Good features should still capture the main shape.',
        es: 'La misma curva se vuelve borrosa. Buenas caracteristicas deberian conservar la forma principal.',
      },
      advanced: {
        en: 'Robust descriptors should remain informative under perturbations that alter individual samples but not the global regime.',
        es: 'Descriptores robustos deben seguir informando bajo perturbaciones que alteran muestras individuales pero no el regimen global.',
      },
    },
    technical: {
      simple: {
        en: 'Noise tests whether the method learned the pattern or only memorized clean examples.',
        es: 'El ruido prueba si el metodo aprendio el patron o solo memorizo ejemplos limpios.',
      },
      advanced: {
        en: 'Perturbation analysis measures invariance, class margin stability, and degradation of model performance.',
        es: 'El analisis de perturbacion mide invariancia, estabilidad del margen de clase y degradacion del rendimiento.',
      },
    },
    analogy: {
      simple: {
        en: 'It is like hearing a melody in a noisy room: the notes are harder to hear, but the song can still be recognized.',
        es: 'Es como oir una melodia en una sala ruidosa: las notas cuestan mas, pero la cancion aun puede reconocerse.',
      },
      advanced: {
        en: 'Noise changes sample-level fidelity while the latent class manifold may remain partially separable.',
        es: 'El ruido cambia la fidelidad de las muestras mientras la variedad latente de clase puede seguir parcialmente separable.',
      },
    },
    example: {
      simple: {
        en: 'If accuracy stays high with noise, the representation is probably capturing real structure.',
        es: 'Si la precision sigue alta con ruido, la representacion probablemente captura estructura real.',
      },
      advanced: {
        en: 'Stable accuracy under perturbation supports descriptor invariance and robust class boundaries.',
        es: 'Precision estable bajo perturbacion apoya invariancia de descriptores y fronteras de clase robustas.',
      },
    },
    keywords: ['perturbation', 'robustness', 'stochastic'],
    visualType: 'noise',
    color: 'amber',
  },
  {
    id: 'autocorrelation',
    title: { en: 'Autocorrelation', es: 'Autocorrelacion' },
    short: {
      simple: {
        en: 'Autocorrelation measures how much a signal still looks like itself a few steps later.',
        es: 'La autocorrelacion mide cuanto se parece una senal a si misma unos pasos despues.',
      },
      advanced: {
        en: 'Autocorrelation estimates temporal self-similarity as a function of lag, revealing memory and recurrence.',
        es: 'La autocorrelacion estima autosimilitud temporal en funcion del retardo, revelando memoria y recurrencia.',
      },
    },
    visual: {
      simple: {
        en: 'A repeating signal remembers itself. Random noise forgets almost immediately.',
        es: 'Una senal repetitiva se recuerda a si misma. El ruido aleatorio olvida casi de inmediato.',
      },
      advanced: {
        en: 'Decay rate helps distinguish periodic persistence from chaotic or stochastic decorrelation.',
        es: 'La tasa de decaimiento ayuda a distinguir persistencia periodica de decorrelacion caotica o estocastica.',
      },
    },
    technical: {
      simple: {
        en: 'This is one way the system notices rhythm without needing to label every peak by hand.',
        es: 'Asi el sistema detecta ritmo sin tener que etiquetar cada pico manualmente.',
      },
      advanced: {
        en: 'Lagged similarity contributes a compact feature that captures recurrence structure.',
        es: 'La similitud con retardo aporta una caracteristica compacta que captura estructura de recurrencia.',
      },
    },
    analogy: {
      simple: {
        en: 'It is like asking: if I clap a rhythm now, how similar is the echo one beat later?',
        es: 'Es como preguntar: si doy una palmada con ritmo ahora, cuanto se parece el eco un tiempo despues?',
      },
      advanced: {
        en: 'The lag parameter shifts the signal against itself and measures normalized overlap.',
        es: 'El retardo desplaza la senal contra si misma y mide solapamiento normalizado.',
      },
    },
    example: {
      simple: {
        en: 'A sine wave has strong autocorrelation. White noise has weak autocorrelation.',
        es: 'Una onda seno tiene autocorrelacion fuerte. El ruido blanco tiene autocorrelacion debil.',
      },
      advanced: {
        en: 'Periodic systems retain high correlation at repeated lags, while chaotic systems decay faster.',
        es: 'Sistemas periodicos retienen alta correlacion en retardos repetidos, mientras sistemas caoticos decaen mas rapido.',
      },
    },
    formula: 'R(\\tau)=\\frac{\\langle x(t)x(t+\\tau)\\rangle}{\\langle x^2\\rangle}',
    formulaLabel: { en: 'Normalized autocorrelation', es: 'Autocorrelacion normalizada' },
    keywords: ['lag', 'memory', 'recurrence'],
    visualType: 'wave',
    color: 'blue',
  },
  {
    id: 'embedding',
    title: { en: 'Embedding', es: 'Embedding' },
    short: {
      simple: {
        en: 'We convert complex signals into a compact mathematical fingerprint so patterns can be recognized quickly.',
        es: 'Convertimos senales complejas en una huella matematica compacta para reconocer patrones rapidamente.',
      },
      advanced: {
        en: 'Embedding V2 extracts statistical descriptors invariant to stochastic perturbations.',
        es: 'Embedding V2 extrae descriptores estadisticos invariantes ante perturbaciones estocasticas.',
      },
    },
    visual: {
      simple: {
        en: 'Each signal becomes a point in a map. Similar behaviors land near each other.',
        es: 'Cada senal se convierte en un punto en un mapa. Comportamientos similares caen cerca.',
      },
      advanced: {
        en: 'Feature vectors induce a geometry where distance approximates dynamical similarity.',
        es: 'Los vectores de caracteristicas inducen una geometria donde la distancia aproxima similitud dinamica.',
      },
    },
    technical: {
      simple: {
        en: 'Instead of comparing every wiggle, we compare the fingerprint.',
        es: 'En vez de comparar cada oscilacion, comparamos la huella.',
      },
      advanced: {
        en: 'The representation compresses variance, entropy, autocorrelation, kurtosis, skewness, frequency, energy, and instability indicators.',
        es: 'La representacion comprime varianza, entropia, autocorrelacion, curtosis, asimetria, frecuencia, energia e indicadores de inestabilidad.',
      },
    },
    analogy: {
      simple: {
        en: 'Like recognizing a person from a fingerprint instead of a full video of them walking.',
        es: 'Como reconocer a una persona por su huella en lugar de mirar un video completo caminando.',
      },
      advanced: {
        en: 'Dimensional compression preserves discriminative structure while discarding sample-level clutter.',
        es: 'La compresion dimensional preserva estructura discriminativa y descarta ruido a nivel de muestra.',
      },
    },
    example: {
      simple: {
        en: 'Embedding V2 can match larger methods while running much faster because it compares compact descriptors.',
        es: 'Embedding V2 puede igualar metodos mayores y correr mucho mas rapido porque compara descriptores compactos.',
      },
      advanced: {
        en: 'Feature extraction shifts cost from expensive sequence comparison to low-dimensional classification.',
        es: 'La extraccion de caracteristicas mueve el coste desde comparacion secuencial cara hacia clasificacion de baja dimension.',
      },
    },
    formula: '\\varphi(x)=(\\lambda_{max},H_s,f_{dom},\\sigma^2,\\tau_c,\\kappa,\\gamma,E)',
    formulaLabel: { en: 'Embedding V2 fingerprint', es: 'Huella de Embedding V2' },
    methodology: {
      simple: {
        en: 'Take a signal, measure several useful properties, place it on the map, then classify by neighborhood.',
        es: 'Toma una senal, mide propiedades utiles, colocala en el mapa y clasifica por vecindad.',
      },
      advanced: {
        en: 'Sample trajectory -> compute descriptors -> normalize vector -> train classifier -> evaluate class separability.',
        es: 'Muestrear trayectoria -> computar descriptores -> normalizar vector -> entrenar clasificador -> evaluar separabilidad.',
      },
    },
    keywords: ['feature vector', 'fingerprint', 'latent map'],
    visualType: 'embedding',
    color: 'cyan',
  },
  {
    id: 'dtw-rocket',
    title: { en: 'DTW and ROCKET', es: 'DTW y ROCKET' },
    short: {
      simple: {
        en: 'DTW bends time to compare two signals. ROCKET throws many random filters at the signal to find useful patterns.',
        es: 'DTW dobla el tiempo para comparar dos senales. ROCKET lanza muchos filtros aleatorios para encontrar patrones utiles.',
      },
      advanced: {
        en: 'DTW aligns sequences through dynamic programming; ROCKET projects time series through randomized convolutional kernels.',
        es: 'DTW alinea secuencias con programacion dinamica; ROCKET proyecta series mediante kernels convolucionales aleatorios.',
      },
    },
    visual: {
      simple: {
        en: 'They are strong baselines, but they can cost more compute than a compact embedding.',
        es: 'Son baselines fuertes, pero pueden costar mas computo que un embedding compacto.',
      },
      advanced: {
        en: 'The benchmark compares accuracy and inference cost against descriptor-based classification.',
        es: 'El benchmark compara precision y coste de inferencia frente a clasificacion basada en descriptores.',
      },
    },
    technical: {
      simple: {
        en: 'Speed matters because a scientific system should test many hypotheses, not wait on one slow comparison.',
        es: 'La velocidad importa porque un sistema cientifico debe probar muchas hipotesis, no esperar una comparacion lenta.',
      },
      advanced: {
        en: 'Lower compute cost increases experimental throughput, enabling broader perturbation and ablation studies.',
        es: 'Menor coste computacional aumenta el throughput experimental y permite mas estudios de perturbacion y ablacion.',
      },
    },
    analogy: {
      simple: {
        en: 'DTW is like carefully matching two songs beat by beat. Embedding is like comparing their musical fingerprints.',
        es: 'DTW es como emparejar dos canciones golpe a golpe. Embedding es comparar sus huellas musicales.',
      },
      advanced: {
        en: 'Sequence alignment preserves detail but can be expensive; descriptor comparison is cheaper after feature extraction.',
        es: 'El alineamiento preserva detalle pero puede ser caro; comparar descriptores es mas barato tras extraer caracteristicas.',
      },
    },
    example: {
      simple: {
        en: 'If two methods are equally accurate, the faster one lets the lab explore more ideas.',
        es: 'Si dos metodos son igual de precisos, el mas rapido permite explorar mas ideas.',
      },
      advanced: {
        en: 'Equal accuracy with lower runtime indicates a better accuracy-cost tradeoff for iterative research.',
        es: 'Igual precision con menor runtime indica mejor compromiso precision-coste para investigacion iterativa.',
      },
    },
    keywords: ['baseline', 'speed', 'accuracy'],
    visualType: 'comparison',
    color: 'emerald',
  },
  {
    id: 'geometric-separability',
    title: { en: 'Geometric separability', es: 'Separabilidad geometrica' },
    short: {
      simple: {
        en: 'If chaos, noise, and periodic motion form separate neighborhoods on the map, the model can tell them apart.',
        es: 'Si caos, ruido y movimiento periodico forman barrios separados en el mapa, el modelo puede distinguirlos.',
      },
      advanced: {
        en: 'Separability means class manifolds occupy distinguishable regions of the induced feature space.',
        es: 'Separabilidad significa que las variedades de clase ocupan regiones distinguibles del espacio de caracteristicas inducido.',
      },
    },
    visual: {
      simple: {
        en: 'Think of colored dots on a map. Good descriptors make each color cluster naturally.',
        es: 'Piensa en puntos de colores en un mapa. Buenos descriptores hacen que cada color se agrupe de forma natural.',
      },
      advanced: {
        en: 'Margins, neighborhood purity, and cluster compactness reveal whether the representation supports classification.',
        es: 'Margenes, pureza de vecindario y compacidad de clusters revelan si la representacion soporta clasificacion.',
      },
    },
    technical: {
      simple: {
        en: 'This is the central discovery: the fingerprint map can expose hidden structure.',
        es: 'Este es el descubrimiento central: el mapa de huellas puede revelar estructura oculta.',
      },
      advanced: {
        en: 'Latent geometry turns dynamical recognition into a spatial problem: distance, curvature, and cluster structure become evidence.',
        es: 'La geometria latente convierte el reconocimiento dinamico en un problema espacial: distancia, curvatura y clusters se vuelven evidencia.',
      },
    },
    analogy: {
      simple: {
        en: 'Like sorting music by sound: jazz, noise, and classical end up on different shelves.',
        es: 'Como ordenar musica por sonido: jazz, ruido y clasica terminan en estantes distintos.',
      },
      advanced: {
        en: 'Class-conditioned neighborhoods encode empirical regularities across different dynamical systems.',
        es: 'Vecindarios condicionados por clase codifican regularidades empiricas entre sistemas dinamicos distintos.',
      },
    },
    example: {
      simple: {
        en: 'When Lorenz and similar chaotic systems land near each other, the map has learned something real.',
        es: 'Cuando Lorenz y sistemas caoticos similares caen cerca, el mapa aprendio algo real.',
      },
      advanced: {
        en: 'Structural asymmetry under continuous domain shifts supports an asymmetric topological adaptation hypothesis.',
        es: 'La asimetría estructural bajo cambios de dominio continuos apoya una hipótesis de adaptación topológica asimétrica.',
      },
    },
    keywords: ['clusters', 'latent space', 'geometry'],
    visualType: 'geometry',
    color: 'violet',
  },
];

export const guidedLearningSteps: GuidedLearningStep[] = [
  {
    id: 'generate',
    title: { en: 'Generate dynamic systems', es: 'Generamos sistemas dinamicos' },
    body: {
      simple: {
        en: 'We create signals from systems that behave differently: repeating, noisy, or chaotic.',
        es: 'Creamos senales de sistemas que se comportan distinto: repetitivos, ruidosos o caoticos.',
      },
      advanced: {
        en: 'Synthetic trajectories are sampled from known regimes so model behavior can be evaluated against controlled structure.',
        es: 'Trayectorias sinteticas se muestrean desde regimenes conocidos para evaluar el modelo contra estructura controlada.',
      },
    },
    outcome: {
      simple: { en: 'The lab starts with signals we can understand.', es: 'El laboratorio empieza con senales que podemos entender.' },
      advanced: { en: 'Controlled data anchors validation.', es: 'Datos controlados anclan la validacion.' },
    },
    conceptIds: ['time-series', 'chaos'],
  },
  {
    id: 'perturb',
    title: { en: 'Add noise', es: 'Anadimos ruido' },
    body: {
      simple: {
        en: 'We make the signals messier to see whether the method still recognizes the underlying behavior.',
        es: 'Hacemos las senales mas desordenadas para ver si el metodo aun reconoce el comportamiento de fondo.',
      },
      advanced: {
        en: 'Perturbation tests robustness and separates fragile memorization from invariant representation.',
        es: 'La perturbacion prueba robustez y separa memorizacion fragil de representacion invariante.',
      },
    },
    outcome: {
      simple: { en: 'Good science survives imperfect data.', es: 'La buena ciencia sobrevive a datos imperfectos.' },
      advanced: { en: 'Robustness becomes measurable.', es: 'La robustez se vuelve medible.' },
    },
    conceptIds: ['noise'],
  },
  {
    id: 'compare',
    title: { en: 'Test competing models', es: 'Probamos modelos' },
    body: {
      simple: {
        en: 'We compare our fingerprint method with strong baselines instead of trusting it blindly.',
        es: 'Comparamos nuestro metodo de huellas con baselines fuertes en vez de confiar a ciegas.',
      },
      advanced: {
        en: 'Benchmarking against DTW and ROCKET evaluates both predictive performance and computational cost.',
        es: 'Benchmarking contra DTW y ROCKET evalua rendimiento predictivo y coste computacional.',
      },
    },
    outcome: {
      simple: { en: 'Accuracy is not enough; speed also matters.', es: 'La precision no basta; la velocidad tambien importa.' },
      advanced: { en: 'The relevant metric is accuracy-cost tradeoff.', es: 'La metrica relevante es el compromiso precision-coste.' },
    },
    conceptIds: ['dtw-rocket', 'embedding'],
  },
  {
    id: 'discover',
    title: { en: 'Detect invariances', es: 'Detectamos invariancias' },
    body: {
      simple: {
        en: 'If the same type of behavior lands in the same region, the map has found a stable pattern.',
        es: 'Si el mismo tipo de comportamiento cae en la misma region, el mapa encontro un patron estable.',
      },
      advanced: {
        en: 'Stable neighborhoods in feature space indicate representation-level invariance across systems and perturbations.',
        es: 'Vecindarios estables en el espacio de caracteristicas indican invariancia representacional entre sistemas y perturbaciones.',
      },
    },
    outcome: {
      simple: { en: 'The system starts to explain what it sees.', es: 'El sistema empieza a explicar lo que ve.' },
      advanced: { en: 'Geometry becomes scientific evidence.', es: 'La geometria se convierte en evidencia cientifica.' },
    },
    conceptIds: ['geometric-separability', 'autocorrelation'],
  },
  {
    id: 'record',
    title: { en: 'Register findings', es: 'Registramos hallazgos' },
    body: {
      simple: {
        en: 'The log keeps the story of what worked, what failed, and what changed our understanding.',
        es: 'El log conserva la historia de que funciono, que fallo y que cambio nuestra comprension.',
      },
      advanced: {
        en: 'Experimental traces preserve reproducibility, validation context, and research decisions.',
        es: 'Las trazas experimentales preservan reproducibilidad, contexto de validacion y decisiones de investigacion.',
      },
    },
    outcome: {
      simple: { en: 'The platform becomes a memory for discovery.', es: 'La plataforma se vuelve memoria del descubrimiento.' },
      advanced: { en: 'The research loop remains auditable.', es: 'El bucle de investigacion queda auditable.' },
    },
    conceptIds: ['embedding', 'geometric-separability'],
  },
];

export const scientificStory: ScientificStoryStep[] = [
  {
    id: 'systems',
    title: { en: 'Systems become signals', es: 'Los sistemas se vuelven senales' },
    body: {
      simple: { en: 'We observe motion through time.', es: 'Observamos movimiento en el tiempo.' },
      advanced: { en: 'Trajectories are sampled as ordered numerical sequences.', es: 'Las trayectorias se muestrean como secuencias numericas ordenadas.' },
    },
    signal: { en: 'Observation', es: 'Observacion' },
  },
  {
    id: 'fingerprint',
    title: { en: 'Signals become fingerprints', es: 'Las senales se vuelven huellas' },
    body: {
      simple: { en: 'We compress the important behavior into a small set of numbers.', es: 'Comprimimos el comportamiento importante en pocos numeros.' },
      advanced: { en: 'Feature extraction maps trajectories into descriptor vectors.', es: 'La extraccion de caracteristicas mapea trayectorias a vectores descriptores.' },
    },
    signal: { en: 'Representation', es: 'Representacion' },
  },
  {
    id: 'map',
    title: { en: 'Fingerprints become a map', es: 'Las huellas se vuelven mapa' },
    body: {
      simple: { en: 'Similar behaviors gather in nearby regions.', es: 'Comportamientos similares se agrupan cerca.' },
      advanced: { en: 'The induced feature space exposes neighborhoods and class margins.', es: 'El espacio inducido expone vecindarios y margenes de clase.' },
    },
    signal: { en: 'Geometry', es: 'Geometria' },
  },
];
