'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Atom, Orbit, Binary, Cpu, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import type { Language } from '@/types';

interface DomainSelectorProps {
  lang: Language;
}

interface DomainOption {
  id: string;
  name: { en: string; es: string };
  icon: React.ComponentType<any>;
  path: string;
  colorClass: string;
  glowClass: string;
}

const DOMAINS: DomainOption[] = [
  {
    id: 'physics',
    name: { en: 'Physics', es: 'Física' },
    icon: Atom,
    path: '/dashboard', // Physics redirects to default dashboard view
    colorClass: 'text-emerald-400',
    glowClass: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300 shadow-[0_0_12px_rgba(52,211,153,0.12)]',
  },
  {
    id: 'satellite',
    name: { en: 'Satellite', es: 'Satélite' },
    icon: Orbit,
    path: '/satellite',
    colorClass: 'text-cyan-400',
    glowClass: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.12)]',
  },
  {
    id: 'mathematics',
    name: { en: 'Mathematics', es: 'Matemáticas' },
    icon: Binary,
    path: '/mathematics',
    colorClass: 'text-amber-400',
    glowClass: 'bg-amber-500/10 border-amber-500/20 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.12)]',
  },
  {
    id: 'quantum',
    name: { en: 'Quantum Lab', es: 'Lab Cuántico' },
    icon: Cpu,
    path: '/quantum',
    colorClass: 'text-violet-400',
    glowClass: 'bg-violet-500/10 border-violet-500/20 text-violet-300 shadow-[0_0_12px_rgba(139,92,246,0.12)]',
  },
];

export function DomainSelector({ lang }: DomainSelectorProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Determine active domain based on URL
  const getActiveDomain = (): DomainOption => {
    if (pathname.includes('/satellite')) {
      return DOMAINS[1]!;
    }
    if (pathname.includes('/mathematics')) {
      return DOMAINS[2]!;
    }
    if (pathname.includes('/quantum')) {
      return DOMAINS[3]!;
    }
    return DOMAINS[0]!; // Default to Physics
  };

  const activeDomain = getActiveDomain();
  const Icon = activeDomain.icon;

  // Handle outside click to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (domain: DomainOption) => {
    setIsOpen(false);
    // Push route preserving language
    router.push(`/${lang}${domain.path}`);
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-3.5 py-1.5 rounded-lg border transition-all duration-200 text-xs font-semibold cursor-pointer border-white/10 bg-white/[0.03] text-white/70 hover:text-white hover:bg-white/[0.06]',
          isOpen && 'border-white/20 bg-white/[0.08]'
        )}
      >
        <span className={cn('flex items-center gap-1.5', activeDomain.colorClass)}>
          <Icon size={14} className="animate-pulse" />
          <span>{activeDomain.name[lang]}</span>
        </span>
        <ChevronDown size={12} className={cn('transition-transform duration-200 text-white/30', isOpen && 'rotate-180')} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="absolute left-0 mt-2 w-52 origin-top-left rounded-xl border border-white/10 bg-[#070b19]/90 p-1.5 backdrop-blur-2xl shadow-[0_10px_30px_rgba(0,0,0,0.5)] z-30"
          >
            <div className="py-1">
              {DOMAINS.map((domain) => {
                const DomIcon = domain.icon;
                const isActive = domain.id === activeDomain.id;

                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => handleSelect(domain)}
                    className={cn(
                      'flex w-full items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-left cursor-pointer transition-all duration-150',
                      isActive
                        ? domain.glowClass
                        : 'text-white/40 hover:text-white/80 hover:bg-white/[0.04]'
                    )}
                  >
                    <DomIcon size={14} className={isActive ? domain.colorClass : 'text-white/30'} />
                    <span className="flex-1">{domain.name[lang]}</span>
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
