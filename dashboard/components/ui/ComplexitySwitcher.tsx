'use client';

import { Brain, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import type { Dictionary } from '@/types';

interface ComplexitySwitcherProps {
  dict: Dictionary;
}

export function ComplexitySwitcher({ dict }: ComplexitySwitcherProps) {
  const { complexityMode, setComplexityMode } = useAppStore();

  return (
    <div className="flex items-center gap-1">
      <span className="text-xs text-white/30 mr-1 hidden sm:block">
        {dict.complexity.label}
      </span>
      <div className="flex items-center rounded-lg border border-white/10 bg-white/[0.03] p-0.5">
        <button
          type="button"
          onClick={() => setComplexityMode('simple')}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all duration-150',
            complexityMode === 'simple'
              ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/20'
              : 'text-white/30 hover:text-white/60'
          )}
          title="Simple mode"
        >
          <FlaskConical size={12} />
          <span className="hidden md:inline">{dict.complexity.simple}</span>
        </button>
        <button
          type="button"
          onClick={() => setComplexityMode('advanced')}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all duration-150',
            complexityMode === 'advanced'
              ? 'bg-violet-500/15 text-violet-300 border border-violet-500/20'
              : 'text-white/30 hover:text-white/60'
          )}
          title="Advanced mode"
        >
          <Brain size={12} />
          <span className="hidden md:inline">{dict.complexity.advanced}</span>
        </button>
      </div>
    </div>
  );
}
