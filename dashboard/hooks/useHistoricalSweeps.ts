import useSWR from 'swr';
import type { HistoricalReport, HistoryIndex, MassiveSweepReport } from '@/types';

const HISTORY_INDEX_URL = '/artifacts/history/history_index.json';
const HISTORY_BASE_URL = '/artifacts/history';

const fetchJson = async <T>(url: string): Promise<T> => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }

  return response.json() as Promise<T>;
};

export interface HistoricalSweepSnapshot {
  index: HistoricalReport;
  report: MassiveSweepReport;
}

export function useHistoricalSweeps() {
  const {
    data: index,
    error: indexError,
    isLoading: isIndexLoading,
    mutate,
  } = useSWR<HistoryIndex, Error>(
    HISTORY_INDEX_URL,
    (url) => fetchJson<HistoryIndex>(url),
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  const snapshotKey = index?.reports.length
    ? index.reports.map((report) => `${HISTORY_BASE_URL}/${report.file}`)
    : null;

  const {
    data: snapshots,
    error: snapshotsError,
    isLoading: areSnapshotsLoading,
  } = useSWR<HistoricalSweepSnapshot[], Error>(
    snapshotKey,
    async (urls: string[]) => {
      const loaded = await Promise.all(
        urls.map(async (url, position) => {
          const report = await fetchJson<MassiveSweepReport>(url);
          const indexEntry = index?.reports[position];

          if (!indexEntry) {
            throw new Error(`Missing history index entry for ${url}`);
          }

          return {
            index: indexEntry,
            report,
          };
        })
      );

      return loaded;
    },
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  const error = indexError ?? snapshotsError;

  return {
    reports: index?.reports ?? [],
    snapshots: snapshots ?? [],
    loading: isIndexLoading || areSnapshotsLoading,
    error,
    isError: Boolean(error),
    mutate,
  };
}
