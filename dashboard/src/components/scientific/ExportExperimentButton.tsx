'use client';

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, FileJson, FileText, Check, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import type { ExperimentSession, Language } from '@/types';

interface ExportBenchmark {
  modelName: string;
  accuracy: number;
  timeSeconds: number;
}

interface ExportExperimentButtonProps {
  lang: Language;
  sessionId: string;
  sessionData: ExperimentSession;
  benchmarkData?: readonly ExportBenchmark[];
}

type ExportFormat = 'json' | 'csv' | 'summary';
type ExportState = 'idle' | 'loading' | 'done';

const FORMATS: { id: ExportFormat; icon: typeof FileJson; label: Record<Language, string>; ext: string }[] = [
  { id: 'json',    icon: FileJson, label: { en: 'Export JSON',    es: 'Exportar JSON'    }, ext: 'json' },
  { id: 'csv',     icon: FileText, label: { en: 'Export CSV',     es: 'Exportar CSV'     }, ext: 'csv'  },
  { id: 'summary', icon: FileText, label: { en: 'Summary Report', es: 'Reporte Resumen'  }, ext: 'txt'  },
];

function toCSV<T extends object>(data: readonly T[], keys: readonly (keyof T)[]): string {
  const header = keys.join(',');
  const rows = data.map(row => keys.map(k => JSON.stringify(row[k] ?? '')).join(','));
  return [header, ...rows].join('\n');
}

function ExportExperimentButtonComponent({
  lang,
  sessionId,
  sessionData,
  benchmarkData = [],
}: ExportExperimentButtonProps) {
  const mountedRef = useRef(false);
  const processingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const resetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [open, setOpen] = useState(false);
  const [states, setStates] = useState<Record<ExportFormat, ExportState>>({
    json: 'idle', csv: 'idle', summary: 'idle',
  });

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (processingTimerRef.current) clearTimeout(processingTimerRef.current);
      if (resetTimerRef.current) clearTimeout(resetTimerRef.current);
    };
  }, []);

  const triggerDownload = useCallback((content: string, filename: string, mime: string) => {
    const blob = new Blob([content], { type: mime });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const doExport = useCallback(async (fmt: ExportFormat) => {
    setStates(s => ({ ...s, [fmt]: 'loading' }));

    await new Promise<void>(resolve => {
      processingTimerRef.current = setTimeout(resolve, 520);
    });

    if (!mountedRef.current) return;

    const stamp = new Date().toISOString().slice(0, 10);

    if (fmt === 'json') {
      const payload = JSON.stringify({ session: sessionData, benchmarks: benchmarkData }, null, 2);
      triggerDownload(payload, `${sessionId}_${stamp}.json`, 'application/json');
    } else if (fmt === 'csv') {
      if (benchmarkData.length > 0) {
        const csv = toCSV(benchmarkData, ['modelName', 'accuracy', 'timeSeconds']);
        triggerDownload(csv, `${sessionId}_benchmark_${stamp}.csv`, 'text/csv');
      }
    } else {
      const lines = [
        `NEUROSYMBOLIC DYNAMIC ATLAS — SESSION REPORT`,
        `Generated: ${new Date().toISOString()}`,
        `Session ID: ${sessionId}`,
        `Status: ${sessionData.status}`,
        `Noise Level: ${sessionData.noiseLevel}`,
        `Started: ${sessionData.startedAt}`,
        `Completed: ${sessionData.completedAt ?? 'N/A'}`,
        ``,
        `BENCHMARK RESULTS`,
        ...benchmarkData.map(b =>
          `  ${b.modelName.padEnd(24)} accuracy=${(b.accuracy * 100).toFixed(1)}%  time=${b.timeSeconds.toFixed(3)}s`
        ),
      ];
      triggerDownload(lines.join('\n'), `${sessionId}_report_${stamp}.txt`, 'text/plain');
    }

    setStates(s => ({ ...s, [fmt]: 'done' }));
    if (resetTimerRef.current) clearTimeout(resetTimerRef.current);
    resetTimerRef.current = setTimeout(() => {
      if (mountedRef.current) setStates(s => ({ ...s, [fmt]: 'idle' }));
    }, 2200);
  }, [sessionId, sessionData, benchmarkData, triggerDownload]);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className={cn(
          'flex items-center gap-2 rounded-xl border px-3.5 py-2 text-xs font-semibold transition-all duration-200',
          open
            ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
            : 'border-white/[0.09] bg-white/[0.03] text-slate-300 hover:bg-white/[0.06] hover:text-white hover:border-white/[0.14]'
        )}
      >
        <Download size={13} />
        {lang === 'es' ? 'Exportar' : 'Export'}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: -4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: -4 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-1.5 z-50 min-w-[190px] rounded-2xl border border-white/[0.09] bg-[rgba(9,13,24,0.96)] backdrop-blur-2xl p-2 shadow-[0_24px_70px_rgba(0,0,0,0.5)]"
          >
            {FORMATS.map(f => {
              const st = states[f.id];
              return (
                <button
                  key={f.id}
                  onClick={() => doExport(f.id)}
                  disabled={st === 'loading'}
                  className={cn(
                    'flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs transition-colors',
                    st === 'done'
                      ? 'text-emerald-400 bg-emerald-500/10'
                      : 'text-slate-300 hover:bg-white/[0.05] hover:text-white'
                  )}
                >
                  {st === 'loading' ? (
                    <Loader2 size={12} className="animate-spin text-cyan-400" />
                  ) : st === 'done' ? (
                    <Check size={12} className="text-emerald-400" />
                  ) : (
                    <f.icon size={12} className="text-slate-500" />
                  )}
                  <span>{f.label[lang]}</span>
                  <span className="ml-auto font-mono text-[9px] text-slate-600">.{f.ext}</span>
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export const ExportExperimentButton = memo(ExportExperimentButtonComponent);
