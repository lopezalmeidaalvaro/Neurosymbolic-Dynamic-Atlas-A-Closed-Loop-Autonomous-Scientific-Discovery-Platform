import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { FileClock, Sparkles } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { scientificLog } from '@/data/scientificLog';
import { ScientificLog } from '@/components/scientific/ScientificLog';
import { Reveal } from '@/components/motion/Reveal';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Scientific Log' };

export default async function LogPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  const insights = scientificLog.filter((e) => e.severity === 'insight').length;
  const successes = scientificLog.filter((e) => e.severity === 'success').length;

  return (
    <FocusContainer size="lg" className="space-y-8 pb-28">
      <ScientificSurface grid className="p-6 sm:p-8">
        <Reveal>
          <span className="research-kicker mb-5">
            <FileClock size={13} />
            {dict.log.title}
          </span>
          <h1 className="cinematic-heading max-w-4xl text-4xl sm:text-5xl lg:text-6xl">
            <Balancer>
              {lang === 'es'
                ? 'La memoria experimental del sistema.'
                : 'The experimental memory of the system.'}
            </Balancer>
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/72">
            {lang === 'es'
              ? 'Registro cronologico de ejecucion, validacion e insights del pipeline de investigacion.'
              : 'Chronological record of execution, validation, and insights from the research pipeline.'}
          </p>
        </Reveal>
      </ScientificSurface>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: dict.log.severity.insight, value: insights, tone: 'text-violet-100' },
          { label: dict.log.severity.success, value: successes, tone: 'text-emerald-100' },
          { label: lang === 'es' ? 'Total' : 'Total', value: scientificLog.length, tone: 'text-slate-100' },
        ].map((item, index) => (
          <Reveal key={item.label} delay={index * 0.06}>
            <GlassPanel density="compact" className="rounded-2xl">
              <Sparkles size={15} className={item.tone} />
              <p className="metric-label mt-4">{item.label}</p>
              <p className="mt-2 text-3xl font-semibold text-white">
                <AnimatedCounter value={item.value} />
              </p>
            </GlassPanel>
          </Reveal>
        ))}
      </div>

      <ScientificLog entries={[...scientificLog].reverse()} lang={lang} />
    </FocusContainer>
  );
}
