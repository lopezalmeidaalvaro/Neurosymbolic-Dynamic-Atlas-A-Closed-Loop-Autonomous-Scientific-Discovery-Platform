import { cn } from '@/lib/utils/cn';

interface ScientificSurfaceProps {
  children: React.ReactNode;
  className?: string;
  grid?: boolean;
}

export function ScientificSurface({ children, className, grid = false }: ScientificSurfaceProps) {
  return (
    <section
      style={{
        backgroundColor: 'rgba(20, 20, 25, 0.95)',
        // backdropFilter: 'blur(40px)', // Disabled for dev environment performance
      }}
      className={cn(
        'relative overflow-hidden rounded-[1.5rem] border border-white/[0.08]',
        'shadow-[0_30px_90px_rgba(0,0,0,0.30)]',
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
