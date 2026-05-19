'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { StatusIndicator } from '@/components/ui/StatusIndicator';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';
import { ComplexitySwitcher } from '@/components/ui/ComplexitySwitcher';
import { FocusMode } from '@/components/layout/FocusMode';
import { Breadcrumbs } from './Breadcrumbs';
import type { Dictionary, Language } from '@/types';

interface HeaderProps {
  lang: Language;
  dict: Dictionary;
}

export function Header({ lang, dict }: HeaderProps) {
  const { systemStatus } = useAppStore();

  return (
    <motion.header
      initial={{ y: -8, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
      className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/[0.08] bg-[rgba(3,6,14,0.62)] px-5 backdrop-blur-2xl lg:px-7"
    >
      <div aria-hidden className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent" />
      <Breadcrumbs lang={lang} dict={dict} />

      <div className="flex items-center gap-2 sm:gap-3">
        <FocusMode />
        <ComplexitySwitcher dict={dict} />
        <div className={cn('hidden h-4 w-px bg-white/10 sm:block')} />
        <StatusIndicator status={systemStatus} dict={dict} />
        <div className={cn('h-4 w-px bg-white/10')} />
        <LanguageSwitcher lang={lang} />
      </div>
    </motion.header>
  );
}
