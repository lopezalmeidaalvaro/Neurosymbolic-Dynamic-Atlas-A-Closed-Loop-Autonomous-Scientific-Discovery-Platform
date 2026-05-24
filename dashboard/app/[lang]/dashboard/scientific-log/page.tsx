import type { Metadata } from 'next';
import { Activity, BrainCircuit, Database, FlaskConical, ShieldCheck, Terminal } from 'lucide-react';
import { hypotheses } from '@/data/hypotheses';
import { openQuestions } from '@/data/openQuestions';
import { LiveTelemetryConsole } from '@/components/scientific/LiveTelemetryConsole';
import { HypothesisTracker } from '@/components/scientific/HypothesisTracker';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language } from '@/types';

export const metadata: Metadata = {
  title: 'Autonomous Scientist',
};

const AGENT_METRICS = [
  {
    icon: BrainCircuit,
    label: { en: 'Reasoner', es: 'Razonador' },
    value: 'LLM',
    detail: { en: 'Hypothesis generation', es: 'Generacion de hipotesis' },
  },
  {
    icon: FlaskConical,
    label: { en: 'Protocol', es: 'Protocolo' },
    value: 'Falsify',
    detail: { en: 'Every claim needs a test', es: 'Cada afirmacion exige prueba' },
  },
  {
    icon: ShieldCheck,
    label: { en: 'Executor', es: 'Ejecutor' },
    value: 'Sandbox',
    detail: { en: 'Isolated code runs', es: 'Ejecuciones aisladas' },
  },
  {
    icon: Database,
    label: { en: 'Memory', es: 'Memoria' },
    value: 'KG/SQL',
    detail: { en: 'Persistent scientific state', es: 'Estado cientifico persistente' },
  },
];

export default async function ScientificLogPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = (rawLang === 'es' ? 'es' : 'en') as Language;

  return (
    <div className="min-h-screen bg-gray-950 text-slate-100">
      <FocusContainer size="xl" className="space-y-8 pb-28">
        <section className="relative overflow-hidden rounded-[1.5rem] border border-emerald-400/15 bg-gray-950 px-5 py-6 shadow-[0_24px_90px_rgba(0,0,0,0.42)] sm:px-8 lg:px-10">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(16,185,129,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.08)_1px,transparent_1px)] bg-[size:38px_38px] opacity-30" />
          <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl" />
          <div className="absolute -bottom-32 left-1/3 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />

          <div className="relative z-10 grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.24em] text-emerald-200">
                <Terminal size={13} />
                {lang === 'es' ? 'Ciclo autonomo online' : 'Autonomous loop online'}
              </div>

              <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
                {lang === 'es' ? 'Autonomous Scientist Control Room' : 'Autonomous Scientist Control Room'}
              </h1>

              <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/76">
                {lang === 'es'
                  ? 'Panel operativo para observar hipotesis vivas, telemetria de ejecucion, criterios de falsacion y memoria experimental del agente neurosimbolico.'
                  : 'Operational panel for observing live hypotheses, execution telemetry, falsification criteria, and experimental memory from the neurosymbolic agent.'}
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-400/15 bg-black/40 p-4 font-mono shadow-inner">
              <div className="mb-3 flex items-center justify-between text-[11px] uppercase tracking-[0.22em] text-emerald-200/80">
                <span>{lang === 'es' ? 'Estado del agente' : 'Agent status'}</span>
                <span className="flex items-center gap-2 text-emerald-300">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,0.9)]" />
                  ACTIVE
                </span>
              </div>
              <div className="space-y-2 text-sm text-slate-300">
                <p>&gt; build_context(domain, goal)</p>
                <p>&gt; generate_hypothesis(confidence_prior)</p>
                <p>&gt; execute_experiment(sandbox=True)</p>
                <p className="text-emerald-300">&gt; update_posterior(epistemic_gain)</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {AGENT_METRICS.map((metric) => {
            const Icon = metric.icon;

            return (
              <GlassPanel key={metric.label.en} density="compact" className="border-emerald-400/10 bg-gray-950/90">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300/70">
                      {metric.label[lang]}
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-white">{metric.value}</p>
                    <p className="mt-2 text-xs leading-5 text-slate-400">{metric.detail[lang]}</p>
                  </div>
                  <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2 text-emerald-200">
                    <Icon size={18} />
                  </div>
                </div>
              </GlassPanel>
            );
          })}
        </section>

        <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="min-h-[560px]">
            <LiveTelemetryConsole lang={lang} sessionId="autonomous-scientist" />
          </div>

          <GlassPanel density="spacious" className="border-emerald-400/10 bg-gray-950/90">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2 text-emerald-200">
                <Activity size={18} />
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300/70">
                  {lang === 'es' ? 'Falsacion en curso' : 'Falsification in progress'}
                </p>
                <h2 className="mt-1 text-2xl font-semibold text-white">
                  {lang === 'es' ? 'Decision epistemica' : 'Epistemic decision'}
                </h2>
              </div>
            </div>

            <div className="space-y-4">
              {[
                {
                  label: { en: 'Prior confidence', es: 'Confianza previa' },
                  value: '0.78',
                  width: '78%',
                },
                {
                  label: { en: 'Posterior confidence', es: 'Confianza posterior' },
                  value: '0.91',
                  width: '91%',
                },
                {
                  label: { en: 'Epistemic gain', es: 'Ganancia epistemica' },
                  value: '0.7295',
                  width: '72%',
                },
              ].map((item) => (
                <div key={item.label.en} className="rounded-2xl border border-white/[0.08] bg-black/25 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <span className="text-sm text-slate-300">{item.label[lang]}</span>
                    <span className="font-mono text-sm text-emerald-200">{item.value}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className="h-full rounded-full bg-emerald-400 shadow-[0_0_18px_rgba(52,211,153,0.55)]" style={{ width: item.width }} />
                  </div>
                </div>
              ))}
            </div>
          </GlassPanel>
        </section>

        <section>
          <HypothesisTracker hypotheses={hypotheses} openQuestions={openQuestions} lang={lang} />
        </section>
      </FocusContainer>
    </div>
  );
}
