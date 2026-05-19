'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface MorphingCardProps extends HTMLMotionProps<'div'> {
  active?: boolean;
}

export function MorphingCard({ children, className, active = false, ...props }: MorphingCardProps) {
  return (
    <motion.div
      layout
      whileHover={{ y: -4, scale: 1.008 }}
      animate={{
        boxShadow: active
          ? '0 30px 80px rgba(45, 212, 191, 0.12)'
          : '0 24px 60px rgba(0, 0, 0, 0.24)',
      }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
