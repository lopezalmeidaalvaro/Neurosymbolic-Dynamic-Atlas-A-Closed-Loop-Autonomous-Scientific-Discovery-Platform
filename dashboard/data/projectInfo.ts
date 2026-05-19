// ═══════════════════════════════════════════════════════════════
// data/projectInfo.ts — Static project metadata
// ═══════════════════════════════════════════════════════════════
import type { ProjectInfo } from '@/types';

export const projectInfo: ProjectInfo = {
  name: 'Neurosymbolic Dynamic Atlas',
  tagline: {
    en: 'Geometric classification of nonlinear dynamical systems via latent embeddings.',
    es: 'Clasificación geométrica de sistemas dinámicos no lineales mediante embeddings latentes.',
  },
  description: {
    en: 'An experimental neuro-symbolic research pipeline that maps chaotic attractors, periodic orbits, and noise into a unified latent feature space, enabling interpretable classification with state-of-the-art competitive performance.',
    es: 'Un pipeline de investigación neuro-simbólico experimental que mapea atractores caóticos, órbitas periódicas y ruido en un espacio de características latente unificado, permitiendo clasificación interpretable con rendimiento competitivo al estado del arte.',
  },
  version: '1.0.0',
  status: 'experimental',
  githubUrl:
    'https://github.com/lopezalmeidaalvaro/Neurosymbolic-Pipeline-for-Dynamical-Systems-Embedding',
  totalPhases: 13,
  completedPhases: 13,
};
