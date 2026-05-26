import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { CheckCircle2, Circle, CircleDot, Map, SignalHigh } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { roadmapItems } from '@/data/roadmapData';
import { cn } from '@/lib/utils/cn';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language, RoadmapStatus } from '@/types';

export const metadata: Metadata = { title: 'Roadmap' };

const STATUS_CONFIG: Record<RoadmapStatus, {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  panel: 'success' | 'active' | 'neutral';
  badge: string;
  marker: string;
  label: (d: ReturnType<typeof getDictionary>) => string;
}> = {
  done: {
    icon: CheckCircle2,
    panel: 'success',
    badge: 'border-emerald-100/18 bg-emerald-100/10 text-emerald-100/80',
    marker: 'bg-emerald-200 text-emerald-200',
    label: (d) => d.roadmap.done,
  },
  'in-progress': {
    icon: CircleDot,
    panel: 'active',
    badge: 'border-cyan-100/18 bg-cyan-100/10 text-cyan-100/80',
    marker: 'bg-cyan-200 text-cyan-200',
    label: (d) => d.roadmap.inProgress,
  },
  planned: {
    icon: Circle,
    panel: 'neutral',
    badge: 'border-white/[0.09] bg-white/[0.04] text-slate-400',
    marker: 'bg-slate-500 text-slate-500',
    label: (d) => d.roadmap.planned,
  },
};

const PRIORITY_MAP = {
  high: 'text-red-200',
  medium: 'text-amber-200',
  low: 'text-slate-500',
};

export default async function RoadmapPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);
  const groups: RoadmapStatus[] = ['in-progress', 'planned', 'done'];

  return (
    <FocusContainer size="xl" className="space-y-9 pb-28">
      <ScientificSurface grid className="p-6 sm:p-8">
        <Reveal>
          <span className="research-kicker mb-5">
            <Map size={13} />
            {dict.roadmap.title}
          </span>
          <h1 className="cinematic-heading max-w-4xl text-4xl sm:text-5xl lg:text-6xl">
            <Balancer>
              {lang === 'es'
                ? 'Una ruta de investigacion, no un tablero de tareas.'
                : 'A research trajectory, not a task board.'}
            </Balancer>
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/72">
            {lang === 'es'
              ? 'Fases planificadas y completadas del observatorio cientifico, agrupadas por madurez experimental.'
              : 'Planned and completed phases of the scientific observatory, grouped by experimental maturity.'}
          </p>
        </Reveal>
      </ScientificSurface>

      <ScrollReveal className="grid grid-cols-1 gap-5 md:grid-cols-3">
        {groups.map((status) => {
          const cfg = STATUS_CONFIG[status];
          const Icon = cfg.icon;
          const items = roadmapItems.filter((r) => r.status === status);

          return (
            <GlassPanel key={status} tone={cfg.panel} density="normal" className="h-full">
              <div className="mb-5 flex items-center gap-3">
                <Icon size={16} className={status === 'done' ? 'text-emerald-100' : status === 'in-progress' ? 'text-cyan-100' : 'text-slate-500'} />
                <div className="min-w-0">
                  <p className="metric-label truncate">{cfg.label(dict)}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {items.length} {lang === 'es' ? 'elementos' : 'items'}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="relative rounded-2xl border border-white/[0.08] bg-white/[0.035] p-4 transition-colors hover:bg-white/[0.055]"
                  >
                    <div className={cn('absolute left-4 top-4 h-2 w-2 rounded-full shadow-[0_0_18px_currentColor]', cfg.marker)} />
                    <div className="pl-5">
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="text-sm font-semibold leading-snug text-slate-100">{item.title[lang]}</h3>
                        <span className={cn('shrink-0 text-[10px] font-semibold uppercase tracking-[0.12em]', PRIORITY_MAP[item.priority])}>
                          {dict.roadmap.priority[item.priority]}
                        </span>
                      </div>
                      <p className="mt-3 text-xs leading-6 text-slate-400">{item.description[lang]}</p>
                      <div className="mt-4 flex items-center justify-between gap-3">
                        <span className={cn('rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em]', cfg.badge)}>
                          {cfg.label(dict)}
                        </span>
                        {item.eta && <span className="text-[10px] text-slate-500">{item.eta}</span>}
                      </div>
                    </div>
                  </div>
                ))}

                {items.length === 0 && (
                  <div className="rounded-2xl border border-dashed border-white/[0.08] p-6 text-center">
                    <SignalHigh size={16} className="mx-auto text-slate-600" />
                    <p className="mt-2 text-xs text-slate-500">{lang === 'es' ? 'Sin elementos' : 'No items'}</p>
                  </div>
                )}
              </div>
            </GlassPanel>
          );
        })}
      </ScrollReveal>
    </FocusContainer>
  );
}
