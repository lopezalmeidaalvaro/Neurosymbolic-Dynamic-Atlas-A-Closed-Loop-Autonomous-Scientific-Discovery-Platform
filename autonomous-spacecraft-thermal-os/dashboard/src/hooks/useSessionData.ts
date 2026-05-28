// ═══════════════════════════════════════════════════════════════
// hooks/useSessionData.ts — SWR hook for experiment session artifacts
// ═══════════════════════════════════════════════════════════════
import useSWR from 'swr';
import type { ExperimentSession } from '@/types';

// ── Generic JSON fetcher ───────────────────────────────────────
const fetcher = async <T>(url: string): Promise<T> => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
};

// ── Session metadata ───────────────────────────────────────────
export function useSessionMetadata(sessionId: string) {
  const { data, error, isLoading } = useSWR<ExperimentSession>(
    `/artifacts/sessions/${sessionId}/metadata.json`,
    fetcher,
    { revalidateOnFocus: false, revalidateIfStale: false }
  );
  return { session: data, isLoading, isError: !!error };
}

// ── Session benchmark ──────────────────────────────────────────
export interface SessionBenchmark {
  id: string;
  modelName: string;
  accuracy: number;
  timeSeconds: number;
  isOurs: boolean;
  color: string;
}

export function useSessionBenchmark(sessionId: string) {
  const { data, error, isLoading } = useSWR<SessionBenchmark[]>(
    `/artifacts/sessions/${sessionId}/benchmark.json`,
    fetcher,
    { revalidateOnFocus: false, revalidateIfStale: false }
  );
  return { benchmarks: data ?? [], isLoading, isError: !!error };
}

// ── Session logs ────────────────────────────────────────────────
export interface SessionLog {
  timestamp: string;
  severity: 'info' | 'warning' | 'error' | 'success' | 'critical';
  message: { en: string; es: string };
}

export function useSessionLogs(sessionId: string) {
  const { data, error, isLoading } = useSWR<SessionLog[]>(
    `/artifacts/sessions/${sessionId}/logs.json`,
    fetcher,
    { refreshInterval: 4000, revalidateOnFocus: true }
  );
  return { logs: data ?? [], isLoading, isError: !!error };
}

// ── Session embeddings ─────────────────────────────────────────
export interface SessionEmbedding {
  t: number;
  x: number;
  y: number;
  curvature: number;
  cluster: number;
}

export interface SessionEmbeddings {
  timesteps: number[];
  embeddings: SessionEmbedding[];
}

export function useSessionEmbeddings(sessionId: string) {
  const { data, error, isLoading } = useSWR<SessionEmbeddings>(
    `/artifacts/sessions/${sessionId}/embeddings.json`,
    fetcher,
    { revalidateOnFocus: false, revalidateIfStale: false }
  );
  return { embeddings: data, isLoading, isError: !!error };
}
