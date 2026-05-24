'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: 'cyan' | 'blue' | 'violet' | 'emerald' | 'none';
  padding?: 'sm' | 'md' | 'lg';
}

const GLOW_CLASSES = {
  cyan: 'hover:shadow-cyan-500/10 hover:border-cyan-500/30',
  blue: 'hover:shadow-blue-500/10 hover:border-blue-500/30',
  violet: 'hover:shadow-violet-500/10 hover:border-violet-500/30',
  emerald: 'hover:shadow-emerald-500/10 hover:border-emerald-500/30',
  none: '',
};

const PADDING_CLASSES = {
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-7',
};

export function GlassCard({
  children,
  className,
  hover = false,
  glow = 'none',
  padding = 'md',
}: GlassCardProps) {
  return (
    <motion.div
      whileHover={hover ? { y: -2 } : undefined}
      transition={{ duration: 0.15 }}
      style={{
        backgroundColor: 'rgba(20, 20, 25, 0.95)',
        // backdropFilter: 'blur(4px)', // Disabled for dev environment performance
      }}
      className={cn(
        'rounded-xl border border-white/[0.06]',
        'shadow-lg transition-all duration-200',
        hover && 'cursor-pointer',
        hover && GLOW_CLASSES[glow],
        PADDING_CLASSES[padding],
        className
      )}
    >
      {children}
    </motion.div>
  );
}
