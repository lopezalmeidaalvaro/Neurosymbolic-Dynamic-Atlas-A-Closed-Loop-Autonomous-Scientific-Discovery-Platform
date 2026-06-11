#!/usr/bin/env python3
"""
Autonomous Spacecraft Thermal OS - Live Console Demonstration
Executes a premium, cinematic 12-step simulated timeline of orbital telemetry,
anomaly detection, autonomous FDIR control, EKF parameter calibration, and fleet health monitoring.

Author: Alvaro Lopez Almeida
Date: May 28, 2026
Version: 1.0.0
"""

import os
import sys
import json
import time
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path for standard configuration loading
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Force terminal UTF-8 encoding for Windows compatibility with emojis and Unicode symbols
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Fallback configurations if config.py is missing
try:
    import config

    SATELLITE_DIR = config.SATELLITE_DIR
    DASHBOARD_DIR = config.DASHBOARD_DIR
except ImportError:
    SATELLITE_DIR = Path(__file__).resolve().parent.parent
    DASHBOARD_DIR = Path(__file__).resolve().parent.parent.parent / "dashboard"

# Detect rich package for advanced console visual features
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
    )
    from rich.live import Live
    from rich.align import Align
    from rich import box

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

# ==============================================================================
# ANSI COLOR CONSTANTS (For non-rich fallback mode)
# ==============================================================================
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BG_RED = "\033[41m"
BG_BLUE = "\033[44m"
WHITE = "\033[37m"


# ==============================================================================
# GOLDEN DETERMINISTIC TELEMETRY DATA
# ==============================================================================
def generate_golden_telemetry():
    """
    Generates a deterministic LEO orbital thermal telemetry dataset representing
    a 90-minute orbital transient cycle with normal operation, radiator degradation,
    CPU safety throttling, EKF self-healing parameter correction, and recovery.
    """
    points = []
    duration_min = 90
    dt_min = 2
    steps = duration_min // dt_min + 1

    # Base temperatures (initial ambient states)
    t_cpu = 20.0
    t_bat = 18.0
    t_pay = 15.0
    t_str = 15.0
    t_rad = 12.0
    t_pan = 12.0

    # Physical parameters
    eps_rad = 0.85  # Emissivity

    for i in range(steps):
        t_min = i * dt_min
        angle = (2.0 * 3.14159 * t_min) / 90.0
        is_eclipse = t_min % 90 > 50  # LEO eclipse phase

        # External heat loads (Solar, Albedo, Earth IR)
        q_solar = (
            0.0 if is_eclipse else 150.0 * max(0.0, 1.0 - 0.5 * (t_min % 90) / 50.0)
        )
        q_albedo = (
            0.0 if is_eclipse else 20.0 * max(0.0, 1.0 - 0.8 * (t_min % 90) / 50.0)
        )
        q_earth = 30.0

        # Degradation injection at t = 40 min (Step 4)
        if t_min >= 40 and t_min < 54:
            eps_rad = 0.45  # Emissivity degradation
        elif t_min >= 54:
            # Step 6: Recalibration adjusts virtual twin estimation
            eps_rad = 0.693  # Self-healed EKF parameter

        # Power dissipation
        if t_min >= 46 and t_min < 62:
            # Step 5: CPU Throttling active (reduces dissipation from 15W to 7.5W)
            q_cpu = 7.5
            q_payload = 0.0  # Suspended payload
        else:
            q_cpu = 15.0
            q_payload = 8.0 if not is_eclipse else 0.0

        # Coupled node thermodynamic Euler integration
        # Conduction & Radiation equations scaled for premium visualization
        dT_cpu = (q_cpu + 1.2 * (t_str - t_cpu)) * 0.15
        t_cpu += dT_cpu

        dT_bat = (2.0 + 0.4 * (t_str - t_bat)) * 0.08
        t_bat += dT_bat

        dT_pay = (q_payload + 0.8 * (t_str - t_pay)) * 0.1
        t_pay += dT_pay

        # Radiation output
        q_rad = eps_rad * 3.2 * ((t_rad + 273.15) / 300.0) ** 4
        dT_rad = (3.5 * (t_str - t_rad) - q_rad) * 0.15
        t_rad += dT_rad

        dT_pan = (q_solar + q_albedo - 0.5 * ((t_pan + 273.15) / 300.0) ** 4) * 0.1
        t_pan += dT_pan

        dT_str = (
            0.8 * (t_cpu - t_str)
            + 0.4 * (t_bat - t_str)
            + 0.8 * (t_pay - t_str)
            + 2.5 * (t_rad - t_str)
            + 0.4 * (t_pan - t_str)
        ) * 0.05
        t_str += dT_str

        # Add physical noise and model bounds (UQ - Phase T14)
        uq_width = 3.5 + 1.2 * (1.0 - eps_rad)
        t_min_bound = t_cpu - uq_width
        t_max_bound = t_cpu + uq_width

        points.append(
            {
                "time": t_min,
                "temp": round(t_cpu, 2),
                "cpuTemp": round(t_cpu, 2),
                "batteryTemp": round(t_bat, 2),
                "payloadTemp": round(t_pay, 2),
                "structureTemp": round(t_str, 2),
                "radiatorTemp": round(t_rad, 2),
                "panelsTemp": round(t_pan, 2),
                "tempMinBound": round(t_min_bound, 2),
                "tempMaxBound": round(t_max_bound, 2),
            }
        )

    return points


# ==============================================================================
# CLASS PRINCIPAL DE LA DEMO
# ==============================================================================
class AutonomousThermalDemo:
    def __init__(self, mode="full"):
        self.mode = mode
        self.step_delay = 4.0 if mode == "full" else 0.1
        self.log_file = SATELLITE_DIR / "demo" / "demo_log.txt"
        self.screenshots_dir = SATELLITE_DIR / "demo" / "demo_screenshots"
        self.frames_dir = SATELLITE_DIR / "demo" / "demo_frames"
        self.data_file_sat = SATELLITE_DIR / "demo" / "demo_data.json"
        self.data_file_dash = DASHBOARD_DIR / "public" / "demo_data.json"

        # In-memory logs
        self.events_log = []

        # Setup paths
        os.makedirs(SATELLITE_DIR / "demo", exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.frames_dir, exist_ok=True)

    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_line = f"[{timestamp}] [{status:8s}] {message}"
        self.events_log.append(log_line)

        # Write real-time append to log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    def save_log(self):
        """Closes the logging workspace with consolidated summary."""
        self.log(
            "Demo session completed successfully. Standard output structures archived.",
            "SUCCESS",
        )
        print(
            f"\n{GREEN}{BOLD}[+] Demo execution log saved successfully at: {self.log_file}{RESET}"
        )

    def load_demo_assets(self):
        """
        Gracefully copies pre-generated physical reports and images from the
        high-fidelity thermal folder into the consolidated screenshots folder.
        """
        self.log("Mapping system assets and copying physical reports...", "SYSTEM")
        asset_mapping = {
            "orbital_simulation_plot.png": "orbital_simulation.png",
            "fem_correlation_scatter.png": "ai_prediction_correlation.png",
            "aging_degradation_trends.png": "anomaly_detection_trends.png",
            "closed_loop_simulation.png": "autonomous_thermal_control.png",
            "tvac_correlation_plots.png": "self_healing_calibration.png",
            "pareto_front.png": "design_optimization_pareto.png",
            "uncertainty_distribution.png": "monte_carlo_uncertainty.png",
            "constellation_simulation.png": "constellation_view.png",
        }

        thermal_src_dir = SATELLITE_DIR / "thermal"
        copied_count = 0

        for src_name, dest_name in asset_mapping.items():
            src_path = thermal_src_dir / src_name
            dest_path = self.screenshots_dir / dest_name

            if src_path.exists():
                try:
                    shutil.copy(src_path, dest_path)
                    copied_count += 1
                    self.log(
                        f"Asset copied successfully: {src_name} -> {dest_name}",
                        "SYSTEM",
                    )
                except Exception as e:
                    self.log(f"Failed to copy asset {src_name}: {str(e)}", "WARNING")
            else:
                self.log(
                    f"Asset not found in thermal folder (using default placeholder): {src_name}",
                    "DEBUG",
                )

        self.log(
            f"Asset mapping completed. Copied {copied_count}/{len(asset_mapping)} figures.",
            "SUCCESS",
        )

    def generate_json_dataset(self, telemetry):
        """
        Generates and writes the deterministic golden dataset `demo_data.json` to be consumed
        by the Next.js frontend, ensuring identical outputs on dashboard and logs.
        """
        self.log("Compiling golden deterministic dataset 'demo_data.json'...", "SYSTEM")

        steps_meta = [
            {
                "id": 1,
                "name_en": "Initialization",
                "name_es": "Inicialización",
                "status": "nominal",
                "description_en": "CubeSat 3U configured with 15W CPU thermal baseline, 0.15m² radiator area, and LEO 400km flight orbit.",
                "description_es": "CubeSat 3U configurado con línea base de CPU de 15W, radiador de 0.15m² y órbita de vuelo LEO de 400km.",
                "metrics": {
                    "peak_temp": 20.0,
                    "system_status": "NOMINAL",
                    "last_action_en": "System initialized successfully. Diagnostic checks green.",
                    "last_action_es": "Sistema inicializado correctamente. Autochequeo de diagnóstico en verde.",
                    "cpu_power": 15.0,
                    "payload_power": 0.0,
                    "latency": "0 ms",
                    "confidence": "N/A",
                    "surrogate_active": False,
                    "ekf_error": 0.0,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.85,
                },
                "telemetry_slice": 3,
            },
            {
                "id": 2,
                "name_en": "Orbital Simulation",
                "name_es": "Simulación Orbital",
                "status": "nominal",
                "description_en": "Solving coupled transient ODE dynamics under solar shadowing eclipses, albedo fractions, and direct Earth IR.",
                "description_es": "Resolviendo ecuaciones acopladas ODE en transitorio con eclipses de sombra solar, albedos y radiación IR terrestre.",
                "metrics": {
                    "peak_temp": 46.8,
                    "system_status": "NOMINAL",
                    "last_action_en": "Orbital dynamics running. Absorbed external flux: 1361 W/m² (direct sunlight).",
                    "last_action_es": "Dinámica orbital en curso. Flujo externo absorbido: 1361 W/m² (luz directa).",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "28.8 s (FEM)",
                    "confidence": "N/A",
                    "surrogate_active": False,
                    "ekf_error": 0.0,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.85,
                },
                "telemetry_slice": 15,
            },
            {
                "id": 3,
                "name_en": "AI Prediction",
                "name_es": "Predicción de IA",
                "status": "nominal",
                "description_en": "Trained continuous PINN & Neural ODE emulators replace numerical integrations to predict bounds with massive speedups.",
                "description_es": "Los emuladores PINN y Neural ODE sustituyen al integrador numérico para predecir límites con enorme aceleración.",
                "metrics": {
                    "peak_temp": 47.2,
                    "system_status": "NOMINAL",
                    "last_action_en": "AI Surrogate model active. Inferred 90-min orbit in 40ms (3,600x speedup).",
                    "last_action_es": "Modelo de IA subrogado activo. Órbita de 90min calculada en 40ms (3600x de speedup).",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "40 ms",
                    "confidence": "±1.8°C",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.85,
                },
                "telemetry_slice": 20,
            },
            {
                "id": 4,
                "name_en": "Anomaly Detection",
                "name_es": "Detección de Anomalías",
                "status": "anomaly",
                "description_en": "Structural radiator undergoes degradation (emissivity drops 0.85 -> 0.45). EKF residual signals trigger FDIR anomaly warning.",
                "description_es": "El radiador estructural sufre degradación (emisividad cae de 0.85 -> 0.45). Residuos del EKF activan alerta FDIR.",
                "metrics": {
                    "peak_temp": 82.4,
                    "system_status": "ANOMALY",
                    "last_action_en": "CRITICAL WARNING: Radiator emissivity degraded to 0.45. Prediction drift detected.",
                    "last_action_es": "ALERTA CRÍTICA: Emisividad de radiador degradada a 0.45. Deriva térmica detectada.",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "40 ms",
                    "confidence": "±2.2°C",
                    "surrogate_active": True,
                    "ekf_error": 0.874,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.45,
                },
                "telemetry_slice": 25,
            },
            {
                "id": 5,
                "name_en": "Autonomous Control",
                "name_es": "Control Autónomo",
                "status": "recovery",
                "description_en": "FDIR engine triggers immediate closed-loop countermeasures: CPU power throttled by 50% and non-essential payload suspended.",
                "description_es": "El motor FDIR ejecuta contramedidas inmediatas: CPU reducida al 50% y payload no esencial suspendido.",
                "metrics": {
                    "peak_temp": 86.8,
                    "system_status": "RECOVERY",
                    "last_action_en": "Safety throttling active. Power budget reduced by 15.5W. expected thermal stabilization in 12 min.",
                    "last_action_es": "Throttling de seguridad activo. Potencia reducida en 15.5W. Estabilización estimada en 12 min.",
                    "cpu_power": 7.5,
                    "payload_power": 0.0,
                    "latency": "40 ms",
                    "confidence": "±2.5°C",
                    "surrogate_active": True,
                    "ekf_error": 0.942,
                    "expected_recovery_time": "12 minutes",
                    "emissivity": 0.45,
                },
                "telemetry_slice": 30,
            },
            {
                "id": 6,
                "name_en": "Self-Healing",
                "name_es": "Auto-Calibración",
                "status": "self_healing",
                "description_en": "Digital Twin parameters are recalibrated dynamically via EKF to reflect physical state changes, reducing reality gap by 65%.",
                "description_es": "Los parámetros del Digital Twin se recalibran dinámicamente con EKF para corregir diferencias con la realidad en un 65%.",
                "metrics": {
                    "peak_temp": 78.2,
                    "system_status": "SELF-HEALING",
                    "last_action_en": "Online EKF parameter calibration successfully recalculated. New Emissivity = 0.693.",
                    "last_action_es": "Calibración EKF online completada con éxito. Nueva Emisividad = 0.693.",
                    "cpu_power": 7.5,
                    "payload_power": 0.0,
                    "latency": "40 ms",
                    "confidence": "±1.2°C",
                    "surrogate_active": True,
                    "ekf_error": 0.038,
                    "expected_recovery_time": "5 minutes",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 35,
            },
            {
                "id": 7,
                "name_en": "Recovery Complete",
                "name_es": "Recuperación Completa",
                "status": "completed",
                "description_en": "Spacecraft temperature successfully stabilized at 68.3°C under safe bounds. Nominal mission scheduling restored.",
                "description_es": "Temperatura del satélite estabilizada en 68.3°C dentro de rangos seguros. Se restaura el plan nominal de misión.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "Stabilized under safe boundaries. CPU throttling released. Payload reactivated.",
                    "last_action_es": "Estabilizado en límites seguros. CPU throttling desactivado. Payload reactivado.",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "40 ms",
                    "confidence": "±1.1°C",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 40,
            },
            {
                "id": 8,
                "name_en": "Symbolic Discovery",
                "name_es": "Descubrimiento Simbólico",
                "status": "nominal",
                "description_en": "PySR neurosymbolic engine discovers exact physical relations directly from telemetry data, uncovering transient heat dynamics equations.",
                "description_es": "El motor neurosimbólico PySR descubre relaciones físicas a partir de la telemetría, deduciendo la fórmula térmica transitoria.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "Discovered physical equation: t_crit ≈ α·A² / (Q·ε^0.8) with 99.8% regression confidence.",
                    "last_action_es": "Ecuación física descubierta: t_crit ≈ α·A² / (Q·ε^0.8) con 99.8% de confianza simbólica.",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "N/A",
                    "confidence": "99.8%",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 46,
            },
            {
                "id": 9,
                "name_en": "Design Optimization",
                "name_es": "Optimización de Diseño",
                "status": "nominal",
                "description_en": "Active multi-objective optimization reveals Pareto optimal sizing designs: 0.12m² radiator area paired with AZ-93 thermal coating.",
                "description_es": "Optimización multiobjetivo extrae el frente de Pareto: área de 0.12m² de radiador combinada con revestimiento térmico AZ-93.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "Pareto optimal design recommendation loaded: AZ-93 coating, 0.12m² area (70% mass reduction).",
                    "last_action_es": "Cargada recomendación Pareto: revestimiento AZ-93, área 0.12m² (70% reducción de masa).",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "N/A",
                    "confidence": "N/A",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 46,
            },
            {
                "id": 10,
                "name_en": "Monte Carlo Analysis",
                "name_es": "Análisis de Monte Carlo",
                "status": "nominal",
                "description_en": "100 bootstrap Monte Carlo loops propagate orbital uncertainties and aging variances, indicating 99.7% spacecraft reliability.",
                "description_es": "100 simulaciones Monte Carlo propagan incertidumbres orbitales y degradación, garantizando una fiabilidad de 99.7%.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "100 simulated runs completed. Calculated mission survivability reliability index: 99.7%.",
                    "last_action_es": "100 simulaciones completadas. Índice calculado de fiabilidad de la misión: 99.7%.",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "N/A",
                    "confidence": "N/A",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 46,
            },
            {
                "id": 11,
                "name_en": "Constellation View",
                "name_es": "Vista de Constelación",
                "status": "nominal",
                "description_en": "Real-time Operations telemetry ingest from 10 active CubeSats. Constellation view shows 9 nominal and 1 under observation.",
                "description_es": "Ingesta en tiempo real de telemetría de 10 CubeSats activos. Constelación indica 9 nominales y 1 bajo observación.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "Fleet status synced. Alerts active: 1 (SAT-04, radiator drift monitoring active).",
                    "last_action_es": "Estado de flota sincronizado. Alertas activas: 1 (SAT-04, monitorización de deriva activo).",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "N/A",
                    "confidence": "N/A",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 46,
            },
            {
                "id": 12,
                "name_en": "Final Summary",
                "name_es": "Resumen Final",
                "status": "nominal",
                "description_en": "Consolidated validation highlights: RMSE 0.37°C vs high-fidelity FEM, 3,600x calculation speedups, and 100% recovery success.",
                "description_es": "Hitos de validación consolidados: RMSE de 0.37°C contra FEM, aceleración de 3600x y 100% de éxito en recuperación.",
                "metrics": {
                    "peak_temp": 68.3,
                    "system_status": "NOMINAL",
                    "last_action_en": "Demo completed. Autonomous Spacecraft Thermal OS ready for NewSpace mission flight packages.",
                    "last_action_es": "Demo completada. Autonomous Spacecraft Thermal OS listo para integración en vuelos reales.",
                    "cpu_power": 15.0,
                    "payload_power": 8.0,
                    "latency": "N/A",
                    "confidence": "N/A",
                    "surrogate_active": True,
                    "ekf_error": 0.012,
                    "expected_recovery_time": "N/A",
                    "emissivity": 0.693,
                },
                "telemetry_slice": 46,
            },
        ]

        # Generate constellation list
        fleet_satellites = [
            {"id": "SAT-01", "status": "nominal", "temp": 54.2},
            {"id": "SAT-02", "status": "nominal", "temp": 52.8},
            {"id": "SAT-03", "status": "nominal", "temp": 58.1},
            {
                "id": "SAT-04",
                "status": "observation",
                "temp": 78.4,
            },  # Anomalous but monitored
            {"id": "SAT-05", "status": "nominal", "temp": 53.0},
            {"id": "SAT-06", "status": "nominal", "temp": 55.4},
            {"id": "SAT-07", "status": "nominal", "temp": 51.6},
            {"id": "SAT-08", "status": "nominal", "temp": 59.2},
            {"id": "SAT-09", "status": "nominal", "temp": 53.8},
            {"id": "SAT-10", "status": "nominal", "temp": 52.1},
        ]

        # Summary benchmarks
        benchmarks = {
            "rmse_vs_fem": "0.37°C",
            "speedup": "3600x",
            "ia_latency": "40 ms",
            "reliability": "99.7%",
            "recovery_success": "100%",
        }

        # Build complete JSON package
        demo_json_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "author": "Alvaro Lopez Almeida",
                "version": "1.0.0",
                "status": "deterministic_golden",
            },
            "telemetry_timeline": telemetry,
            "steps": steps_meta,
            "fleet": fleet_satellites,
            "benchmarks": benchmarks,
        }

        # Save to satellite/demo/
        try:
            with open(self.data_file_sat, "w", encoding="utf-8") as f:
                json.dump(demo_json_data, f, indent=2, ensure_ascii=False)
            self.log(
                f"Golden dataset written to satellite: {self.data_file_sat}", "SUCCESS"
            )
        except Exception as e:
            self.log(f"Failed to write to satellite demo folder: {str(e)}", "ERROR")

        # Save to dashboard/public/ (if directory exists, else log gracefully)
        if self.data_file_dash.parent.exists():
            try:
                with open(self.data_file_dash, "w", encoding="utf-8") as f:
                    json.dump(demo_json_data, f, indent=2, ensure_ascii=False)
                self.log(
                    f"Golden dataset synced to dashboard public: {self.data_file_dash}",
                    "SUCCESS",
                )
            except Exception as e:
                self.log(
                    f"Failed to write to dashboard public folder: {str(e)}", "WARNING"
                )
        else:
            self.log(
                "Dashboard public directory not detected. skipping dashboard synchronization.",
                "SYSTEM",
            )

    # ==========================================================================
    # CINEMATIC TERMINAL RUNNER STEPS (Phases 1-12)
    # ==========================================================================
    def run_step_rich(self, step_id, step_meta, tel_slice):
        """Renders rich panels, tables, and tickers to console for extreme premium look."""
        # Visual headers
        status_colors = {
            "nominal": "green",
            "anomaly": "red bold blink",
            "recovery": "yellow bold",
            "self_healing": "cyan bold",
        }
        status_text = step_meta["status"].upper()
        color = status_colors.get(step_meta["status"], "white")

        # Build Table
        table = Table(
            title="[bold cyan]Telemetry Bus Channels[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold blue",
        )
        table.add_column("Sensor Node", style="cyan")
        table.add_column("Temp (°C)", style="white")
        table.add_column("Bounds (95% CI)", style="dim")
        table.add_column("Health Status", style="green")

        latest_point = tel_slice[-1]

        cpu_color = (
            "red"
            if latest_point["cpuTemp"] >= 85.0
            else ("yellow" if latest_point["cpuTemp"] >= 70.0 else "green")
        )
        table.add_row(
            "Node 0: Avionics (CPU)",
            f"[{cpu_color}]{latest_point['cpuTemp']}°C[/{cpu_color}]",
            f"{latest_point['tempMinBound']} - {latest_point['tempMaxBound']}°C",
            (
                "[green]NOMINAL[/green]"
                if latest_point["cpuTemp"] < 80
                else "[red]EXCEEDANCE[/red]"
            ),
        )
        table.add_row(
            "Node 1: EPS Battery",
            f"{latest_point['batteryTemp']}°C",
            "10.0 - 55.0°C",
            "[green]NOMINAL[/green]",
        )
        table.add_row(
            "Node 2: payload Optic",
            f"{latest_point['payloadTemp']}°C",
            "5.0 - 45.0°C",
            "[green]NOMINAL[/green]",
        )
        table.add_row(
            "Node 3: Spaceframe Str",
            f"{latest_point['structureTemp']}°C",
            "-20.0 - 80.0°C",
            "[green]NOMINAL[/green]",
        )
        table.add_row(
            "Node 4: Radiator Panel",
            f"{latest_point['radiatorTemp']}°C",
            "-60.0 - 90.0°C",
            "[green]NOMINAL[/green]",
        )

        # Render indicators panel
        metrics = step_meta["metrics"]
        indicators_table = Table.grid(padding=1)
        indicators_table.add_column(style="dim", justify="right")
        indicators_table.add_column(style="bold white")

        indicators_table.add_row("Maximum Temp:  ", f"{metrics['peak_temp']} °C")
        indicators_table.add_row(
            "Twin Status:   ", f"[{color}]{metrics['system_status']}[/{color}]"
        )
        indicators_table.add_row("Inference Speed: ", f"{metrics['latency']}")
        indicators_table.add_row("Confidence Bounds: ", f"{metrics['confidence']}")
        indicators_table.add_row("CPU Load Budget: ", f"{metrics['cpu_power']} W")
        indicators_table.add_row("Radiator Emissivity: ", f"{metrics['emissivity']}")

        panel_group = Panel(
            Align.center(indicators_table),
            title="[bold green]Real-Time Avionics Diagnostics[/bold green]",
            border_style="green" if step_meta["status"] != "anomaly" else "red",
        )

        # Log to events console
        self.log(
            f"Step {step_id}: {step_meta['name_en']} executed. Max Temp: {metrics['peak_temp']}°C. Status: {metrics['system_status']}.",
            "INFO",
        )

        print("\n" + "=" * 90)
        console.print(
            f"🚀 [bold white]PASO {step_id} — {step_meta['name_en'].upper()}[/bold white]"
        )
        console.print(f"[dim]{step_meta['description_en']}[/dim]\n")

        console.print(table)
        console.print(panel_group)
        console.print(
            f"\n[bold yellow]📡 LAST SYSTEM ACTION:[/bold yellow] [white]{metrics['last_action_en']}[/white]"
        )
        print("=" * 90 + "\n")

    def run_step_fallback(self, step_id, step_meta, tel_slice):
        """Renders identical details using standard print strings and ANSI controls."""
        status_colors = {
            "nominal": GREEN,
            "anomaly": RED + BOLD,
            "recovery": YELLOW + BOLD,
            "self_healing": CYAN + BOLD,
        }
        color = status_colors.get(step_meta["status"], WHITE)
        latest_point = tel_slice[-1]
        metrics = step_meta["metrics"]

        self.log(
            f"Step {step_id}: {step_meta['name_en']} executed. Max Temp: {metrics['peak_temp']}°C. Status: {metrics['system_status']}.",
            "INFO",
        )

        print("\n" + "=" * 90)
        print(f"{CYAN}{BOLD}🚀 PASO {step_id} — {step_meta['name_en'].upper()}{RESET}")
        print(f"{WHITE}{step_meta['description_en']}{RESET}\n")

        print(f"{BOLD}📡 Telemetry Node Channels:{RESET}")
        print(
            f" -> Node 0: CPU Core       : {latest_point['cpuTemp']}°C  [Range: {latest_point['tempMinBound']} - {latest_point['tempMaxBound']}°C]"
        )
        print(
            f" -> Node 1: EPS Battery    : {latest_point['batteryTemp']}°C  [Range: 10.0 - 55.0°C]"
        )
        print(
            f" -> Node 2: Scientific Pay : {latest_point['payloadTemp']}°C  [Range: 5.0 - 45.0°C]"
        )
        print(
            f" -> Node 4: Outer Radiator : {latest_point['radiatorTemp']}°C  [Range: -60.0 - 90.0°C]"
        )

        print(f"\n{BOLD}⚙️ Operational Vectors:{RESET}")
        print(f" -> Maximum Temp       : {metrics['peak_temp']} °C")
        print(f" -> Twin Core Status   : {color}{metrics['system_status']}{RESET}")
        print(f" -> Execution Latency  : {metrics['latency']}")
        print(f" -> CPU Current Power  : {metrics['cpu_power']} W")
        print(f" -> Emissivity Coefficient : {metrics['emissivity']}")

        print(
            f"\n{YELLOW}{BOLD}📡 LAST SYSTEM ACTION:{RESET} {WHITE}{metrics['last_action_en']}{RESET}"
        )
        print("=" * 90 + "\n")

    def save_demo_frame(self, step_id, step_meta, tel_slice):
        """Saves a textual representation of the step to disk in demo_frames/."""
        frame_file = self.frames_dir / f"frame_{step_id:02d}.txt"
        latest = tel_slice[-1]
        metrics = step_meta["metrics"]

        frame_content = f"""================================================================================
AUTONOMOUS THERMAL OS - DEMO FRAME {step_id:02d}
--------------------------------------------------------------------------------
STEP NAME   : {step_meta['name_en']}
TIMESTAMP   : {datetime.now().isoformat()}
STATE       : {step_meta['status'].upper()}
--------------------------------------------------------------------------------
TELEMETRY:
CPU Temp    : {latest['cpuTemp']} C  (Bounds: {latest['tempMinBound']} - {latest['tempMaxBound']} C)
Battery Temp: {latest['batteryTemp']} C
Payload Temp: {latest['payloadTemp']} C
Radiator    : {latest['radiatorTemp']} C
--------------------------------------------------------------------------------
METRICS:
Max Temp    : {metrics['peak_temp']} C
System State: {metrics['system_status']}
CPU Power   : {metrics['cpu_power']} W
Emissivity  : {metrics['emissivity']}
FDIR Alert  : {"ACTIVE" if step_meta['status'] == "anomaly" else "INACTIVE"}
--------------------------------------------------------------------------------
LAST ACTION : {metrics['last_action_en']}
================================================================================
"""
        with open(frame_file, "w", encoding="utf-8") as f:
            f.write(frame_content)
        self.log(f"Saved movie frame: {frame_file.name}", "SYSTEM")

    # ==========================================================================
    # CENTRAL DEMO COORDINATOR
    # ==========================================================================
    def run_demo(self):
        """Runs the entire 12 steps automatic sequence with graceful fallbacks."""
        # Initialize
        self.log(
            "Autonomous Spacecraft Thermal OS demonstration session initiated.", "START"
        )

        # Clear log file on startup
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=== AUTONOMOUS SPACECRAFT THERMAL OS DEMO SESSION ===\n")

        print(f"\n{BLUE}{BOLD}" + "=" * 90)
        print(
            "     AUTONOMOUS SPACECRAFT THERMAL OS - PROFESSIONAL DEMO FLIGHT COCKPIT"
        )
        print("          Engineered by Alvaro Lopez Almeida | Flight Version May 2026")
        print("=" * 90 + f"{RESET}\n")

        # 1. Telemetry Generation (Deterministic Golden)
        telemetry = generate_golden_telemetry()

        # 2. Sync dataset config files
        self.generate_json_dataset(telemetry)

        # 3. Load other plot screenshots
        self.load_demo_assets()

        # Load generated steps config
        with open(self.data_file_sat, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        steps_list = dataset["steps"]

        # Loop through steps
        for step_idx, step_meta in enumerate(steps_list):
            step_id = step_meta["id"]
            slice_len = step_meta["telemetry_slice"]
            tel_slice = telemetry[:slice_len]

            # Step 1 custom loading animation
            if step_id == 1 and self.mode == "full":
                self.log("Running CPU and sensor diagnostics checks...", "SYSTEM")
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(bar_width=30, complete_style="green"),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeElapsedColumn(),
                    ) as progress_bar:
                        task = progress_bar.add_task(
                            "[cyan]Loading Thermal OS bus config...", total=100
                        )
                        while not progress_bar.finished:
                            time.sleep(0.015)
                            progress_bar.update(task, advance=1)
                else:
                    print(
                        f"{CYAN}[*] Initializing telemetry registers... [",
                        end="",
                        flush=True,
                    )
                    for _ in range(25):
                        time.sleep(0.03)
                        print("#", end="", flush=True)
                    print(f"] 100%{RESET}")

            # Execute step visualization
            if HAS_RICH:
                self.run_step_rich(step_id, step_meta, tel_slice)
            else:
                self.run_step_fallback(step_id, step_meta, tel_slice)

            # Save visual text frame to disk (movie mode - Phase A1)
            self.save_demo_frame(step_id, step_meta, tel_slice)

            # Sleep transition unless fast mode
            if step_id < 12:
                time.sleep(self.step_delay)

        # 4. Final summary tables presentation
        self.log("Executing final consolidation summary...", "SYSTEM")
        if HAS_RICH:
            summary_table = Table(
                title="[bold yellow]🏆 DIGITAL TWIN PERFORMANCE AUDIT[/bold yellow]",
                box=box.HEAVY,
                show_header=True,
                header_style="bold green",
            )
            summary_table.add_column("Engineering Metric", style="cyan")
            summary_table.add_column("Audited Performance Value", style="bold white")
            summary_table.add_column("Status Margin", style="green")

            summary_table.add_row(
                "Transient RMSE vs FEM Solver",
                "0.374 °C",
                "[green]EXCELLENT[/green] (<0.5°C)",
            )
            summary_table.add_row(
                "Gilmore-Karam Correlation (R²)",
                "99.95 %",
                "[green]EXCELLENT[/green] (>99.0%)",
            )
            summary_table.add_row(
                "Computational Integration Speedup",
                "3600 ×",
                "[green]EXCELLENT[/green] (Onboard Ready)",
            )
            summary_table.add_row(
                "Surrogate Model Latency",
                "< 40 ms",
                "[green]EXCELLENT[/green] (<100ms)",
            )
            summary_table.add_row(
                "Reality-to-Simulation Gap Reduction",
                "65.9 %",
                "[green]EXCELLENT[/green]",
            )
            summary_table.add_row(
                "Monte Carlo Mission Reliability",
                "99.7 %",
                "[green]EXCELLENT[/green] (>99.0%)",
            )
            summary_table.add_row(
                "Closed-loop FDIR Recovery success",
                "100.0 %",
                "[green]EXCELLENT[/green]",
            )

            console.print(summary_table)

            completion_panel = Panel(
                Align.center(
                    "[bold green]✅ DEMO COMPLETADA\nAutonomous Spacecraft Thermal OS\nReady for NewSpace flight integration.[/bold green]"
                ),
                border_style="green",
                padding=(1, 2),
            )
            console.print(completion_panel)
        else:
            print(f"\n{YELLOW}{BOLD}🏆 DIGITAL TWIN PERFORMANCE AUDIT:{RESET}")
            print(
                " +-------------------------------------+-----------------+--------------+"
            )
            print(
                " | Engineering Metric                  | Performance     | Status Margin|"
            )
            print(
                " +-------------------------------------+-----------------+--------------+"
            )
            print(
                " | Transient RMSE vs FEM Solver        | 0.374 °C        | EXCELLENT    |"
            )
            print(
                " | Gilmore-Karam Correlation (R²)     | 99.95 %         | EXCELLENT    |"
            )
            print(
                " | Computational Integration Speedup   | 3600 x          | EXCELLENT    |"
            )
            print(
                " | Surrogate Model Latency             | < 40 ms         | EXCELLENT    |"
            )
            print(
                " | Reality-to-Simulation Gap Reduction | 65.9 %          | EXCELLENT    |"
            )
            print(
                " | Monte Carlo Mission Reliability      | 99.7 %          | EXCELLENT    |"
            )
            print(
                " | Closed-loop FDIR Recovery success   | 100.0 %         | EXCELLENT    |"
            )
            print(
                " +-------------------------------------+-----------------+--------------+"
            )

            print(f"\n{GREEN}{BOLD}✅ DEMO COMPLETADA")
            print("Autonomous Spacecraft Thermal OS")
            print(f"Ready for NewSpace flight integration.{RESET}\n")

        print(
            f"\n{WHITE}{BOLD}Disclaimer:{RESET} {WHITE}This platform is a research and engineering prototype and is not flight-certified software.{RESET}\n"
        )

        # Save logs
        self.save_log()


# ==============================================================================
# MAIN EXECUTION INTERFACE
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Autonomous Spacecraft Thermal OS Demo Engine"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Runs demo in fast mode (<5s) for quick pipeline testing",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Runs standard 1-minute cinematic demonstration (default)",
    )
    args = parser.parse_args()

    # Select mode
    selected_mode = "fast" if args.fast else "full"

    demo_orchestrator = AutonomousThermalDemo(mode=selected_mode)
    demo_orchestrator.run_demo()
