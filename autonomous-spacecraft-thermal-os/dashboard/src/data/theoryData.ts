// ═══════════════════════════════════════════════════════════════
// data/theoryData.ts — Scientific theory blocks with semantic layers
// ═══════════════════════════════════════════════════════════════
import type { TheoryBlock } from '@/types';

export const theoryBlocks: TheoryBlock[] = [
  {
    id: 'embedding-v2',
    title: { en: 'Embedding V2: Feature Extraction', es: 'Embedding V2: Extracción de Características' },
    tag: 'Core',
    color: 'cyan',
    content: {
      simple: {
        en: 'We describe each time series using 8 numbers that capture its "personality": how chaotic it is, how spread out its values are, and how it oscillates. Think of it as a fingerprint for a signal.',
        es: 'Describimos cada serie temporal usando 8 números que capturan su "personalidad": qué tan caótica es, cuán dispersos están sus valores y cómo oscila. Piénsalo como una huella dactilar de una señal.',
      },
      advanced: {
        en: 'Each trajectory x(t) is mapped to an 8-dimensional feature vector φ(x) ∈ ℝ⁸ comprising: maximum Lyapunov exponent (λ_max), spectral entropy (H_s), dominant frequency (f_dom), variance (σ²), autocorrelation decay time (τ_c), excess kurtosis (κ), skewness (γ), and RMS energy (E). This embedding induces a metric structure on the space of dynamical systems.',
        es: 'Cada trayectoria x(t) se mapea a un vector de características 8-dimensional φ(x) ∈ ℝ⁸ que comprende: exponente máximo de Lyapunov (λ_max), entropía espectral (H_s), frecuencia dominante (f_dom), varianza (σ²), tiempo de decaimiento de autocorrelación (τ_c), curtosis exceso (κ), asimetría (γ) y energía RMS (E).',
      },
    },
    formula: '\\varphi(x) = (\\lambda_{\\max}, H_s, f_{\\text{dom}}, \\sigma^2, \\tau_c, \\kappa, \\gamma, E) \\in \\mathbb{R}^8',
    formulaLabel: { en: 'Feature Map', es: 'Mapa de Características' },
  },
  {
    id: 'variance',
    title: { en: 'Variance', es: 'Varianza' },
    tag: 'Feature',
    color: 'blue',
    content: {
      simple: {
        en: 'Variance measures how spread out the values of a signal are around its average. A chaotic signal has high variance; a flat signal has zero variance.',
        es: 'La varianza mide cuán dispersos están los valores de una señal alrededor de su promedio. Una señal caótica tiene alta varianza; una señal plana tiene varianza cero.',
      },
      advanced: {
        en: 'The variance σ² of a discrete time series {x_i} of length N quantifies the second central moment of the empirical distribution. For non-stationary signals, a windowed estimator is preferred. In the embedding V2, this serves as a proxy for the amplitude of oscillations in phase space.',
        es: 'La varianza σ² de una serie temporal discreta {x_i} de longitud N cuantifica el segundo momento central de la distribución empírica. Para señales no estacionarias se prefiere un estimador con ventana. En el embedding V2, sirve como proxy de la amplitud de oscilaciones en el espacio de fases.',
      },
    },
    formula: '\\sigma^2 = \\frac{1}{N}\\sum_{i=1}^{N}(x_i - \\mu)^2',
    formulaLabel: { en: 'Sample Variance', es: 'Varianza Muestral' },
  },
  {
    id: 'spectral-entropy',
    title: { en: 'Spectral Entropy', es: 'Entropía Espectral' },
    tag: 'Feature',
    color: 'violet',
    content: {
      simple: {
        en: 'Spectral entropy tells us how "disordered" the frequency content of a signal is. White noise has maximum spectral entropy (all frequencies equally present). A pure sine wave has minimum entropy (only one frequency).',
        es: 'La entropía espectral nos dice qué tan "desordenado" está el contenido de frecuencias de una señal. El ruido blanco tiene máxima entropía espectral (todas las frecuencias igualmente presentes). Una onda sinusoidal pura tiene mínima entropía (solo una frecuencia).',
      },
      advanced: {
        en: 'Given the power spectral density P(f) = |X(f)|² / ∫|X(f)|²df, where X(f) is the DFT of x(t), the spectral entropy H_s quantifies the Shannon information of the normalized PSD. H_s = 0 for periodic signals and log₂(N/2) for white noise. It serves as a discriminant between periodic, quasi-periodic and chaotic regimes.',
        es: 'Dada la densidad espectral de potencia P(f) = |X(f)|² / ∫|X(f)|²df, donde X(f) es la DFT de x(t), la entropía espectral H_s cuantifica la información de Shannon de la DEP normalizada. H_s = 0 para señales periódicas y log₂(N/2) para ruido blanco.',
      },
    },
    formula: 'H_s = -\\sum_k P(f_k)\\log_2 P(f_k)',
    formulaLabel: { en: 'Spectral Entropy', es: 'Entropía Espectral' },
  },
  {
    id: 'lyapunov',
    title: { en: 'Lyapunov Exponent', es: 'Exponente de Lyapunov' },
    tag: 'Chaos',
    color: 'emerald',
    content: {
      simple: {
        en: 'The Lyapunov exponent measures how fast two nearby trajectories diverge. If it is positive, the system is chaotic: a tiny difference in initial conditions grows exponentially over time — the "butterfly effect".',
        es: 'El exponente de Lyapunov mide qué tan rápido divergen dos trayectorias cercanas. Si es positivo, el sistema es caótico: una pequeña diferencia en condiciones iniciales crece exponencialmente con el tiempo — el "efecto mariposa".',
      },
      advanced: {
        en: 'For a discrete map f: ℝ→ℝ, the maximum Lyapunov exponent λ_max = lim_{n→∞} (1/n) Σ ln|f\'(x_i)| characterizes the exponential rate of separation of infinitesimally close trajectories. λ_max > 0 is the rigorous criterion for deterministic chaos. For the logistic map at r=3.9, λ_max ≈ 0.497 nats/iteration.',
        es: 'Para un mapa discreto f: ℝ→ℝ, el exponente máximo de Lyapunov λ_max = lim_{n→∞} (1/n) Σ ln|f\'(x_i)| caracteriza la tasa exponencial de separación de trayectorias infinitesimalmente cercanas. λ_max > 0 es el criterio riguroso de caos determinista.',
      },
    },
    formula: '\\lambda_{\\max} = \\lim_{n\\to\\infty}\\frac{1}{n}\\sum_{i=0}^{n-1}\\ln\\left|f\'(x_i)\\right|',
    formulaLabel: { en: 'Maximum Lyapunov Exponent', es: 'Exponente Máximo de Lyapunov' },
  },
  {
    id: 'autocorrelation',
    title: { en: 'Autocorrelation Decay', es: 'Decaimiento de Autocorrelación' },
    tag: 'Feature',
    color: 'blue',
    content: {
      simple: {
        en: 'Autocorrelation measures how similar a signal is to itself after a time delay. Chaotic signals lose their self-similarity quickly (fast decay). Periodic signals remain correlated forever.',
        es: 'La autocorrelación mide cuán similar es una señal consigo misma después de un retraso temporal. Las señales caóticas pierden su auto-similitud rápidamente (decaimiento rápido). Las señales periódicas permanecen correlacionadas indefinidamente.',
      },
      advanced: {
        en: 'The autocorrelation function R(τ) = ⟨x(t)x(t+τ)⟩ / ⟨x²⟩ measures temporal memory. In Embedding V2, τ_c is defined as the first lag where |R(τ)| < 1/e, corresponding to the decorrelation time. For chaotic attractors, τ_c is finite and related to the Kolmogorov-Sinai entropy.',
        es: 'La función de autocorrelación R(τ) = ⟨x(t)x(t+τ)⟩ / ⟨x²⟩ mide la memoria temporal. En Embedding V2, τ_c se define como el primer lag donde |R(τ)| < 1/e, correspondiente al tiempo de decorrelación.',
      },
    },
    formula: 'R(\\tau) = \\frac{\\langle x(t)\\,x(t+\\tau)\\rangle}{\\langle x^2 \\rangle}',
    formulaLabel: { en: 'Normalized ACF', es: 'ACF Normalizada' },
  },
  {
    id: 'universality',
    title: { en: 'Asymmetric Topological Adaptation', es: 'Adaptación Topológica Asimétrica' },
    tag: 'Finding',
    color: 'cyan',
    content: {
      simple: {
        en: 'Our key finding: generalisation is driven by a structural asymmetry. The V3 embedding achieves an AUC of 0.830 on the MIT-BIH clinical database but fails universal geometric transport, resulting in coordinated latent collapse (D_emb = 0.982) alongside explanatory attribution survival (D_attr = 0.763).',
        es: 'Nuestro hallazgo clave: la generalización se debe a una asimetría estructural. El Embedding V3 logra un AUC de 0.830 en la base de datos MIT-BIH pero fracasa en el transporte geométrico universal, mostrando un colapso latente coordinado (D_emb = 0.982) junto a una supervivencia atributiva (D_attr = 0.763).',
      },
      advanced: {
        en: 'Continuous representation transport across Synthetic (A), Biophysical (B), and Clinical (C) domains reveals Asymmetric Representational Decay. While the latent manifold collapses and is completely deformed geometrically (D_emb = 1 - CKA = 0.982), the causal attribution mechanism remains structurally preserved (D_attr = 1 - rho = 0.763), explaining the robust clinical survival performance.',
        es: 'El transporte continuo de representaciones entre dominios Sintético (A), Biofísico (B) y Clínico (C) revela una Degradación Representacional Asimétrica. Mientras la variedad latente colapsa y se deforma geométricamente (D_emb = 1 - CKA = 0.982), el mecanismo de atribución causal se preserva estructuralmente (D_attr = 1 - rho = 0.763), explicando la robusta supervivencia clínica.',
      },
    },
    formula: 'D_{emb} = 1 - \\text{CKA}(E_A, E_C) \\quad \\text{vs} \\quad D_{attr} = 1 - \\rho(\\bar{C}_A, \\bar{C}_C)',
    formulaLabel: { en: 'Asymmetry of Deformation', es: 'Asimetría de Deformación' },
  },
];
