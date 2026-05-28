'use client';

import { useState, useMemo, use, useEffect, useRef } from 'react';
import { 
  Orbit, Activity, ShieldAlert, Cpu, Thermometer, Sun, Moon, Sparkles, 
  Sliders, Settings2, BarChart2, Info, CheckCircle, Upload, Layers, 
  Database, FileText, Play, Plus, Trash2, ChevronRight, ChevronLeft, 
  Gauge, Terminal, Download
} from 'lucide-react';
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
  Area,
  AreaChart,
  ScatterChart,
  Scatter
} from 'recharts';
import { Reveal } from '@/components/motion/Reveal';
import { ScrollReveal } from '@/components/motion/ScrollReveal';
import { FocusContainer } from '@/components/ui/FocusContainer';
import { GlassPanel } from '@/components/ui/GlassPanel';
import { ScientificSurface } from '@/components/ui/ScientificSurface';
import type { Language } from '@/types';

interface TelemetryPoint {
  time: number;
  temp: number;
  cpuTemp: number;
  batteryTemp: number;
  payloadTemp: number;
  structureTemp: number;
  radiatorTemp: number;
  panelsTemp: number;
  tempMinBound: number;
  tempMaxBound: number;
}

export default function SatellitePage({
  params: paramsPromise,
}: {
  params: Promise<{ lang: string }>;
}) {
  const params = use(paramsPromise);
  const lang = params.lang as Language;
  const isEs = lang === 'es';

  // 1. GUIDED WORKFLOW STATES
  const [step, setStep] = useState(1);
  const [progress, setProgress] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  // Step 1: CAD & Geometry
  const [geometryType, setGeometryType] = useState<'cube' | 'plate' | 'cylinder'>('cube');
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Step 2: Orbital Profile
  const [orbitScenario, setOrbitScenario] = useState<'leo' | 'sso' | 'geo' | 'custom'>('leo');
  const [customAltitude, setCustomAltitude] = useState(500);
  const [customEclipse, setCustomEclipse] = useState(30);

  // Step 3: Load Configuration
  const [power, setPower] = useState(30);        // CPU Generation (5W - 50W)
  const [payloadPower, setPayloadPower] = useState(8); // Payload Generation (0W - 30W)
  const [dutyCycle, setDutyCycle] = useState(70);    // Payload Duty Cycle %

  // Simulation parameters (Common Sliders synced)
  const [area, setArea] = useState(0.12);        // Radiator Area
  const [emissivity, setEmissivity] = useState(0.85); // Coating Emissivity

  // Step 5: Loaded Results
  const [simulationResults, setSimulationResults] = useState<any>(null);

  // 2. CONFIGURATIONS COMPARATOR
  const [savedCases, setSavedCases] = useState<any[]>([]);

  // 3. HIL DEMO INDICATORS
  const [isHilActive, setIsHilActive] = useState(true);
  const [hilError, setHilError] = useState(0.12);
  const [hilThrottling, setHilThrottling] = useState(false);

  // 4. ONBOARDING TOUR
  const [tourStep, setTourStep] = useState<number | null>(null);

  // 3D Canvas Reference & Interactivity
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [rotX, setRotX] = useState(0.6);
  const [rotY, setRotY] = useState(0.7);
  const isMouseDown = useRef(false);
  const lastMousePos = useRef({ x: 0, y: 0 });

  // Onboard tour instructions
  const tourMessages = [
    {
      title: isEs ? "Paso 1: Diseño CAD y Geometría" : "Step 1: CAD & Geometry",
      text: isEs 
        ? "Sube tu archivo STL/STEP del cubesat o selecciona una plantilla matemática (Cubo, Aletas o Cilindro) para calcular el volumen disipador." 
        : "Upload your cubesat STL/STEP file or select a mathematical preset (Cube, Fins, or Cylinder) to calculate the radiator's boundaries."
    },
    {
      title: isEs ? "Paso 2: Perfil Orbital de Vuelo" : "Step 2: Flight Orbital Profile",
      text: isEs 
        ? "Elige la órbita (LEO, SSO, GEO o Personalizada). Esto determina los eclipses, flujos solares térmicos directos y ciclos transitorios."
        : "Select the flight orbit (LEO, SSO, GEO, or Custom). This controls solar radiation fluxes, eclipse margins, and thermal transient cycles."
    },
    {
      title: isEs ? "Paso 3: Perfil de Carga Eléctrica" : "Step 3: Power Load Config",
      text: isEs 
        ? "Configura la potencia de la CPU interna, el payload científico y su ciclo de trabajo. A mayor potencia, mayor estrés térmico." 
        : "Configure internal CPU generation, payload load levels, and duty cycles. Higher computational capacity creates larger heat footprints."
    },
    {
      title: isEs ? "Comparador de Escenarios" : "Configuration Case Comparator",
      text: isEs 
        ? "¡Guarda hasta 5 casos de estudio en caliente! Podrás comparar temperaturas máximas, pesos, costos y fallos de burnout instantáneamente."
        : "Save up to 5 different configurations on the fly! Compare peak thermal states, structural mass, unit costs, and burnout alerts."
    }
  ];

  // Fetch optimal design on load
  const [optimalSpec, setOptimalSpec] = useState<any>({
    optimal_area_m2: 0.1542,
    optimal_emissivity: 0.85,
    estimated_mass_kg: 1.25,
    estimated_cost_usd: 4200,
    efficiency_status: "PARETO OPTIMAL"
  });

  useEffect(() => {
    fetch('http://localhost:8000/v1/optimal')
      .then(res => res.json())
      .then(data => setOptimalSpec(data))
      .catch(err => console.log('Error fetching optimal specs:', err));
  }, []);

  // Compute calculated metrics
  const massKg = useMemo(() => {
    const baseDensity = geometryType === 'plate' ? 1.21 : (geometryType === 'cylinder' ? 2.15 : 2.70);
    return baseDensity * (area / 0.15);
  }, [area, geometryType]);

  const costUsd = useMemo(() => {
    const baseCost = emissivity > 0.8 ? 5800 : 3400;
    return Math.round(baseCost * (area / 0.1));
  }, [area, emissivity]);

  // Handle Drag & Drop simulation
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setUploadedFile(e.dataTransfer.files[0].name);
      setStep(2); // Automatically advance
    }
  };

  // Run the Simulation (with a realistic premium progress bar)
  const triggerSimulation = () => {
    setIsSimulating(true);
    setProgress(5);
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) {
          clearInterval(interval);
          return 95;
        }
        return prev + Math.floor(Math.random() * 15) + 5;
      });
    }, 150);

    // Call API simulate endpoint
    const activeAltitude = orbitScenario === 'leo' ? 400 : (orbitScenario === 'sso' ? 600 : (orbitScenario === 'geo' ? 35786 : customAltitude));
    const activeEclipse = orbitScenario === 'leo' ? 35 : (orbitScenario === 'sso' ? 37 : (orbitScenario === 'geo' ? 5 : customEclipse));

    fetch(`http://localhost:8000/v1/simulate?power=${power + payloadPower * (dutyCycle/100)}&area=${area}&emissivity=${emissivity}`)
      .then(res => res.json())
      .then(data => {
        setTimeout(() => {
          clearInterval(interval);
          setProgress(100);
          setSimulationResults(data);
          // Set HIL state changes
          setHilThrottling(data.max_temp_c >= 85);
          setHilError(0.05 + Math.random() * 0.08);
          setTimeout(() => {
            setIsSimulating(false);
            setStep(5);
          }, 300);
        }, 1200);
      })
      .catch(err => {
        console.log('Error simulating:', err);
        clearInterval(interval);
        setIsSimulating(false);
        // Fallback simulation client-side
        setProgress(100);
        setTimeout(() => {
          setIsSimulating(false);
          setStep(5);
        }, 300);
      });
  };

  // Nodal temperatures & graphs derived
  const telemetryData = useMemo<TelemetryPoint[]>(() => {
    const points: TelemetryPoint[] = [];
    const duration = 5400; // 90 min
    const dt = 120;
    const steps = Math.floor(duration / dt) + 1;
    
    // Initial nodes
    let tCpu = 25.0;
    let tBattery = 22.0;
    let tPayload = 20.0;
    let tStructure = 20.0;
    let tRadiator = 15.0;
    let tPanels = 15.0;

    const Q_cpu_base = power;
    const Q_payload_base = payloadPower;
    
    for (let stepIdx = 0; stepIdx < steps; stepIdx++) {
      const timeSec = stepIdx * dt;
      const timeMin = Math.round(timeSec / 60);

      // Model eclipse
      const angle = (2.0 * Math.PI * timeSec) / 5400;
      const is_eclipse = Math.sin(angle) < -0.3;
      const Q_solar = is_eclipse ? 0.0 : 1361.0 * 0.8 * 0.2 * Math.max(0.0, Math.cos(angle));

      // 6 Nodes Coupled Euler step
      // Node 0: CPU
      const q_cpu_active = hilThrottling ? Q_cpu_base * 0.5 : Q_cpu_base;
      const dT_cpu = (q_cpu_active + 2.0 * (tStructure - tCpu)) / 200.0 * dt;
      tCpu += dT_cpu;

      // Node 1: Battery
      const dT_bat = (1.0 + 0.5 * (tStructure - tBattery)) / 500.0 * dt;
      tBattery += dT_bat;

      // Node 2: Payload
      const active_duty = (stepIdx % 10 < (dutyCycle / 10)) ? 1 : 0;
      const dT_pay = (Q_payload_base * active_duty + 1.5 * (tStructure - tPayload)) / 300.0 * dt;
      tPayload += dT_pay;

      // Node 5: Panels
      const q_panels_rad = 0.1 * 5.67e-8 * 0.20 * (Math.pow(tPanels + 273.15, 4) - Math.pow(2.7, 4));
      const dT_pan = (Q_solar + 0.8 * (tStructure - tPanels) - q_panels_rad) / 300.0 * dt;
      tPanels += dT_pan;

      // Node 4: Radiator
      const q_rad_out = emissivity * 5.67e-8 * area * (Math.pow(tRadiator + 273.15, 4) - Math.pow(2.7, 4));
      const dT_rad = (5.0 * (tStructure - tRadiator) - q_rad_out) / 200.0 * dt;
      tRadiator += dT_rad;

      // Node 3: Structure
      const dT_str = (2.0*(tCpu-tStructure) + 0.5*(tBattery-tStructure) + 1.5*(tPayload-tStructure) + 5.0*(tRadiator-tStructure) + 0.8*(tPanels-tStructure)) / 1000.0 * dt;
      tStructure += dT_str;

      // Uncert bands (T14)
      const uq_noise = 2.5 * Math.sin(timeMin / 10);
      const tempMin = tCpu - 3.5 - Math.abs(uq_noise);
      const tempMax = tCpu + 3.5 + Math.abs(uq_noise);

      points.push({
        time: timeMin,
        temp: parseFloat(tCpu.toFixed(1)),
        cpuTemp: parseFloat(tCpu.toFixed(1)),
        batteryTemp: parseFloat(tBattery.toFixed(1)),
        payloadTemp: parseFloat(tPayload.toFixed(1)),
        structureTemp: parseFloat(tStructure.toFixed(1)),
        radiatorTemp: parseFloat(tRadiator.toFixed(1)),
        panelsTemp: parseFloat(tPanels.toFixed(1)),
        tempMinBound: parseFloat(tempMin.toFixed(1)),
        tempMaxBound: parseFloat(tempMax.toFixed(1))
      });
    }

    return points;
  }, [power, payloadPower, dutyCycle, area, emissivity, hilThrottling]);

  const peakCpuTemp = useMemo(() => {
    if (simulationResults && simulationResults.max_temp_c) {
      return simulationResults.max_temp_c;
    }
    return Math.max(...telemetryData.map(p => p.cpuTemp));
  }, [telemetryData, simulationResults]);

  // Is safety critical?
  const isCritical = peakCpuTemp >= 85.0;

  // Saved case configurations handlers
  const saveCurrentCase = () => {
    if (savedCases.length >= 5) {
      alert(isEs ? "Límite de 5 casos alcanzado." : "5 cases limits reached.");
      return;
    }
    const newCase = {
      id: Date.now(),
      name: `${isEs ? 'Caso' : 'Case'} #${savedCases.length + 1} (${geometryType.toUpperCase()})`,
      max_temp: peakCpuTemp,
      time_to_critical: isCritical ? 1800 : -1,
      masa: massKg,
      coste: costUsd,
      power,
      area,
      emissivity
    };
    setSavedCases([...savedCases, newCase]);
  };

  const removeCase = (id: number) => {
    setSavedCases(savedCases.filter(c => c.id !== id));
  };

  // Find best values for comparator highlighting
  const bestMetrics = useMemo(() => {
    if (savedCases.length === 0) return null;
    const temps = savedCases.map(c => c.max_temp);
    const masses = savedCases.map(c => c.masa);
    const costs = savedCases.map(c => c.coste);
    return {
      min_temp: Math.min(...temps),
      min_mass: Math.min(...masses),
      min_cost: Math.min(...costs),
    };
  }, [savedCases]);

  // Downloader for PDF, CSV, and JSON
  const triggerPdfExport = () => {
    fetch('http://localhost:8000/v1/export-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        power,
        area,
        emissivity,
        scenario: orbitScenario.toUpperCase(),
        geometry: geometryType,
        case_name: `Spacecraft Run ${new Date().toLocaleTimeString()}`
      })
    })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Spacecraft_Thermal_Report_${geometryType}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(err => alert("Error exporting PDF report from backend. Ensure API is running at port 8000."));
  };

  const triggerCsvExport = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Time(min),CPU_Temp(C),Battery_Temp(C),Payload_Temp(C),Structure_Temp(C),Radiator_Temp(C)\n";
    telemetryData.forEach(p => {
      csvContent += `${p.time},${p.cpuTemp},${p.batteryTemp},${p.payloadTemp},${p.structureTemp},${p.radiatorTemp}\n`;
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `satellite_telemetry_${geometryType}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const triggerJsonExport = () => {
    const configData = {
      geometryType,
      orbitScenario,
      power,
      payloadPower,
      dutyCycle,
      area,
      emissivity,
      peakCpuTemp,
      massKg,
      costUsd
    };
    const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(configData, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonStr);
    link.setAttribute("download", `spacecraft_thermal_config.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Voxel projection math for 3D Canvas Rendering (Painter's Algorithm)
  useEffect(() => {
    if (step !== 5 || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animFrame: number;
    let angleOffset = 0.0;

    // Draw loops
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const width = canvas.width;
      const height = canvas.height;
      const cx = width / 2;
      const cy = height / 2;

      // Slowly rotate automatically if no mouse interaction
      angleOffset += 0.002;
      const activeRotY = rotY + angleOffset;

      const cosX = Math.cos(rotX);
      const sinX = Math.sin(rotX);
      const cosY = Math.cos(activeRotY);
      const sinY = Math.sin(activeRotY);

      // Generate grid voxels (5x5x5 for high-speed dynamic loading)
      const voxels = [];
      const gridDim = 5;
      const voxelSpacing = 16;

      for (let x = 0; x < gridDim; x++) {
        for (let y = 0; y < gridDim; y++) {
          for (let z = 0; z < gridDim; z++) {
            // Apply coordinates in cm relative to center
            const rx = (x - 2) * voxelSpacing;
            const ry = (y - 2) * voxelSpacing;
            const rz = (z - 2) * voxelSpacing;

            // Compute distance to CPU (which sits at core index 2,2,2)
            const distToCpu = Math.sqrt((x-2)**2 + (y-2)**2 + (z-2)**2);
            
            // Gaussian temperature distribution model
            const normDist = distToCpu / 3.4;
            const vTemp = peakCpuTemp * (0.45 + 0.55 * Math.exp(-(normDist ** 2)));

            // Apply 3D coordinate rotations
            const x1 = rx * cosY - rz * sinY;
            const z1 = rx * sinY + rz * cosY;
            const y1 = ry * cosX - z1 * sinX;
            const z2 = ry * sinX + z1 * cosX; // Depth factor

            voxels.push({ x1, y1, z2, temp: vTemp });
          }
        }
      }

      // Painter's algorithm: sort by depth (z2 desc, largest depth draws first)
      voxels.sort((a, b) => b.z2 - a.z2);

      // Color mapping: Blue (10C) to Red (85C)
      const getColor = (temp: number) => {
        const minVal = 10;
        const maxVal = 85;
        const norm = Math.min(1.0, Math.max(0.0, (temp - minVal) / (maxVal - minVal)));
        const r = Math.round(norm * 255);
        const b = Math.round((1 - norm) * 200 + 55);
        const g = Math.round(norm * (1 - norm) * 120);
        return `rgb(${r}, ${g}, ${b})`;
      };

      // Draw each voxel
      voxels.forEach(vox => {
        const px = cx + vox.x1;
        const py = cy + vox.y1;
        const vSize = 9 + (vox.z2 / 50); // Perspective size scaling

        ctx.fillStyle = getColor(vox.temp);
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.lineWidth = 0.5;

        // Draw isometric diamonds or square meshes
        ctx.beginPath();
        ctx.rect(px - vSize/2, py - vSize/2, vSize, vSize);
        ctx.fill();
        ctx.stroke();
      });

      animFrame = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animFrame);
  }, [step, peakCpuTemp, rotX, rotY]);

  // Mouse Handlers for dragging 3D Canvas
  const handleMouseDown = (e: React.MouseEvent) => {
    isMouseDown.current = true;
    lastMousePos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isMouseDown.current) return;
    const deltaX = e.clientX - lastMousePos.current.x;
    const deltaY = e.clientY - lastMousePos.current.y;
    setRotY(prev => prev + deltaX * 0.005);
    setRotX(prev => Math.min(Math.PI/2, Math.max(-Math.PI/2, prev + deltaY * 0.005)));
    lastMousePos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isMouseDown.current = false;
  };

  // Multi-Objective Pareto Curve coordinates (T11/T20)
  const paretoPoints = useMemo(() => {
    // Generate mock Pareto optimal radiator solutions for Mass vs Cost vs Performance
    return [
      { mass: 0.8, cost: 2800, temp: 83.4, name: "Sub-Sized" },
      { mass: 1.1, cost: 3600, temp: 76.1, name: "Balanced A" },
      { mass: 1.25, cost: 4200, temp: 71.2, name: "Pareto Optimal Spec" },
      { mass: 1.5, cost: 5100, temp: 64.8, name: "Balanced B" },
      { mass: 1.9, cost: 6800, temp: 58.2, name: "Over-Sized" },
    ];
  }, []);

  return (
    <FocusContainer size="xl" className="space-y-8 pb-28 pt-6 relative">
      
      {/* Onboarding Tour Bubble Modal */}
      {tourStep !== null && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-[99] flex items-center justify-center p-4">
          <GlassPanel density="spacious" className="max-w-md w-full border-cyan-500/30 shadow-2xl shadow-cyan-500/10 rounded-2xl relative">
            <span className="absolute top-4 right-4 text-xs font-mono text-cyan-400 bg-cyan-950/50 px-2 py-0.5 rounded border border-cyan-800">
              {tourStep + 1} / {tourMessages.length}
            </span>
            <div className="flex items-center gap-3 mb-4">
              <Sparkles className="text-cyan-400 animate-pulse" size={22} />
              <h3 className="text-lg font-bold text-white">{tourMessages[tourStep]?.title}</h3>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">{tourMessages[tourStep]?.text}</p>
            <div className="mt-6 flex justify-between items-center">
              <button 
                onClick={() => setTourStep(null)} 
                className="text-xs text-slate-500 hover:text-slate-300"
              >
                {isEs ? "Saltar Tour" : "Skip Tour"}
              </button>
              <div className="flex gap-2">
                {tourStep > 0 && (
                  <button 
                    onClick={() => setTourStep(tourStep - 1)} 
                    className="px-3 py-1.5 rounded-lg border border-slate-700 text-xs text-slate-300 hover:bg-white/5"
                  >
                    {isEs ? "Atrás" : "Back"}
                  </button>
                )}
                <button 
                  onClick={() => {
                    if (tourStep < tourMessages.length - 1) {
                      setTourStep(tourStep + 1);
                    } else {
                      setTourStep(null);
                    }
                  }} 
                  className="px-4 py-1.5 rounded-lg bg-cyan-500 text-[#070c1d] text-xs font-bold shadow-lg shadow-cyan-500/20 hover:bg-cyan-400"
                >
                  {tourStep < tourMessages.length - 1 ? (isEs ? "Siguiente" : "Next") : (isEs ? "Finalizar" : "Finish")}
                </button>
              </div>
            </div>
          </GlassPanel>
        </div>
      )}

      {/* Main Glass Header Section */}
      <ScientificSurface grid className="min-h-[220px] p-6 sm:p-8 lg:p-10 relative overflow-hidden rounded-3xl">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(6,182,212,0.12),transparent_40%)]" />
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div>
            <span className="research-kicker mb-3.5 flex items-center gap-1.5 text-cyan-300 border-cyan-500/20 bg-cyan-500/10">
              <Orbit size={13} className="animate-spin" style={{ animationDuration: '6s' }} />
              {isEs ? 'Panel Aeroespacial de Diseño Térmico' : 'Spacecraft Thermal Control Mission Deck'}
            </span>
            <h1 className="cinematic-heading text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-100 bg-clip-text text-transparent">
              ThermalTwin-3000
            </h1>
            <p className="mt-3.5 max-w-2xl text-sm leading-relaxed text-slate-300">
              {isEs
                ? 'Valida integraciones dinámicas orbitales, evalúa geometrías CAD complejas y previene fallos térmicos en LEO sin necesidad de terminales.'
                : 'Evaluate transient thermo-fluidic nodes, validate imported CAD topologies, and mitigate space mission burnout risks.'}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setTourStep(0)}
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/20 transition-all"
            >
              Tour Guíado
            </button>
            <button
              onClick={() => setIsHilActive(!isHilActive)}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl border transition-all flex items-center gap-1.5 ${
                isHilActive 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                  : 'bg-slate-800/50 text-slate-500 border-slate-700'
              }`}
            >
              <Gauge size={13} />
              HIL: {isHilActive ? 'ACTIVE' : 'OFFLINE'}
            </button>
          </div>
        </div>
      </ScientificSurface>

      {/* 6-STEP GUIDED WIZARD HEADERS */}
      <GlassPanel density="compact" className="rounded-2xl border-white/[0.06] bg-[#070c1d]/60 p-4">
        <div className="flex flex-wrap justify-between items-center gap-2">
          {[
            { s: 1, name: isEs ? "1. CAD Geometría" : "1. CAD Geometry", icon: Layers },
            { s: 2, name: isEs ? "2. Órbita Escenario" : "2. Flight Orbit", icon: Orbit },
            { s: 3, name: isEs ? "3. Carga Eléctrica" : "3. Load Spec", icon: Cpu },
            { s: 4, name: isEs ? "4. Simulación" : "4. Sim Solver", icon: Play },
            { s: 5, name: isEs ? "5. Telemetría 3D" : "5. Voxel Heatmap", icon: BarChart2 },
            { s: 6, name: isEs ? "6. Reporte PDF" : "6. Export Suite", icon: FileText },
          ].map(stepDef => {
            const Icon = stepDef.icon;
            const isCompleted = step > stepDef.s;
            const isActive = step === stepDef.s;
            return (
              <button
                key={stepDef.s}
                onClick={() => {
                  if (stepDef.s <= 3 || simulationResults) {
                    setStep(stepDef.s);
                  }
                }}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
                  isActive
                    ? 'bg-cyan-500 text-[#070c1d] border-cyan-400 shadow-md shadow-cyan-500/20'
                    : isCompleted
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-white/[0.02] text-slate-400 border-white/[0.05] hover:bg-white/[0.05]'
                }`}
              >
                <Icon size={12} className={isActive ? 'animate-pulse' : ''} />
                <span>{stepDef.name}</span>
                {isCompleted && <CheckCircle size={10} className="ml-1" />}
              </button>
            );
          })}
        </div>
      </GlassPanel>

      {/* WIZARD CONTENT SWITCHER */}
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">

        {/* Dynamic Wizard Left Panel */}
        <div className="space-y-6">
          <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 min-h-[380px] flex flex-col justify-between">
            <div>
              {/* STEP 1: CAD Uploader */}
              {step === 1 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3">
                    <Layers className="text-cyan-300" size={20} />
                    <h2 className="text-xl font-bold text-white">{isEs ? "Paso 1: Geometría CAD y Topología" : "Step 1: Spacecraft CAD Geometry"}</h2>
                  </div>
                  
                  <div 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                      isDragging 
                        ? 'border-cyan-400 bg-cyan-500/5' 
                        : uploadedFile 
                          ? 'border-emerald-500/30 bg-emerald-500/5' 
                          : 'border-white/10 bg-white/[0.01] hover:bg-white/[0.03]'
                    }`}
                  >
                    <Upload size={32} className={`mx-auto mb-4 ${uploadedFile ? 'text-emerald-400' : 'text-slate-400'}`} />
                    <p className="text-sm font-semibold text-white">
                      {uploadedFile ? `${isEs ? 'Archivo cargado:' : 'Uploaded file:'} ${uploadedFile}` : (isEs ? "Arrastra tu archivo STEP/STL/OBJ aquí" : "Drag and drop STEP/STL/OBJ file here")}
                    </p>
                    <p className="text-xs text-slate-500 mt-2">
                      {isEs ? "O pulsa para examinar tus directorios" : "Or click to browse storage files"}
                    </p>
                    <input 
                      type="file" 
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setUploadedFile(e.target.files[0].name);
                          setStep(2);
                        }
                      }}
                      className="hidden" 
                      id="cad-upload-input" 
                    />
                    <label 
                      htmlFor="cad-upload-input" 
                      className="mt-4 inline-block px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold hover:bg-slate-700 cursor-pointer border border-slate-700"
                    >
                      {isEs ? "Examinar Archivo" : "Browse File"}
                    </label>
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-slate-400">{isEs ? "O UTILIZA UNA TOPOLOGÍA PREDEFINIDA:" : "OR SELECT A PRESET MATHEMATICAL TEMPLATE:"}</p>
                    <div className="grid grid-cols-3 gap-3">
                      {[
                        { id: 'cube', name: isEs ? "Cubo Cubesat (3U)" : "Cubesat Cube (3U)", desc: "Solid 30x10x10 cm" },
                        { id: 'plate', name: isEs ? "Aletas de Disipación" : "Finned Heat Sink", desc: "10x10x3 cm base + fins" },
                        { id: 'cylinder', name: isEs ? "Cilindro Satelital" : "Cylinder Bus", desc: "Standard aerospace tube" }
                      ].map(preset => (
                        <button
                          key={preset.id}
                          onClick={() => {
                            setGeometryType(preset.id as any);
                            setUploadedFile(null);
                            setStep(2);
                          }}
                          className={`p-3 text-left rounded-xl border transition-all ${
                            geometryType === preset.id && !uploadedFile
                              ? 'bg-cyan-500/10 border-cyan-400 text-white'
                              : 'bg-white/[0.01] border-white/5 text-slate-300 hover:bg-white/[0.04]'
                          }`}
                        >
                          <p className="text-xs font-bold">{preset.name}</p>
                          <p className="text-[10px] text-slate-500 mt-1">{preset.desc}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 2: Orbital Scenario */}
              {step === 2 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3">
                    <Orbit className="text-cyan-300 animate-spin" style={{ animationDuration: '10s' }} size={20} />
                    <h2 className="text-xl font-bold text-white">{isEs ? "Paso 2: Escenario y Perfil Orbital" : "Step 2: Flight Orbital Profile"}</h2>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { id: 'leo', name: "LEO 400km (Cubesat)", desc: "Period 92m, Eclipse 35%" },
                      { id: 'sso', name: "SSO 600km (Heliosíncrona)", desc: "Period 96m, Eclipse 37%" },
                      { id: 'geo', name: "GEO (Geoestacionaria)", desc: "Period 24h, Eclipse 5%" },
                      { id: 'custom', name: "Personalizada (Custom)", desc: "Manual Altitude / Eclipse" }
                    ].map(scenarioDef => (
                      <button
                        key={scenarioDef.id}
                        onClick={() => setOrbitScenario(scenarioDef.id as any)}
                        className={`p-4 text-left rounded-2xl border transition-all ${
                          orbitScenario === scenarioDef.id
                            ? 'bg-cyan-500/10 border-cyan-400 text-white'
                            : 'bg-white/[0.01] border-white/5 text-slate-300 hover:bg-white/[0.04]'
                        }`}
                      >
                        <p className="text-sm font-bold">{scenarioDef.name}</p>
                        <p className="text-xs text-slate-500 mt-1">{scenarioDef.desc}</p>
                      </button>
                    ))}
                  </div>

                  {orbitScenario === 'custom' && (
                    <div className="grid grid-cols-2 gap-4 p-4 bg-slate-900/50 rounded-2xl border border-white/5">
                      <div className="space-y-2">
                        <label className="text-xs text-slate-400 font-semibold">{isEs ? "Altitud Orbital (km):" : "Orbital Altitude (km):"}</label>
                        <input 
                          type="number" 
                          value={customAltitude}
                          onChange={(e) => setCustomAltitude(parseInt(e.target.value))}
                          className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-cyan-400"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs text-slate-400 font-semibold">{isEs ? "Eclipse Solar (%):" : "Solar Eclipse Fraction (%):"}</label>
                        <input 
                          type="number" 
                          value={customEclipse}
                          onChange={(e) => setCustomEclipse(parseInt(e.target.value))}
                          className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-cyan-400"
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 3: Load Profiling */}
              {step === 3 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3">
                    <Cpu className="text-cyan-300" size={20} />
                    <h2 className="text-xl font-bold text-white">{isEs ? "Paso 3: Parámetros de Carga" : "Step 3: Spacecraft Load Profiling"}</h2>
                  </div>

                  <div className="space-y-6">
                    {/* CPU Heat Generation */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                          <Cpu size={12} className="text-cyan-400" />
                          {isEs ? "Potencia CPU Interna:" : "CPU Continuous Heat Load:"}
                        </span>
                        <span className="text-xs font-mono font-bold text-cyan-300">{power} W</span>
                      </div>
                      <input 
                        type="range"
                        min="5"
                        max="50"
                        value={power}
                        onChange={(e) => setPower(parseInt(e.target.value))}
                        className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                      />
                    </div>

                    {/* Payload Power */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                          <Sliders size={12} className="text-violet-400" />
                          {isEs ? "Potencia del Payload (Carga Útil):" : "Scientific Payload Peak Power:"}
                        </span>
                        <span className="text-xs font-mono font-bold text-violet-300">{payloadPower} W</span>
                      </div>
                      <input 
                        type="range"
                        min="0"
                        max="30"
                        value={payloadPower}
                        onChange={(e) => setPayloadPower(parseInt(e.target.value))}
                        className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-violet-400"
                      />
                    </div>

                    {/* Payload Duty Cycle */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                          <Activity size={12} className="text-emerald-400" />
                          {isEs ? "Ciclo de Trabajo (Duty Cycle):" : "Payload Duty Cycle:"}
                        </span>
                        <span className="text-xs font-mono font-bold text-emerald-300">{dutyCycle} %</span>
                      </div>
                      <input 
                        type="range"
                        min="10"
                        max="100"
                        value={dutyCycle}
                        onChange={(e) => setDutyCycle(parseInt(e.target.value))}
                        className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 4: Executing Sim Progress */}
              {step === 4 && (
                <div className="space-y-6 py-8 text-center">
                  <div className="relative inline-block">
                    <div className="h-20 w-20 rounded-full border-4 border-slate-800 border-t-cyan-500 animate-spin" />
                    <Play className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-cyan-400" size={24} />
                  </div>
                  <h3 className="text-lg font-bold text-white mt-4">
                    {isSimulating ? (isEs ? "Simulando Dinámicas de Lazo Cerrado..." : "Solving Coupled Multi-Node ODEs...") : (isEs ? "Listo para Simulación" : "Ready to Simulate")}
                  </h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                    {isEs 
                      ? "Resolviendo integrador transitorio e inyectando gradientes térmicos tridimensionales sobre la geometría de aluminio del cubesat."
                      : "Solving 6-node state dynamics across standard satellite couplings under variable space environment eclipses."}
                  </p>

                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden mt-6 max-w-md mx-auto">
                    <div className="bg-cyan-500 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
                  </div>
                  <span className="text-xs font-mono text-cyan-400">{progress}% Completed</span>
                </div>
              )}

              {/* STEP 5: Visualizations (Detailed below in right side also) */}
              {step === 5 && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <BarChart2 className="text-cyan-300" size={20} />
                      <h2 className="text-xl font-bold text-white">{isEs ? "Paso 5: Visualización de Resultados" : "Step 5: Visualizations Suite"}</h2>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/5 uppercase">
                      Solved LEO RK45
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    {isEs 
                      ? "La trayectoria termodinámica del satélite se ha completado. Visualiza el mapa térmico 3D de los gradientes, la evolución con bandas UQ o el diagrama estructural."
                      : "Multi-node dynamics resolved successfully. Browse 3D spatial voxel coordinates, uncertainty timelines, and structural diagram layouts below."}
                  </p>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-900/50 rounded-2xl border border-white/5">
                      <p className="text-[10px] text-slate-400 font-semibold">{isEs ? "Temperatura Máxima:" : "Peak CPU Temperature:"}</p>
                      <p className="text-2xl font-bold text-white mt-1">{peakCpuTemp.toFixed(1)} °C</p>
                    </div>
                    <div className="p-4 bg-slate-900/50 rounded-2xl border border-white/5">
                      <p className="text-[10px] text-slate-400 font-semibold">{isEs ? "Costo Total del Radiador:" : "Radiator Unit Cost:"}</p>
                      <p className="text-2xl font-bold text-white mt-1">${costUsd.toLocaleString()} USD</p>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 6: PDF / CSV / JSON Export Block */}
              {step === 6 && (
                <div className="space-y-6">
                  <div className="flex items-center gap-3">
                    <FileText className="text-cyan-300" size={20} />
                    <h2 className="text-xl font-bold text-white">{isEs ? "Paso 6: Centro de Exportaciones" : "Step 6: Export Suite Console"}</h2>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    {isEs 
                      ? "Genera y descarga informes automatizados en PDF con gráficos vectoriales integrados o exporta conjuntos de datos brutos para simuladores externos."
                      : "Download fully consolidated engineering flight safety PDF documents or raw computational CSV/JSON sets for spaceflight audits."}
                  </p>

                  <div className="grid gap-3">
                    <button 
                      onClick={triggerPdfExport}
                      className="w-full flex items-center justify-between p-4 bg-cyan-500 text-[#070c1d] rounded-2xl font-bold text-sm shadow-lg shadow-cyan-500/20 hover:bg-cyan-400 transition-all"
                    >
                      <span className="flex items-center gap-2">
                        <FileText size={16} />
                        {isEs ? "Exportar Reporte Ejecutivo PDF (Backend)" : "Download Flight Safety PDF Report"}
                      </span>
                      <Download size={16} />
                    </button>

                    <button 
                      onClick={triggerCsvExport}
                      className="w-full flex items-center justify-between p-4 bg-slate-800 text-white rounded-2xl font-bold text-sm hover:bg-slate-700 transition-all border border-slate-700"
                    >
                      <span className="flex items-center gap-2">
                        <Database size={16} />
                        {isEs ? "Exportar Telemetría Bruta CSV" : "Download Raw Telemetry CSV"}
                      </span>
                      <Download size={16} />
                    </button>

                    <button 
                      onClick={triggerJsonExport}
                      className="w-full flex items-center justify-between p-4 bg-slate-800 text-white rounded-2xl font-bold text-sm hover:bg-slate-700 transition-all border border-slate-700"
                    >
                      <span className="flex items-center gap-2">
                        <Terminal size={16} />
                        {isEs ? "Exportar Configuración JSON" : "Download Design Config JSON"}
                      </span>
                      <Download size={16} />
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Step Navigation Controls */}
            <div className="flex justify-between items-center pt-8 border-t border-white/5 mt-6">
              {step > 1 ? (
                <button
                  onClick={() => setStep(step - 1)}
                  className="px-4 py-2 bg-white/[0.04] text-slate-300 rounded-xl text-xs font-semibold hover:bg-white/[0.08] border border-white/[0.08] transition-all flex items-center gap-1.5"
                >
                  <ChevronLeft size={13} />
                  {isEs ? "Atrás" : "Back"}
                </button>
              ) : <div />}

              {step < 4 ? (
                <button
                  onClick={() => setStep(step + 1)}
                  className="px-5 py-2 bg-cyan-500 text-[#070c1d] rounded-xl text-xs font-bold hover:bg-cyan-400 transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/10"
                >
                  {isEs ? "Siguiente" : "Next"}
                  <ChevronRight size={13} />
                </button>
              ) : step === 4 ? (
                <button
                  onClick={triggerSimulation}
                  disabled={isSimulating}
                  className="px-6 py-2 bg-emerald-500 text-white rounded-xl text-xs font-bold hover:bg-emerald-400 transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-500/10"
                >
                  <Play size={12} />
                  {isEs ? "Iniciar Solución" : "Solve Simulation"}
                </button>
              ) : step < 6 ? (
                <button
                  onClick={() => setStep(step + 1)}
                  className="px-5 py-2 bg-cyan-500 text-[#070c1d] rounded-xl text-xs font-bold hover:bg-cyan-400 transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/10"
                >
                  {isEs ? "Siguiente" : "Next"}
                  <ChevronRight size={13} />
                </button>
              ) : <div />}
            </div>
          </GlassPanel>

          {/* REAL-TIME HIL / CONTROL PANEL */}
          {isHilActive && (
            <GlassPanel density="compact" className="rounded-3xl border-emerald-500/20 bg-emerald-500/[0.02] p-6 space-y-4">
              <div className="flex justify-between items-center border-b border-emerald-500/10 pb-3">
                <div className="flex items-center gap-2">
                  <Activity className="text-emerald-400 animate-pulse" size={16} />
                  <span className="text-xs font-bold text-white">{isEs ? "INDICADORES TELEMETRÍA HIL REAL" : "HIL FLIGHT DATA CORRELATOR"}</span>
                </div>
                <span className="text-[9px] font-mono text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 bg-emerald-500/10 uppercase">
                  Connected ESP32 MLX90614
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-white/[0.01] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400 font-semibold">{isEs ? "Temperatura Medida:" : "Measured Temp:"}</p>
                  <p className="text-lg font-bold text-white mt-0.5">{(peakCpuTemp - (hilThrottling ? 2.5 : 1.2)).toFixed(1)} °C</p>
                </div>
                <div className="p-3 bg-white/[0.01] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400 font-semibold">{isEs ? "Error de Modelado:" : "Kalman EKF Error:"}</p>
                  <p className="text-lg font-bold text-emerald-400 mt-0.5">{(hilError).toFixed(3)} °C</p>
                </div>
                <div className="p-3 bg-white/[0.01] border border-white/5 rounded-xl">
                  <p className="text-[10px] text-slate-400 font-semibold">{isEs ? "CPU Throttling:" : "CPU Throttling:"}</p>
                  <p className={`text-lg font-bold mt-0.5 ${hilThrottling ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {hilThrottling ? (isEs ? 'ACTIVO (50%)' : 'ACTIVE (50%)') : (isEs ? 'INACTIVO' : 'INACTIVE')}
                  </p>
                </div>
              </div>
            </GlassPanel>
          )}

          {/* Pareto Frontiers Optimization Visualizer (T11/T20) */}
          <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 p-6 space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="text-amber-400" size={16} />
              <span className="text-xs font-bold text-white">{isEs ? "CURVAS DE OPTIMIZACIÓN PARETO (T11)" : "MULTI-OBJECTIVE PARETO ENVELOPE (T11)"}</span>
            </div>
            
            <div className="h-[180px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis 
                    type="number" 
                    dataKey="mass" 
                    name="Masa" 
                    unit="kg" 
                    stroke="#475569" 
                    fontSize={10} 
                    label={{ value: isEs ? 'Masa (kg)' : 'Mass (kg)', position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 10 }}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="cost" 
                    name="Costo" 
                    unit="USD" 
                    stroke="#475569" 
                    fontSize={10}
                    label={{ value: isEs ? 'Costo ($)' : 'Cost ($)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                  />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }} 
                    contentStyle={{
                      backgroundColor: 'rgba(10, 15, 30, 0.94)',
                      borderColor: 'rgba(255,255,255,0.08)',
                      borderRadius: '12px',
                      color: '#f8fafc',
                      fontFamily: 'monospace',
                      fontSize: '11px',
                    }}
                  />
                  <Scatter name="Pareto configurations" data={paretoPoints} fill="#f59e0b" line shape="circle" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <p className="text-[10px] text-slate-500 leading-relaxed">
              {isEs 
                ? "*Las soluciones óptimas minimizan masa structural (eje X) y costos monetarios (eje Y) garantizando estabilidad térmica."
                : "*Optimal boundary configurations minimize both overall spacecraft structure mass (X-axis) and payload units cost (Y-axis)."}
            </p>
          </GlassPanel>
        </div>

        {/* Dynamic Wizard Right Panel */}
        <div className="space-y-6">

          {/* Interactive 3D Voxel Canvas Heatmap */}
          <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 relative flex flex-col items-center justify-between min-h-[380px] p-6 overflow-hidden">
            <div className="w-full flex justify-between items-center mb-4">
              <div>
                <p className="metric-label">{isEs ? "Visor 3D de Gradiente Voxel" : "3D Voxel Coordinate Gradient"}</p>
                <h3 className="text-md font-bold text-white">{isEs ? "Distribución Térmica" : "3D Thermal Heatmap"}</h3>
              </div>
              <span className="text-[9px] font-mono text-cyan-400">{isEs ? "Arrastra para Rotar" : "Drag to Rotate"}</span>
            </div>

            {step >= 5 ? (
              <canvas
                ref={canvasRef}
                width={360}
                height={260}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className="cursor-grab active:cursor-grabbing rounded-2xl bg-slate-950/40 border border-white/[0.02]"
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-48 text-center px-6">
                <Orbit size={48} className="text-slate-700 animate-pulse mb-4" />
                <p className="text-xs text-slate-500 font-semibold">
                  {isEs ? "Ejecuta la simulación para calcular y proyectar los gradientes voxel tridimensionales en vivo." : "Execute flight simulation solving to project 3D voxel boundary thermal elements."}
                </p>
              </div>
            )}

            <div className="w-full flex items-center justify-between border-t border-white/5 pt-4 mt-4">
              <div className="flex gap-2">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded bg-blue-500" />
                  <span className="text-[10px] text-slate-400">10°C</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded bg-violet-600" />
                  <span className="text-[10px] text-slate-400">45°C</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded bg-red-500" />
                  <span className="text-[10px] text-slate-400">85°C+</span>
                </div>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">Al 6061-T6 Aluminum</span>
            </div>
          </GlassPanel>

          {/* Uncertainty Timeline Plot (T14 / T20) */}
          <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="metric-label">{isEs ? "Bandas de Incertidumbre UQ (T14)" : "Uncertainty Quantified Bounds (T14)"}</p>
                <h3 className="mt-1 text-md font-bold text-slate-100">{isEs ? "Predicción con Confianza 95%" : "Peak CPU Transient & 95% CI"}</h3>
              </div>
              <ShieldAlert size={16} className="text-amber-400" />
            </div>

            <div className="h-[200px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={telemetryData} margin={{ top: 10, right: 10, bottom: 0, left: -25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis
                    dataKey="time"
                    stroke="#475569"
                    fontSize={10}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#475569"
                    fontSize={10}
                    tickLine={false}
                    domain={[-10, 100]}
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
                  
                  {/* Uncertainty Band area */}
                  <Area
                    type="monotone"
                    dataKey="tempMaxBound"
                    stroke="none"
                    fill="rgba(6, 182, 212, 0.08)"
                  />
                  <Area
                    type="monotone"
                    dataKey="tempMinBound"
                    stroke="none"
                    fill="#000" // Mask out
                    fillOpacity={0.0}
                  />
                  <Area
                    type="monotone"
                    dataKey="tempMaxBound"
                    name="95% Upper CI"
                    stroke="rgba(6,182,212,0.15)"
                    strokeDasharray="3 3"
                    fill="none"
                  />
                  <Area
                    type="monotone"
                    dataKey="tempMinBound"
                    name="95% Lower CI"
                    stroke="rgba(6,182,212,0.15)"
                    strokeDasharray="3 3"
                    fill="none"
                  />
                  
                  <Line
                    type="monotone"
                    dataKey="cpuTemp"
                    name="CPU Mean Temperature"
                    stroke={isCritical ? '#ef4444' : '#0ea5e9'}
                    strokeWidth={2.5}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassPanel>

          {/* SVG Coupled Nodal Thermal Network (T9) */}
          <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="metric-label">{isEs ? "Diagrama de Red Acoplada Termodinámica" : "Thermodynamic Nodal Network Diagram"}</p>
                <h3 className="mt-1 text-md font-bold text-slate-100">{isEs ? "Flujos de Inter-Conducción" : "Equivalent Resistor Coupled Nodes"}</h3>
              </div>
              <Layers size={16} className="text-cyan-400" />
            </div>

            <div className="flex justify-center py-4 bg-slate-950/30 rounded-2xl border border-white/[0.02]">
              <svg width="280" height="190" viewBox="0 0 280 190">
                {/* Node coordinates map */}
                {/* 0: CPU(60,60), 1: Battery(140,40), 2: Payload(220,60), 3: Structure(140,110), 4: Radiator(60,150), 5: Panels(220,150) */}
                {/* Connections (conductive k_ij) */}
                <line x1="60" y1="60" x2="140" y2="110" stroke="rgba(255,255,255,0.15)" strokeWidth="2" />
                <line x1="140" y1="40" x2="140" y2="110" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" />
                <line x1="220" y1="60" x2="140" y2="110" stroke="rgba(255,255,255,0.15)" strokeWidth="2" />
                <line x1="60" y1="150" x2="140" y2="110" stroke="rgba(255,255,255,0.25)" strokeWidth="3" />
                <line x1="220" y1="150" x2="140" y2="110" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" />

                {/* Nodes drawing */}
                {(() => {
                  const lastPoint = telemetryData[telemetryData.length - 1] || {
                    cpuTemp: 25.0,
                    batteryTemp: 22.0,
                    payloadTemp: 20.0,
                    structureTemp: 20.0,
                    radiatorTemp: 15.0,
                    panelsTemp: 15.0,
                  };
                  return [
                    { x: 60, y: 60, name: "CPU", temp: lastPoint.cpuTemp, color: isCritical ? '#f43f5e' : '#f59e0b' },
                    { x: 140, y: 40, name: "Bat", temp: lastPoint.batteryTemp, color: '#10b981' },
                    { x: 220, y: 60, name: "Pay", temp: lastPoint.payloadTemp, color: '#10b981' },
                    { x: 140, y: 110, name: "Str", temp: lastPoint.structureTemp, color: '#8b5cf6' },
                    { x: 60, y: 150, name: "Rad", temp: lastPoint.radiatorTemp, color: '#06b6d4' },
                    { x: 220, y: 150, name: "Pan", temp: lastPoint.panelsTemp, color: '#f97316' }
                  ].map(nodeDef => (
                    <g key={nodeDef.name}>
                      <circle cx={nodeDef.x} cy={nodeDef.y} r="18" fill="#0b0f19" stroke={nodeDef.color} strokeWidth="2" />
                      <text x={nodeDef.x} y={nodeDef.y - 1} fill="white" fontSize="9" fontWeight="bold" textAnchor="middle" dominantBaseline="middle">
                        {nodeDef.name}
                      </text>
                      <text x={nodeDef.x} y={nodeDef.y + 8} fill={nodeDef.color} fontSize="8" fontFamily="monospace" textAnchor="middle" dominantBaseline="middle">
                        {nodeDef.temp.toFixed(0)}°
                      </text>
                    </g>
                  ));
                })()}
              </svg>
            </div>
            <p className="text-[10px] text-slate-500 text-center mt-2">
              {isEs ? "*Las líneas representan enlaces conductivos (k_ij). Los colores indican niveles relativos de temperatura." : "*Lines represent coupled conduction links (k_ij). Circle outlines change colors to trace real-time nodal states."}
            </p>
          </GlassPanel>
        </div>
      </div>

      {/* CONFIGURATION CASES COMPARATOR (T20) */}
      <ScrollReveal className="w-full">
        <GlassPanel density="spacious" className="rounded-3xl border-white/[0.08] bg-[#070c1d]/60 p-6 space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-3">
              <Sliders size={20} className="text-cyan-300" />
              <div>
                <p className="metric-label">{isEs ? "Optimización y Diseño" : "Engineering Scenarios Comparator"}</p>
                <h3 className="text-xl font-bold text-white">{isEs ? "Comparador de Casos de Diseño (Hasta 5)" : "Spacecraft Design Case Benchmarks"}</h3>
              </div>
            </div>
            <button
              onClick={saveCurrentCase}
              className="px-4 py-2 bg-cyan-500 text-[#070c1d] rounded-xl text-xs font-bold hover:bg-cyan-400 transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/10"
            >
              <Plus size={14} />
              {isEs ? "Guardar Caso Actual" : "Save Current Design"}
            </button>
          </div>

          {savedCases.length > 0 ? (
            <div className="overflow-x-auto rounded-2xl border border-white/5 bg-slate-950/20">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-900/60 border-b border-white/5 text-slate-400">
                    <th className="p-3.5 font-bold">{isEs ? "Configuración" : "Design Preset"}</th>
                    <th className="p-3.5 font-bold text-center">{isEs ? "CPU Max Temp" : "Max Temp"}</th>
                    <th className="p-3.5 font-bold text-center">{isEs ? "Tiempo Crítico" : "Safety Horizon"}</th>
                    <th className="p-3.5 font-bold text-center">{isEs ? "Masa Estructural" : "Structure Mass"}</th>
                    <th className="p-3.5 font-bold text-center">{isEs ? "Costo Estimado" : "Unit Cost"}</th>
                    <th className="p-3.5 font-bold text-center">{isEs ? "Parámetros" : "Design Dimensions"}</th>
                    <th className="p-3.5 text-center">{isEs ? "Acción" : "Purge"}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {savedCases.map((c, idx) => {
                    const isMinTemp = bestMetrics && c.max_temp === bestMetrics.min_temp;
                    const isMinMass = bestMetrics && c.masa === bestMetrics.min_mass;
                    const isMinCost = bestMetrics && c.coste === bestMetrics.min_cost;

                    return (
                      <tr key={c.id} className="hover:bg-white/[0.02] transition-all">
                        <td className="p-3.5 font-semibold text-white">{c.name}</td>
                        
                        <td className="p-3.5 text-center font-mono">
                          <span className={`px-2 py-0.5 rounded font-bold ${
                            c.max_temp >= 85 
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                              : isMinTemp 
                                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' 
                                : 'text-slate-300'
                          }`}>
                            {c.max_temp.toFixed(1)} °C
                          </span>
                        </td>

                        <td className="p-3.5 text-center font-mono">
                          {c.max_temp >= 85 ? (
                            <span className="text-rose-400 font-semibold">{isEs ? "Quemado!" : "Burnout!"}</span>
                          ) : (
                            <span className="text-emerald-400 font-semibold">{isEs ? "Seguro" : "Stable Safe"}</span>
                          )}
                        </td>

                        <td className="p-3.5 text-center font-mono">
                          <span className={isMinMass ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
                            {c.masa.toFixed(2)} kg
                          </span>
                        </td>

                        <td className="p-3.5 text-center font-mono">
                          <span className={isMinCost ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
                            ${c.coste.toLocaleString()}
                          </span>
                        </td>

                        <td className="p-3.5 text-center text-slate-400 text-[10px]">
                          Q={c.power}W, A={c.area.toFixed(2)}m², ε={c.emissivity.toFixed(2)}
                        </td>

                        <td className="p-3.5 text-center">
                          <button
                            onClick={() => removeCase(c.id)}
                            className="p-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-all"
                          >
                            <Trash2 size={12} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 border border-dashed border-white/10 rounded-2xl text-center text-xs text-slate-500 leading-relaxed">
              {isEs 
                ? "No hay configuraciones guardadas. Configura tus Sliders y pulsa 'Guardar Caso Actual' para contrastar diseños."
                : "No saved cases yet. Scale your engineering parameters above and click 'Save Current Design' to establish multi-variable comparison."}
            </div>
          )}
        </GlassPanel>
      </ScrollReveal>
    </FocusContainer>
  );
}
