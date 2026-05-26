import useSWR from 'swr';
import type { ManifoldSnapshotsReport } from '@/types';

const MANIFOLD_SNAPSHOTS_URL = '/artifacts/embeddings/manifold_snapshots.json';

const fetcher = async (url: string): Promise<ManifoldSnapshotsReport> => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load manifold snapshots: ${response.status}`);
  }

  return response.json() as Promise<ManifoldSnapshotsReport>;
};

export function useManifoldSnapshots() {
  const { data, error, isLoading, mutate } = useSWR<ManifoldSnapshotsReport, Error>(
    MANIFOLD_SNAPSHOTS_URL,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateIfStale: false,
    }
  );

  const isEmpty = Boolean(
    data && (!Array.isArray(data.systems) || data.systems.length === 0)
  );

  return {
    snapshotsReport: data,
    isLoading,
    isError: Boolean(error),
    isEmpty,
    error,
    mutate,
  };
}
