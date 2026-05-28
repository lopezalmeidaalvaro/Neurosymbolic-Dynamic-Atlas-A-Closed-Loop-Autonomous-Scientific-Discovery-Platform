'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface AuroraLayerProps {
  className?: string;
  tone?: 'neutral' | 'active' | 'validated' | 'benchmark';
}

const TONE_CLASS = {
  neutral: 'from-sky-300/10 via-teal-300/5 to-violet-300/10',
  active: 'from-cyan-300/14 via-emerald-300/8 to-blue-300/12',
  validated: 'from-emerald-300/14 via-teal-300/8 to-sky-300/10',
  benchmark: 'from-amber-200/10 via-cyan-300/8 to-violet-300/12',
};

export function AuroraLayer({ className, tone = 'neutral' }: AuroraLayerProps) {
  return (
    <motion.div
      aria-hidden
      className={cn('pointer-events-none absolute inset-0 overflow-hidden', className)}
      initial={false}
    >
      <motion.div
        className={cn(
          'absolute left-[-12%] top-[8%] h-[28rem] w-[72rem] rotate-[-9deg] rounded-[40%]',
          'bg-gradient-to-r blur-3xl',
          TONE_CLASS[tone]
        )}
        animate={{
          x: ['-2%', '4%', '-1%'],
          y: ['0%', '5%', '0%'],
          opacity: [0.58, 0.82, 0.58],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-[-18%] right-[-12%] h-[34rem] w-[64rem] rotate-[11deg] rounded-[42%] bg-gradient-to-r from-indigo-300/8 via-cyan-200/6 to-emerald-200/8 blur-3xl"
        animate={{
          x: ['3%', '-3%', '3%'],
          y: ['0%', '-4%', '0%'],
          opacity: [0.34, 0.58, 0.34],
        }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.div>
  );
}
