'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';

interface PremiumCardProps {
  children: React.ReactNode;
  className?: string;
  active?: boolean;
}

export function PremiumCard({ children, className, active = false }: PremiumCardProps) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      style={{
        backgroundColor: 'rgba(20, 20, 25, 0.95)',
        // backdropFilter: 'blur(24px)', // Disabled for dev environment performance
      }}
      className={cn(
        'relative overflow-hidden rounded-[1.15rem] border border-white/[0.08]',
        'shadow-[0_18px_60px_rgba(0,0,0,0.24)]',
        active && 'border-cyan-200/20 shadow-[0_26px_70px_rgba(56,189,248,0.10)]',
        className
      )}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/35 to-transparent" />
      <div className="pointer-events-none absolute -inset-x-12 -top-24 h-40 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.10),transparent_66%)]" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
