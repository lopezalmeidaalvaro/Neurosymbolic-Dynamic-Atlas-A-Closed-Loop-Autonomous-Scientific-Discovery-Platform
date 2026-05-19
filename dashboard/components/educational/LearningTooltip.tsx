'use client';

import { useState } from 'react';
import { HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

interface LearningTooltipProps {
  label: string;
  children: React.ReactNode;
  className?: string;
}

export function LearningTooltip({ label, children, className }: LearningTooltipProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className={cn('relative inline-flex align-middle', className)}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        aria-label={label}
        aria-expanded={open}
        className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-cyan-100/18 bg-cyan-100/[0.06] text-cyan-100/75 transition-colors hover:text-cyan-50"
      >
        <HelpCircle size={13} />
      </button>
      {open && (
        <div
          role="tooltip"
          className="absolute left-1/2 top-8 z-50 w-72 -translate-x-1/2 rounded-2xl border border-white/[0.1] bg-[rgba(5,8,16,0.94)] p-4 text-left text-xs leading-6 text-slate-300 shadow-[0_24px_80px_rgba(0,0,0,0.42)] backdrop-blur-2xl"
        >
          {children}
        </div>
      )}
    </div>
  );
}
