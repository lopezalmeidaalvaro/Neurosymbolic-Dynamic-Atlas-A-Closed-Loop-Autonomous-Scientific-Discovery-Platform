import useSWR from 'swr';
import type { NoiseRobustnessReport } from '@/types';

export interface LatentEmbeddings {
  names: string[];
  pca_coords: [number, number][];
  curvatures: number[];
  lambda_g: number[];
  labels: number[];
}

const fetcher = async <T>(url: string): Promise<T> => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json() as Promise<T>;
};

export function useScientificArtifacts() {
  const { data, error, isLoading, mutate } = useSWR<LatentEmbeddings, Error>(
    '/artifacts/embeddings/latent_embeddings.json',
    (url) => fetcher<LatentEmbeddings>(url),
    {
      revalidateOnFocus: false,
      revalidateIfStale: false, // Embeddings are heavyweight and static per pipeline run
    }
  );

  return {
    embeddings: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}

export function useRobustnessReport() {
  const { data, error, isLoading, mutate } = useSWR<NoiseRobustnessReport, Error>(
    '/artifacts/discoveries/noise_robustness_report.json',
    (url) => fetcher<NoiseRobustnessReport>(url),
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  return {
    report: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}

