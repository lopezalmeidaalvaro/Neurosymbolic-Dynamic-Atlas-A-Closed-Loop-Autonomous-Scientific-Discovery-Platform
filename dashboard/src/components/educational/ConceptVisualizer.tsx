import { cn } from '@/lib/utils/cn';
import type { EducationalConcept } from '@/types';

interface ConceptVisualizerProps {
  type: EducationalConcept['visualType'];
  className?: string;
}

const dots = [
  ['left-[18%] top-[24%] bg-cyan-200', 'left-[24%] top-[36%] bg-cyan-100', 'left-[17%] top-[48%] bg-cyan-300'],
  ['left-[58%] top-[28%] bg-violet-200', 'left-[67%] top-[40%] bg-violet-100', 'left-[55%] top-[52%] bg-violet-300'],
  ['left-[40%] top-[66%] bg-emerald-200', 'left-[48%] top-[72%] bg-emerald-100', 'left-[36%] top-[78%] bg-emerald-300'],
];

export function ConceptVisualizer({ type, className }: ConceptVisualizerProps) {
  if (type === 'embedding' || type === 'geometry') {
    return (
      <div className={cn('relative h-56 overflow-hidden rounded-2xl border border-white/[0.08] bg-black/24', className)}>
        <div className="absolute inset-0 scientific-grid opacity-[0.10]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_45%_35%,rgba(125,211,252,0.10),transparent_42%)]" />
        {dots.flat().map((dot, index) => (
          <div key={dot} className={cn('absolute h-3 w-3 rounded-full shadow-[0_0_22px_currentColor]', dot)}>
            <div className="absolute -inset-3 rounded-full border border-current opacity-10" />
            {type === 'geometry' && index % 3 === 0 && (
              <div className="absolute left-3 top-1 h-px w-16 rotate-12 bg-current opacity-20" />
            )}
          </div>
        ))}
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-slate-500">
          <span>latent map</span>
          <span>neighborhoods</span>
        </div>
      </div>
    );
  }

  if (type === 'noise') {
    return (
      <div className={cn('relative h-56 overflow-hidden rounded-2xl border border-white/[0.08] bg-black/24 p-5', className)}>
        <div className="absolute inset-0 noise-texture opacity-25" />
        <div className="relative mt-12 flex h-20 items-end gap-1">
          {Array.from({ length: 36 }).map((_, i) => (
            <div
              key={i}
              className="w-full rounded-full bg-amber-100/55 shadow-[0_0_18px_rgba(253,230,138,0.12)]"
              style={{ height: `${26 + ((i * 17) % 42)}px` }}
            />
          ))}
        </div>
        <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-slate-500">
          <span>signal</span>
          <span>perturbation</span>
        </div>
      </div>
    );
  }

  if (type === 'comparison') {
    return (
      <div className={cn('relative h-56 overflow-hidden rounded-2xl border border-white/[0.08] bg-black/24 p-5', className)}>
        <div className="grid h-full grid-cols-3 items-end gap-4">
          {[
            ['DTW', 'h-36 bg-violet-200/45'],
            ['ROCKET', 'h-44 bg-sky-200/45'],
            ['Embedding', 'h-16 bg-cyan-100/80'],
          ].map(([label, height]) => (
            <div key={label} className="flex h-full flex-col justify-end gap-3">
              <div className={cn('rounded-t-2xl border border-white/10 shadow-[0_0_30px_rgba(125,211,252,0.10)]', height)} />
              <span className="text-center text-[10px] text-slate-400">{label}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('relative h-56 overflow-hidden rounded-2xl border border-white/[0.08] bg-black/24 p-5', className)}>
      <div className="absolute inset-0 scientific-grid opacity-[0.08]" />
      <div className="relative mt-14 flex h-20 items-center gap-1">
        {Array.from({ length: 42 }).map((_, i) => {
          const height = type === 'wave'
            ? 18 + Math.abs(Math.sin(i / 3)) * 54
            : 22 + ((i * 11) % 38);
          return (
            <div
              key={i}
              className="w-full rounded-full bg-cyan-100/65 shadow-[0_0_18px_rgba(186,230,253,0.10)]"
              style={{ height: `${height}px` }}
            />
          );
        })}
      </div>
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-slate-500">
        <span>time</span>
        <span>amplitude</span>
      </div>
    </div>
  );
}
