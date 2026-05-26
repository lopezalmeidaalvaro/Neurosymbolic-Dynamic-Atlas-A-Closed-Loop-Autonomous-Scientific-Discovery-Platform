// ═══════════════════════════════════════════════════════════════
// lib/utils/cn.ts — Utility for conditional class merging
// ═══════════════════════════════════════════════════════════════
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes safely without conflicts.
 * Combines clsx (conditional classes) + tailwind-merge (deduplication).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
