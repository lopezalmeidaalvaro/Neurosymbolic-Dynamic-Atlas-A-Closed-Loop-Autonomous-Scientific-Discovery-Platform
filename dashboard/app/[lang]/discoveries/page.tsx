import type { Metadata } from 'next';
import { FileCheck2 } from 'lucide-react';
import { hypotheses } from '@/data/hypotheses';
import { openQuestions } from '@/data/openQuestions';
import { scientificReferences } from '@/data/references';
import { researchFindings } from '@/data/researchFindings';
import { scientificMemory } from '@/data/scientificMemory';
import { DiscoveryCard } from '@/components/scientific/DiscoveryCard';
import { DiscoveryHero } from '@/components/scientific/DiscoveryHero';
import { EvidencePanel } from '@/components/scientific/EvidencePanel';
import { HypothesisTracker } from '@/components/scientific/HypothesisTracker';
import { InsightCard } from '@/components/scientific/InsightCard';
import { RelatedResearchPanel } from '@/components/scientific/RelatedResearchPanel';
import { ResearchNarrative } from '@/components/scientific/ResearchNarrative';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Discoveries' };

export default async function DiscoveriesPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const primaryFinding = researchFindings[0];

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28">
      <DiscoveryHero findings={researchFindings} hypotheses={hypotheses} lang={lang} />

      <ScrollReveal>
        <div className="mb-5">
          <p className="metric-label">{lang === 'es' ? 'Sistema de discoveries' : 'Discovery system'}</p>
          <h2 className="mt-2 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Hallazgos con evidencia, incertidumbre y siguiente paso' : 'Findings with evidence, uncertainty, and next step'}
          </h2>
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          {researchFindings.map((finding, index) => (
            <DiscoveryCard key={finding.id} finding={finding} lang={lang} index={index} />
          ))}
        </div>
      </ScrollReveal>

      {primaryFinding && (
        <ScrollReveal className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
          <EvidencePanel finding={primaryFinding} lang={lang} />
          <InsightCard finding={primaryFinding} references={scientificReferences} lang={lang} />
        </ScrollReveal>
      )}

      <ScrollReveal>
        <ResearchNarrative entries={scientificMemory} lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <HypothesisTracker hypotheses={hypotheses} openQuestions={openQuestions} lang={lang} />
      </ScrollReveal>

      <ScrollReveal className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <GlassPanel density="spacious">
          <div className="mb-5 flex items-center gap-3">
            <FileCheck2 size={17} className="text-cyan-100" />
            <div>
              <p className="metric-label">{lang === 'es' ? 'Narrativa obligatoria' : 'Required narrative'}</p>
              <h2 className="mt-1 text-2xl font-semibold text-white/90">
                {lang === 'es' ? 'El ciclo completo de descubrimiento' : 'The full discovery cycle'}
              </h2>
            </div>
          </div>
          <div className="space-y-3">
            {[
              lang === 'es' ? 'Generamos sistemas dinamicos' : 'We generate dynamical systems',
              lang === 'es' ? 'Introducimos ruido y perturbaciones' : 'We introduce noise and perturbations',
              lang === 'es' ? 'Probamos multiples modelos' : 'We test multiple models',
              lang === 'es' ? 'Medimos degradacion y robustez' : 'We measure degradation and robustness',
              lang === 'es' ? 'Observamos invariancias geometricas' : 'We observe geometric invariances',
              lang === 'es' ? 'Registramos descubrimientos' : 'We register discoveries',
              lang === 'es' ? 'Refinamos hipotesis' : 'We refine hypotheses',
            ].map((step, index) => (
              <div key={step} className="flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.03] p-3">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-cyan-100/16 bg-cyan-100/[0.06] text-xs text-cyan-100">
                  {index + 1}
                </span>
                <span className="text-sm text-slate-300/78">{step}</span>
              </div>
            ))}
          </div>
        </GlassPanel>

        <RelatedResearchPanel references={scientificReferences} lang={lang} />
      </ScrollReveal>
    </FocusContainer>
  );
}
