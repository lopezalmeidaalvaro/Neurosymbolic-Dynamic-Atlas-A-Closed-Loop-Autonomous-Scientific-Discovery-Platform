import { cn } from '@/lib/utils/cn';

interface NoiseTextureProps {
  className?: string;
}

export function NoiseTexture({ className }: NoiseTextureProps) {
  return <div aria-hidden className={cn('pointer-events-none absolute inset-0 noise-texture', className)} />;
}
