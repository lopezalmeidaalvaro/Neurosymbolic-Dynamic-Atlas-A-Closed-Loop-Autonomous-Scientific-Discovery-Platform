// ═══════════════════════════════════════════════════════════════
// types/telemetry.ts — Computational telemetry & pipeline metrics
// ═══════════════════════════════════════════════════════════════

import type { MultilingualText } from './scientific';

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

export type RoadmapStatus = 'done' | 'in-progress' | 'planned';

export interface RoadmapItem {
  id: string;
  title: MultilingualText;
  description: MultilingualText;
  status: RoadmapStatus;
  priority: 'high' | 'medium' | 'low';
  eta?: string;
}

export interface NavItem {
  id: string;
  label: MultilingualText;
  href: string;
  icon: string;
  badge?: string;
}

export type LogSeverity = 'info' | 'success' | 'warning' | 'error' | 'insight';

export interface ScientificLogEntry {
  id: string;
  timestamp: string;
  severity: LogSeverity;
  phase: string;
  message: MultilingualText;
  details?: string;
}
