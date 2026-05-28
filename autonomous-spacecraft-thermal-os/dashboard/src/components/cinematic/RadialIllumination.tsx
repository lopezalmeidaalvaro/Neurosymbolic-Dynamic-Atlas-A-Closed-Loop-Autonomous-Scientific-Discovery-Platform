import { cn } from '@/lib/utils/cn';

interface RadialIlluminationProps {
  className?: string;
  origin?: 'center' | 'top' | 'left';
}

const ORIGIN = {
  center: 'bg-[radial-gradient(circle_at_50%_24%,rgba(226,232,240,0.14),transparent_42%)]',
  top: 'bg-[radial-gradient(circle_at_50%_0%,rgba(203,213,225,0.16),transparent_44%)]',
  left: 'bg-[radial-gradient(circle_at_16%_18%,rgba(186,230,253,0.16),transparent_42%)]',
};

export function RadialIllumination({ className, origin = 'top' }: RadialIlluminationProps) {
  return <div aria-hidden className={cn('pointer-events-none absolute inset-0', ORIGIN[origin], className)} />;
}
