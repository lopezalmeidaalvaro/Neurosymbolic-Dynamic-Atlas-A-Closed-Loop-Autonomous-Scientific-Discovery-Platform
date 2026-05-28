'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Globe } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { SUPPORTED_LANGUAGES } from '@/lib/i18n/dictionaries';
import type { Language } from '@/types';

interface LanguageSwitcherProps {
  lang: Language;
}

export function LanguageSwitcher({ lang }: LanguageSwitcherProps) {
  const router = useRouter();
  const pathname = usePathname();

  const switchTo = (target: Language) => {
    // Replace the current lang segment with the target lang
    const newPath = pathname.replace(`/${lang}`, `/${target}`);
    router.push(newPath);
  };

  return (
    <div className="flex items-center gap-1">
      <Globe size={13} className="text-white/30 mr-1" />
      {SUPPORTED_LANGUAGES.map((l) => (
        <button
          type="button"
          key={l}
          onClick={() => switchTo(l)}
          aria-label={`Switch language to ${l}`}
          className={cn(
            'text-xs px-2 py-1 rounded transition-all duration-150 font-medium uppercase tracking-wide',
            l === lang
              ? 'bg-white/10 text-white/90 border border-white/10'
              : 'text-white/30 hover:text-white/60 hover:bg-white/[0.04]'
          )}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
