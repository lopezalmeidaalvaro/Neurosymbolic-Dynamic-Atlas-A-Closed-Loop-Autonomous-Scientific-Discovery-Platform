'use client';

import { memo, useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Pause, Play, Filter, Trash2, Radio } from 'lucide-react';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { cn } from '@/lib/utils/cn';
import type { Language } from '@/types';

// ── Types ──────────────────────────────────────────────────────
type Severity = 'info' | 'warning' | 'error' | 'success' | 'critical';

interface LogLine {
  id: string;
  timestamp: string;
  severity: Severity;
  message: Record<'en' | 'es', string>;
}

interface LiveTelemetryConsoleProps {
  lang: Language;
  sessionId?: string;
}

// ── Severity config ─────────────────────────────────────────────
const SEV: Record<Severity, { dot: string; text: string; badge: string; label: Record<Language, string> }> = {
  info:     { dot: 'bg-sky-400',     text: 'text-sky-300',     badge: 'bg-sky-500/10 border-sky-500/20',     label: { en: 'INFO',     es: 'INFO'     } },
  success:  { dot: 'bg-emerald-400', text: 'text-emerald-300', badge: 'bg-emerald-500/10 border-emerald-500/20', label: { en: 'SUCCESS', es: 'ÉXITO'   } },
  warning:  { dot: 'bg-amber-400',   text: 'text-amber-300',   badge: 'bg-amber-500/10 border-amber-500/20',   label: { en: 'WARNING', es: 'AVISO'    } },
  error:    { dot: 'bg-rose-400',    text: 'text-rose-300',    badge: 'bg-rose-500/10 border-rose-500/20',     label: { en: 'ERROR',   es: 'ERROR'    } },
  critical: { dot: 'bg-red-500',     text: 'text-red-300',     badge: 'bg-red-500/15 border-red-500/30',       label: { en: 'CRITICAL',es: 'CRÍTICO'  } },
};

// ── Static seed log ─────────────────────────────────────────────
const SEED_LOGS: Omit<LogLine, 'id'>[] = [
  { timestamp: '15:00:02', severity: 'info',    message: { en: 'Initializing RK4 integrator (σ=10, ρ=28, β=8/3).', es: 'Inicializando integrador RK4 (σ=10, ρ=28, β=8/3).' } },
  { timestamp: '15:00:08', severity: 'success', message: { en: 'Lorenz attractor integration complete — 1000 steps.', es: 'Integración del atractor de Lorenz completa — 1000 pasos.' } },
  { timestamp: '15:00:21', severity: 'info',    message: { en: 'Computing structural descriptors (8 features).', es: 'Calculando descriptores estructurales (8 características).' } },
  { timestamp: '15:00:35', severity: 'success', message: { en: 'PCA projection completed. Explained variance: 91.4%.', es: 'Proyección PCA completada. Varianza explicada: 91.4%.' } },
  { timestamp: '15:01:12', severity: 'warning', message: { en: 'Marginal entropy elevation in high-frequency band.', es: 'Elevación marginal de entropía en banda de alta frecuencia.' } },
  { timestamp: '15:01:48', severity: 'success', message: { en: 'λ_max = 0.902 > 0 confirmed. Chaotic regime validated.', es: 'λ_max = 0.902 > 0 confirmado. Régimen caótico validado.' } },
];

// ── Streaming log pool ─────────────────────────────────────────
const STREAM_POOL: Omit<LogLine, 'id' | 'timestamp'>[] = [
  { severity: 'info',    message: { en: 'Sampling trajectory snapshot at t+1.', es: 'Muestreando instantánea de trayectoria en t+1.' } },
  { severity: 'info',    message: { en: 'Revalidating attractor basin boundaries.', es: 'Revalidando fronteras de la cuenca del atractor.' } },
  { severity: 'success', message: { en: 'Embedding distance matrix updated.', es: 'Matriz de distancias del embedding actualizada.' } },
  { severity: 'warning', message: { en: 'High curvature region detected in latent manifold.', es: 'Región de alta curvatura detectada en la variedad latente.' } },
  { severity: 'info',    message: { en: 'DBSCAN clustering iteration complete.', es: 'Iteración de clustering DBSCAN completada.' } },
  { severity: 'critical',message: { en: 'Sensitivity threshold exceeded at trajectory fork.', es: 'Umbral de sensibilidad excedido en bifurcación de trayectoria.' } },
  { severity: 'success', message: { en: 'NODE classifier accuracy stable at 98.5%.', es: 'Precisión del clasificador NODE estable en 98.5%.' } },
  { severity: 'info',    message: { en: 'Exporting embedding snapshot to /artifacts/embeddings/', es: 'Exportando instantánea de embedding a /artifacts/embeddings/' } },
];

const seedLog = (line: Omit<LogLine, 'id'>, index: number): LogLine => ({
  ...line,
  id: `seed-log-${index}`,
});

function LiveTelemetryConsoleComponent({ lang }: LiveTelemetryConsoleProps) {
  const nextIdRef = useRef(100);
  const streamIndexRef = useRef(0);
  const [logs, setLogs] = useState<LogLine[]>(
    () => SEED_LOGS.map(seedLog)
  );
  const [paused, setPaused] = useState(false);
  const [activeFilter, setActiveFilter] = useState<Severity | 'all'>('all');
  const endRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Auto-scroll to bottom ──────────────────────────────────
  useEffect(() => {
    if (!paused) endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs, paused]);

  // ── Stream new log lines ────────────────────────────────────
  const tick = useCallback(() => {
    const entry = STREAM_POOL[streamIndexRef.current % STREAM_POOL.length]!;
    streamIndexRef.current += 1;
    const now = new Date();
    const ts = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
    nextIdRef.current += 1;
    const newLine: LogLine = { id: `log-${nextIdRef.current}`, timestamp: ts, severity: entry.severity, message: entry.message };
    setLogs(prev => [...prev.slice(-199), newLine]);
  }, []);

  useEffect(() => {
    if (!paused) {
      intervalRef.current = setInterval(tick, 1800);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [paused, tick]);

  // ── Filtered view ──────────────────────────────────────────
  const visible = useMemo(
    () => activeFilter === 'all' ? logs : logs.filter(l => l.severity === activeFilter),
    [logs, activeFilter]
  );

  const severities = useMemo(
    () => ['all', 'info', 'success', 'warning', 'error', 'critical'] as const,
    []
  );

  return (
    <GlassPanel data-testid="telemetry-console" density="compact" className="flex flex-col gap-0 h-full min-h-[480px]">
      {/* ── Header ────────────────────────────────────────────── */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
            <Terminal size={15} className="text-cyan-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-mono">
              {lang === 'es' ? 'Consola en Vivo' : 'Live Console'}
            </p>
            <h3 className="text-sm font-semibold text-white/90">
              {lang === 'es' ? 'Flujo de Telemetría' : 'Telemetry Stream'}
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Live indicator */}
          {!paused && (
            <div className="flex items-center gap-1.5">
              <motion.div
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ repeat: Infinity, duration: 1.2 }}
                className="w-1.5 h-1.5 rounded-full bg-red-400"
              />
              <span className="text-[9px] font-bold uppercase tracking-widest text-red-400 font-mono">
                {lang === 'es' ? 'EN VIVO' : 'LIVE'}
              </span>
            </div>
          )}

          {/* Pause / Resume */}
          <button
            onClick={() => setPaused(p => !p)}
            className={cn(
              'flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wider transition-colors',
              paused
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20'
                : 'border-white/10 bg-white/[0.04] text-slate-400 hover:bg-white/[0.07] hover:text-white'
            )}
          >
            {paused ? <Play size={10} /> : <Pause size={10} />}
            {paused ? (lang === 'es' ? 'Reanudar' : 'Resume') : (lang === 'es' ? 'Pausar' : 'Pause')}
          </button>

          {/* Clear */}
          <button
            onClick={() => setLogs([])}
            className="flex items-center gap-1.5 rounded-lg border border-white/[0.07] bg-white/[0.02] px-2.5 py-1.5 text-[10px] text-slate-500 hover:text-rose-400 hover:border-rose-500/20 transition-colors"
          >
            <Trash2 size={10} />
          </button>
        </div>
      </div>

      {/* ── Filter pills ──────────────────────────────────────── */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        <Filter size={11} className="mt-0.5 text-slate-600 shrink-0" />
        {severities.map(sev => {
          const selectedClass = sev === 'all'
            ? 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
            : `${SEV[sev].badge} ${SEV[sev].text}`;
          const label = sev === 'all' ? (lang === 'es' ? 'Todos' : 'All') : SEV[sev].label[lang];

          return (
            <button
              key={sev}
              onClick={() => setActiveFilter(sev)}
              className={cn(
                'rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest transition-colors',
                activeFilter === sev
                  ? selectedClass
                  : 'border-white/[0.06] bg-white/[0.02] text-slate-600 hover:text-slate-300'
              )}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* ── Log stream ─────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-white/[0.06] bg-[#010409]/70 p-3 font-mono text-[11px] space-y-1.5 min-h-0">
        <AnimatePresence initial={false}>
          {visible.map(line => (
            <motion.div
              key={line.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-start gap-2.5"
            >
              {/* Timestamp */}
              <span className="shrink-0 text-slate-600 mt-px">{line.timestamp}</span>

              {/* Severity dot */}
              <div className={cn('mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full', SEV[line.severity].dot)} />

              {/* Badge */}
              <span className={cn(
                'shrink-0 rounded border px-1 py-px text-[8px] font-bold uppercase tracking-widest',
                SEV[line.severity].badge, SEV[line.severity].text
              )}>
                {SEV[line.severity].label[lang]}
              </span>

              {/* Message */}
              <span className="leading-relaxed text-slate-300/80">{line.message[lang]}</span>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* ── Footer ────────────────────────────────────────────── */}
      <div className="mt-3 flex items-center justify-between text-[9px] font-mono uppercase tracking-wider text-slate-600">
        <div className="flex items-center gap-1.5">
          <Radio size={9} className="text-cyan-600" />
          <span>{lang === 'es' ? `${visible.length} entradas` : `${visible.length} entries`}</span>
        </div>
        <span>{lang === 'es' ? 'Intervalo de muestreo: 1.8s' : 'Sampling interval: 1.8s'}</span>
      </div>
    </GlassPanel>
  );
}

export const LiveTelemetryConsole = memo(LiveTelemetryConsoleComponent);
