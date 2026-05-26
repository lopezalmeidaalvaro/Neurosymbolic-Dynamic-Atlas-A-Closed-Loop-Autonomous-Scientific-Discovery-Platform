import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { Orbit, Activity, ShieldAlert, Sparkles } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import dynamic from 'next/dynamic';

const SignalPlayground = dynamic(
  () => import('@/components/interactive/SignalPlayground').then((m) => m.SignalPlayground)
);
const NoiseVisualizer = dynamic(
  () => import('@/components/interactive/NoiseVisualizer').then((m) => m.NoiseVisualizer)
);
const GeometryVisualizer = dynamic(
  () => import('@/components/interactive/GeometryVisualizer').then((m) => m.GeometryVisualizer)
);
const EmbeddingExplorer = dynamic(
  () => import('@/components/interactive/EmbeddingExplorer').then((m) => m.EmbeddingExplorer)
);
const ModelComparator = dynamic(
  () => import('@/components/interactive/ModelComparator').then((m) => m.ModelComparator)
);
const DynamicSystemSimulator = dynamic(
  () =>
    import('@/components/interactive/DynamicSystemSimulator').then(
      (m) => m.DynamicSystemSimulator
    )
);
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Interactive Science Lab' };

export default async function InteractivePage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28">
      {/* Cinematic Header Section */}
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(139,92,246,0.12),transparent_32%)]" />
        <div className="grid min-h-[360px] gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <Reveal className="max-w-4xl self-center">
            <span className="research-kicker mb-6">
              <Orbit size={13} />
              {lang === 'es' ? 'Simulaciones en Tiempo Real' : 'Real-time Simulations'}
            </span>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl">
              <Balancer>
                {lang === 'es'
                  ? 'Laboratorio Interactivo de Exploración Científica.'
                  : 'Interactive Computational Exploration Lab.'}
              </Balancer>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300/76 sm:text-lg">
              <Balancer>
                {lang === 'es'
                  ? 'Manipula señales caóticas, introduce distorsiones físicas gaussianas y observa de forma interactiva la robustez de nuestros modelos.'
                  : 'Manipulate chaotic physical signals, inject gaussian distortions, and interactively experience the mathematical robustness of our models.'}
              </Balancer>
            </p>
          </Reveal>

          <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              { icon: Activity, label: lang === 'es' ? 'Simuladores' : 'Simulators', value: '3 Active' },
              { icon: ShieldAlert, label: lang === 'es' ? 'Filtro de Ruido' : 'Noise Filters', value: 'σ [0.0 - 1.2]' },
              { icon: Orbit, label: lang === 'es' ? 'Atractores' : 'Attractors', value: 'Lorenz 3D' },
              { icon: Sparkles, label: lang === 'es' ? 'Espacio Latente' : 'Latent Space', value: '512-dim' },
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

      {/* Grid of Interactive Explorations */}
      <ScrollReveal className="grid gap-6 lg:grid-cols-2">
        <SignalPlayground lang={lang} />
        <NoiseVisualizer lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <DynamicSystemSimulator lang={lang} />
      </ScrollReveal>

      <ScrollReveal className="grid gap-6 lg:grid-cols-2">
        <GeometryVisualizer lang={lang} />
        <EmbeddingExplorer lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <ModelComparator lang={lang} />
      </ScrollReveal>
    </FocusContainer>
  );
}
