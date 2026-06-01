'use client';

import { useEffect, useRef } from 'react';
import katex from 'katex';
import { cn } from '@/lib/utils/cn';

interface KaTeXProps {
  formula: string;
  block?: boolean;
  className?: string;
}

/**
 * Client-side KaTeX renderer.
 * Uses katex.render() imperatively to avoid SSR issues.
 */
export function KaTeX({ formula, block = false, className }: KaTeXProps) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    try {
      katex.render(formula, ref.current, {
        throwOnError: false,
        displayMode: block,
        output: 'html',
      });
    } catch {
      if (ref.current) ref.current.textContent = formula;
    }
  }, [formula, block]);

  return block ? (
    <div
      ref={ref as React.RefObject<HTMLDivElement>}
      className={cn('katex-display my-2 overflow-x-auto', className)}
    />
  ) : (
    <span ref={ref} className={cn('katex-inline', className)} />
  );
}
