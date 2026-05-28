import { cn } from '@/lib/utils/cn';
import type { DiscoveryState, Language } from '@/types';

interface ConfidenceBadgeProps {
  state: DiscoveryState;
  confidence?: number;
  lang: Language;
  className?: string;
}

const STATE_STYLE: Record<DiscoveryState, string> = {
  validated: 'border-cyan-100/24 bg-cyan-100/10 text-cyan-50 shadow-[0_0_28px_rgba(34,211,238,0.12)]',
  observed: 'border-sky-100/22 bg-sky-100/[0.08] text-sky-50',
  hypothesis: 'border-violet-100/24 bg-violet-100/[0.08] text-violet-50 animate-pulse',
  uncertain: 'border-amber-100/24 bg-amber-100/[0.08] text-amber-50',
  rejected: 'border-red-100/18 bg-red-100/[0.055] text-red-100/75',
};

const STATE_LABEL: Record<DiscoveryState, { en: string; es: string }> = {
  validated: { en: 'Validated', es: 'Validado' },
  observed: { en: 'Observed', es: 'Observado' },
  hypothesis: { en: 'Hypothesis', es: 'Hipotesis' },
  uncertain: { en: 'Uncertain', es: 'Incierto' },
  rejected: { en: 'Rejected', es: 'Rechazado' },
};

export function ConfidenceBadge({ state, confidence, lang, className }: ConfidenceBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]',
        STATE_STYLE[state],
        className
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current shadow-[0_0_14px_currentColor]" />
      {STATE_LABEL[state][lang]}
      {typeof confidence === 'number' && <span className="font-mono opacity-75">{confidence}%</span>}
    </span>
  );
}
