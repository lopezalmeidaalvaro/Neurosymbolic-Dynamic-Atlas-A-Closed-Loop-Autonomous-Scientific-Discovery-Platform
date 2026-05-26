'use client';

import { useState, useMemo, use } from 'react';
import type { Metadata } from 'next';
import { Orbit, Activity, ShieldAlert, Cpu, Thermometer, Sun, Moon, Sparkles, Sliders, Settings2 } from 'lucide-react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
  ReferenceArea,
} from 'recharts';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

// Constants for physical solver
const C_THERMAL = 135000; // Thermal capacity (m * Cp = 150kg * 900 J/kgK = 135000 J/K)
const G_SOL = 1361;       // Solar flux constant (W/m2)
const SIGMA = 5.67e-8;    // Stefan-Boltzmann constant (W/m2K4)
const T_ORBIT = 5677;     // LEO Orbit period (seconds, ~94.6 minutes)
const STEP_SIZE = 30;     // 30 seconds per step
const STEPS = 190;        // ~1.5 orbits (~95 minutes / 30s)

interface TelemetryPoint {
  time: number;       // Minutes into orbit
  temp: number;       // Temperature in °C
  solarInput: number; // Q_solar in Watts
  radOutput: number;  // Q_out in Watts
  isEclipse: boolean; // Shadow state
}

export default function SatellitePage({
  params: paramsPromise,
}: {
  params: Promise<{ lang: string }>;
}) {
  // Unwrap parameters
  const params = use(paramsPromise);
  const lang = params.lang as Language;
  const isEs = lang === 'es';

  // Slider State Variables
  const [power, setPower] = useState(220);        // Internal Power (0W - 1000W)
  const [area, setArea] = useState(2.2);          // Radiator Area (0.5m2 - 10.0m2)
  const [absorptivity, setAbsorptivity] = useState(0.28); // Absorptivity (0.05 - 0.95)
  const [emissivity, setEmissivity] = useState(0.78);     // Emissivity (0.05 - 0.95)

  // Run the physical solver (Euler numerical integration)
  const telemetryData = useMemo<TelemetryPoint[]>(() => {
    let T = 293.15; // Initial temperature (20°C in Kelvin)
    const points: TelemetryPoint[] = [];

    // Solve 3 full orbits first to stabilize the limit cycle and prevent initial transients
    const totalSteps = STEPS * 3;
    const startRecordStep = STEPS * 2; // Only record the last 1 orbit cycle

    for (let step = 0; step < totalSteps; step++) {
      const timeSec = step * STEP_SIZE;
      const angle = (2 * Math.PI * timeSec) / T_ORBIT;
      
      // LEO Eclipse shadow modeling: Earth blocks sun for ~40% of the orbit
      // modeled as sin(angle) < -0.3
      const isEclipse = Math.sin(angle) < -0.3;
      
      // Calculate solar irradiance
      let Q_solar = 0;
      if (!isEclipse) {
        // cosine factor representing angle of solar rays to radiator area
        const cosFactor = Math.max(0, Math.cos(angle));
        Q_solar = absorptivity * area * G_SOL * cosFactor;
      }
      
      const Q_earth = emissivity * area * 230; // Earth IR constant (230 W/m2)
      const Q_in = Q_solar + Q_earth + power;
      
      // Radiator output: Stefan-Boltzmann radiation to deep space at 3K
      const Q_out = SIGMA * emissivity * area * Math.pow(T, 4);
      
      // Euler numerical step
      const dT = ((Q_in - Q_out) / C_THERMAL) * STEP_SIZE;
      T = T + dT;
      
      // Record telemetry in the final orbit cycle
      if (step >= startRecordStep) {
        const timeMin = Math.round(((step - startRecordStep) * STEP_SIZE) / 60);
        points.push({
          time: timeMin,
          temp: parseFloat((T - 273.15).toFixed(1)),
          solarInput: Math.round(Q_solar),
          radOutput: Math.round(Q_out),
          isEclipse,
        });
      }
    }
    
    return points;
  }, [power, area, absorptivity, emissivity]);

  // Derived telemetry metrics
  const { minTemp, maxTemp, avgTemp, status, statusColor, statusBg, statusBorder, statusMessage } = useMemo(() => {
    const temps = telemetryData.map(p => p.temp);
    const min = Math.min(...temps);
    const max = Math.max(...temps);
    const avg = parseFloat((temps.reduce((sum, t) => sum + t, 0) / temps.length).toFixed(1));

    let state: 'OPTIMAL' | 'WARNING' | 'CRITICAL' = 'OPTIMAL';
    let color = 'text-emerald-400';
    let bg = 'bg-emerald-500/10';
    let border = 'border-emerald-500/20';
    let msg = isEs
      ? 'Telemetría óptima. El satélite mantiene un equilibrio térmico seguro.'
      : 'Optimal telemetry. The spacecraft maintains a safe thermal equilibrium.';

    // Warning range: Temp drops below -20°C or rises above 65°C
    if (min < -20 || max > 65) {
      state = 'WARNING';
      color = 'text-amber-400';
      bg = 'bg-amber-500/10';
      border = 'border-amber-500/20';
      msg = isEs
        ? 'Estrés térmico moderado. Los componentes electrónicos experimentan fluctuaciones elevadas.'
        : 'Moderate thermal stress. Electronic components are undergoing high temperature fluctuations.';
    }

    // Critical failure range: Temp drops below -40°C (freeze) or rises above 85°C (burnout)
    if (min < -40 || max > 85) {
      state = 'CRITICAL';
      color = 'text-rose-400';
      bg = 'bg-rose-500/15';
      border = 'border-rose-500/30';
      if (max > 85 && min < -40) {
        msg = isEs
          ? '¡FALLO CRÍTICO MÚLTIPLE! El satélite se quema en el sol y se congela en eclipse. Aumenta la capacidad térmica o disminuye la emisividad.'
          : 'MULTIPLE CRITICAL FAILURES! Spacecraft burns in sunlight and freezes in eclipse. Increase thermal capacity or lower radiator area/emissivity.';
      } else if (max > 85) {
        msg = isEs
          ? '¡FALLO CRÍTICO: QUEMADO! Temperatura pico > 85°C. Disminuye la potencia interna, aumenta el área del radiador o reduce la absorptividad.'
          : 'CRITICAL FAILURE: BURNOUT! Peak temperature > 85°C. Decrease power, increase radiator area, or reduce solar absorptivity.';
      } else {
        msg = isEs
          ? '¡FALLO CRÍTICO: CONGELADO! Temperatura cae < -40°C. Aumenta la potencia interna, reduce el área del radiador o reduce la emisividad.'
          : 'CRITICAL FAILURE: FREEZING! Orbit temperature drops < -40°C. Increase power, reduce radiator area, or lower emissivity.';
      }
    }

    return {
      minTemp: min,
      maxTemp: max,
      avgTemp: avg,
      status: state,
      statusColor: color,
      statusBg: bg,
      statusBorder: border,
      statusMessage: msg,
    };
  }, [telemetryData, isEs]);

  return (
    <FocusContainer size="xl" className="space-y-10 pb-28 pt-6">
      <ScientificSurface grid className="min-h-[440px] p-6 sm:p-8 lg:p-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_72%_18%,rgba(34,211,238,0.11),transparent_34%)]" />
        <div className="grid min-h-[360px] gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
          <Reveal className="max-w-3xl self-center relative z-10">
            <span className="research-kicker mb-6 flex items-center gap-1.5 text-cyan-300 border-cyan-500/20 bg-cyan-500/10">
              <Orbit size={13} className="animate-spin" style={{ animationDuration: '6s' }} />
              {isEs ? 'Gemelo Digital Térmico Orbital' : 'Orbital Thermal Digital Twin'}
            </span>
            <h1 className="cinematic-heading text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-100 bg-clip-text text-transparent">
              ThermalDigitalTwin
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300">
              {isEs
                ? 'Simulador físico interactivo en tiempo real para el control de temperatura de satélites en Órbita Baja Terrestre (LEO). Regula los parámetros térmicos para mantener la aviónica estable.'
                : 'Real-time interactive physical simulator for spacecraft thermal control in Low Earth Orbit (LEO). Regulate thermal parameters to maintain avionics stability.'}
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <span className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-cyan-100/90">
                {isEs ? 'Simulador Activo' : 'Simulator Active'}
              </span>
              <span className="rounded-full border border-white/[0.08] bg-white/[0.035] px-3 py-1.5 text-xs text-slate-400">
                1-Node LEO Solver
              </span>
              <span className="rounded-full border border-violet-500/16 bg-violet-500/[0.06] px-3 py-1.5 text-xs text-violet-300/80">
                {isEs ? 'Modo Hardware in the Loop' : 'Hardware in the Loop mode'}
              </span>
            </div>
          </Reveal>

          {/* Quick Stats Panel */}
          <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              {
                icon: Thermometer,
                label: isEs ? 'Temp Promedio' : 'Average Temp',
                value: avgTemp,
                suffix: ' °C',
                tone: 'text-cyan-300',
              },
              {
                icon: Sun,
                label: isEs ? 'Temperatura Máx' : 'Max Orbit Temp',
                value: maxTemp,
                suffix: ' °C',
                tone: maxTemp > 85 ? 'text-rose-400' : 'text-amber-300',
              },
              {
                icon: Moon,
                label: isEs ? 'Temperatura Mín' : 'Min Orbit Temp',
                value: minTemp,
                suffix: ' °C',
                tone: minTemp < -40 ? 'text-rose-400' : 'text-blue-300',
              },
              {
                icon: Activity,
                label: isEs ? 'Balance de Energía' : 'Energy Balance',
                value: Math.round(power + (avgTemp < 50 ? 300 : 200)),
                suffix: ' W',
                tone: 'text-violet-300',
              },
            ].map(({ icon: Icon, label, value, suffix, tone }) => (
              <GlassPanel key={label} density="compact" className="rounded-2xl border-white/[0.06] bg-white/[0.02]">
                <Icon size={16} className={tone} />
                <p className="metric-label mt-4">{label}</p>
                <p className="mt-2 text-2xl font-bold tabular-nums text-white">
                  {value}
                  <span className="text-sm font-medium text-slate-400">{suffix}</span>
                </p>
              </GlassPanel>
            ))}
          </Reveal>
        </div>
      </ScientificSurface>

      {/* Main Interactive Grid */}
      <ScrollReveal className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        
        {/* Sliders Control Panel */}
        <GlassPanel density="spacious" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl">
          <div className="mb-6 flex items-center gap-3">
            <Sliders size={18} className="text-cyan-300" />
            <div>
              <p className="metric-label">{isEs ? 'Parámetros del Sistema' : 'System Parameters'}</p>
              <h2 className="mt-1 text-xl font-bold text-white/90">{isEs ? 'Regulación Térmica Cubesat' : 'Cubesat Thermal Regulation'}</h2>
            </div>
          </div>

          <div className="space-y-6">
            {/* Slider 1: Internal Power */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Cpu size={13} className="text-cyan-400" />
                  {isEs ? 'Potencia Eléctrica Interna (P)' : 'Internal Electrical Power (P)'}
                </span>
                <span className="font-mono text-xs text-cyan-300 font-semibold">{power} W</span>
              </div>
              <input
                type="range"
                min="0"
                max="1000"
                step="10"
                value={power}
                onChange={(e) => setPower(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Calor generado por la CPU, transmisores y baterías.' : 'Electrical dissipation by scientific payloads, processors, and batteries.'}
              </p>
            </div>

            {/* Slider 2: Radiator Area */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Settings2 size={13} className="text-emerald-400" />
                  {isEs ? 'Área del Radiador (A)' : 'Radiator Surface Area (A)'}
                </span>
                <span className="font-mono text-xs text-emerald-300 font-semibold">{area} m²</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="10.0"
                step="0.1"
                value={area}
                onChange={(e) => setArea(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Área total de las caras externas configuradas para irradiar calor al espacio.' : 'Total surface area exposed to space used to radiate heat away.'}
              </p>
            </div>

            {/* Slider 3: Absorptivity */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Sun size={13} className="text-amber-400" />
                  {isEs ? 'Absorbitancia Solar (α)' : 'Solar Absorptivity (α)'}
                </span>
                <span className="font-mono text-xs text-amber-300 font-semibold">{absorptivity}</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.95"
                step="0.01"
                value={absorptivity}
                onChange={(e) => setAbsorptivity(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Fracción de luz solar absorbida por la superficie (recubrimientos de pintura).' : 'Fraction of incident solar radiation absorbed (e.g. golden kapton foil vs white paint).'}
              </p>
            </div>

            {/* Slider 4: Emissivity */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Moon size={13} className="text-violet-400" />
                  {isEs ? 'Emisividad Infrarroja (ε)' : 'Infrared Emissivity (ε)'}
                </span>
                <span className="font-mono text-xs text-violet-300 font-semibold">{emissivity}</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.95"
                step="0.01"
                value={emissivity}
                onChange={(e) => setEmissivity(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-violet-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Eficacia de emisión de calor infrarrojo al espacio profundo (3 Kelvin).' : 'Efficiency in emitting infrared heat to the deep cold space vacuum.'}
              </p>
            </div>
          </div>

          {/* Dynamic Diagnostic Card */}
          <div className={`mt-8 p-4 rounded-xl border ${statusBg} ${statusBorder} transition-all duration-300 flex gap-3.5`}>
            <ShieldAlert className={`shrink-0 ${statusColor} mt-0.5`} size={20} />
            <div>
              <h4 className={`text-sm font-bold uppercase tracking-wider ${statusColor}`}>{status}</h4>
              <p className="mt-1 text-xs leading-relaxed text-slate-200">{statusMessage}</p>
            </div>
          </div>
        </GlassPanel>

        {/* Real-time Telemetry Plot */}
        <GlassPanel density="spacious" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl flex flex-col justify-between">
          <div>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="metric-label">{isEs ? 'Simulación en Vivo' : 'Live Simulation'}</p>
                <h3 className="mt-1 text-xl font-bold text-slate-100">{isEs ? 'Ciclo Térmico de la Órbita LEO' : 'LEO Orbit Thermal Cycle'}</h3>
              </div>
              <Sparkles size={16} className="text-cyan-400 animate-pulse" />
            </div>

            <div className="h-[280px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={telemetryData} margin={{ top: 10, right: 10, bottom: 0, left: -25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="time"
                    stroke="#475569"
                    fontSize={10}
                    tickLine={false}
                    label={{ value: isEs ? 'Tiempo (minutos)' : 'Orbit Time (minutes)', position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 10 }}
                  />
                  <YAxis
                    stroke="#475569"
                    fontSize={10}
                    tickLine={false}
                    domain={[-60, 110]}
                    label={{ value: isEs ? 'Temperatura (°C)' : 'Temperature (°C)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(10, 15, 30, 0.94)',
                      borderColor: 'rgba(255,255,255,0.08)',
                      borderRadius: '12px',
                      color: '#f8fafc',
                      fontFamily: 'monospace',
                      fontSize: '11px',
                    }}
                  />
                  
                  {/* Safety bounds areas */}
                  <ReferenceArea y1={85} y2={110} fill="rgba(244,63,94,0.05)" />
                  <ReferenceArea y1={-60} y2={-40} fill="rgba(59,130,246,0.05)" />
                  
                  {/* Critical boundary lines */}
                  <ReferenceLine y={85} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: 'Burnout', fill: '#f43f5e', fontSize: 9, position: 'insideTopRight' }} />
                  <ReferenceLine y={-40} stroke="#3b82f6" strokeDasharray="4 4" label={{ value: 'Freeze', fill: '#3b82f6', fontSize: 9, position: 'insideBottomRight' }} />
                  
                  <Line
                    type="monotone"
                    dataKey="temp"
                    name="Temperature"
                    stroke={status === 'CRITICAL' ? '#f43f5e' : status === 'WARNING' ? '#f59e0b' : '#22d3ee'}
                    strokeWidth={3}
                    dot={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 border-t border-white/5 pt-4 mt-4">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-cyan-400" />
              <span className="text-[10px] text-slate-400">
                {isEs ? 'Equilibrio Térmico Activo' : 'Active Thermal Equilibrium'}
              </span>
            </div>
            <div className="text-right text-[10px] font-mono text-slate-500">
              LEO Orbit: 94.6 min | Δt = 30s
            </div>
          </div>
        </GlassPanel>
      </ScrollReveal>
    </FocusContainer>
  );
}
