'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface FloatingParticlesProps {
  className?: string;
  count?: number;
}

const PARTICLES = Array.from({ length: 34 }, (_, index) => ({
  id: index,
  left: (index * 29) % 100,
  top: (index * 47) % 100,
  size: 1 + (index % 3),
  delay: (index % 9) * 0.8,
  duration: 15 + (index % 7) * 2,
}));

export function FloatingParticles({ className, count = 24 }: FloatingParticlesProps) {
  // Dual safety: bypass particle animation calculations in development environment
  if (process.env.NODE_ENV === 'development') return null;

  return (
    <div aria-hidden className={cn('pointer-events-none absolute inset-0 overflow-hidden', className)}>
      {PARTICLES.slice(0, count).map((particle) => (
        <motion.span
          key={particle.id}
          className="absolute rounded-full bg-white/35 shadow-[0_0_18px_rgba(186,230,253,0.18)]"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`,
            width: particle.size,
            height: particle.size,
          }}
          animate={{
            y: [-10, -42, -10],
            x: [0, particle.id % 2 === 0 ? 16 : -16, 0],
            opacity: [0, 0.48, 0],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}
