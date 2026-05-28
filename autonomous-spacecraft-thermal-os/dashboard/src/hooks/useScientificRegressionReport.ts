import useSWR from 'swr';
import type { ScientificRegressionReport } from '@/types';

const REGRESSION_REPORT_URL = '/artifacts/discoveries/scientific_regression_report.json';

const fetcher = async (url: string): Promise<ScientificRegressionReport> => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load scientific regression report: ${response.status}`);
  }

  return response.json() as Promise<ScientificRegressionReport>;
};

export function useScientificRegressionReport() {
  const { data, error, isLoading, mutate } = useSWR<ScientificRegressionReport, Error>(
    REGRESSION_REPORT_URL,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  return {
    report: data,
    isLoading,
    isError: Boolean(error),
    error,
    mutate,
  };
}
