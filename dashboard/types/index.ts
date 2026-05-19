// ═══════════════════════════════════════════════════════════════
// types/index.ts — Complete shared type definitions
// ═══════════════════════════════════════════════════════════════

// ── Core utility types ──────────────────────────────────────────
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

// ── Timeline ────────────────────────────────────────────────────
export type TimelineEventStatus = 'completed' | 'active' | 'planned';

export interface TimelineEvent {
  id: string;
  date: string;
  title: MultilingualText;
  description: MultilingualText;
  semanticDescription?: SemanticText;
  status: TimelineEventStatus;
  tags: string[];
  phaseName?: MultilingualText;
}

// ── Benchmark ───────────────────────────────────────────────────
export interface BenchmarkResult {
  id: string;
  modelName: string;
  accuracy: number;
  timeSeconds: number;
  isOurs: boolean;
  color: string;
}

// ── Scientific Log ──────────────────────────────────────────────
export type LogSeverity = 'info' | 'success' | 'warning' | 'error' | 'insight';

export interface ScientificLogEntry {
  id: string;
  timestamp: string;
  severity: LogSeverity;
  phase: string;
  message: MultilingualText;
  details?: string;
}

// ── Experiment ──────────────────────────────────────────────────
export type ExperimentStatus = 'idle' | 'running' | 'completed' | 'failed';

export interface ExperimentState {
  id: string;
  name: MultilingualText;
  status: ExperimentStatus;
  progress: number;
  startedAt?: string;
  completedAt?: string;
  scriptPath: string;
}

// ── KPI ─────────────────────────────────────────────────────────
export type KPITrend = 'up' | 'down' | 'stable';

export interface KPIEntry {
  id: string;
  label: MultilingualText;
  value: string | number;
  unit?: string;
  trend?: KPITrend;
  trendValue?: string;
  description?: MultilingualText;
  color?: 'cyan' | 'blue' | 'violet' | 'emerald' | 'amber';
}

// ── Project Info ────────────────────────────────────────────────
export interface ProjectInfo {
  name: string;
  tagline: MultilingualText;
  description: MultilingualText;
  version: string;
  status: 'experimental' | 'beta' | 'stable';
  githubUrl: string;
  totalPhases: number;
  completedPhases: number;
}

// ── Roadmap ─────────────────────────────────────────────────────
export type RoadmapStatus = 'done' | 'in-progress' | 'planned';

export interface RoadmapItem {
  id: string;
  title: MultilingualText;
  description: MultilingualText;
  status: RoadmapStatus;
  priority: 'high' | 'medium' | 'low';
  eta?: string;
}

// ── Navigation ──────────────────────────────────────────────────
export interface NavItem {
  id: string;
  label: MultilingualText;
  href: string;
  icon: string;
  badge?: string;
}

// ── Theory / Documentation ──────────────────────────────────────
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

// Research discovery memory
export type DiscoveryState = 'validated' | 'observed' | 'hypothesis' | 'uncertain' | 'rejected';

export interface DiscoveryMetric {
  label: MultilingualText;
  value: number;
  unit?: string;
}

export interface ResearchFinding {
  id: string;
  state: DiscoveryState;
  title: MultilingualText;
  summary: SemanticText;
  whyItMatters: SemanticText;
  methodology: SemanticText;
  evidence: SemanticText[];
  linkedExperiments: string[];
  metrics: {
    significance: number;
    confidence: number;
    reproducibility: number;
  };
  quantitativeSignals: DiscoveryMetric[];
  literatureRefs: string[];
  nextStep: SemanticText;
}

export interface ResearchHypothesis {
  id: string;
  state: DiscoveryState;
  title: MultilingualText;
  claim: SemanticText;
  rationale: SemanticText;
  evidenceIds: string[];
  blocker: SemanticText;
  nextExperiment: SemanticText;
  confidence: number;
}

export interface OpenQuestion {
  id: string;
  title: MultilingualText;
  question: SemanticText;
  whyOpen: SemanticText;
  priority: 'high' | 'medium' | 'low';
  relatedFindingIds: string[];
}

export interface ScientificMemoryEntry {
  id: string;
  date: string;
  type: 'experiment' | 'finding' | 'hypothesis' | 'question' | 'literature';
  title: MultilingualText;
  narrative: SemanticText;
  linkedIds: string[];
}

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
