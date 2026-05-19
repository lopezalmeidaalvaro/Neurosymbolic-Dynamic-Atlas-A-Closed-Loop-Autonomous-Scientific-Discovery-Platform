import { cn } from '@/lib/utils/cn';

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  density?: 'compact' | 'normal' | 'spacious';
  tone?: 'neutral' | 'active' | 'success' | 'warning';
}

const DENSITY = {
  compact: 'p-4',
  normal: 'p-5 lg:p-6',
  spacious: 'p-6 lg:p-8',
};

const TONE = {
  neutral: 'border-white/[0.09]',
  active: 'border-cyan-200/18 shadow-[0_22px_70px_rgba(14,165,233,0.08)]',
  success: 'border-emerald-200/18 shadow-[0_22px_70px_rgba(16,185,129,0.08)]',
  warning: 'border-amber-200/18 shadow-[0_22px_70px_rgba(245,158,11,0.08)]',
};

export function GlassPanel({
  children,
  className,
  density = 'normal',
  tone = 'neutral',
}: GlassPanelProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-[1.35rem] border bg-[rgba(9,13,24,0.62)]',
        'backdrop-blur-2xl shadow-[0_24px_80px_rgba(0,0,0,0.28)]',
        'before:pointer-events-none before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-white/30 before:to-transparent',
        'after:pointer-events-none after:absolute after:inset-0 after:bg-[radial-gradient(circle_at_22%_0%,rgba(255,255,255,0.07),transparent_32%)]',
        DENSITY[density],
        TONE[tone],
        className
      )}
    >
      <div className="relative z-10">{children}</div>
    </div>
  );
}
