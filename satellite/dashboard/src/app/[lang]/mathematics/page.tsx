import type { Metadata } from 'next';
import { Binary, Sigma, HelpCircle, ShieldAlert, Sparkles } from 'lucide-react';
import { Reveal } from '@/components/motion/Reveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Mathematics Lab' };

export default async function MathematicsPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;

  const isEs = lang === 'es';

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28 pt-6">
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(245,158,11,0.08),transparent_40%)]" />
        <div className="flex flex-col justify-center min-h-[360px] max-w-3xl self-center relative z-10">
          <Reveal className="mb-4">
            <span className="research-kicker flex items-center gap-1.5 text-amber-300 border-amber-500/20 bg-amber-500/10">
              <Binary size={13} />
              {isEs ? 'Fase de Planificación Científica' : 'Scientific Planning Phase'}
            </span>
          </Reveal>

          <Reveal delay={0.1}>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-amber-200 bg-clip-text text-transparent">
              {isEs ? 'Mathematics Lab' : 'Mathematics Lab'}
            </h1>
          </Reveal>

          <Reveal delay={0.2}>
            <p className="mt-6 text-base leading-8 text-slate-300 sm:text-lg max-w-2xl">
              {isEs
                ? 'Exploración formal avanzada y descubrimiento simbólico matemático automatizado. Próximamente integrado tras completar la Fase 18.'
                : 'Advanced formal exploration and automated mathematical symbolic discovery. Coming soon upon completion of Phase 18.'}
            </p>
          </Reveal>

          <Reveal delay={0.3} className="mt-8 flex flex-wrap gap-3">
            <span className="rounded-full border border-amber-500/20 bg-amber-500/10 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-amber-200">
              {isEs ? 'PLANIFICADO' : 'PLANNED'}
            </span>
            <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-3.5 py-1.5 text-xs text-slate-400">
              {isEs ? 'Post-Fase 18' : 'Post-Phase 18'}
            </span>
            <span className="rounded-full border border-amber-500/10 bg-amber-500/5 px-3.5 py-1.5 text-xs text-amber-300/80">
              {isEs ? 'Integración Lean/Coq' : 'Lean/Coq Integration'}
            </span>
          </Reveal>
        </div>
      </ScientificSurface>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[
          {
            icon: Sigma,
            title: isEs ? 'Regresión Simbólica de Alto Orden' : 'High-Order Symbolic Regression',
            desc: isEs
              ? 'Algoritmos evolutivos guiados por redes neuronales para deducir las ecuaciones algebraicas y diferenciales exactas que gobiernan la dinámica latente.'
              : 'Evolutionary algorithms guided by neural networks to deduce the exact algebraic and differential equations governing latent dynamics.',
          },
          {
            icon: ShieldAlert,
            title: isEs ? 'Verificación Formal de Estabilidad' : 'Formal Stability Verification',
            desc: isEs
              ? 'Integración con asistentes de prueba matemáticos (Lean 4) para verificar formalmente las regiones de estabilidad y cotas de Lyapunov descubiertas.'
              : 'Integration with mathematical proof assistants (Lean 4) to formally verify the discovered stability regions and Lyapunov bounds.',
          },
          {
            icon: Sparkles,
            title: isEs ? 'Auditoría en Teoría de Grupos' : 'Group Theory Audit',
            desc: isEs
              ? 'Clasificación algebraica de sistemas de conservación y cálculo automatizado de invariantes dinámicos a través de los teoremas de Noether.'
              : 'Algebraic classification of conservation systems and automated calculation of dynamical invariants via Noether theorems.',
          },
        ].map((item, index) => {
          const ItemIcon = item.icon;
          return (
            <GlassPanel key={item.title} className="p-6 rounded-2xl flex flex-col justify-between">
              <div>
                <div className="p-2 w-9 h-9 rounded-lg border border-amber-500/20 bg-amber-500/10 text-amber-300 mb-4 flex items-center justify-center">
                  <ItemIcon size={18} />
                </div>
                <h3 className="text-lg font-semibold text-white/90 mb-2">{item.title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{item.desc}</p>
              </div>
            </GlassPanel>
          );
        })}
      </div>
    </FocusContainer>
  );
}
