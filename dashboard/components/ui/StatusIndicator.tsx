'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import type { Dictionary } from '@/types';

interface StatusIndicatorProps {
  status: 'online' | 'processing' | 'idle';
  dict: Dictionary;
}

const STATUS_CONFIG = {
  online: { color: 'bg-emerald-400', label: (d: Dictionary) => d.status.online },
  processing: { color: 'bg-amber-400', label: (d: Dictionary) => d.status.processing },
  idle: { color: 'bg-white/30', label: (d: Dictionary) => d.status.idle },
} as const;

export function StatusIndicator({ status, dict }: StatusIndicatorProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center justify-center">
        {/* Pulse ring */}
        {status !== 'idle' && (
          <motion.div
            animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
            transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
            className={cn('absolute w-2 h-2 rounded-full', config.color, 'opacity-40')}
          />
        )}
        <div className={cn('w-2 h-2 rounded-full', config.color)} />
      </div>
      <span className="hidden text-xs text-white/50 sm:inline">{config.label(dict)}</span>
    </div>
  );
}
