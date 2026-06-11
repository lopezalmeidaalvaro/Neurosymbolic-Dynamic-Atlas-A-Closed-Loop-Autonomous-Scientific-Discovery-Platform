'use client';

import { motion } from 'framer-motion';
import { GraduationCap, Smile } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { ComplexitySwitcher } from '@/components/ui/ComplexitySwitcher';
import { FocusMode } from '@/components/layout/FocusMode';
import { Breadcrumbs } from './Breadcrumbs';
import { DomainSelector } from './DomainSelector';
import type { Dictionary, Language } from '@/types';

interface HeaderProps {
  lang: Language;
  dict: Dictionary;
}

export function Header({ lang, dict }: HeaderProps) {
  const { systemStatus, isTeenagerMode, toggleTeenagerMode } = useAppStore();

  return (
    <motion.header
      initial={{ y: -8, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
      className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/[0.08] bg-[rgba(3,6,14,0.62)] px-5 backdrop-blur-2xl lg:px-7"
    >
      <div aria-hidden className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent" />
      <div className="flex items-center gap-4">
        <Breadcrumbs lang={lang} dict={dict} />
        <div className="hidden h-5 w-px bg-white/10 md:block" />
        <DomainSelector lang={lang} />
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <FocusMode />
        <ComplexitySwitcher dict={dict} />
        
        <button
          type="button"
          onClick={toggleTeenagerMode}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-all duration-150 text-xs font-medium cursor-pointer',
            isTeenagerMode
              ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/20 shadow-[0_0_12px_rgba(16,185,129,0.12)]'
              : 'border-white/10 bg-white/[0.03] text-white/30 hover:text-white/60'
          )}
          title={isTeenagerMode ? 'Switch to Scientific Mode' : 'Switch to Teenager Mode (ELI15)'}
        >
          {isTeenagerMode ? (
            <>
              <Smile size={13} className="text-emerald-400" />
              <span className="hidden sm:inline">{lang === 'es' ? 'Modo ELI15' : 'ELI15 Mode'}</span>
            </>
          ) : (
            <>
              <GraduationCap size={13} />
              <span className="hidden sm:inline">{lang === 'es' ? 'Modo Científico' : 'Scientific Mode'}</span>
            </>
          )}
        </button>

        <div className={cn('hidden h-4 w-px bg-white/10 sm:block')} />
        <StatusIndicator status={systemStatus} dict={dict} />
        <div className={cn('h-4 w-px bg-white/10')} />
        <LanguageSwitcher lang={lang} />
      </div>
    </motion.header>
  );
}
