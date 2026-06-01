// ═══════════════════════════════════════════════════════════════
// lib/i18n/dictionaries.ts — EN/ES (Phase 2 extended)
// ═══════════════════════════════════════════════════════════════
import type { Dictionary, Language } from '@/types';

const en: Dictionary = {
  nav: {
    overview: 'Overview',
    learn: 'Learn',
    discoveries: 'Discoveries',
    timeline: 'Timeline',
    benchmark: 'Benchmark',
    scientificLog: 'Scientific Log',
    roadmap: 'Roadmap',
    settings: 'Settings',
    interactive: 'Interactive Lab',
  },
  header: {
    status: 'System Status',
    language: 'Language',
    collapse: 'Collapse sidebar',
    expand: 'Expand sidebar',
  },
  kpi: {
    totalExperiments: 'Total Experiments',
    completedPhases: 'Completed Phases',
    avgAccuracy: 'Avg. Accuracy',
    speedAdvantage: 'Speed Advantage',
  },
  status: {
    online: 'Online',
    processing: 'Processing',
    idle: 'Idle',
  },
  breadcrumbs: {
    home: 'Home',
    dashboard: 'Dashboard',
  },
  complexity: {
    simple: 'Simple',
    advanced: 'Advanced',
    label: 'Mode',
  },
  timeline: {
    title: 'Research Timeline',
    completed: 'Completed',
    active: 'Active',
    planned: 'Planned',
  },
  log: {
    title: 'Scientific Log',
    severity: {
      info: 'Info',
      success: 'Success',
      warning: 'Warning',
      error: 'Error',
      insight: 'Insight',
    },
  },
  benchmark: {
    title: 'SOTA Benchmark',
    accuracy: 'Accuracy',
    time: 'Time (s)',
    winner: 'Winner',
    ours: 'Our model',
  },
  roadmap: {
    title: 'Roadmap',
    done: 'Done',
    inProgress: 'In Progress',
    planned: 'Planned',
    priority: {
      high: 'High',
      medium: 'Medium',
      low: 'Low',
    },
  },
  theory: {
    title: 'Mathematical Theory',
    formula: 'Formula',
  },
};

const es: Dictionary = {
  nav: {
    overview: 'Resumen',
    learn: 'Aprender',
    discoveries: 'Descubrimientos',
    timeline: 'Línea de Tiempo',
    benchmark: 'Benchmark',
    scientificLog: 'Log Científico',
    roadmap: 'Hoja de Ruta',
    settings: 'Ajustes',
    interactive: 'Laboratorio',
  },
  header: {
    status: 'Estado del Sistema',
    language: 'Idioma',
    collapse: 'Colapsar barra lateral',
    expand: 'Expandir barra lateral',
  },
  kpi: {
    totalExperiments: 'Experimentos Totales',
    completedPhases: 'Fases Completadas',
    avgAccuracy: 'Precisión Media',
    speedAdvantage: 'Ventaja de Velocidad',
  },
  status: {
    online: 'En línea',
    processing: 'Procesando',
    idle: 'Inactivo',
  },
  breadcrumbs: {
    home: 'Inicio',
    dashboard: 'Panel',
  },
  complexity: {
    simple: 'Simple',
    advanced: 'Avanzado',
    label: 'Modo',
  },
  timeline: {
    title: 'Línea de Tiempo de Investigación',
    completed: 'Completado',
    active: 'Activo',
    planned: 'Planificado',
  },
  log: {
    title: 'Log Científico',
    severity: {
      info: 'Info',
      success: 'Éxito',
      warning: 'Aviso',
      error: 'Error',
      insight: 'Insight',
    },
  },
  benchmark: {
    title: 'Benchmark SOTA',
    accuracy: 'Precisión',
    time: 'Tiempo (s)',
    winner: 'Ganador',
    ours: 'Nuestro modelo',
  },
  roadmap: {
    title: 'Hoja de Ruta',
    done: 'Completado',
    inProgress: 'En Progreso',
    planned: 'Planificado',
    priority: {
      high: 'Alta',
      medium: 'Media',
      low: 'Baja',
    },
  },
  theory: {
    title: 'Teoría Matemática',
    formula: 'Fórmula',
  },
};

const dictionaries: Record<Language, Dictionary> = { en, es };

export function getDictionary(lang: Language): Dictionary {
  return dictionaries[lang] ?? dictionaries.en;
}

export const SUPPORTED_LANGUAGES: Language[] = ['en', 'es'];
export const DEFAULT_LANGUAGE: Language = 'en';
