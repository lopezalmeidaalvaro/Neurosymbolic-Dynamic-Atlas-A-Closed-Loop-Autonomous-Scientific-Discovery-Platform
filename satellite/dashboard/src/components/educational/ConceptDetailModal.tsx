'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, BookOpen, Calculator, HelpCircle } from 'lucide-react';
import { useAppStore } from '@/stores/appStore';
import { KaTeX } from '@/components/ui/KaTeX';
import type { EducationalConcept, Language } from '@/types';

interface ConceptDetailModalProps {
  concept: EducationalConcept | null;
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

const FORMULA_BREAKDOWNS: Record<string, Array<{ symbol: string; label: string; explanation: string }>> = {
  'time-series': [
    { symbol: 'x(t)', label: 'Valor medido (Measured Value)', explanation: 'El estado físico o lectura del sistema en el instante t.' },
    { symbol: 't', label: 'Tiempo (Time)', explanation: 'La variable de tiempo donde cada paso indica una medición cronológica secuencial.' }
  ],
  'chaos': [
    { symbol: '\\lambda_{\\max}', label: 'Exponente de Lyapunov (Lyapunov Exponent)', explanation: 'El valor que mide la velocidad a la que dos caminos inicialmente casi idénticos se separan.' },
    { symbol: '> 0', label: 'Criterio positivo (Positive Criterion)', explanation: 'Si la tasa es mayor a cero, la trayectoria se considera caótica e impredecible a largo plazo.' }
  ],
  'noise': [
    { symbol: '\\eta(t)', label: 'Señal ruidosa (Noisy Signal)', explanation: 'El ruido aleatorio o estocástico que perturba la señal original e ideal x(t).' },
    { symbol: '\\sigma', label: 'Desviación estándar (Standard Deviation)', explanation: 'La fuerza o amplitud de la perturbación o vibración del ruido.' }
  ],
  'autocorrelation': [
    { symbol: 'R(\\tau)', label: 'Autocorrelación (Autocorrelation Score)', explanation: 'Qué tanto se parece la señal a sí misma después de un retraso de tiempo.' },
    { symbol: '\\tau', label: 'Retardo (Lag / Delay)', explanation: 'La cantidad de pasos o tiempo que desplazamos la señal para compararla con su estado original.' },
    { symbol: 'x(t)', label: 'Señal en t (Signal at t)', explanation: 'El valor de la trayectoria en el instante de tiempo t.' }
  ],
  'embedding': [
    { symbol: '\\varphi(x)', label: 'Vector Huella (Fingerprint Vector)', explanation: 'El conjunto final de características que representan de forma compacta e invariable la señal.' },
    { symbol: '\\lambda_{\\max}', label: 'Exponente de Lyapunov', explanation: 'Sensibilidad a las condiciones iniciales del sistema.' },
    { symbol: 'H_s', label: 'Entropía Espectral', explanation: 'Complejidad y desorden de la frecuencia de la señal.' },
    { symbol: '\\sigma^2', label: 'Varianza', explanation: 'Dispersión y rango de amplitud del comportamiento.' }
  ],
  'geometric-separability': [
    { symbol: 'd(p, q)', label: 'Distancia euclídea (Euclidean Distance)', explanation: 'La separación física y geométrica entre dos firmas latentes en el espacio de características.' },
    { symbol: 'M_c', label: 'Margen de clase (Class Margin)', explanation: 'El espacio de seguridad que separa a la familia caótica del ruido o movimiento periódico.' }
  ]
};

export function ConceptDetailModal({ concept, isOpen, onClose, lang }: ConceptDetailModalProps) {
  if (!concept) return null;

  const { isTeenagerMode } = useAppStore();
  const breakdown = FORMULA_BREAKDOWNS[concept.id] || [];

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 lg:p-10">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/80 backdrop-blur-md"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="relative z-10 w-full max-w-4xl overflow-hidden rounded-3xl border border-white/[0.08] bg-[#0c101b] p-6 shadow-2xl md:p-8"
          >
            {/* Background glowing effects */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(139,92,246,0.06),transparent_65%)] pointer-events-none" />
            <div className="absolute inset-0 scientific-grid opacity-[0.03] pointer-events-none" />

            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/[0.03] text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <X size={16} />
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3 border-b border-white/[0.08] pb-4 mb-6">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
                <BookOpen size={15} />
              </span>
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
                  {lang === 'es' ? 'Concepto Interactivo' : 'Interactive Concept'}
                </span>
                <h2 className="text-xl font-bold text-white leading-tight">
                  {concept.title[lang]}
                </h2>
              </div>
            </div>

            {/* Modal Content Grid */}
            <div className="grid gap-6 md:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-6">
                {/* 1. Real-World Analogy & Simple Explanation */}
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <div className="flex items-center gap-2 mb-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
                    <Sparkles size={12} className="animate-pulse" />
                    <span>{lang === 'es' ? 'La Analogía (Explicación Sencilla)' : 'The Analogy (Simple Explanation)'}</span>
                  </div>
                  <p className="text-sm leading-relaxed text-emerald-50/90 font-medium">
                    {concept.analogy[isTeenagerMode ? 'simple' : 'advanced']?.[lang] || concept.short.simple[lang]}
                  </p>
                  <p className="mt-3 text-xs leading-relaxed text-slate-400/90">
                    {concept.short[isTeenagerMode ? 'simple' : 'advanced'][lang]}
                  </p>
                </div>

                {/* 3. Mathematical Rigor & KaTeX Formula */}
                <div className="rounded-2xl border border-white/[0.07] bg-black/30 p-4">
                  <div className="flex items-center gap-2 mb-3 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
                    <Calculator size={12} />
                    <span>{lang === 'es' ? 'Rigor Matemático Real' : 'Real Mathematical Rigor'}</span>
                  </div>
                  
                  {concept.formula ? (
                    <div className="my-4 py-2 border-y border-white/[0.05] bg-white/[0.01] rounded-xl flex items-center justify-center">
                      <KaTeX formula={concept.formula} block className="text-base text-cyan-200" />
                    </div>
                  ) : (
                    <div className="my-2 text-xs text-slate-500 italic py-2 text-center">
                      {lang === 'es' ? 'Fórmula implícita en la representación representacional.' : 'Formula implicit in the representational framework.'}
                    </div>
                  )}

                  {breakdown.length > 0 && (
                    <div className="space-y-2.5 mt-3">
                      <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                        {lang === 'es' ? 'Glosario de Variables:' : 'Variable Breakdown:'}
                      </p>
                      <div className="grid gap-2 text-xs">
                        {breakdown.map((item, i) => (
                          <div key={i} className="flex gap-2 items-start border-b border-white/[0.04] pb-2 last:border-b-0">
                            <span className="font-mono text-cyan-300 font-bold shrink-0 min-w-[50px]"><KaTeX formula={item.symbol} /></span>
                            <div>
                              <p className="font-medium text-slate-200 text-[11px]">{item.label}</p>
                              <p className="text-slate-400 text-[10px] leading-relaxed">{item.explanation}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 2. Visual Blueprint / SVG Animation Scheme */}
              <div className="flex flex-col rounded-2xl border border-white/[0.08] bg-black/40 p-4 relative overflow-hidden items-center justify-center min-h-[300px]">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(139,92,246,0.03),transparent_70%)]" />
                <div className="absolute top-3 left-3 text-[9px] uppercase tracking-wider text-slate-500 font-mono">
                  {lang === 'es' ? 'Diagrama Interactivo' : 'Interactive Blueprint'}
                </div>

                {/* Wave Visual Type */}
                {concept.visualType === 'wave' && (
                  <svg viewBox="0 0 100 40" className="w-full h-32 overflow-visible">
                    <motion.path
                      d="M 0,20 Q 12.5,5 25,20 T 50,20 T 75,20 T 100,20"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="1.5"
                      animate={{
                        d: [
                          "M 0,20 Q 12.5,5 25,20 T 50,20 T 75,20 T 100,20",
                          "M 0,20 Q 12.5,35 25,20 T 50,20 T 75,20 T 100,20",
                          "M 0,20 Q 12.5,5 25,20 T 50,20 T 75,20 T 100,20"
                        ]
                      }}
                      transition={{ repeat: Infinity, duration: 3.5, ease: "easeInOut" }}
                    />
                    <path
                      d="M 0,20 L 100,20"
                      stroke="rgba(255,255,255,0.06)"
                      strokeWidth="0.5"
                      strokeDasharray="2 2"
                    />
                  </svg>
                )}

                {/* Noise Visual Type */}
                {concept.visualType === 'noise' && (
                  <svg viewBox="0 0 100 40" className="w-full h-32 overflow-visible">
                    <motion.path
                      d="M 0,20 L 10,12 L 20,28 L 30,5 L 40,32 L 50,15 L 60,35 L 70,8 L 80,26 L 90,14 L 100,20"
                      fill="none"
                      stroke="#f59e0b"
                      strokeWidth="1"
                      animate={{
                        d: [
                          "M 0,20 L 10,12 L 20,28 L 30,5 L 40,32 L 50,15 L 60,35 L 70,8 L 80,26 L 90,14 L 100,20",
                          "M 0,20 L 10,24 L 20,10 L 30,32 L 40,8 L 50,28 L 60,12 L 70,30 L 80,10 L 90,24 L 100,20",
                          "M 0,20 L 10,12 L 20,28 L 30,5 L 40,32 L 50,15 L 60,35 L 70,8 L 80,26 L 90,14 L 100,20"
                        ]
                      }}
                      transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
                    />
                    <path
                      d="M 0,20 M 10,12 L 10,20 M 20,28 L 20,20 M 30,5 L 30,20 M 40,32 L 40,20 M 50,15 L 50,20 M 60,35 L 60,20"
                      stroke="rgba(245,158,11,0.22)"
                      strokeWidth="0.5"
                    />
                  </svg>
                )}

                {/* Embedding Visual Type */}
                {concept.visualType === 'embedding' && (
                  <div className="flex flex-col items-center gap-3">
                    <svg viewBox="0 0 100 40" className="w-48 h-12 overflow-visible">
                      <path
                        d="M 0,20 Q 10,5 20,30 T 40,15 T 60,25"
                        fill="none"
                        stroke="rgba(255,255,255,0.18)"
                        strokeWidth="1"
                      />
                      <motion.circle
                        cx="60" cy="25" r="2"
                        fill="#22d3ee"
                        animate={{ cx: [60, 85], cy: [25, 20], opacity: [1, 0] }}
                        transition={{ repeat: Infinity, duration: 1.8, ease: "easeOut" }}
                      />
                      <line x1="60" y1="25" x2="85" y2="20" stroke="#22d3ee" strokeWidth="0.5" strokeDasharray="2 2" opacity="0.3" />
                      <circle cx="85" cy="20" r="3.5" fill="#22d3ee" className="animate-pulse shadow-lg" />
                    </svg>
                    <span className="text-[10px] font-mono text-cyan-400">
                      {lang === 'es' ? 'Señal compleja (100 pts) ➜ Huella digital (1 pt)' : 'Complex Signal (100 pts) ➜ Fingerprint (1 pt)'}
                    </span>
                  </div>
                )}

                {/* Geometry/Separability Visual Type */}
                {concept.visualType === 'geometry' && (
                  <svg viewBox="0 0 40 40" className="w-32 h-32 overflow-visible">
                    {/* Basin A */}
                    <polygon points="5,5 15,3 22,12 8,14" fill="rgba(34,211,238,0.14)" stroke="#22d3ee" strokeWidth="0.3" strokeDasharray="1 1" />
                    <circle cx="10" cy="7" r="1.2" fill="#22d3ee" />
                    <circle cx="12" cy="11" r="1" fill="#22d3ee" />
                    <circle cx="16" cy="5" r="1" fill="#22d3ee" />

                    {/* Basin B */}
                    <polygon points="25,28 36,22 38,34 22,36" fill="rgba(167,139,250,0.14)" stroke="#a78bfa" strokeWidth="0.3" strokeDasharray="1 1" />
                    <circle cx="28" cy="30" r="1.2" fill="#a78bfa" />
                    <circle cx="32" cy="26" r="1" fill="#a78bfa" />
                    <circle cx="35" cy="32" r="1" fill="#a78bfa" />

                    <path d="M 12,11 L 28,30" stroke="rgba(255,255,255,0.06)" strokeWidth="0.4" strokeDasharray="2 2" />
                    <text x="18" y="22" fill="#f59e0b" fontSize="2.5" fontFamily="monospace" opacity="0.6">d(p, q)</text>
                  </svg>
                )}

                {/* Comparison Visual Type */}
                {concept.visualType === 'comparison' && (
                  <svg viewBox="0 0 100 40" className="w-full h-32 overflow-visible">
                    <path
                      d="M 0,20 Q 12.5,5 25,20 T 50,20 T 75,20 T 100,20"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="1.2"
                      opacity="0.8"
                    />
                    <motion.path
                      d="M 0,20 Q 12.5,5 25,20 T 50,20 T 75,20 T 100,20"
                      fill="none"
                      stroke="#8b5cf6"
                      strokeWidth="1.2"
                      animate={{ x: [0, 16, 0] }}
                      transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                    />
                  </svg>
                )}

                <p className="text-[10px] text-slate-500 font-mono mt-4 text-center px-6 leading-relaxed">
                  {concept.visual[isTeenagerMode ? 'simple' : 'advanced']?.[lang]}
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
