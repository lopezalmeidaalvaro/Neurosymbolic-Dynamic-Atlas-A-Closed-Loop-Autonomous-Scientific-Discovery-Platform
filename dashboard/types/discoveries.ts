// ═══════════════════════════════════════════════════════════════
// types/discoveries.ts — Scientific findings, hypotheses & memory
// ═══════════════════════════════════════════════════════════════

import type { MultilingualText, SemanticText } from './scientific';

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

export interface NoiseRun {
  session_id: string;
  noise_level: number;
  accuracy: number;
  rocket_accuracy: number;
  dtw_accuracy: number;
  average_drift: number;
  drift_by_system: Record<string, number>;
}

export interface EvaluatedHypothesis {
  hypothesis: string;
  status: string;
  evidence: string;
  critical_collapse_points?: {
    noise_level: number;
    accuracy: number;
    average_drift: number;
  }[];
}

export interface NoiseRobustnessReport {
  metadata: {
    title: string;
    timestamp: string;
    pipeline_model: string;
  };
  analysis_results: {
    baseline_session_id: string;
    systems_analyzed: string[];
    runs: NoiseRun[];
  };
  hypotheses_evaluation: Record<string, EvaluatedHypothesis>;
}

// ── Phase 3.3B: Massive Sweep Certification Types ────────────────────────────
// Matches massive_sweep_report.json produced by save_massive_sweep_report().
// certified_results is an ARRAY — each element carries a "system" key.
// Verified against real JSON output on 2026-05-20.

export type CriticalLevel = 'strong' | 'moderate' | 'none';
export type ReproducibilityStatus = 'validated' | 'replicated' | 'preliminary' | 'uncertain';

export interface CertificationEvidence {
  acceleration: number;
  acceleration_std: number;
  seed_count: number;
}

export interface Certification {
  version: string;                    // e.g. "1.2.0"
  critical_level: CriticalLevel;
  critical_score: number;
  confidence_score: number;           // confidence_v2 = seed_factor * stability_factor
  confidence_method: string;          // e.g. "confidence_v2"
  reproducibility_status: ReproducibilityStatus;
  evidence: CertificationEvidence;
}

export type CertificationBlock = Certification;

export interface CertifiedSystemResult {
  system: string;
  noise: number[];
  mean_drift: number[];
  std_drift: number[];
  velocity: number[];
  acceleration: number[];
  mean_accuracy: number[];
  std_accuracy: number[];
  mean_rocket_accuracy: number[];
  std_rocket_accuracy: number[];
  mean_dtw_accuracy: number[];
  std_dtw_accuracy: number[];
  certification: Certification;
}

export interface MassiveSweepReport {
  metadata: {
    title: string;
    timestamp: string;
    pipeline_model: string;
    certification_schema_version: string;  // "1.2.0"
    confidence_method: string;             // "confidence_v2"
    systems: string[];
    seeds: number[];
    noise_levels: number[];
  };
  /** Raw mathematical results dict (unchanged vectors) */
  results: Record<string, Omit<CertifiedSystemResult, 'system' | 'certification'>>;
  /** Single source of truth for certified data — typed as ARRAY, not dict */
  certified_results: CertifiedSystemResult[];
}

export interface HistoricalReport {
  timestamp: string;
  file: string;
  systems: string[];
  seeds: number[];
  noise_levels: number[];
  certification_schema_version?: string;
  confidence_method?: string;
}

export interface HistoryIndex {
  reports: HistoricalReport[];
}
