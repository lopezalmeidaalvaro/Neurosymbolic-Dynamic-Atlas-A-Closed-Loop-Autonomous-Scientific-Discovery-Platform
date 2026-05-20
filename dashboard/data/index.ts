// ═══════════════════════════════════════════════════════════════
// dashboard/data/index.ts — Consolidated Data Registry
// ═══════════════════════════════════════════════════════════════

import { researchFindings } from './researchFindings';
import { hypotheses } from './hypotheses';
import { openQuestions } from './openQuestions';
import { educationalConcepts } from './learningData';
import { bibliography } from './bibliography';

import type {
  ResearchFinding,
  ResearchHypothesis,
  OpenQuestion,
  EducationalConcept,
  ScientificReference
} from '@/types';

// Re-export all individual data modules for seamless integration
export * from './researchFindings';
export * from './hypotheses';
export * from './openQuestions';
export * from './learningData';
export * from './bibliography';
export * from './benchmarkData';
export * from './projectInfo';
export * from './scientificLog';
export * from './scientificMemory';
export * from './theoryData';
export * from './timelineData';
export * from './roadmapData';

/**
 * Retrieves a research finding by its unique ID.
 */
export function getFindingById(id: string): ResearchFinding | undefined {
  return researchFindings.find((f) => f.id === id);
}

/**
 * Retrieves a research hypothesis by its unique ID.
 */
export function getHypothesisById(id: string): ResearchHypothesis | undefined {
  return hypotheses.find((h) => h.id === id);
}

/**
 * Retrieves an open scientific question by its unique ID.
 */
export function getOpenQuestionById(id: string): OpenQuestion | undefined {
  return openQuestions.find((q) => q.id === id);
}

/**
 * Retrieves an educational concept by its unique ID.
 */
export function getConceptById(id: string): EducationalConcept | undefined {
  return educationalConcepts.find((c) => c.id === id);
}

/**
 * Retrieves a peer-reviewed bibliography reference by its unique ID.
 */
export function getBibliographyEntryById(id: string): ScientificReference | undefined {
  return bibliography.find((b) => b.id === id);
}
