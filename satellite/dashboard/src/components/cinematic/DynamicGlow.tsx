'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';

interface DynamicGlowProps {
  className?: string;
}

export function DynamicGlow({ className }: DynamicGlowProps) {
  const { systemStatus, activeExperimentStatus } = useAppStore();
  const isActive = systemStatus === 'processing' || activeExperimentStatus === 'running';
  const isValidated = activeExperimentStatus === 'completed';

  return (
    <motion.div
      aria-hidden
      className={cn('pointer-events-none absolute inset-0', className)}
      animate={{
        opacity: isActive ? 0.9 : isValidated ? 0.75 : 0.52,
      }}
      transition={{ duration: 1.8, ease: 'easeOut' }}
    >
      <motion.div
        className={cn(
          'absolute inset-x-[12%] top-[10%] h-[28rem] blur-3xl',
          isValidated
            ? 'bg-[radial-gradient(ellipse_at_center,rgba(87,199,133,0.13),transparent_68%)]'
            : isActive
              ? 'bg-[radial-gradient(ellipse_at_center,rgba(125,211,252,0.16),transparent_68%)]'
              : 'bg-[radial-gradient(ellipse_at_center,rgba(148,163,184,0.10),transparent_68%)]'
        )}
        animate={{ scale: isActive ? [1, 1.045, 1] : [1, 1.015, 1] }}
        transition={{ duration: isActive ? 8 : 14, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.div>
  );
}
