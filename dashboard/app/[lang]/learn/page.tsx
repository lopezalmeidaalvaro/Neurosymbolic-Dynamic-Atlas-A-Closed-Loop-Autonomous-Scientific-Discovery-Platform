import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { BookOpen, Brain, Compass, Microscope } from 'lucide-react';
import { educationalConcepts, guidedLearningSteps, scientificStory } from '@/data/learningData';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { ExplainLikeIm15 } from '@/components/educational/ExplainLikeIm15';
import { GuidedConceptFlow } from '@/components/educational/GuidedConceptFlow';
import { InteractiveAnalogy } from '@/components/educational/InteractiveAnalogy';
import { ProgressiveExplanation } from '@/components/educational/ProgressiveExplanation';
import { ScientificStory } from '@/components/educational/ScientificStory';
import { StepByStepDiscovery } from '@/components/educational/StepByStepDiscovery';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { ConceptBreakdown } from '@/components/scientific/ConceptBreakdown';
import { InteractiveEquation } from '@/components/scientific/InteractiveEquation';
import { MethodologyExplorer } from '@/components/scientific/MethodologyExplorer';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Learn' };

export default async function LearnPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  const embedding = educationalConcepts.find((concept) => concept.id === 'embedding')!;
  const autocorrelation = educationalConcepts.find((concept) => concept.id === 'autocorrelation')!;
  const chaos = educationalConcepts.find((concept) => concept.id === 'chaos')!;
  const geometry = educationalConcepts.find((concept) => concept.id === 'geometric-separability')!;

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28">
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(125,211,252,0.12),transparent_32%)]" />
        <div className="grid min-h-[360px] gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <Reveal className="max-w-4xl self-center">
            <span className="research-kicker mb-6">
              <BookOpen size={13} />
              {dict.nav.learn}
            </span>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl">
              <Balancer>
                {lang === 'es'
                  ? 'Aprende el experimento sin perder el rigor.'
                  : 'Learn the experiment without losing the rigor.'}
              </Balancer>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300/76 sm:text-lg">
              <Balancer>
                {lang === 'es'
                  ? 'Una ruta visual para entender series temporales, caos, ruido, embeddings y separabilidad geometrica con dos niveles cognitivos.'
                  : 'A visual route for understanding time series, chaos, noise, embeddings, and geometric separability with two cognitive levels.'}
              </Balancer>
            </p>
          </Reveal>

          <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              { icon: Brain, label: lang === 'es' ? 'Modo simple' : 'Simple mode', value: lang === 'es' ? 'Narrativo' : 'Narrative' },
              { icon: Microscope, label: lang === 'es' ? 'Modo avanzado' : 'Advanced mode', value: lang === 'es' ? 'Tecnico' : 'Technical' },
              { icon: Compass, label: lang === 'es' ? 'Conceptos' : 'Concepts', value: String(educationalConcepts.length) },
              { icon: BookOpen, label: lang === 'es' ? 'Ruta' : 'Path', value: `${guidedLearningSteps.length} ${lang === 'es' ? 'pasos' : 'steps'}` },
            ].map(({ icon: Icon, label, value }) => (
              <GlassPanel key={label} density="compact" className="rounded-2xl">
                <Icon size={16} className="text-cyan-100" />
                <p className="metric-label mt-4">{label}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
              </GlassPanel>
            ))}
          </Reveal>
        </div>
      </ScientificSurface>

      <ScrollReveal>
        <ScientificStory steps={scientificStory} lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <StepByStepDiscovery steps={guidedLearningSteps} lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <div className="mb-5">
          <p className="metric-label">{lang === 'es' ? 'Mapa de conceptos' : 'Concept map'}</p>
          <h2 className="mt-2 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Lo que necesitas entender' : 'What you need to understand'}
          </h2>
        </div>
        <GuidedConceptFlow concepts={educationalConcepts} lang={lang} />
      </ScrollReveal>

      <ScrollReveal className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <ExplainLikeIm15 title={embedding.title} text={embedding.short} example={embedding.example} lang={lang} />
        <InteractiveAnalogy title={chaos.title} analogy={chaos.analogy} technical={chaos.technical} lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <ProgressiveExplanation concept={embedding} lang={lang} />
      </ScrollReveal>

      <ScrollReveal className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <InteractiveEquation
          title={autocorrelation.title}
          formula={autocorrelation.formula ?? ''}
          lang={lang}
          terms={[
            {
              symbol: 'R(tau)',
              label: { en: 'Autocorrelation score', es: 'Puntuacion de autocorrelacion' },
              explanation: {
                en: 'A high value means the signal still resembles itself after the chosen delay.',
                es: 'Un valor alto significa que la senal aun se parece a si misma tras el retardo elegido.',
              },
            },
            {
              symbol: 'tau',
              label: { en: 'Lag', es: 'Retardo' },
              explanation: {
                en: 'The number of steps we shift the signal before comparing it with itself.',
                es: 'El numero de pasos que desplazamos la senal antes de compararla consigo misma.',
              },
            },
            {
              symbol: 'x(t)',
              label: { en: 'Signal value', es: 'Valor de la senal' },
              explanation: {
                en: 'The measured value of the system at a specific moment in time.',
                es: 'El valor medido del sistema en un momento concreto.',
              },
            },
          ]}
        />
        <ConceptBreakdown concept={geometry} lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <MethodologyExplorer steps={guidedLearningSteps} lang={lang} />
      </ScrollReveal>
    </FocusContainer>
  );
}
