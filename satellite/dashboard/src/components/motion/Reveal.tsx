'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface RevealProps extends HTMLMotionProps<'div'> {
  delay?: number;
}

export function Reveal({ children, className, delay = 0, ...props }: RevealProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      transition={{ duration: 0.75, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}
