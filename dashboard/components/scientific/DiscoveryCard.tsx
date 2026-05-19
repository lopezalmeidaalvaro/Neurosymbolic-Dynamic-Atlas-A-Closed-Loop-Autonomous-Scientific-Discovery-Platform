'use client';

import { motion } from 'framer-motion';
import { Microscope, Network, ShieldCheck } from 'lucide-react';
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

export function DiscoveryCard({ finding, lang, index = 0 }: DiscoveryCardProps) {
  const { complexityMode } = useAppStore();

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
        </div>
      </GlassPanel>
    </motion.div>
  );
}
