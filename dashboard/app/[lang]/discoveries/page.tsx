import type { Metadata } from 'next';
import { Atom, Binary, FileCode2, FunctionSquare, GitBranch, Sigma } from 'lucide-react';
import { FormulaCard } from '@/components/scientific/FormulaCard';
import { InteractiveEquation } from '@/components/scientific/InteractiveEquation';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { KaTeX } from '@/components/ui/KaTeX';
import type { Language, TheoryBlock } from '@/types';

export const metadata: Metadata = {
  title: 'Symbolic Discovery',
};

const symbolicBlocks: TheoryBlock[] = [
  {
    id: 'lorenz-sindy',
    title: { en: 'Recovered Lorenz Vector Field', es: 'Campo Vectorial de Lorenz Recuperado' },
    tag: 'SINDy',
    color: 'emerald',
    content: {
      simple: {
        en: 'Sparse regression searches for the smallest equation set that still reproduces the observed trajectory.',
        es: 'La regresion dispersa busca el conjunto minimo de ecuaciones que reproduce la trayectoria observada.',
      },
      advanced: {
        en: 'The symbolic layer compares discovered candidate equations against the known Lorenz residual structure using SymPy simplification and term-overlap diagnostics.',
        es: 'La capa simbolica compara ecuaciones candidatas contra la estructura residual de Lorenz usando simplificacion SymPy y solapamiento de terminos.',
      },
    },
    formula: '\\dot{x}=\\sigma(y-x),\\quad \\dot{y}=x(\\rho-z)-y,\\quad \\dot{z}=xy-\\beta z',
    formulaLabel: { en: 'Continuous dynamics', es: 'Dinamica continua' },
  },
  {
    id: 'duffing-pysr',
    title: { en: 'Duffing Candidate Law', es: 'Ley Candidata de Duffing' },
    tag: 'PySR',
    color: 'violet',
    content: {
      simple: {
        en: 'Evolutionary symbolic regression proposes compact formulas and ranks them by accuracy and complexity.',
        es: 'La regresion simbolica evolutiva propone formulas compactas y las ordena por precision y complejidad.',
      },
      advanced: {
        en: 'PySR explores nonlinear operator grammars, while physics penalties discourage forbidden couplings and reward expected structural terms.',
        es: 'PySR explora gramaticas de operadores no lineales, mientras las penalizaciones fisicas desalientan acoplamientos prohibidos y premian terminos esperados.',
      },
    },
    formula: '\\dot{x}=v,\\quad \\dot{v}=x-x^3-\\delta v+\\gamma\\cos(\\omega t)',
    formulaLabel: { en: 'Forced oscillator law', es: 'Ley de oscilador forzado' },
  },
  {
    id: 'ev3-asymmetry',
    title: { en: 'Representation/Attribution Asymmetry', es: 'Asimetria Representacion/Atribucion' },
    tag: 'Audit',
    color: 'cyan',
    content: {
      simple: {
        en: 'The clinical classifier can transfer even when the geometry of the representation changes almost completely.',
        es: 'El clasificador clinico puede transferir aunque la geometria de la representacion cambie casi por completo.',
      },
      advanced: {
        en: 'The observatory treats representational collapse and attribution survival as separate measurable channels rather than a single transfer score.',
        es: 'El observatorio trata el colapso representacional y la supervivencia atributiva como canales medibles separados, no como una unica puntuacion de transferencia.',
      },
    },
    formula: 'D_{emb}=1-CKA(E_A,E_C)\\gg D_{attr}=1-\\rho(\\bar{C}_A,\\bar{C}_C)',
    formulaLabel: { en: 'Transfer asymmetry', es: 'Asimetria de transferencia' },
  },
];

const discoveryRows = [
  {
    system: 'Lorenz',
    method: 'SINDy',
    status: 'validated',
    score: '0.94',
    formula: '\\dot{x}=10(y-x)',
  },
  {
    system: 'Rossler',
    method: 'SINDy',
    status: 'candidate',
    score: '0.87',
    formula: '\\dot{x}=-y-z',
  },
  {
    system: 'Duffing',
    method: 'PySR',
    status: 'validated',
    score: '0.91',
    formula: '\\dot{v}=x-x^3-0.3v',
  },
  {
    system: 'Logistic',
    method: 'Fallback',
    status: 'validated',
    score: '0.89',
    formula: 'x_{n+1}=rx_n(1-x_n)',
  },
];

export default async function DiscoveriesPage({
  params,
}: {
  params: Promise<{ lang: string }>;
}) {
  const { lang: rawLang } = await params;
  const lang = (rawLang === 'es' ? 'es' : 'en') as Language;

  return (
    <div className="min-h-screen bg-gray-950 text-slate-100">
      <FocusContainer size="xl" className="space-y-8 pb-28">
        <section className="relative overflow-hidden rounded-[1.5rem] border border-emerald-400/15 bg-gray-950 p-6 shadow-[0_24px_90px_rgba(0,0,0,0.42)] sm:p-8 lg:p-10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(52,211,153,0.18),transparent_28%),linear-gradient(rgba(16,185,129,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.06)_1px,transparent_1px)] bg-[size:auto,42px_42px,42px_42px]" />
          <div className="relative z-10 grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.24em] text-emerald-200">
                <Sigma size={13} />
                {lang === 'es' ? 'Observatorio Simbolico' : 'Symbolic Observatory'}
              </div>

              <h1 className="max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
                {lang === 'es' ? 'Symbolic Discovery Observatory' : 'Symbolic Discovery Observatory'}
              </h1>

              <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300/76">
                {lang === 'es'
                  ? 'Una superficie de lectura para ecuaciones descubiertas por SINDy, PySR y recuperacion determinista, conectada al ciclo neurosimbolico de hipotesis y falsacion.'
                  : 'A reading surface for equations discovered by SINDy, PySR, and deterministic recovery, connected to the neurosymbolic hypothesis and falsification loop.'}
              </p>
            </div>

            <GlassPanel density="compact" className="border-emerald-400/10 bg-black/45">
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2 text-emerald-200">
                  <FunctionSquare size={18} />
                </div>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300/70">
                    {lang === 'es' ? 'Mejor candidato' : 'Best candidate'}
                  </p>
                  <h2 className="text-xl font-semibold text-white">Duffing / PySR</h2>
                </div>
              </div>
              <div className="rounded-2xl border border-white/[0.08] bg-gray-950/80 p-4">
                <KaTeX formula="\\dot{v}=x-x^3-0.3v" block />
              </div>
            </GlassPanel>
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { icon: Atom, label: { en: 'Systems', es: 'Sistemas' }, value: '5', detail: 'Lorenz / Rossler / Duffing' },
            { icon: Binary, label: { en: 'Methods', es: 'Metodos' }, value: '3', detail: 'SINDy / PySR / fallback' },
            { icon: GitBranch, label: { en: 'Term overlap', es: 'Solapamiento' }, value: '0.75+', detail: 'Jaccard threshold' },
            { icon: FileCode2, label: { en: 'Artifacts', es: 'Artefactos' }, value: 'JSON', detail: 'artifacts/discovery_*.json' },
          ].map((item) => {
            const Icon = item.icon;

            return (
              <GlassPanel key={item.label.en} density="compact" className="border-emerald-400/10 bg-gray-950/90">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300/70">
                      {item.label[lang]}
                    </p>
                    <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
                    <p className="mt-2 text-xs leading-5 text-slate-400">{item.detail}</p>
                  </div>
                  <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2 text-emerald-200">
                    <Icon size={18} />
                  </div>
                </div>
              </GlassPanel>
            );
          })}
        </section>

        <section className="grid gap-5 lg:grid-cols-3">
          {symbolicBlocks.map((block, index) => (
            <FormulaCard key={block.id} block={block} lang={lang} index={index} />
          ))}
        </section>

        <section className="grid gap-5 xl:grid-cols-[1fr_0.95fr]">
          <InteractiveEquation
            lang={lang}
            title={{
              en: 'Physics-penalized symbolic objective',
              es: 'Objetivo simbolico con penalizacion fisica',
            }}
            formula="\\mathcal{L}(f)=\\mathrm{MSE}(\\dot{x},f(x))+\\lambda_c\\,C(f)+\\lambda_p\\,P_{phys}(f)"
            terms={[
              {
                symbol: '\\mathrm{MSE}',
                label: { en: 'Trajectory fit', es: 'Ajuste de trayectoria' },
                explanation: {
                  en: 'Measures how well a candidate symbolic expression predicts observed derivatives.',
                  es: 'Mide que tan bien una expresion simbolica candidata predice derivadas observadas.',
                },
              },
              {
                symbol: 'C(f)',
                label: { en: 'Complexity cost', es: 'Coste de complejidad' },
                explanation: {
                  en: 'Keeps equations compact enough to be audited, compared, and interpreted.',
                  es: 'Mantiene las ecuaciones suficientemente compactas para auditarlas, compararlas e interpretarlas.',
                },
              },
              {
                symbol: 'P_{phys}',
                label: { en: 'Physics penalty', es: 'Penalizacion fisica' },
                explanation: {
                  en: 'Penalizes missing expected terms or forbidden couplings in the discovered law.',
                  es: 'Penaliza terminos esperados ausentes o acoplamientos prohibidos en la ley descubierta.',
                },
              },
            ]}
          />

          <GlassPanel density="spacious" className="border-emerald-400/10 bg-gray-950/90">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-xl border border-emerald-400/15 bg-emerald-400/10 p-2 text-emerald-200">
                <FileCode2 size={18} />
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300/70">
                  {lang === 'es' ? 'Hall of fame' : 'Hall of fame'}
                </p>
                <h2 className="mt-1 text-2xl font-semibold text-white">
                  {lang === 'es' ? 'Candidatos auditables' : 'Auditable candidates'}
                </h2>
              </div>
            </div>

            <div className="space-y-3">
              {discoveryRows.map((row) => (
                <div key={`${row.system}-${row.method}`} className="rounded-2xl border border-white/[0.08] bg-black/25 p-4">
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{row.system}</p>
                      <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate-500">{row.method}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.16em] text-emerald-200">
                        {row.status}
                      </span>
                      <span className="font-mono text-xs text-slate-400">{row.score}</span>
                    </div>
                  </div>
                  <div className="rounded-xl border border-white/[0.06] bg-gray-950/80 px-3 py-2">
                    <KaTeX formula={row.formula} block />
                  </div>
                </div>
              ))}
            </div>
          </GlassPanel>
        </section>
      </FocusContainer>
    </div>
  );
}
