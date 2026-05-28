import Balancer from 'react-wrap-balancer';
import { BrainCircuit, DatabaseZap, Sparkles } from 'lucide-react';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { Reveal } from '@/components/motion/Reveal';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language, ResearchFinding, ResearchHypothesis } from '@/types';

interface DiscoveryHeroProps {
  findings: ResearchFinding[];
  hypotheses: ResearchHypothesis[];
  lang: Language;
}

export function DiscoveryHero({ findings, hypotheses, lang }: DiscoveryHeroProps) {
  const validated = findings.filter((finding) => finding.state === 'validated').length;
  const avgConfidence = Math.round(
    findings.reduce((sum, finding) => sum + finding.metrics.confidence, 0) / Math.max(findings.length, 1)
  );

  return (
    <ScientificSurface grid className="min-h-[460px] p-6 sm:p-8 lg:p-10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_74%_22%,rgba(34,211,238,0.14),transparent_34%)]" />
      <div className="grid min-h-[380px] gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
        <Reveal className="max-w-4xl self-center">
          <span className="research-kicker mb-6">
            <Sparkles size={13} />
            {lang === 'es' ? 'Observatorio de descubrimientos' : 'Discovery observatory'}
          </span>
          <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl">
            <Balancer>
              {lang === 'es'
                ? 'La investigacion como memoria viva.'
                : 'Research as living memory.'}
            </Balancer>
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300/76 sm:text-lg">
            <Balancer>
              {lang === 'es'
                ? 'Hallazgos, evidencia, hipotesis e incertidumbre organizados como una narrativa cientifica verificable.'
                : 'Findings, evidence, hypotheses, and uncertainty organized as a verifiable scientific narrative.'}
            </Balancer>
          </p>
        </Reveal>

        <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
          {[
            { icon: DatabaseZap, label: lang === 'es' ? 'Findings' : 'Findings', value: findings.length, suffix: '' },
            { icon: Sparkles, label: lang === 'es' ? 'Validados' : 'Validated', value: validated, suffix: '' },
            { icon: BrainCircuit, label: lang === 'es' ? 'Hipotesis' : 'Hypotheses', value: hypotheses.length, suffix: '' },
            { icon: DatabaseZap, label: lang === 'es' ? 'Confianza media' : 'Avg confidence', value: avgConfidence, suffix: '%' },
          ].map(({ icon: Icon, label, value, suffix }) => (
            <GlassPanel key={label} density="compact" className="rounded-2xl">
              <Icon size={16} className="text-cyan-100" />
              <p className="metric-label mt-4">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                <AnimatedCounter value={value} suffix={suffix} />
              </p>
            </GlassPanel>
          ))}
        </Reveal>
      </div>
    </ScientificSurface>
  );
}
