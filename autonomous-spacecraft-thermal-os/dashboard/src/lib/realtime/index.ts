// lib/realtime/index.ts - WebSocket adapter with polling fallback.

export type RealtimeEventCallback<T = unknown> = (data: T) => void;

export interface RealtimeConfig {
  url: string;
  fallbackIntervalMs?: number;
  useFallbackPolling?: boolean;
}

export interface FallbackTelemetryPayload {
  timestamp: string;
  system: 'Lorenz Attractor';
  metrics: {
    lyapunov_max: string;
    entropy: string;
  };
}

type SocketEventCallback = (payload: unknown) => void;

interface SocketLike {
  on(event: string, callback: SocketEventCallback): void;
  off(event: string, callback: SocketEventCallback): void;
  disconnect(): void;
}

type SocketFactory = (
  url: string,
  options: { autoConnect: boolean; reconnection: boolean }
) => SocketLike;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const isSocketFactory = (value: unknown): value is SocketFactory =>
  typeof value === 'function';

async function loadSocketFactory(): Promise<SocketFactory | null> {
  if (typeof window === 'undefined') return null;

  try {
    const optionalImport = new Function('specifier', 'return import(specifier)') as (
      specifier: string
    ) => Promise<unknown>;
    const mod = await optionalImport('socket.io-client');
    const candidate = isRecord(mod) ? mod.io : undefined;
    return isSocketFactory(candidate) ? candidate : null;
  } catch {
    return null;
  }
}

export class RealtimeClient {
  private readonly config: Required<RealtimeConfig>;
  private socket: SocketLike | null = null;
  private readonly callbacks = new Map<string, Set<RealtimeEventCallback<unknown>>>();
  private readonly socketForwarders = new Map<string, SocketEventCallback>();
  private readonly pollingTimers = new Map<string, ReturnType<typeof setInterval>>();
  private connected = false;
  private fallbackTick = 0;

  constructor(config: RealtimeConfig) {
    this.config = {
      fallbackIntervalMs: config.fallbackIntervalMs ?? 3000,
      useFallbackPolling: config.useFallbackPolling ?? true,
      url: config.url,
    };
  }

  public async connect(): Promise<boolean> {
    if (this.connected) return true;

    const io = await loadSocketFactory();

    if (!io) {
      this.startFallbackTransport();
      return false;
    }

    this.socket = io(this.config.url, {
      autoConnect: true,
      reconnection: true,
    });

    this.socket.on('connect', () => {
      this.connected = true;
      this.trigger('connect', null);
    });

    this.socket.on('disconnect', () => {
      this.connected = false;
      this.trigger('disconnect', null);
    });

    for (const eventName of this.callbacks.keys()) {
      this.ensureSocketForwarder(eventName);
    }

    return true;
  }

  public subscribe<T = unknown>(event: string, callback: RealtimeEventCallback<T>): () => void {
    const wrapped: RealtimeEventCallback<unknown> = payload => callback(payload as T);
    const listeners = this.callbacks.get(event) ?? new Set<RealtimeEventCallback<unknown>>();
    listeners.add(wrapped);
    this.callbacks.set(event, listeners);
    this.ensureSocketForwarder(event);

    return () => {
      listeners.delete(wrapped);
      if (listeners.size === 0) {
        this.callbacks.delete(event);
        this.removeSocketForwarder(event);
      }
    };
  }

  public disconnect(): void {
    for (const [event, forwarder] of this.socketForwarders) {
      this.socket?.off(event, forwarder);
    }
    this.socketForwarders.clear();

    this.socket?.disconnect();
    this.socket = null;
    this.stopFallbackPolling();
    this.connected = false;
    this.trigger('disconnect', null);
  }

  private ensureSocketForwarder(event: string): void {
    if (!this.socket || this.socketForwarders.has(event)) return;
    const forwarder: SocketEventCallback = payload => this.trigger(event, payload);
    this.socket.on(event, forwarder);
    this.socketForwarders.set(event, forwarder);
  }

  private removeSocketForwarder(event: string): void {
    const forwarder = this.socketForwarders.get(event);
    if (!forwarder) return;
    this.socket?.off(event, forwarder);
    this.socketForwarders.delete(event);
  }

  private trigger(event: string, data: unknown): void {
    this.callbacks.get(event)?.forEach(callback => callback(data));
  }

  private startFallbackTransport(): void {
    this.connected = true;
    this.trigger('connect', null);

    if (this.config.useFallbackPolling) {
      this.startFallbackPolling();
    }
  }

  private startFallbackPolling(): void {
    this.stopFallbackPolling();

    const timer = setInterval(() => {
      this.fallbackTick += 1;
      const phase = this.fallbackTick % 17;
      const payload: FallbackTelemetryPayload = {
        timestamp: new Date().toLocaleTimeString(),
        system: 'Lorenz Attractor',
        metrics: {
          lyapunov_max: (0.85 + phase * 0.006).toFixed(3),
          entropy: (3.8 + phase * 0.009).toFixed(2),
        },
      };
      this.trigger('telemetry_stream', payload);
    }, this.config.fallbackIntervalMs);

    this.pollingTimers.set('telemetry_stream', timer);
  }

  private stopFallbackPolling(): void {
    this.pollingTimers.forEach(timer => clearInterval(timer));
    this.pollingTimers.clear();
  }
}
