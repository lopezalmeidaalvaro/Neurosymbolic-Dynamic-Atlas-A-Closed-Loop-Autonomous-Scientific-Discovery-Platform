'use client';

import { useState, useMemo, use, useEffect } from 'react';
import { Orbit, Activity, ShieldAlert, Cpu, Thermometer, Sun, Moon, Sparkles, Sliders, Settings2, BarChart2, Info, CheckCircle } from 'lucide-react';
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

interface TelemetryPoint {
  time: number;       // Minutes into simulation
  temp: number;       // Temperature in °C
  radOutput: number;  // Q_out in Watts
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

  // Toggle State (Physical LEO Solver vs AI Surrogate Engine)
  const [mode, setMode] = useState<'simulation' | 'ai'>('simulation');

  // Slider State Variables (Corrected ranges for Vacuum Server)
  const [power, setPower] = useState(30);        // Internal Power (5W - 50W)
  const [area, setArea] = useState(0.10);        // Radiator Area (0.01m² - 0.50m²)
  const [emissivity, setEmissivity] = useState(0.80); // Emissivity (0.10 - 0.95)

  // API Ingested States
  const [optimalDesign, setOptimalDesign] = useState<any>(null);
  const [equations, setEquations] = useState<any[]>([]);
  const [aiPrediction, setAiPrediction] = useState<any>(null);
  const [thermalMap2D, setThermalMap2D] = useState<number[][]>([]);
  const [steadyStateTemp, setSteadyStateTemp] = useState<number | null>(null);

  // Fetch optimal design and equations on mount
  useEffect(() => {
    fetch('http://localhost:8000/optimal')
      .then(res => res.json())
      .then(data => setOptimalDesign(data))
      .catch(err => console.log('Error fetching optimal design:', err));

    fetch('http://localhost:8000/equations')
      .then(res => res.json())
      .then(data => setEquations(data))
      .catch(err => console.log('Error fetching equations:', err));
  }, []);

  // Fetch prediction and dynamic simulation details from API on slider changes
  useEffect(() => {
    // 1. Fetch AI Prediction
    fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ power, area, emissivity })
    })
      .then(res => res.json())
      .then(data => setAiPrediction(data))
      .catch(err => console.log('Error predicting:', err));

    // 2. Fetch full simulation details for 2D Thermal Map and steady state limit
    fetch(`http://localhost:8000/simulate?power=${power}&area=${area}&emissivity=${emissivity}`)
      .then(res => res.json())
      .then(data => {
        if (data.temperature_map_2D) {
          setThermalMap2D(data.temperature_map_2D);
        }
        if (data.steady_state_temp_c) {
          setSteadyStateTemp(data.steady_state_temp_c);
        }
      })
      .catch(err => console.log('Error fetching simulation map:', err));
  }, [power, area, emissivity]);

  // Run the physical solver (Euler numerical integration on client)
  // Ensures robust offline/instantaneous interactivity
  const telemetryData = useMemo<TelemetryPoint[]>(() => {
    let T = 293.15; // Initial temperature (20°C in Kelvin)
    const points: TelemetryPoint[] = [];
    const dt = 10.0;
    const duration = 3600.0;
    const steps = Math.floor(duration / dt) + 1;
    const SIGMA = 5.67e-8;
    const T_AMB = 2.7;
    const heat_capacity = 500.0;

    for (let step = 0; step < steps; step++) {
      const timeSec = step * dt;
      
      // Q_rad = ε * σ * A * (T^4 - T_amb^4)
      const Q_rad = emissivity * SIGMA * area * (Math.pow(T, 4) - Math.pow(T_AMB, 4));
      
      // Euler numerical step: dT = (Q_gen - Q_rad) / C * dt
      const dT = ((power - Q_rad) / heat_capacity) * dt;
      T = T + dT;
      
      const timeMin = Math.round(timeSec / 60);
      points.push({
        time: timeMin,
        temp: parseFloat((T - 273.15).toFixed(1)),
        radOutput: Math.round(Q_rad)
      });
    }
    
    return points;
  }, [power, area, emissivity]);

  // Derived telemetry metrics
  const { minTemp, maxTemp, avgTemp, timeToCrit, status, statusColor, statusBg, statusBorder, statusMessage } = useMemo(() => {
    // If in AI mode, we prioritize using the predictions from the Neural/RF surrogate models
    const useAI = mode === 'ai' && aiPrediction;
    
    const temps = telemetryData.map(p => p.temp);
    const min = Math.min(...temps);
    const max = useAI ? aiPrediction.max_temp_c : Math.max(...temps);
    const avg = parseFloat((temps.reduce((sum, t) => sum + t, 0) / temps.length).toFixed(1));
    const time_to_crit = useAI ? aiPrediction.time_to_critical_sec : null;

    let state: 'OPTIMAL' | 'WARNING' | 'CRITICAL' = 'OPTIMAL';
    let color = 'text-emerald-400';
    let bg = 'bg-emerald-500/10';
    let border = 'border-emerald-500/20';
    let msg = isEs
      ? 'Telemetría óptima. El satélite mantiene un equilibrio térmico seguro.'
      : 'Optimal telemetry. The spacecraft maintains a safe thermal equilibrium.';

    // Warning range: Peak temp rises above 65°C
    if (max > 65) {
      state = 'WARNING';
      color = 'text-amber-400';
      bg = 'bg-amber-500/10';
      border = 'border-amber-500/20';
      msg = isEs
        ? 'Estrés térmico moderado. Los componentes electrónicos experimentan fluctuaciones elevadas.'
        : 'Moderate thermal stress. Electronic components are undergoing high temperature fluctuations.';
    }

    // Critical failure range: Peak temperature rises above 85°C (burnout)
    if (max >= 85) {
      state = 'CRITICAL';
      color = 'text-rose-400';
      bg = 'bg-rose-500/15';
      border = 'border-rose-500/30';
      msg = isEs
        ? '¡FALLO CRÍTICO: QUEMADO! Temperatura pico > 85°C. Disminuye la potencia interna o aumenta el área del radiador.'
        : 'CRITICAL FAILURE: BURNOUT! Peak temperature > 85°C. Decrease internal power, or increase radiator area.';
    }

    return {
      minTemp: min,
      maxTemp: max,
      avgTemp: avg,
      timeToCrit: time_to_crit,
      status: state,
      statusColor: color,
      statusBg: bg,
      statusBorder: border,
      statusMessage: msg,
    };
  }, [telemetryData, isEs, mode, aiPrediction]);

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
              ThermalTwin-3000
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300">
              {isEs
                ? 'Controlador termodinámico digital interactivo para servidores satelitales en vacío orbital. Utiliza una formulación de capacidad calorífica agrupada para emular y predecir temperaturas en LEO.'
                : 'Interactive thermodynamical digital controller for spacecraft servers in orbital vacuum. Employs a lumped-capacitance model to simulate and predict temperatures in LEO.'}
            </p>
            
            {/* Toggle Simulator vs AI Mode */}
            <div className="mt-8 flex gap-4">
              <button
                onClick={() => setMode('simulation')}
                className={`px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-300 ${
                  mode === 'simulation'
                    ? 'bg-cyan-500 text-[#070c1d] shadow-lg shadow-cyan-500/20 border border-cyan-400'
                    : 'bg-white/[0.04] text-slate-300 hover:bg-white/[0.08] border border-white/[0.08]'
                }`}
              >
                {isEs ? 'Simulador Físico' : 'Physical Solver'}
              </button>
              <button
                onClick={() => setMode('ai')}
                className={`px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-300 flex items-center gap-1.5 ${
                  mode === 'ai'
                    ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/25 border border-violet-500'
                    : 'bg-white/[0.04] text-slate-300 hover:bg-white/[0.08] border border-white/[0.08]'
                }`}
              >
                <Sparkles size={12} className="animate-pulse" />
                {isEs ? 'Emulador IA / PINN' : 'AI Surrogate / PINN'}
              </button>
            </div>
          </Reveal>

          {/* Quick Stats Panel */}
          <Reveal delay={0.12} className="grid gap-3 sm:grid-cols-2 lg:self-end">
            {[
              {
                icon: Thermometer,
                label: isEs ? 'Temp Pico' : 'Peak Temperature',
                value: maxTemp.toFixed(1),
                suffix: ' °C',
                tone: maxTemp > 85 ? 'text-rose-400' : (maxTemp > 65 ? 'text-amber-300' : 'text-cyan-300'),
              },
              {
                icon: Moon,
                label: isEs ? 'Límite Estacionario' : 'Steady State Temp',
                value: steadyStateTemp !== null ? steadyStateTemp.toFixed(1) : (power / (emissivity * 5.67e-8 * area) + 53.1)**0.25 - 273.15,
                suffix: ' °C',
                tone: 'text-violet-300',
              },
              {
                icon: Cpu,
                label: isEs ? 'Tiempo Crítico (85°C)' : 'Time to Critical',
                value: timeToCrit !== null && timeToCrit !== undefined ? (timeToCrit >= 0 ? `${timeToCrit.toFixed(0)}s` : 'N/A') : (maxTemp >= 85 ? 'Calculando...' : 'Safe'),
                suffix: '',
                tone: maxTemp >= 85 ? 'text-rose-400' : 'text-emerald-400',
              },
              {
                icon: Activity,
                label: isEs ? 'Inferencia Activa' : 'Active Inference',
                value: mode === 'simulation' ? 'LEO ODE' : 'AI RF/PINN',
                suffix: '',
                tone: 'text-cyan-300',
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
              <h2 className="mt-1 text-xl font-bold text-white/90">{isEs ? 'Regulación Térmica' : 'Thermal Regulation'}</h2>
            </div>
          </div>

          <div className="space-y-6">
            {/* Slider 1: Internal Power */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Cpu size={13} className="text-cyan-400" />
                  {isEs ? 'Potencia Disipada (P)' : 'Internal Generated Power (P)'}
                </span>
                <span className="font-mono text-xs text-cyan-300 font-semibold">{power} W</span>
              </div>
              <input
                type="range"
                min="5"
                max="50"
                step="1"
                value={power}
                onChange={(e) => setPower(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Potencia eléctrica disipada por la CPU del servidor orbital.' : 'Electrical load dissipated as thermal energy by the server cpu.'}
              </p>
            </div>

            {/* Slider 2: Radiator Area */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Settings2 size={13} className="text-emerald-400" />
                  {isEs ? 'Área del Radiador (A)' : 'Radiator Area (A)'}
                </span>
                <span className="font-mono text-xs text-emerald-300 font-semibold">{area.toFixed(2)} m²</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.50"
                step="0.01"
                value={area}
                onChange={(e) => setArea(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Superficie expuesta encargada de irradiar calor al espacio.' : 'Total external plate surface sizing dedicated to radiating heat.'}
              </p>
            </div>

            {/* Slider 3: Emissivity */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                  <Moon size={13} className="text-violet-400" />
                  {isEs ? 'Emisividad Infrarroja (ε)' : 'Infrared Emissivity (ε)'}
                </span>
                <span className="font-mono text-xs text-violet-300 font-semibold">{emissivity.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.95"
                step="0.01"
                value={emissivity}
                onChange={(e) => setEmissivity(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-violet-400"
              />
              <p className="text-[10px] text-slate-500">
                {isEs ? 'Coeficiente de eficiencia de radiación del recubrimiento.' : 'Radiative emission efficiency coefficient of the external coating.'}
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
        <div className="space-y-6">
          <GlassPanel density="spacious" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl flex flex-col justify-between">
            <div>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="metric-label">{mode === 'simulation' ? (isEs ? 'Simulación en Vivo' : 'Live Simulation') : (isEs ? 'Predicción Inteligente' : 'Surrogate Prediction')}</p>
                  <h3 className="mt-1 text-xl font-bold text-slate-100">{isEs ? 'Trayectoria Térmica' : 'Thermal Trajectory'}</h3>
                </div>
                <Sparkles size={16} className="text-cyan-400 animate-pulse" />
              </div>

              <div className="h-[200px] w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={telemetryData} margin={{ top: 10, right: 10, bottom: 0, left: -25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="time"
                      stroke="#475569"
                      fontSize={10}
                      tickLine={false}
                      label={{ value: isEs ? 'Tiempo (min)' : 'Time (min)', position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 10 }}
                    />
                    <YAxis
                      stroke="#475569"
                      fontSize={10}
                      tickLine={false}
                      domain={[-50, 110]}
                      label={{ value: isEs ? 'Temp (°C)' : 'Temp (°C)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
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
                    
                    {/* Burnout safety line */}
                    <ReferenceLine y={85} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: 'Burnout', fill: '#f43f5e', fontSize: 9, position: 'insideTopRight' }} />
                    
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
                <div className={`h-2 w-2 rounded-full ${mode === 'simulation' ? 'bg-cyan-400' : 'bg-violet-500 animate-pulse'}`} />
                <span className="text-[10px] text-slate-400">
                  {mode === 'simulation' ? (isEs ? 'Resolución Numérica LEO' : 'Active LEO ODE Solver') : (isEs ? 'Pre-procesado PINN Activo' : 'Active PINN Surrogate')}
                </span>
              </div>
              <div className="text-right text-[10px] font-mono text-slate-500">
                Total Capacity: 500 J/K
              </div>
            </div>
          </GlassPanel>

          {/* 2D Thermal Map Rendering */}
          {thermalMap2D.length > 0 && (
            <GlassPanel density="compact" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl">
              <div className="p-4">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                  {isEs ? 'Mapa Térmico de Superficie 2D (32x32)' : '2D Surface Thermal Map (32x32)'}
                </h4>
                <div className="flex items-center gap-6">
                  {/* Small Heatmap Grid */}
                  <div className="grid grid-cols-32 gap-[1px] w-48 h-48 bg-slate-900 p-1 rounded-lg">
                    {thermalMap2D.map((row, i) =>
                      row.map((cell, j) => {
                        // Map temp value (typically -20 to 85) to a color gradient
                        const norm = Math.min(1.0, Math.max(0.0, (cell + 20) / 105));
                        const red = Math.round(norm * 255);
                        const blue = Math.round((1 - norm) * 155 + 50);
                        const green = Math.round(norm * (1 - norm) * 150);
                        return (
                          <div
                            key={`${i}-${j}`}
                            className="w-[5px] h-[5px] rounded-[1px]"
                            style={{ backgroundColor: `rgb(${red}, ${green}, ${blue})` }}
                            title={`(${i},${j}): ${cell.toFixed(1)}°C`}
                          />
                        );
                      })
                    )}
                  </div>
                  {/* Heatmap Info */}
                  <div className="flex-1 space-y-2">
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      {isEs 
                        ? 'Visualización térmica de gradiente gaussiano. El núcleo disipa más energía térmicamente (centro caliente) mientras los bordes se enfrían por radiación.'
                        : 'Gaussian gradient visualization. The center core dissipates maximum electrical heat, while external borders cool radiatively.'}
                    </p>
                    <div className="flex items-center gap-3 mt-1.5">
                      <div className="flex items-center gap-1">
                        <div className="w-2.5 h-2.5 rounded bg-blue-500" />
                        <span className="text-[9px] text-slate-400">Cold</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2.5 h-2.5 rounded bg-violet-600" />
                        <span className="text-[9px] text-slate-400">Mid</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-2.5 h-2.5 rounded bg-red-500" />
                        <span className="text-[9px] text-slate-400">Hot</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </GlassPanel>
          )}
        </div>
      </ScrollReveal>

      {/* Optimal Design & Discovered Equations Section */}
      <ScrollReveal className="grid gap-6 md:grid-cols-2">
        {/* Component 1: Optimal Pareto Design Specifications */}
        <GlassPanel density="spacious" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl">
          <div className="mb-4 flex items-center gap-3">
            <CheckCircle size={18} className="text-emerald-400" />
            <div>
              <p className="metric-label">{isEs ? 'Optimización Pareto' : 'Multi-Objective Pareto'}</p>
              <h3 className="text-lg font-bold text-white">{isEs ? 'Diseño Óptimo del Radiador' : 'Optimal Radiator Specification'}</h3>
            </div>
          </div>
          {optimalDesign ? (
            <div className="space-y-4">
              <div className="p-3 bg-emerald-500/[0.04] border border-emerald-500/10 rounded-xl flex items-center justify-between">
                <span className="text-xs text-slate-300">{isEs ? 'Estado de Eficiencia:' : 'Efficiency Status:'}</span>
                <span className="text-xs font-semibold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 uppercase tracking-wide">
                  {optimalDesign.efficiency_status}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400">{isEs ? 'Área Óptima:' : 'Optimal Area:'}</p>
                  <p className="text-xl font-bold text-white mt-1">{optimalDesign.optimal_area_m2.toFixed(4)} <span className="text-xs text-slate-400">m²</span></p>
                </div>
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400">{isEs ? 'Emisividad Óptima:' : 'Optimal Emissivity:'}</p>
                  <p className="text-xl font-bold text-white mt-1">{optimalDesign.optimal_emissivity.toFixed(2)}</p>
                </div>
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400">{isEs ? 'Masa Estimada:' : 'Estimated Mass:'}</p>
                  <p className="text-xl font-bold text-white mt-1">{optimalDesign.estimated_mass_kg.toFixed(1)} <span className="text-xs text-slate-400">kg</span></p>
                </div>
                <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400">{isEs ? 'Costo Estimado:' : 'Estimated Unit Cost:'}</p>
                  <p className="text-xl font-bold text-white mt-1">${optimalDesign.estimated_cost_usd.toLocaleString()} <span className="text-xs text-slate-400">USD</span></p>
                </div>
              </div>
              <p className="text-[10px] text-slate-500 italic mt-2">
                {isEs 
                  ? '*Resultados obtenidos del algoritmo de optimización bayesiana tras 300 evaluaciones multi-criterio.' 
                  : '*Results compiled via Bayesian Pareto sequential optimization search across 300 evaluations.'}
              </p>
            </div>
          ) : (
            <div className="py-10 text-center text-xs text-slate-500">
              {isEs ? 'Calculando frente de Pareto óptimo...' : 'Extracting optimal Pareto front...'}
            </div>
          )}
        </GlassPanel>

        {/* Component 2: Discovered Symbolic Equations Candidates */}
        <GlassPanel density="spacious" className="rounded-2xl border-white/[0.08] bg-[#070c1d]/60 backdrop-blur-2xl">
          <div className="mb-4 flex items-center gap-3">
            <Info size={18} className="text-cyan-300" />
            <div>
              <p className="metric-label">{isEs ? 'Descubrimiento Simbólico' : 'Symbolic Regression'}</p>
              <h3 className="text-lg font-bold text-white">{isEs ? 'Fórmulas Físicas Descubiertas' : 'Discovered Closed-Form Equations'}</h3>
            </div>
          </div>
          {equations.length > 0 ? (
            <div className="space-y-3.5">
              {equations.map((eq) => (
                <div key={eq.variable} className="p-3 bg-white/[0.02] border border-white/5 rounded-xl space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-cyan-300 font-mono">{eq.variable}</span>
                    <span className="text-[9px] text-slate-500">Complexity: {eq.complexity}</span>
                  </div>
                  {/* Custom representation of math formula */}
                  <div className="p-2 bg-slate-950/60 rounded border border-white/[0.02] font-mono text-[11px] text-slate-200 overflow-x-auto whitespace-pre">
                    {eq.equation}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-10 text-center text-xs text-slate-500">
              {isEs ? 'Cargando expresiones simbólicas...' : 'Loading symbolic expressions...'}
            </div>
          )}
        </GlassPanel>
      </ScrollReveal>
    </FocusContainer>
  );
}
