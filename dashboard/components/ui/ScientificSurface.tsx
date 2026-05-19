import { cn } from '@/lib/utils/cn';

interface ScientificSurfaceProps {
  children: React.ReactNode;
  className?: string;
  grid?: boolean;
}

export function ScientificSurface({ children, className, grid = false }: ScientificSurfaceProps) {
  return (
    <section
      className={cn(
        'relative overflow-hidden rounded-[1.5rem] border border-white/[0.08]',
        'bg-[linear-gradient(180deg,rgba(10,16,30,0.72),rgba(4,7,14,0.70))]',
        'shadow-[0_30px_90px_rgba(0,0,0,0.30)] backdrop-blur-2xl',
        className
      )}
    >
      {grid && <div aria-hidden className="absolute inset-0 scientific-grid opacity-[0.13]" />}
      <div aria-hidden className="absolute inset-0 bg-[radial-gradient(circle_at_16%_0%,rgba(125,211,252,0.11),transparent_34%)]" />
      <div aria-hidden className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/35 to-transparent" />
      <div className="relative z-10">{children}</div>
    </section>
  );
}
