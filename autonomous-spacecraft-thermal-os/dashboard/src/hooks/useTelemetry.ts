import useSWR from 'swr';

export interface LorenzTelemetryPoint {
  x: number;
  y: number;
  z: number;
  t: number;
}

export interface LorenzTelemetry {
  system: string;
  parameters: {
    sigma: number;
    rho: number;
    beta: number;
  };
  metrics: {
    lyapunov_max: number;
    shannon_entropy: number;
    is_chaotic: boolean;
    dimension: number;
  };
  trajectory: LorenzTelemetryPoint[];
}

const fetcher = async (url: string): Promise<LorenzTelemetry> => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }
  return res.json();
};

export function useTelemetry() {
  const { data, error, isLoading, mutate } = useSWR<LorenzTelemetry, Error>(
    '/artifacts/telemetry/lorenz_telemetry.json',
    fetcher,
    {
      refreshInterval: 5000, // Autorefresh every 5 seconds to simulate dynamic laboratory observations
      dedupingInterval: 2000,
      revalidateOnFocus: false,
    }
  );

  return {
    telemetry: data,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
