import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { Activity, CheckCircle2, Clock, GitCommit, Microscope, RadioTower, Zap } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { kpiEntries } from '@/data/benchmarkData';
import { projectInfo } from '@/data/projectInfo';
import { timelineEvents } from '@/data/timelineData';
import { KPICard } from '@/components/dashboard/KPICard';
import { AnimatedCounter } from '@/components/motion/AnimatedCounter';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Overview' };

export default async function DashboardPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  const completedEvents = timelineEvents.filter((e) => e.status === 'completed');
  const activeEvents = timelineEvents.filter((e) => e.status === 'active');

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28">
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_18%,rgba(45,212,191,0.13),transparent_34%)]" />
        <div className="grid min-h-[360px] gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <Reveal className="max-w-3xl self-center">
            <span className="research-kicker mb-6">
              <RadioTower size={13} />
              {lang === 'es' ? 'Observatorio automatizado' : 'Automated observatory'}
            </span>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl">
              <Balancer>{projectInfo.name}</Balancer>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300/76 sm:text-lg">
              <Balancer>{projectInfo.tagline[lang]}</Balancer>
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <span className="rounded-full border border-emerald-100/18 bg-emerald-100/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-100/80">
                {projectInfo.status}
              </span>
              <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-3 py-1.5 text-xs text-slate-300">
                v{projectInfo.version}
              </span>
              <span className="rounded-full border border-cyan-100/16 bg-cyan-100/[0.06] px-3 py-1.5 text-xs text-cyan-100/80">
                {lang === 'es' ? 'Sistema experimental vivo' : 'Living experimental system'}
              </span>
            </div>
          </Reveal>

          <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              {
                icon: CheckCircle2,
                label: lang === 'es' ? 'Fases completadas' : 'Phases completed',
                value: projectInfo.completedPhases,
                suffix: ` / ${projectInfo.totalPhases}`,
                tone: 'text-emerald-100',
              },
              {
                icon: GitCommit,
                label: lang === 'es' ? 'Nodos experimentales' : 'Experimental nodes',
                value: 16,
                suffix: '',
                tone: 'text-sky-100',
              },
              {
                icon: Zap,
                label: lang === 'es' ? 'Ventaja velocidad' : 'Speed advantage',
                value: 79,
                suffix: 'x',
                tone: 'text-cyan-100',
              },
              {
                icon: Clock,
                label: lang === 'es' ? 'Estado mision' : 'Mission state',
                value: null,
                suffix: lang === 'es' ? 'Activo' : 'Active',
                tone: 'text-violet-100',
              },
            ].map(({ icon: Icon, label, value, suffix, tone }) => (
              <GlassPanel key={label} density="compact" className="rounded-2xl">
                <Icon size={16} className={tone} />
                <p className="metric-label mt-4">{label}</p>
                <p className="mt-2 text-2xl font-semibold tabular-nums text-white">
                  {value === null ? suffix : <AnimatedCounter value={value} suffix={suffix} />}
                </p>
              </GlassPanel>
            ))}
          </Reveal>
        </div>
      </ScientificSurface>

      <ScrollReveal>
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <p className="metric-label">{lang === 'es' ? 'Senales de mision' : 'Mission signals'}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white/90">{lang === 'es' ? 'Estado computacional' : 'Computational state'}</h2>
          </div>
          <Microscope className="text-slate-500" size={20} />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiEntries.map((kpi, i) => (
            <KPICard key={kpi.id} kpi={kpi} lang={lang} index={i} />
          ))}
        </div>
      </ScrollReveal>

      <ScrollReveal className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <GlassPanel density="spacious">
          <p className="metric-label">{lang === 'es' ? 'Declaracion de mision' : 'Mission statement'}</p>
          <h2 className="mt-3 text-3xl font-semibold leading-tight text-white/92">
            {lang === 'es' ? 'Un sistema operativo para descubrir estructura dinamica.' : 'An operating system for discovering dynamic structure.'}
          </h2>
          <p className="mt-5 leading-8 text-slate-300/72">
            {projectInfo.description[lang]}
          </p>
          <div className="mt-7 grid grid-cols-3 gap-3 text-center">
            {[
              [completedEvents.length, lang === 'es' ? 'validado' : 'validated'],
              [activeEvents.length, lang === 'es' ? 'activo' : 'active'],
              [timelineEvents.length, lang === 'es' ? 'eventos' : 'events'],
            ].map(([value, label]) => (
              <div key={label} className="rounded-2xl border border-white/[0.08] bg-white/[0.035] p-3">
                <p className="text-2xl font-semibold text-white">{value}</p>
                <p className="mt-1 text-[10px] uppercase tracking-[0.14em] text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </GlassPanel>

        <GlassPanel density="normal" tone="active">
          <div className="mb-5 flex items-center gap-3">
            <Activity size={17} className="text-cyan-100" />
            <div>
              <p className="metric-label">{lang === 'es' ? 'Actividad reciente' : 'Recent activity'}</p>
              <h2 className="mt-1 text-xl font-semibold text-white/90">{lang === 'es' ? 'Bitacora de investigacion' : 'Research trace'}</h2>
            </div>
          </div>
          <div className="space-y-3">
            {[...completedEvents].slice(-4).reverse().map((event) => (
              <div key={event.id} className="grid gap-4 rounded-2xl border border-white/[0.07] bg-white/[0.03] p-4 sm:grid-cols-[auto_1fr_auto]">
                <div className="mt-1 h-2 w-2 rounded-full bg-emerald-200 shadow-[0_0_18px_rgba(167,243,208,0.45)]" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-100">{event.title[lang]}</p>
                  <p className="mt-1 line-clamp-1 text-xs text-slate-400">{event.description[lang]}</p>
                </div>
                <span className="text-xs text-slate-500">{event.date}</span>
              </div>
            ))}

            {activeEvents.map((event) => (
              <div key={event.id} className="grid gap-4 rounded-2xl border border-cyan-100/18 bg-cyan-100/[0.055] p-4 sm:grid-cols-[auto_1fr_auto]">
                <div className="mt-1 h-2 w-2 rounded-full bg-cyan-100 shadow-[0_0_18px_rgba(186,230,253,0.55)]" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-cyan-50">{event.title[lang]}</p>
                  <p className="mt-1 line-clamp-1 text-xs text-cyan-100/55">{event.description[lang]}</p>
                </div>
                <span className="text-xs text-cyan-100/60">{lang === 'es' ? 'Activo' : 'Active'}</span>
              </div>
            ))}
          </div>
        </GlassPanel>
      </ScrollReveal>
    </FocusContainer>
  );
}
