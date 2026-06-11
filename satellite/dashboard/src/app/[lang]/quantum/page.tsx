import type { Metadata } from 'next';
import { Cpu, Zap, Radio, Terminal, Compass } from 'lucide-react';
import { Reveal } from '@/components/motion/Reveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Quantum Lab' };

export default async function QuantumPage({
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
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(139,92,246,0.08),transparent_40%)]" />
        <div className="flex flex-col justify-center min-h-[360px] max-w-3xl self-center relative z-10">
          <Reveal className="mb-4">
            <span className="research-kicker flex items-center gap-1.5 text-violet-300 border-violet-500/20 bg-violet-500/10">
              <Cpu size={13} />
              {isEs ? 'Exploración Cuántica Avanzada' : 'Advanced Quantum Exploration'}
            </span>
          </Reveal>

          <Reveal delay={0.1}>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-violet-200 bg-clip-text text-transparent">
              {isEs ? 'Quantum Lab' : 'Quantum Lab'}
            </h1>
          </Reveal>

          <Reveal delay={0.2}>
            <p className="mt-6 text-base leading-8 text-slate-300 sm:text-lg max-w-2xl">
              {isEs
                ? 'Modelización híbrida cuántica-clásica de sistemas dinámicos complejos y topologías de espín. Próximamente integrado tras completar la Fase 18.'
                : 'Hybrid quantum-classical modeling of complex dynamical systems and spin network topologies. Coming soon upon completion of Phase 18.'}
            </p>
          </Reveal>

          <Reveal delay={0.3} className="mt-8 flex flex-wrap gap-3">
            <span className="rounded-full border border-violet-500/20 bg-violet-500/10 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-violet-200">
              {isEs ? 'PLANIFICADO' : 'PLANNED'}
            </span>
            <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-3.5 py-1.5 text-xs text-slate-400">
              {isEs ? 'Post-Fase 18' : 'Post-Phase 18'}
            </span>
            <span className="rounded-full border border-violet-500/10 bg-violet-500/5 px-3.5 py-1.5 text-xs text-violet-300/80">
              {isEs ? 'Variational Quantum Algorithms' : 'Variational Quantum Algorithms'}
            </span>
          </Reveal>
        </div>
      </ScientificSurface>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[
          {
            icon: Zap,
            title: isEs ? 'Algoritmos Cuánticos Variacionales (VQE)' : 'Variational Quantum Algorithms (VQE)',
            desc: isEs
              ? 'Optimización de circuitos cuánticos parametrizados para resolver los estados fundamentales y espectros energéticos en modelos de gravedad cuántica y espín.'
              : 'Optimization of parameterized quantum circuits to solve ground states and energy spectra in quantum gravity and spin networks.',
          },
          {
            icon: Radio,
            title: isEs ? 'Computación de Depósito Cuántico' : 'Quantum Reservoir Computing',
            desc: isEs
              ? 'Uso de la decoherencia controlada y el entrelazamiento físico en procesadores cuánticos NISQ para predecir dinámicas caóticas no lineales.'
              : 'Harnessing controlled decoherence and physical entanglement on NISQ quantum processors to predict complex non-linear chaotic dynamics.',
          },
          {
            icon: Compass,
            title: isEs ? 'Embeddings de Redes de Tensores' : 'Tensor Network Embeddings',
            desc: isEs
              ? 'Compresión de espacios de fase latentes de alta dimensión mediante tensores de matriz de transferencia para agilizar cálculos clásicos.'
              : 'Compression of high-dimensional latent phase spaces using transfer-matrix tensor networks to accelerate classical computations.',
          },
        ].map((item, index) => {
          const ItemIcon = item.icon;
          return (
            <GlassPanel key={item.title} className="p-6 rounded-2xl flex flex-col justify-between">
              <div>
                <div className="p-2 w-9 h-9 rounded-lg border border-violet-500/20 bg-violet-500/10 text-violet-300 mb-4 flex items-center justify-center">
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
