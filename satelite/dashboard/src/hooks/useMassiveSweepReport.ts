import useSWR from 'swr';
import type { MassiveSweepReport } from '@/types';

const MASSIVE_SWEEP_REPORT_URL = '/artifacts/discoveries/massive_sweep_report.json';

const fetcher = async (url: string): Promise<MassiveSweepReport> => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load massive sweep report: ${response.status}`);
  }

  return response.json() as Promise<MassiveSweepReport>;
};

export function useMassiveSweepReport() {
  const { data, error, isLoading, mutate } = useSWR<MassiveSweepReport, Error>(
    MASSIVE_SWEEP_REPORT_URL,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  const isEmpty = Boolean(
    data && (!Array.isArray(data.certified_results) || data.certified_results.length === 0)
  );

  return {
    report: data,
    isLoading,
    isError: Boolean(error),
    isEmpty,
    error,
    mutate,
  };
}
