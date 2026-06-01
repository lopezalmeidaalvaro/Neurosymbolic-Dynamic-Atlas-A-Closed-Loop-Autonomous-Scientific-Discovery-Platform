// ═══════════════════════════════════════════════════════════════
// types/experiments.ts — Physical simulations & benchmark outcomes
// ═══════════════════════════════════════════════════════════════

import type { MultilingualText, SemanticText } from './scientific';

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

export interface BenchmarkResult {
  id: string;
  modelName: string;
  accuracy: number;
  timeSeconds: number;
  isOurs: boolean;
  color: string;
}

export interface ExperimentSession {
  id: string;
  startedAt: string;
  completedAt?: string;
  status: 'running' | 'completed' | 'failed';
  models: string[];
  noiseLevel: number;
  tags: string[];
  description?: MultilingualText;
}
