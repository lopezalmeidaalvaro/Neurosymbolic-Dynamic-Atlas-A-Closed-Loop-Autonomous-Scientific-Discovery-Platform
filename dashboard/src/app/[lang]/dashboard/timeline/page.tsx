import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { GitBranch, Orbit } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { timelineEvents } from '@/data/timelineData';
import { Reveal } from '@/components/motion/Reveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import { TimelineClient } from './TimelineClient';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Timeline' };

export default async function TimelinePage({
  params,
}: {
  params: Promise<{ lang: Language }>;
}) {
  const { lang } = await params;
  const dict = getDictionary(lang);

  return (
    <FocusContainer size="lg" className="space-y-9 pb-28">
      <ScientificSurface grid className="p-6 sm:p-8">
        <Reveal>
          <span className="research-kicker mb-5">
            <GitBranch size={13} />
            {dict.timeline.title}
          </span>
          <h1 className="cinematic-heading max-w-4xl text-4xl sm:text-5xl lg:text-6xl">
            <Balancer>
              {lang === 'es'
                ? 'La trayectoria experimental del atlas.'
                : 'The experimental trajectory of the atlas.'}
            </Balancer>
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/72">
            {lang === 'es'
              ? 'Una lectura cronologica de fases, validaciones e hitos de investigacion que mantiene el contexto sin convertir el sistema en un tablero administrativo.'
              : 'A chronological reading of phases, validations, and research milestones that preserves context without turning the system into an admin board.'}
          </p>
          <div className="mt-7 flex items-center gap-3 text-xs text-slate-400">
            <Orbit size={14} className="text-cyan-100/70" />
            <span>{lang === 'es' ? 'Ritmo de descubrimiento' : 'Discovery cadence'}</span>
          </div>
        </Reveal>
      </ScientificSurface>

      <TimelineClient
        events={timelineEvents}
        lang={lang}
        labels={{
          completed: dict.timeline.completed,
          active: dict.timeline.active,
          planned: dict.timeline.planned,
        }}
      />
    </FocusContainer>
  );
}
