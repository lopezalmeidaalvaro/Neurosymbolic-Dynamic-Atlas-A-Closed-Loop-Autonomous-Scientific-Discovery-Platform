'use client';

import { useState } from 'react';
import { Lightbulb, Microscope } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAppStore } from '@/stores/appStore';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, MultilingualText, SemanticText } from '@/types';

interface InteractiveAnalogyProps {
  title: MultilingualText;
  analogy: SemanticText;
  technical: SemanticText;
  lang: Language;
}

export function InteractiveAnalogy({ title, analogy, technical, lang }: InteractiveAnalogyProps) {
  const [mode, setMode] = useState<'analogy' | 'science'>('analogy');
  const { complexityMode } = useAppStore();
  const activeText = mode === 'analogy' ? analogy : technical;

  return (
    <GlassPanel density="normal">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="metric-label">{lang === 'es' ? 'Puente mental' : 'Mental bridge'}</p>
          <h3 className="mt-1 text-base font-semibold text-white/90">{title[lang]}</h3>
        </div>
        <div className="flex rounded-xl border border-white/[0.08] bg-white/[0.035] p-1">
          {[
            { id: 'analogy' as const, icon: Lightbulb, label: lang === 'es' ? 'Analogía' : 'Analogy' },
            { id: 'science' as const, icon: Microscope, label: lang === 'es' ? 'Ciencia' : 'Science' },
          ].map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              type="button"
              onClick={() => setMode(id)}
              className={cn(
                'inline-flex h-8 items-center gap-1.5 rounded-lg px-2.5 text-xs transition-colors',
                mode === id ? 'bg-cyan-100/10 text-cyan-100' : 'text-slate-500 hover:text-slate-200'
              )}
            >
              <Icon size={13} />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </div>
      <p className="text-sm leading-7 text-slate-300/74">{activeText[complexityMode][lang]}</p>
    </GlassPanel>
  );
}
