'use client';

import { animate, motion, useMotionValue, useTransform } from 'framer-motion';
import { useEffect } from 'react';

interface AnimatedCounterProps {
  value: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}

export function AnimatedCounter({
  value,
  decimals = 0,
  suffix = '',
  prefix = '',
  className,
}: AnimatedCounterProps) {
  const motionValue = useMotionValue(0);
  const rounded = useTransform(motionValue, (latest) => {
    const formatted = latest.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    return `${prefix}${formatted}${suffix}`;
  });

  useEffect(() => {
    const controls = animate(motionValue, value, {
      duration: 1.8,
      ease: [0.22, 1, 0.36, 1],
    });
    return controls.stop;
  }, [motionValue, value]);

  return <motion.span className={className}>{rounded}</motion.span>;
}
