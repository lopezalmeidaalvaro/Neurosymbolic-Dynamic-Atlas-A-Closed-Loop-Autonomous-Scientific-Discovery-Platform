'use client';

import { useState } from 'react';
import Balancer from 'react-wrap-balancer';
import { 
  BookOpen, Brain, Compass, Microscope, Sparkles, LayoutDashboard, 
  Search, FlaskConical, Clock, Gauge, History, Layers, Milestone, Info
} from 'lucide-react';
import { motion } from 'framer-motion';
import { educationalConcepts, guidedLearningSteps, scientificStory } from '@/data/learningData';
import { ExplainLikeIm15 } from '@/components/educational/ExplainLikeIm15';
import { GuidedConceptFlow } from '@/components/educational/GuidedConceptFlow';
import { InteractiveAnalogy } from '@/components/educational/InteractiveAnalogy';
import { ProgressiveExplanation } from '@/components/educational/ProgressiveExplanation';
import { ScientificStory } from '@/components/educational/ScientificStory';
import { StepByStepDiscovery } from '@/components/educational/StepByStepDiscovery';
import { ConceptBreakdown } from '@/components/scientific/ConceptBreakdown';
import { InteractiveEquation } from '@/components/scientific/InteractiveEquation';
import { MethodologyExplorer } from '@/components/scientific/MethodologyExplorer';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import { ConceptDetailModal } from '@/components/educational/ConceptDetailModal';
import type { EducationalConcept, Dictionary, Language } from '@/types';

interface LearnPageClientProps {
  lang: Language;
  dict: Dictionary;
}

export function LearnPageClient({ lang, dict }: LearnPageClientProps) {
  const [selectedConcept, setSelectedConcept] = useState<EducationalConcept | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleSelectConcept = (concept: EducationalConcept) => {
    setSelectedConcept(concept);
    setModalOpen(true);
  };

  const embedding = educationalConcepts.find((concept) => concept.id === 'embedding')!;
  const autocorrelation = educationalConcepts.find((concept) => concept.id === 'autocorrelation')!;
  const chaos = educationalConcepts.find((concept) => concept.id === 'chaos')!;
  const geometry = educationalConcepts.find((concept) => concept.id === 'geometric-separability')!;

  const sectionsOnboarding = [
    {
      icon: LayoutDashboard,
      title: { en: 'Summary / Dashboard', es: 'Resumen / Dashboard' },
      desc: {
        en: 'The mission control room. Monitor pipeline execution states, active trajectories, and high-level metrics in real-time.',
        es: 'La central de control. Monitorea estados del pipeline, trayectorias activas y métricas generales del experimento en tiempo real.'
      },
      color: 'text-cyan-400'
    },
    {
      icon: BookOpen,
      title: { en: 'Learn Portal', es: 'Portal Aprender' },
      desc: {
        en: 'Your interactive physics handbook. Dive into core concepts, graphical tutorials, and formulas explained step by step.',
        es: 'Tu manual de física interactivo. Explora conceptos clave, tutoriales gráficos y las ecuaciones explicadas paso a paso.'
      },
      color: 'text-violet-400'
    },
    {
      icon: Search,
      title: { en: 'Discoveries Log', es: 'Descubrimientos' },
      desc: {
        en: 'The registry of autonomous findings. Review which physical laws we recovered and where our confidence boundary stops.',
        es: 'El registro de descubrimientos autónomos. Revisa qué leyes físicas hemos redescubierto y los límites de incertidumbre.'
      },
      color: 'text-emerald-400'
    },
    {
      icon: FlaskConical,
      title: { en: 'Science Lab (Interactive)', es: 'Laboratorio (Interactivo)' },
      desc: {
        en: 'The interactive physics sandbox. Play with parameters, inject gaussian noise, and test SOTA classification resistance.',
        es: 'El sandbox interactivo del laboratorio. Ajusta parámetros, inyecta ruido gaussiano y prueba clasificadores SOTA.'
      },
      color: 'text-amber-400'
    },
    {
      icon: Clock,
      title: { en: 'Milestones Timeline', es: 'Línea de Tiempo' },
      desc: {
        en: 'The historical sequence. Track research milestones, algorithmic evolutions, and plan phases chronologically.',
        es: 'El recorrido histórico. Sigue los hitos del pipeline de investigación, avances algorítmicos y fases cronológicamente.'
      },
      color: 'text-pink-400'
    },
    {
      icon: Gauge,
      title: { en: 'Benchmark Arena', es: 'Arena Benchmark' },
      desc: {
        en: 'Speed and accuracy racetrack. Experience formal speed comparisons between Embedding V2 and strong baselines.',
        es: 'La pista de velocidad y precisión. Compara el rendimiento y coste computacional de Embedding V2 frente a SOTA.'
      },
      color: 'text-rose-400'
    },
    {
      icon: History,
      title: { en: 'Scientific Logs', es: 'Logs Científicos' },
      desc: {
        en: 'Immutable computational memory. Review execution histories, telemetry outputs, and auditable parameter configurations.',
        es: 'La memoria computacional inalterable. Audita ejecuciones del pipeline, salidas de telemetría y configuraciones de ejecución.'
      },
      color: 'text-indigo-400'
    },
    {
      icon: Layers,
      title: { en: 'Binary Compare', es: 'Comparar Sistemas' },
      desc: {
        en: 'Dual-pane telemetry explorer. Contrast embedding space shapes and phase orbits of two different systems side-by-side.',
        es: 'Visualizador de órbita binaria. Contrasta formas geométricas latentes y órbitas de fase de dos sistemas dinámicos a la vez.'
      },
      color: 'text-sky-400'
    },
    {
      icon: Milestone,
      title: { en: 'Future Roadmap', es: 'Hoja de Ruta' },
      desc: {
        en: 'Strategic flight plan. Follow our engineering milestones and pending mathematical challenges.',
        es: 'El plan de vuelo estratégico. Sigue los hitos pendientes de ingeniería y desafíos matemáticos del equipo.'
      },
      color: 'text-blue-400'
    }
  ];

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28">
      {/* 1. Cinematic Header & Project Overview Welcome */}
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_18%,rgba(125,211,252,0.12),transparent_32%)]" />
        <div className="grid min-h-[360px] gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div className="max-w-4xl self-center">
            <span className="research-kicker mb-6">
              <BookOpen size={13} />
              {dict.nav.learn}
            </span>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl">
              <Balancer>
                {lang === 'es'
                  ? 'Aprende el experimento sin perder el rigor.'
                  : 'Learn the experiment without losing the rigor.'}
              </Balancer>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300/76 sm:text-lg">
              <Balancer>
                {lang === 'es'
                  ? 'Una ruta visual para entender series temporales, caos, ruido, embeddings y separabilidad geométrica con dos niveles cognitivos.'
                  : 'A visual route for understanding time series, chaos, noise, embeddings, and geometric separability with two cognitive levels.'}
              </Balancer>
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              { icon: Brain, label: lang === 'es' ? 'Modo simple' : 'Simple mode', value: lang === 'es' ? 'Narrativo' : 'Narrative' },
              { icon: Microscope, label: lang === 'es' ? 'Modo avanzado' : 'Advanced mode', value: lang === 'es' ? 'Técnico' : 'Technical' },
              { icon: Compass, label: lang === 'es' ? 'Conceptos' : 'Concepts', value: String(educationalConcepts.length) },
              { icon: BookOpen, label: lang === 'es' ? 'Ruta' : 'Path', value: `${guidedLearningSteps.length} ${lang === 'es' ? 'pasos' : 'steps'}` },
            ].map(({ icon: Icon, label, value }) => (
              <GlassPanel key={label} density="compact" className="rounded-2xl border border-white/[0.08]">
                <Icon size={16} className="text-cyan-100" />
                <p className="metric-label mt-4">{label}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
              </GlassPanel>
            ))}
          </div>
        </div>
      </ScientificSurface>

      {/* 2. Educational Introduction Section: What are we building? */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <GlassPanel density="spacious" className="border border-emerald-500/20 bg-emerald-500/5 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(16,185,129,0.06),transparent_40%)]" />
          <div className="absolute top-4 right-4 text-emerald-400/30 flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-widest">
            <Sparkles size={11} className="animate-spin-slow" />
            <span>Onboarding ELI15</span>
          </div>

          <div className="flex items-center gap-3 mb-4">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10 text-emerald-400">
              <Info size={17} />
            </span>
            <div>
              <p className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest font-mono">
                {lang === 'es' ? 'Introducción de Bienvenida' : 'Welcome Introduction'}
              </p>
              <h2 className="text-lg font-bold text-white leading-tight">
                {lang === 'es' ? '¿Qué estamos construyendo aquí?' : 'What are we building here?'}
              </h2>
            </div>
          </div>

          <p className="text-sm leading-relaxed text-emerald-50/90 font-medium">
            {lang === 'es' ? (
              <span>
                Estamos construyendo un <strong>Traductor Universal del Caos</strong>. Imagina que la naturaleza habla en un idioma de señales físicas complejas y desordenadas (como los latidos del corazón, turbulencias de aviones o circuitos caóticos). Nuestro sistema toma esas señales "ruidosas" e indescifrables, las comprime en una <strong>huella digital única (Embedding)</strong> y las organiza en un mapa ordenadamente para que una Inteligencia Artificial pueda entenderlas, clasificarlas y predecir su comportamiento en microsegundos.
              </span>
            ) : (
              <span>
                We are building a <strong>Universal Chaos Translator</strong>. Nature speaks in a language of complex, chaotic physical signals (like heartbeats, airplane turbulence, or chaotic circuits). Our system takes these noisy, indecipherable signals, compresses them into a <strong>unique digital fingerprint (Embedding)</strong>, and maps them geometrically so an Artificial Intelligence can understand, classify, and predict them in microseconds.
              </span>
            )}
          </p>
        </GlassPanel>
      </motion.div>

      {/* 3. Onboarding Infographic: Dashboard Map Guide */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <GlassPanel density="spacious">
          <div className="mb-6">
            <p className="metric-label">{lang === 'es' ? 'Guía del Panel' : 'Dashboard Guide'}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white/90">
              {lang === 'es' ? 'Explora el mapa del proyecto' : 'Explore the project map'}
            </h2>
            <p className="text-xs text-slate-400/90 leading-relaxed mt-2">
              {lang === 'es' 
                ? 'Conoce coloquialmente qué hace cada sección del dashboard para navegar con total seguridad y entendimiento.' 
                : 'Get to know what each section of the dashboard does in plain English so you can navigate with absolute confidence.'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {sectionsOnboarding.map((sec, i) => {
              const Icon = sec.icon;
              return (
                <div 
                  key={i} 
                  className="rounded-2xl border border-white/[0.07] bg-white/[0.025] hover:bg-white/[0.05] hover:border-cyan-500/20 transition-all duration-200 p-4 flex flex-col group cursor-pointer"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`p-2 rounded-xl bg-white/[0.03] group-hover:bg-cyan-500/10 ${sec.color} transition-all`}>
                      <Icon size={15} />
                    </span>
                    <h3 className="text-sm font-semibold text-white/90 group-hover:text-cyan-300 transition-colors">
                      {sec.title[lang]}
                    </h3>
                  </div>
                  <p className="text-xs leading-relaxed text-slate-400 group-hover:text-slate-300 transition-colors flex-1">
                    {sec.desc[lang]}
                  </p>
                </div>
              );
            })}
          </div>
        </GlassPanel>
      </motion.div>

      <div className="h-px bg-white/[0.08]" />

      {/* 4. Original Sections & Interactive Concept Flow connected to Modal */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15 }}
      >
        <ScientificStory steps={scientificStory} lang={lang} />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <StepByStepDiscovery steps={guidedLearningSteps} lang={lang} />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.25 }}
      >
        <div className="mb-5">
          <p className="metric-label">{lang === 'es' ? 'Mapa de conceptos' : 'Concept map'}</p>
          <h2 className="mt-2 text-2xl font-semibold text-white/90">
            {lang === 'es' ? 'Lo que necesitas entender (Interactivos)' : 'What you need to understand (Interactive)'}
          </h2>
          <p className="text-xs text-slate-500/90 leading-relaxed mt-1">
            {lang === 'es' 
              ? 'Haz clic en cualquier tarjeta de concepto para abrir un visualizador matemático con esquemas dinámicos, analogías sencillas y desgloses de ecuaciones.' 
              : 'Click on any concept card to open a mathematical visualizer complete with dynamic SVGs, analogies, and variable breakdowns.'}
          </p>
        </div>
        <GuidedConceptFlow concepts={educationalConcepts} lang={lang} onSelectConcept={handleSelectConcept} />
      </motion.div>

      <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <ExplainLikeIm15 title={embedding.title} text={embedding.short} example={embedding.example} lang={lang} />
        <InteractiveAnalogy title={chaos.title} analogy={chaos.analogy} technical={chaos.technical} lang={lang} />
      </div>

      <ProgressiveExplanation concept={embedding} lang={lang} />

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <InteractiveEquation
          title={autocorrelation.title}
          formula={autocorrelation.formula ?? ''}
          lang={lang}
          terms={[
            {
              symbol: 'R(tau)',
              label: { en: 'Autocorrelation score', es: 'Puntuación de autocorrelación' },
              explanation: {
                en: 'A high value means the signal still resembles itself after the chosen delay.',
                es: 'Un valor alto significa que la señal aún se parece a sí misma tras el retardo elegido.',
              },
            },
            {
              symbol: 'tau',
              label: { en: 'Lag', es: 'Retardo' },
              explanation: {
                en: 'The number of steps we shift the signal before comparing it with itself.',
                es: 'El número de pasos que desplazamos la señal antes de compararla consigo misma.',
              },
            },
            {
              symbol: 'x(t)',
              label: { en: 'Signal value', es: 'Valor de la señal' },
              explanation: {
                en: 'The measured value of the system at a specific moment in time.',
                es: 'El valor medido del sistema en un momento concreto.',
              },
            },
          ]}
        />
        <ConceptBreakdown concept={geometry} lang={lang} />
      </div>

      <MethodologyExplorer steps={guidedLearningSteps} lang={lang} />

      {/* Interactive Concept Detail Modal */}
      <ConceptDetailModal
        concept={selectedConcept}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        lang={lang}
      />
    </FocusContainer>
  );
}
