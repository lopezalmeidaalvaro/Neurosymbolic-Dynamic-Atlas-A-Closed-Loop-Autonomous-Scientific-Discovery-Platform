'use client';

import { Maximize2, Minimize2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';

interface FocusModeProps {
  className?: string;
}

export function FocusMode({ className }: FocusModeProps) {
  const { focusModeEnabled, toggleFocusMode } = useAppStore();

  return (
    <button
      type="button"
      onClick={toggleFocusMode}
      aria-pressed={focusModeEnabled}
      className={cn(
        'inline-flex h-8 w-8 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.035] text-slate-400 transition-colors hover:text-white',
        focusModeEnabled && 'border-cyan-100/20 text-cyan-100 shadow-[0_0_28px_rgba(125,211,252,0.10)]',
        className
      )}
      title={focusModeEnabled ? 'Exit focus mode' : 'Enter focus mode'}
    >
      {focusModeEnabled ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
    </button>
  );
}
