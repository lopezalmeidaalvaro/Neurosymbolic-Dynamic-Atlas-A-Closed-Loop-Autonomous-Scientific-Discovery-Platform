// ═══════════════════════════════════════════════════════════════
// types/scientific.ts — Foundational scientific & cognitive types
// ═══════════════════════════════════════════════════════════════

export interface MultilingualText {
  en: string;
  es: string;
}

export type ComplexityMode = 'simple' | 'advanced';

/** Semantic double-layer: same content at two cognitive depths */
export interface SemanticText {
  simple: MultilingualText;
  advanced: MultilingualText;
}

export interface TheoryBlock {
  id: string;
  title: MultilingualText;
  content: SemanticText;
  formula?: string;         // Raw KaTeX string
  formulaLabel?: MultilingualText;
  tag?: string;
  color?: 'cyan' | 'blue' | 'violet' | 'emerald';
}

// Educational explainability
export interface EducationalConcept {
  id: string;
  title: MultilingualText;
  short: SemanticText;
  visual: SemanticText;
  technical: SemanticText;
  analogy: SemanticText;
  example: SemanticText;
  formula?: string;
  formulaLabel?: MultilingualText;
  methodology?: SemanticText;
  keywords: string[];
  visualType: 'wave' | 'noise' | 'embedding' | 'comparison' | 'geometry';
  color?: 'cyan' | 'blue' | 'violet' | 'emerald' | 'amber';
}

export interface GuidedLearningStep {
  id: string;
  title: MultilingualText;
  body: SemanticText;
  outcome: SemanticText;
  conceptIds: string[];
}

export interface ScientificStoryStep {
  id: string;
  title: MultilingualText;
  body: SemanticText;
  signal: MultilingualText;
}

export interface ScientificMemoryEntry {
  id: string;
  date: string;
  type: 'experiment' | 'finding' | 'hypothesis' | 'question' | 'literature';
  title: MultilingualText;
  narrative: SemanticText;
  linkedIds: string[];
}

// Bibliography entry model
export interface ScientificReference {
  id: string;
  title: string;
  authors: string[];
  year: number;
  venue: string;
  doi: string | null;
  arxiv: string | null;
  url: string;
  tags: string[];
  category: 'benchmark' | 'methodology' | 'dataset' | 'theory';
  context: SemanticText;
  citation?: string;
  bibtex?: string;
  importance?: 'core' | 'supporting' | 'contextual';
}

// ── i18n ────────────────────────────────────────────────────────
export type Language = 'en' | 'es';

export interface Dictionary {
  nav: {
    overview: string;
    learn: string;
    discoveries: string;
    timeline: string;
    benchmark: string;
    scientificLog: string;
    roadmap: string;
    settings: string;
    interactive: string;
  };
  header: {
    status: string;
    language: string;
    collapse: string;
    expand: string;
  };
  kpi: {
    totalExperiments: string;
    completedPhases: string;
    avgAccuracy: string;
    speedAdvantage: string;
  };
  status: {
    online: string;
    processing: string;
    idle: string;
  };
  breadcrumbs: {
    home: string;
    dashboard: string;
  };
  complexity: {
    simple: string;
    advanced: string;
    label: string;
  };
  timeline: {
    title: string;
    completed: string;
    active: string;
    planned: string;
  };
  log: {
    title: string;
    severity: {
      info: string;
      success: string;
      warning: string;
      error: string;
      insight: string;
    };
  };
  benchmark: {
    title: string;
    accuracy: string;
    time: string;
    winner: string;
    ours: string;
  };
  roadmap: {
    title: string;
    done: string;
    inProgress: string;
    planned: string;
    priority: {
      high: string;
      medium: string;
      low: string;
    };
  };
  theory: {
    title: string;
    formula: string;
  };
}
