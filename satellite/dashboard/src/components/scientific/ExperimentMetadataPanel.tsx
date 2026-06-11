'use client';

import { CalendarClock, Database, GitBranch, Layers, Sigma } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, MassiveSweepReport } from '@/types';

interface ExperimentMetadataPanelProps {
  metadata: MassiveSweepReport['metadata'];
  lang: Language;
}

export function ExperimentMetadataPanel({ metadata, lang }: ExperimentMetadataPanelProps) {
  const items = [
    {
      icon: CalendarClock,
      label: lang === 'es' ? 'Marca temporal' : 'Experiment timestamp',
      value: metadata.timestamp,
    },
    {
      icon: Layers,
      label: lang === 'es' ? 'Sistemas' : 'Systems',
      value: metadata.systems.join(', '),
    },
    {
      icon: GitBranch,
      label: lang === 'es' ? 'Semillas' : 'Seeds',
      value: metadata.seeds.join(', '),
    },
    {
      icon: Sigma,
      label: lang === 'es' ? 'Niveles de ruido' : 'Noise levels',
      value: metadata.noise_levels.join(', '),
    },
    {
      icon: Database,
      label: lang === 'es' ? 'Version del esquema' : 'Certification schema version',
      value: metadata.certification_schema_version,
    },
    {
      icon: Database,
      label: lang === 'es' ? 'Metodo de confianza' : 'Confidence method',
      value: metadata.confidence_method,
    },
  ];

  return (
    <GlassPanel density="spacious" tone="active">
      <div className="mb-5">
        <p className="metric-label">{lang === 'es' ? 'Metadatos del experimento' : 'Experiment metadata'}</p>
        <h2 className="mt-2 text-2xl font-semibold text-white/90">
          {metadata.title}
        </h2>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.label}
              className="rounded-xl border border-white/[0.06] bg-slate-950/35 p-4"
            >
              <div className="mb-3 flex items-center gap-2 text-cyan-200">
                <Icon size={15} />
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-slate-400">
                  {item.label}
                </span>
              </div>
              <p className="break-words font-mono text-sm leading-6 text-slate-100">
                {item.value}
              </p>
            </div>
          );
        })}
      </div>
    </GlassPanel>
  );
}
