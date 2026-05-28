'use client';

import { ReferenceArea } from 'recharts';
import type { CertifiedSystemResult } from '@/types';

interface CriticalRegionDetectorProps {
  result: CertifiedSystemResult;
}

const REGION_STYLE = {
  strong: {
    fill: '#ef4444',
    fillOpacity: 0.12,
    stroke: '#ef4444',
    strokeOpacity: 0.28,
  },
  moderate: {
    fill: '#f59e0b',
    fillOpacity: 0.12,
    stroke: '#f59e0b',
    strokeOpacity: 0.28,
  },
} as const;

export function CriticalRegionDetector({ result }: CriticalRegionDetectorProps) {
  const level = result.certification.critical_level;

  if (level === 'none' || result.noise.length === 0) {
    return null;
  }

  const startNoise = result.noise[0];
  const endNoise = result.noise[result.noise.length - 1];

  if (startNoise === undefined || endNoise === undefined) {
    return null;
  }

  return (
    <ReferenceArea
      x1={startNoise}
      x2={endNoise}
      yAxisId="values"
      ifOverflow="extendDomain"
      {...REGION_STYLE[level]}
    />
  );
}
