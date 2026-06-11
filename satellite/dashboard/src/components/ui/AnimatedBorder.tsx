'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface AnimatedBorderProps {
  children: React.ReactNode;
  className?: string;
  color?: 'cyan' | 'blue' | 'violet' | 'emerald';
  active?: boolean;
}

const COLOR_MAP = {
  cyan: 'from-cyan-500/60 via-cyan-400/20 to-transparent',
  blue: 'from-blue-500/60 via-blue-400/20 to-transparent',
  violet: 'from-violet-500/60 via-violet-400/20 to-transparent',
  emerald: 'from-emerald-500/60 via-emerald-400/20 to-transparent',
};

export function AnimatedBorder({
  children,
  className,
  color = 'cyan',
  active = true,
}: AnimatedBorderProps) {
  return (
    <div className={cn('relative rounded-xl p-px overflow-hidden', className)}>
      {/* Rotating gradient border */}
      {active && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          className={cn(
            'absolute inset-0 rounded-xl bg-gradient-conic opacity-60',
            `bg-[conic-gradient(from_0deg,transparent_60%,var(--border-color)_80%,transparent_100%)]`
          )}
          style={
            {
              '--border-color':
                color === 'cyan' ? '#22d3ee44'
                : color === 'blue' ? '#3b82f644'
                : color === 'violet' ? '#8b5cf644'
                : '#10b98144',
            } as React.CSSProperties
          }
        />
      )}
      {/* Static gradient fallback */}
      <div
        className={cn(
          'absolute inset-0 rounded-xl bg-gradient-to-br opacity-30',
          COLOR_MAP[color]
        )}
      />
      {/* Inner content */}
      <div className="relative rounded-[11px] bg-[#030712] overflow-hidden">
        {children}
      </div>
    </div>
  );
}
