'use client';

import { useMemo } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  Clock, 
  Database,
  Gauge
} from 'lucide-react';
import { useScientificRegressionReport } from '@/hooks/useScientificRegressionReport';
import { GlassPanel } from '@/components/ui/GlassPanel';
import type { Language, ScientificRegressionSystem } from '@/types';

interface ScientificRegressionPanelProps {
  lang: Language;
}

function signed(value: number) {
  if (value === 0) return '0.000000';
  return value > 0 ? `+${value.toFixed(6)}` : value.toFixed(6);
}

export function ScientificRegressionPanel({ lang }: ScientificRegressionPanelProps) {
  const { report, isLoading, isError, error } = useScientificRegressionReport();

  const metricsOrder = [
    { key: 'critical_score', label: 'critical_score', hasPct: true },
    { key: 'confidence_score', label: 'confidence_score', hasPct: true },
    { key: 'acceleration', label: 'acceleration', hasPct: true },
    { key: 'acceleration_std', label: 'acceleration_std', hasPct: true },
    { key: 'reproducibility_status', label: 'reproducibility', hasPct: false }
  ];

  if (isLoading) {
    return (
      <GlassPanel className="p-6">
        <p className="font-mono text-sm text-slate-400 animate-pulse">
          {lang === 'es' 
            ? 'Analizando regresiones científicas contra baseline...' 
            : 'Analyzing scientific regressions against baseline...'}
        </p>
      </GlassPanel>
    );
  }

  if (isError || !report) {
    return (
      <GlassPanel tone="warning" className="p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-400" />
          <p className="text-sm text-amber-200">
            {lang === 'es' 
              ? 'Reporte de regresión no disponible. Ejecuta "python scientific_regression.py" primero.' 
              : 'Regression report unavailable. Please run "python scientific_regression.py" first.'}
          </p>
        </div>
      </GlassPanel>
    );
  }

  const { status, baseline_name, baseline_timestamp, current_timestamp } = report.summary;

  const headerColors = {
    pass: 'border-emerald-500/20 bg-emerald-950/10 text-emerald-300',
    warning: 'border-amber-500/20 bg-amber-950/10 text-amber-300',
    failure: 'border-rose-500/20 bg-rose-950/10 text-rose-300'
  };

  const statusIcons = {
    pass: <CheckCircle2 className="h-6 w-6 text-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.3)]" />,
    warning: <AlertTriangle className="h-6 w-6 text-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.3)]" />,
    failure: <ShieldAlert className="h-6 w-6 text-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.3)]" />
  };

  const statusTexts = {
    pass: {
      es: 'Validación Científica Exitosa (Sin Regresiones)',
      en: 'Scientific Validation Passed (No Regressions)'
    },
    warning: {
      es: 'Alerta de Deriva Científica (Desviaciones Leves)',
      en: 'Scientific Drift Alert (Mild Deviations)'
    },
    failure: {
      es: 'Regresión Científica Detectada (Fuera de Thresholds)',
      en: 'Scientific Regression Detected (Out of Thresholds)'
    }
  };

  const systemStatusBadge = (s: 'pass' | 'warning' | 'failure') => {
    const styles = {
      pass: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
      warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
      failure: 'bg-rose-500/10 border-rose-500/20 text-rose-400'
    };
    return (
      <span className={`px-2 py-0.5 rounded-full border text-[10px] uppercase font-mono tracking-wider font-semibold ${styles[s]}`}>
        {s}
      </span>
    );
  };

  const metricStatusDot = (s: 'pass' | 'warning' | 'failure') => {
    const colors = {
      pass: 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.4)]',
      warning: 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.4)]',
      failure: 'bg-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.4)]'
    };
    return <span className={`h-1.5 w-1.5 rounded-full ${colors[s]}`} />;
  };

  return (
    <GlassPanel density="spacious" tone={status === 'failure' ? 'warning' : 'active'}>
      {/* Upper Status Banner */}
      <div className={`mb-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 rounded-2xl border ${headerColors[status]}`}>
        <div className="flex items-center gap-3">
          {statusIcons[status]}
          <div>
            <h4 className="font-semibold text-lg leading-tight">
              {statusTexts[status][lang]}
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              {lang === 'es' ? 'Validación automática frente a baselines' : 'Automated baseline guardrails active'}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3 font-mono text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5 bg-slate-950/40 px-2.5 py-1 rounded-lg">
            <Database size={11} className="text-cyan-400" />
            {baseline_name}
          </span>
          <span className="flex items-center gap-1.5 bg-slate-950/40 px-2.5 py-1 rounded-lg">
            <Clock size={11} />
            {baseline_timestamp.substring(11, 19)}
          </span>
        </div>
      </div>

      {/* Systems Breakdown */}
      <div className="space-y-6">
        {report.systems.map((sys: ScientificRegressionSystem) => (
          <div key={sys.system} className="border border-white/[0.05] bg-slate-950/20 rounded-2xl p-5">
            <div className="flex items-center justify-between border-b border-white/[0.05] pb-3 mb-4">
              <h5 className="text-md font-semibold text-white/90 capitalize flex items-center gap-2">
                <Gauge size={14} className="text-slate-400" />
                {sys.system.replaceAll('_', ' ')}
              </h5>
              {systemStatusBadge(sys.status)}
            </div>

            {sys.message ? (
              <p className="text-sm font-mono text-slate-400 p-2 italic bg-slate-950/40 rounded-xl">
                {sys.message}
              </p>
            ) : sys.metrics ? (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-left border-separate border-spacing-y-1.5">
                  <thead className="font-mono text-[9px] uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-1">metric</th>
                      <th className="px-3 py-1">baseline</th>
                      <th className="px-3 py-1 text-center"></th>
                      <th className="px-3 py-1">current</th>
                      <th className="px-3 py-1">delta</th>
                      <th className="px-3 py-1">pct change</th>
                      <th className="px-3 py-1 text-right">status</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-xs text-slate-200">
                    {metricsOrder.map(({ key, label, hasPct }) => {
                      const metricData = (sys.metrics as any)[key];
                      if (!metricData) return null;

                      const isRepro = key === 'reproducibility_status';
                      
                      return (
                        <tr key={key} className="bg-slate-950/30 hover:bg-slate-950/50 transition-colors">
                          <td className="px-3 py-2 text-slate-400 font-medium rounded-l-xl">{label}</td>
                          <td className="px-3 py-2">
                            {isRepro ? metricData.baseline : metricData.baseline.toFixed(6)}
                          </td>
                          <td className="px-3 py-2 text-slate-500 text-center">
                            <ArrowRight size={12} className="inline" />
                          </td>
                          <td className="px-3 py-2 font-semibold">
                            {isRepro ? metricData.current : metricData.current.toFixed(6)}
                          </td>
                          <td className="px-3 py-2">
                            {isRepro ? '-' : signed(metricData.delta)}
                          </td>
                          <td className="px-3 py-2">
                            {hasPct ? `${metricData.pct_change.toFixed(2)}%` : '-'}
                          </td>
                          <td className="px-3 py-2 rounded-r-xl text-right">
                            <span className="inline-flex items-center gap-1.5 capitalize font-semibold">
                              {metricStatusDot(metricData.status)}
                              <span className={
                                metricData.status === 'failure' ? 'text-rose-400' :
                                metricData.status === 'warning' ? 'text-amber-400' : 'text-emerald-400'
                              }>
                                {metricData.status}
                              </span>
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
