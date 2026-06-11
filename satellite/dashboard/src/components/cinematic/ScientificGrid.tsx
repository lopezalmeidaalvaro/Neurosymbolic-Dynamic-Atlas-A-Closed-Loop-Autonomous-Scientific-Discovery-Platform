import { cn } from '@/lib/utils/cn';

interface ScientificGridProps {
  className?: string;
  intensity?: 'low' | 'medium' | 'high';
}

const INTENSITY = {
  low: 'opacity-[0.12]',
  medium: 'opacity-[0.18]',
  high: 'opacity-[0.26]',
};

export function ScientificGrid({ className, intensity = 'medium' }: ScientificGridProps) {
  return (
    <div
      aria-hidden
      className={cn(
        'pointer-events-none absolute inset-0',
        INTENSITY[intensity],
        className
      )}
    >
      <div className="absolute inset-0 scientific-grid" />
      <div className="absolute inset-0 scientific-grid-major" />
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
    </div>
  );
}
