import type { Metadata } from 'next';
import Balancer from 'react-wrap-balancer';
import { Gauge, Microscope, Timer } from 'lucide-react';
import { getDictionary } from '@/lib/i18n/dictionaries';
import { benchmarkResults, kpiEntries } from '@/data/benchmarkData';
import { theoryBlocks } from '@/data/theoryData';
import { KPICard } from '@/components/dashboard/KPICard';
import { BenchmarkChart } from '@/components/dashboard/BenchmarkChart';
import { FormulaCard } from '@/components/scientific/FormulaCard';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import { NoiseRobustnessObservatory } from '@/components/scientific/NoiseRobustnessObservatory';
import { ScientificObservabilityDashboard } from '@/components/scientific/ScientificObservabilityDashboard';
import type { Language } from '@/types';

export const metadata: Metadata = { title: 'Benchmark' };

export default async function BenchmarkPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = rawLang as Language;
  const dict = getDictionary(lang);
  const embeddingBlock = theoryBlocks.find((b) => b.id === 'embedding-v2')!;
  const universalityBlock = theoryBlocks.find((b) => b.id === 'universality')!;

  return (
    <FocusContainer size="lg" className="space-y-9 pb-28">
      <ScientificSurface grid className="p-6 sm:p-8">
        <Reveal>
          <span className="research-kicker mb-5">
            <Gauge size={13} />
            {dict.benchmark.title}
          </span>
          <h1 className="cinematic-heading max-w-4xl text-4xl sm:text-5xl lg:text-6xl">
            <Balancer>
              {lang === 'es'
                ? 'Rendimiento experimental sin exceso computacional.'
                : 'Experimental performance without computational excess.'}
            </Balancer>
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/72">
            {lang === 'es'
              ? 'Comparacion formal de Embedding V2 frente al estado del arte en clasificacion de series temporales sinteticas.'
              : 'Formal comparison of Embedding V2 against state-of-the-art classifiers for synthetic dynamical time series.'}
          </p>
        </Reveal>
      </ScientificSurface>

      <ScrollReveal>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiEntries.map((kpi, i) => (
            <KPICard key={kpi.id} kpi={kpi} lang={lang} index={i} />
          ))}
        </div>
      </ScrollReveal>

      <ScrollReveal className="grid grid-cols-1 gap-5 md:grid-cols-2">
        <GlassPanel density="spacious" tone="success">
          <div className="mb-6 flex items-center gap-3">
            <Microscope size={17} className="text-emerald-100" />
            <div>
              <p className="metric-label">{dict.benchmark.accuracy}</p>
              <h2 className="mt-1 text-xl font-semibold text-white/90">
                {lang === 'es' ? 'Fidelidad de clasificacion' : 'Classification fidelity'}
              </h2>
            </div>
          </div>
          <BenchmarkChart results={benchmarkResults} lang={lang} metric="accuracy" />
        </GlassPanel>

        <GlassPanel density="spacious" tone="active">
          <div className="mb-6 flex items-center gap-3">
            <Timer size={17} className="text-cyan-100" />
            <div>
              <p className="metric-label">{dict.benchmark.time}</p>
              <h2 className="mt-1 text-xl font-semibold text-white/90">
                {lang === 'es' ? 'Coste temporal' : 'Temporal cost'}
              </h2>
            </div>
          </div>
          <BenchmarkChart results={benchmarkResults} lang={lang} metric="time" />
        </GlassPanel>
      </ScrollReveal>

      <ScrollReveal>
        <GlassPanel density="spacious">
          <p className="metric-label">{lang === 'es' ? 'Metodologia' : 'Methodology'}</p>
          <p className="mt-4 text-sm leading-8 text-slate-300/72">
            {lang === 'es'
              ? 'Dataset sintetico: 150 series temporales, 50 por clase, longitud 200 pasos. Clases: caos, periodico y ruido. Division 70/30 train/test. ROCKET usa 1000 kernels con RidgeClassifierCV; DTW usa 1-NN; Embedding V2 usa varianza, skewness, curtosis y autocorrelacion lag-1 con RandomForest.'
              : 'Synthetic dataset: 150 time series, 50 per class, length 200 steps. Classes: chaos, periodic, and noise. 70/30 train/test split. ROCKET uses 1000 kernels with RidgeClassifierCV; DTW uses 1-NN; Embedding V2 uses variance, skewness, kurtosis, and lag-1 autocorrelation with RandomForest.'}
          </p>
        </GlassPanel>
      </ScrollReveal>

      <ScrollReveal>
        <NoiseRobustnessObservatory lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <ScientificObservabilityDashboard lang={lang} />
      </ScrollReveal>

      <ScrollReveal>
        <div className="mb-5">
          <p className="metric-label">{dict.theory.title}</p>
          <h2 className="mt-2 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Fundamento matematico' : 'Mathematical foundation'}
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormulaCard block={embeddingBlock} lang={lang} index={0} />
          <FormulaCard block={universalityBlock} lang={lang} index={1} />
        </div>
      </ScrollReveal>
    </FocusContainer>
  );
}
