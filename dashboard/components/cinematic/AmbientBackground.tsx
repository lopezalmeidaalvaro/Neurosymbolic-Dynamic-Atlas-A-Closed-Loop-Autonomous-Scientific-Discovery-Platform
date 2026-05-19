'use client';

import { usePathname } from 'next/navigation';
import { AuroraLayer } from './AuroraLayer';
import { DynamicGlow } from './DynamicGlow';
import { FloatingParticles } from './FloatingParticles';
import { NoiseTexture } from './NoiseTexture';
import { RadialIllumination } from './RadialIllumination';
import { ScientificGrid } from './ScientificGrid';

function toneFromPath(pathname: string) {
  if (pathname.includes('/benchmark')) return 'benchmark' as const;
  if (pathname.includes('/learn')) return 'active' as const;
  if (pathname.includes('/discoveries')) return 'validated' as const;
  if (pathname.includes('/log') || pathname.includes('/scientific-log')) return 'active' as const;
  if (pathname.includes('/roadmap')) return 'validated' as const;
  return 'neutral' as const;
}

export function AmbientBackground() {
  const pathname = usePathname();
  const tone = toneFromPath(pathname);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-[var(--surface-void)]">
      <div className="absolute inset-0 bg-[linear-gradient(180deg,#02040a_0%,#050810_44%,#02040a_100%)]" />
      <ScientificGrid intensity="medium" />
      <RadialIllumination origin="top" className="opacity-80" />
      <AuroraLayer tone={tone} />
      <DynamicGlow />
      <div className="absolute inset-0 topology-overlay opacity-[0.13]" />
      <FloatingParticles count={26} className="opacity-70" />
      <NoiseTexture className="opacity-[0.28]" />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(2,4,10,0.72),transparent_18%,transparent_76%,rgba(2,4,10,0.72))]" />
    </div>
  );
}
