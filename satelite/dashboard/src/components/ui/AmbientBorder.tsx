import { cn } from '@/lib/utils/cn';

interface AmbientBorderProps {
  children: React.ReactNode;
  className?: string;
  tone?: 'cyan' | 'emerald' | 'violet' | 'amber' | 'neutral';
}

const TONE = {
  cyan: 'from-cyan-200/30 via-white/8 to-blue-300/20',
  emerald: 'from-emerald-200/28 via-white/8 to-teal-300/18',
  violet: 'from-violet-200/24 via-white/8 to-sky-300/18',
  amber: 'from-amber-200/24 via-white/8 to-cyan-300/16',
  neutral: 'from-white/18 via-white/6 to-white/10',
};

export function AmbientBorder({ children, className, tone = 'neutral' }: AmbientBorderProps) {
  return (
    <div className={cn('relative rounded-[1.35rem] p-px', className)}>
      <div className={cn('absolute inset-0 rounded-[inherit] bg-gradient-to-br', TONE[tone])} />
      <div className="relative rounded-[calc(1.35rem-1px)] bg-[rgba(5,8,16,0.76)]">
        {children}
      </div>
    </div>
  );
}
