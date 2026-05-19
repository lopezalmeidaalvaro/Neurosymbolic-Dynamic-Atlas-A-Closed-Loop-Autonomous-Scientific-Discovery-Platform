// ═══════════════════════════════════════════════════════════════
// constants/index.ts — App-wide constants
// ═══════════════════════════════════════════════════════════════
import type { NavItem } from '@/types';

export const APP_NAME = 'Neurosymbolic Atlas';
export const APP_VERSION = '1.0.0-phase1';
export const GITHUB_URL =
  'https://github.com/lopezalmeidaalvaro/Neurosymbolic-Pipeline-for-Dynamical-Systems-Embedding';

export const SIDEBAR_WIDTH = 240;
export const SIDEBAR_COLLAPSED_WIDTH = 64;

export const NAV_ITEMS: NavItem[] = [
  {
    id: 'overview',
    label: { en: 'Overview', es: 'Resumen' },
    href: '/dashboard',
    icon: 'LayoutDashboard',
  },
  {
    id: 'learn',
    label: { en: 'Learn', es: 'Aprender' },
    href: '/learn',
    icon: 'BookOpen',
  },
  {
    id: 'discoveries',
    label: { en: 'Discoveries', es: 'Descubrimientos' },
    href: '/discoveries',
    icon: 'Sparkles',
  },
  {
    id: 'timeline',
    label: { en: 'Timeline', es: 'Línea de Tiempo' },
    href: '/dashboard/timeline',
    icon: 'GitBranch',
  },
  {
    id: 'benchmark',
    label: { en: 'Benchmark', es: 'Benchmark' },
    href: '/dashboard/benchmark',
    icon: 'BarChart3',
    badge: 'SOTA',
  },
  {
    id: 'log',
    label: { en: 'Scientific Log', es: 'Log Científico' },
    href: '/dashboard/scientific-log',
    icon: 'ScrollText',
  },
  {
    id: 'roadmap',
    label: { en: 'Roadmap', es: 'Hoja de Ruta' },
    href: '/dashboard/roadmap',
    icon: 'Map',
  },
];

export const PALETTE = {
  bg: '#030712',
  cyan: '#22d3ee',
  blue: '#3b82f6',
  violet: '#8b5cf6',
} as const;
