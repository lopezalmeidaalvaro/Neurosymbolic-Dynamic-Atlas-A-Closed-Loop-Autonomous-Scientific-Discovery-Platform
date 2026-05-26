'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Microscope, Network, ShieldCheck, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { ConfidenceBadge } from './ConfidenceBadge';
import type { DiscoveryState, Language, ResearchFinding } from '@/types';

interface DiscoveryCardProps {
  finding: ResearchFinding;
  lang: Language;
  index?: number;
}

const STATE_PANEL: Record<DiscoveryState, 'neutral' | 'active' | 'success' | 'warning'> = {
  validated: 'active',
  observed: 'neutral',
  hypothesis: 'neutral',
  uncertain: 'warning',
  rejected: 'neutral',
};

const STATE_RING: Record<DiscoveryState, string> = {
  validated: 'bg-[radial-gradient(circle_at_50%_0%,rgba(34,211,238,0.16),transparent_44%)]',
  observed: 'bg-[radial-gradient(circle_at_50%_0%,rgba(96,165,250,0.13),transparent_44%)]',
  hypothesis: 'bg-[radial-gradient(circle_at_50%_0%,rgba(167,139,250,0.15),transparent_44%)]',
  uncertain: 'bg-[radial-gradient(circle_at_50%_0%,rgba(251,191,36,0.13),transparent_44%)]',
  rejected: 'bg-[radial-gradient(circle_at_50%_0%,rgba(248,113,113,0.10),transparent_44%)]',
};

const ELI15_ANALOGIES: Record<string, { es: string; en: string }> = {
  'embedding-v2-speed-parity': {
    es: 'Es como tomar una huella dactilar a una canción en lugar de analizar cada nota de audio por horas. Logramos identificar la familia del sistema caos de forma inmediata sin perder nada de precisión y con una velocidad 79 veces mayor.',
    en: 'It\'s like taking a song\'s digital fingerprint instead of analyzing every single audio wave for hours. We can recognize complex chaos patterns instantly without losing any accuracy, running 79x faster.'
  },
  'latent-geometry-separability': {
    es: 'Es como cuando ordenas libros en una estantería: las novelas de misterio van juntas en una sección y los libros de cocina en otra. Descubrimos que las diferentes señales de la física se agrupan de forma ordenada y espacial en nuestro mapa virtual según su comportamiento interno.',
    en: 'It\'s like arranging books in a library: mystery novels naturally end up on one shelf, and cooking books on another. We discovered that chaotic systems group themselves beautifully in our virtual map based on their physics.'
  },
  'feigenbaum-structural-signal': {
    es: 'Es como un grifo que gotea: primero cae una gota a ritmo regular. Si aumentas la presión, empieza a gotear de dos en dos, luego de cuatro en cuatro, hasta que de repente se vuelve un caos absoluto. El sistema redescubrió de forma completamente autónoma esta famosa constante universal del caos de la física.',
    en: 'It\'s like a dripping faucet: first it drips steadily. If you increase the pressure, it drips in twos, then fours, until it suddenly breaks into absolute chaos. Our system rediscovered this universal constant of chaotic physics completely on its own!'
  },
  'structural-noise-boundary': {
    es: 'Es como probar un coche de carreras súper potente pero solo en una pista lisa de laboratorio. Aún no hemos probado cómo se comportará en el barro y bajo la tormenta. Es decir, sabemos y documentamos con total honestidad dónde terminan los límites y certezas de nuestro propio software.',
    en: 'It\'s like testing a fast racecar but only on a smooth laboratory track. We don\'t yet know how it will handle mud, gravel, or a heavy storm. We mapped out and documented exactly where our confidence boundaries stop.'
  }
};

function renderFormattedAnalogy(text: string, lang: string) {
  const terms = [
    { key: lang === 'es' ? 'Atractor de Lorenz' : 'Lorenz attractor', id: 'chaos' },
    { key: lang === 'es' ? 'Espacio Latente' : 'Latent space', id: 'embedding' },
    { key: lang === 'es' ? 'Serie temporal' : 'Time series', id: 'time-series' },
    { key: lang === 'es' ? 'caos' : 'chaos', id: 'chaos' },
  ];

  let elements: React.ReactNode[] = [text];

  terms.forEach(({ key, id }) => {
    elements = elements.flatMap((el) => {
      if (typeof el !== 'string') return el;
      const parts = el.split(new RegExp(`(${key})`, 'gi'));
      return parts.map((part, index) => {
        if (part.toLowerCase() === key.toLowerCase()) {
          return (
            <Link
              key={index}
              href={`/${lang}/learn#concept-${id}`}
              className="text-cyan-300 font-semibold underline decoration-cyan-400/40 hover:decoration-cyan-400/80 transition-all decoration-2 cursor-pointer inline-flex items-center gap-0.5 hover:text-cyan-200"
            >
              {part}
            </Link>
          );
        }
        return part;
      });
    });
  });

  return elements;
}

export function DiscoveryCard({ finding, lang, index = 0 }: DiscoveryCardProps) {
  const { complexityMode, isTeenagerMode } = useAppStore();
  const [showRigor, setShowRigor] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 18, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.65, delay: index * 0.06, ease: [0.22, 1, 0.36, 1] }}
    >
      <GlassPanel density="normal" tone={STATE_PANEL[finding.state]} className="h-full">
        <div aria-hidden className={cn('absolute inset-0', STATE_RING[finding.state])} />
        <div className="relative">
          <div className="mb-5 flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="metric-label">{lang === 'es' ? 'Discovery' : 'Discovery'}</p>
              <h3 className="mt-2 text-xl font-semibold leading-tight text-white/92">{finding.title[lang]}</h3>
            </div>
            <ConfidenceBadge state={finding.state} lang={lang} />
          </div>

          {/* Teenager ELI15 Section */}
          {isTeenagerMode && (
            <div className="mb-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] ELI15">
              <div className="flex items-center gap-2 mb-2 text-emerald-400 text-[10px] font-semibold uppercase tracking-wider">
                <Sparkles size={12} className="animate-pulse" />
                <span>{lang === 'es' ? 'Explicación Sencilla (ELI15)' : 'Simple Explanation (ELI15)'}</span>
              </div>
              <p className="text-sm leading-relaxed text-emerald-50/90 font-medium">
                {renderFormattedAnalogy(ELI15_ANALOGIES[finding.id]?.[lang] || finding.summary.simple[lang], lang)}
              </p>

              <button
                type="button"
                onClick={() => setShowRigor(!showRigor)}
                className="mt-4 flex items-center gap-1.5 text-xs text-emerald-400/70 hover:text-emerald-400 transition-colors font-medium border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 rounded-xl cursor-pointer"
              >
                {showRigor ? (
                  <>
                    <ChevronUp size={12} />
                    <span>{lang === 'es' ? 'Ocultar rigor científico' : 'Hide scientific rigor'}</span>
                  </>
                ) : (
                  <>
                    <ChevronDown size={12} />
                    <span>{lang === 'es' ? 'Ver rigor científico' : 'Show scientific rigor'}</span>
                  </>
                )}
              </button>
            </div>
          )}

          <AnimatePresence initial={false}>
            {(!isTeenagerMode || showRigor) && (
              <motion.div
                initial={isTeenagerMode ? { height: 0, opacity: 0 } : false}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                className={cn("overflow-hidden", isTeenagerMode && "pt-2 border-t border-white/[0.06]")}
              >
                <p className="text-sm leading-7 text-slate-300/76">{finding.summary[complexityMode][lang]}</p>

                <div className="mt-5 grid grid-cols-3 gap-2">
                  {[
                    { icon: Microscope, label: lang === 'es' ? 'Significancia' : 'Significance', value: finding.metrics.significance },
                    { icon: ShieldCheck, label: lang === 'es' ? 'Confianza' : 'Confidence', value: finding.metrics.confidence },
                    { icon: Network, label: lang === 'es' ? 'Reproducible' : 'Reproducible', value: finding.metrics.reproducibility },
                  ].map(({ icon: Icon, label, value }) => (
                    <div key={label} className="rounded-2xl border border-white/[0.08] bg-white/[0.035] p-3">
                      <Icon size={14} className="text-cyan-100/75" />
                      <p className="mt-3 text-[10px] uppercase tracking-[0.12em] text-slate-500">{label}</p>
                      <p className="mt-1 text-lg font-semibold text-white">
                        <AnimatedCounter value={value} suffix="%" />
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-5 rounded-2xl border border-white/[0.08] bg-black/20 p-4">
                  <p className="metric-label">{lang === 'es' ? 'Por que importa' : 'Why it matters'}</p>
                  <p className="mt-2 text-sm leading-7 text-slate-300/74">{finding.whyItMatters[complexityMode][lang]}</p>
                </div>

                <div className="mt-4 flex flex-wrap gap-1.5">
                  {finding.linkedExperiments.map((experiment) => (
                    <span key={experiment} className="rounded-full border border-white/[0.07] bg-white/[0.03] px-2 py-1 text-[10px] text-slate-400">
                      {experiment}
                    </span>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </GlassPanel>
    </motion.div>
  );
}
