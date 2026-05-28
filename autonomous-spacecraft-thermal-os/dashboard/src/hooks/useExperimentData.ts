import useSWR from 'swr';
import type { ExperimentStatus } from '@/types';

export interface PipelineState {
  status: ExperimentStatus;
  progress: number;
  currentStep: number;
  totalSteps: number;
  lastRunTimestamp: string;
  logs: string[];
}

const fetcher = async (url: string): Promise<PipelineState> => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
};

export function useExperimentData() {
  const { data, error, isLoading, mutate } = useSWR<PipelineState, Error>(
    '/artifacts/experiments/pipeline_state.json',
    fetcher,
    {
      refreshInterval: 3000, // Short polling (3s) to watch automated runner status
      dedupingInterval: 1000,
      revalidateOnFocus: true,
    }
  );

  return {
    pipelineState: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
