#!/usr/bin/env python3
"""
Phase T41: Spacecraft Electromagnetic Compatibility (EMC) and EMI Coupling Analysis
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

np.random.seed(42)

class EMICouplingModel:
    """
    Models high-frequency Electromagnetic Interference (EMI) coupling from Cubesat
    subsystems onto analog temperature sensor lines and communication buses.
    """
    def __init__(self):
        # Nodes: 0: CPU, 1: Battery, 2: Payload, 3: Structure, 4: Radiator, 5: Panels
        self.node_names = ["CPU", "Battery", "Payload", "Structure", "Radiator", "Paneles"]
        self.n_nodes = 6
        
        # Sources of EMI
        self.sources = ["DC_DC_Converter", "PWM_Heater", "Reaction_Wheels", "RF_Transmitter"]
        
        # Positions in 3D Cubesat space (x, y, z in meters)
        # 10x10x30 cm Cubesat (3U)
        self.sensor_positions = np.array([
            [0.05, 0.05, 0.25],  # CPU (Top)
            [0.05, 0.05, 0.15],  # Battery (Middle)
            [0.05, 0.05, 0.08],  # Payload (Lower middle)
            [0.05, 0.02, 0.15],  # Structure (Side)
            [0.01, 0.05, 0.20],  # Radiator (Exterior panel)
            [0.09, 0.05, 0.10]   # Panels (Exterior solar panels)
        ])
        
        self.source_positions = np.array([
            [0.05, 0.05, 0.18],  # DC-DC (Power board above Battery)
            [0.05, 0.04, 0.14],  # PWM Heater (Directly on Battery)
            [0.05, 0.05, 0.12],  # Reaction Wheels (ADCS block below Battery)
            [0.05, 0.05, 0.28]   # RF Transmitter (Comms board above CPU)
        ])
        
        # Source strengths (Voltage amplitude or field strength in Volts or mV)
        self.source_amplitudes = {
            "DC_DC_Converter": 0.050,  # 50 mV p-p switching ripple
            "PWM_Heater": 0.250,       # 250 mV high-frequency capacitive transient
            "Reaction_Wheels": 0.030,  # 30 mV inductive motor harmonic
            "RF_Transmitter": 0.600    # 600 mV RF field demodulation offset
        }
        
        # Coupling factors (representing shielding and capacitive/inductive transfer ratios)
        # Unshielded base coupling coefficients
        self.coupling_factors = {
            "DC_DC_Converter": 0.04,
            "PWM_Heater": 0.12,
            "Reaction_Wheels": 0.03,
            "RF_Transmitter": 0.08
        }
        
        # Sensor sensitivity: 10 mV/°C (0.01 V/°C)
        self.sensor_sensitivity = 0.01
        
    def calculate_distances(self):
        """
        Calculates the Euclidean distance matrix between EMI sources and sensors.
        """
        distances = np.zeros((self.n_nodes, len(self.sources)))
        for i in range(self.n_nodes):
            for j in range(len(self.sources)):
                dist = np.linalg.norm(self.sensor_positions[i] - self.source_positions[j])
                # Lower bound distance to prevent division by zero in near-field
                distances[i, j] = max(0.01, dist)
        return distances

    def compute_noise_waveform(self, t, active_sources=None):
        """
        Generates the instantaneous coupled noise voltage waveforms at time t (microsecond steps).
        """
        if active_sources is None:
            active_sources = {s: True for s in self.sources}
            
        distances = self.calculate_distances()
        node_noise = np.zeros((self.n_nodes, len(t)))
        
        # Frequencies of sources
        f_dcdc = 100e3  # 100 kHz switching converter
        f_pwm = 1e3     # 1 kHz PWM frequency
        f_wheels = 25e3 # 25 kHz reaction wheels harmonics
        f_rf = 2.2e9    # 2.2 GHz RF carrier (demodulates as a DC shift due to amplifier rectification)
        
        for i in range(self.n_nodes):
            noise_v = np.zeros(len(t))
            
            # 1. DC-DC Converter Noise (100kHz saw-tooth/sinusoidal ripple)
            if active_sources.get("DC_DC_Converter", False):
                dist = distances[i, 0]
                coupled_amp = self.source_amplitudes["DC_DC_Converter"] * self.coupling_factors["DC_DC_Converter"] / dist
                noise_v += coupled_amp * np.sin(2.0 * np.pi * f_dcdc * t)
                
            # 2. PWM Heater (1kHz square pulses with 0.1 duty cycle, capacitive spike edges)
            if active_sources.get("PWM_Heater", False):
                dist = distances[i, 1]
                coupled_amp = self.source_amplitudes["PWM_Heater"] * self.coupling_factors["PWM_Heater"] / dist
                # Model high dV/dt transients on square wave edges (high-pass filter effect)
                pwm_wave = np.sign(np.sin(2.0 * np.pi * f_pwm * t))
                pwm_edges = np.diff(pwm_wave, prepend=pwm_wave[0])
                noise_v += coupled_amp * 0.1 * pwm_edges
                
            # 3. Reaction Wheels (5-50kHz motor harmonics)
            if active_sources.get("Reaction_Wheels", False):
                dist = distances[i, 2]
                coupled_amp = self.source_amplitudes["Reaction_Wheels"] * self.coupling_factors["Reaction_Wheels"] / dist
                noise_v += coupled_amp * (np.sin(2.0 * np.pi * f_wheels * t) + 0.5 * np.sin(2.0 * np.pi * 2 * f_wheels * t))
                
            # 4. RF Transmitter (2.2GHz carrier rectifies as a continuous DC offset bias)
            if active_sources.get("RF_Transmitter", False):
                dist = distances[i, 3]
                coupled_amp = self.source_amplitudes["RF_Transmitter"] * self.coupling_factors["RF_Transmitter"] / dist
                # RF rectification creates a DC envelope voltage offset
                noise_v += coupled_amp * 1.0 # Pure DC bias
                
            node_noise[i, :] = noise_v
            
        return node_noise


def run_emc_study():
    print("======================================================================")
    print("             Phase T41: EMC / EMI Subsystem Compatibility            ")
    print("======================================================================\n")
    
    model = EMICouplingModel()
    distances = model.calculate_distances()
    
    # Let's run a microsecond simulation to visualize the EMI waveforms over 5 milliseconds
    t = np.linspace(0.0, 0.005, 5000) # 5 ms at 1 microsecond resolution
    
    # 1. Scenario Nominal (All sources active)
    print("[*] Simulando Escenario NOMINAL (Todos los subsistemas activos)...")
    noise_nominal = model.compute_noise_waveform(t, active_sources={s: True for s in model.sources})
    
    # 2. Scenario Silent (Only DC-DC active, wheels/heaters/transmitters off)
    print("[*] Simulando Escenario SILENCIOSO (Solo regulador DC-DC activo)...")
    noise_silent = model.compute_noise_waveform(t, active_sources={"DC_DC_Converter": True})
    
    # Compute RMS Noise Voltage and Equivalent Temperature Error
    results_records = []
    
    print("\n--- Resultados de Ruido y SNR por Sensor ---")
    for i in range(model.n_nodes):
        name = model.node_names[i]
        
        # Nominal RMS
        v_rms_nom = np.sqrt(np.mean(noise_nominal[i]**2))
        temp_err_nom = v_rms_nom / model.sensor_sensitivity
        
        # Silent RMS
        v_rms_sil = np.sqrt(np.mean(noise_silent[i]**2))
        temp_err_sil = v_rms_sil / model.sensor_sensitivity
        
        # Signal-to-Noise Ratio (SNR) in dB
        # Assuming nominal signal voltage range is 1.0V (representing typical sensor swing)
        snr_nom = 20.0 * np.log10(1.0 / max(1e-6, v_rms_nom))
        snr_sil = 20.0 * np.log10(1.0 / max(1e-6, v_rms_sil))
        
        shielding_needed = "Sí (Sesgo crítico RF/PWM)" if temp_err_nom > 1.5 else "No (Seguro)"
        
        print(f"Sensor: {name:10s} | Nom Error: {temp_err_nom:5.2f}°C (SNR: {snr_nom:4.1f}dB) | Sil Error: {temp_err_sil:5.2f}°C (SNR: {snr_sil:4.1f}dB) | Blindaje: {shielding_needed}")
        
        results_records.append({
            "Sensor": name,
            "Dist_to_DCDC_m": distances[i, 0],
            "Dist_to_RF_m": distances[i, 3],
            "Nominal_RMS_V": v_rms_nom,
            "Nominal_Temp_Error_C": temp_err_nom,
            "Nominal_SNR_dB": snr_nom,
            "Silent_RMS_V": v_rms_sil,
            "Silent_Temp_Error_C": temp_err_sil,
            "Silent_SNR_dB": snr_sil,
            "Shielding_Required": "YES" if temp_err_nom > 1.5 else "NO"
        })
        
    df_emc = pd.DataFrame(results_records)
    csv_path = "satellite/emc/emc_results.csv"
    df_emc.to_csv(csv_path, index=False)
    print(f"\n[+] Resultados EMC guardados en: {csv_path}")
    
    # Plot coupled waveforms for CPU and Battery
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5))
    fig.patch.set_facecolor('#070b19')
    ax1.set_facecolor('#0d1527')
    ax2.set_facecolor('#0d1527')
    
    t_ms = t * 1000.0 # to milliseconds
    
    # CPU Noise Waveform
    ax1.plot(t_ms, noise_nominal[0] * 1000.0, label="Nominal (Todos los subsistemas)", color='#ff2a5f', linewidth=1.5)
    ax1.plot(t_ms, noise_silent[0] * 1000.0, label="Silencioso (Solo DC-DC)", color='#00f0ff', linewidth=1.5, alpha=0.7)
    ax1.set_title("Forma de Onda de Ruido Acoplado en el Sensor de CPU (Top)", color='white', fontsize=12, pad=10)
    ax1.set_ylabel("Voltaje de Ruido (mV)", color='#94a3b8')
    ax1.spines['bottom'].set_color('#334155')
    ax1.spines['top'].set_color('#334155')
    ax1.spines['left'].set_color('#334155')
    ax1.spines['right'].set_color('#334155')
    ax1.tick_params(colors='white')
    ax1.grid(color='white', linestyle=':', alpha=0.08)
    ax1.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc='upper right')
    
    # Battery Noise Waveform (High PWM Heater spike proximity)
    ax2.plot(t_ms, noise_nominal[1] * 1000.0, label="Nominal (Todos los subsistemas)", color='#ffb821', linewidth=1.5)
    ax2.plot(t_ms, noise_silent[1] * 1000.0, label="Silencioso (Solo DC-DC)", color='#26ffad', linewidth=1.5, alpha=0.7)
    ax2.set_title("Ruido Acoplado en Batería (Cercanía a Calefactor PWM e Involucración Motor ADCS)", color='white', fontsize=12, pad=10)
    ax2.set_xlabel("Tiempo (milisegundos)", color='#94a3b8')
    ax2.set_ylabel("Voltaje de Ruido (mV)", color='#94a3b8')
    ax2.spines['bottom'].set_color('#334155')
    ax2.spines['top'].set_color('#334155')
    ax2.spines['left'].set_color('#334155')
    ax2.spines['right'].set_color('#334155')
    ax2.tick_params(colors='white')
    ax2.grid(color='white', linestyle=':', alpha=0.08)
    ax2.legend(facecolor='#0f172a', edgecolor='#1e293b', labelcolor='white', loc='upper right')
    
    plt.tight_layout()
    plot_path = "satellite/emc/emc_noise_plot.png"
    plt.savefig(plot_path, facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close()
    print(f"[+] Gráfico de ruido EMC guardado en: {plot_path}")
    
    # 3. Generate detailed markdown report
    report_path = "satellite/emc/emc_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Informe de Compatibilidad Electromagnética (EMC / EMI) (Fase T41)\n\n")
        f.write(f"**Generado:** {time.strftime('%Y-%m-%d %H:%M:%S')} | **Semilla:** 42\n\n")
        f.write("Este informe detalla el análisis físico y de compatibilidad electromagnética de los acoplamientos parásitos (capacitivos, inductivos y por rectificación de radiofrecuencia) de los subsistemas del Cubesat sobre las líneas analógicas de instrumentación térmica.\n\n")
        
        f.write("## 1. Tabla de Análisis de Interferencia y SNR por Nodo\n\n")
        f.write("| Sensor | Error Térmico Nominal (°C) | SNR Nominal (dB) | Error Térmico Silencioso (°C) | SNR Silencioso (dB) | Blindaje Adicional Requerido |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in df_emc.iterrows():
            f.write(f"| **{r['Sensor']}** | {r['Nominal_Temp_Error_C']:.2f}°C | {r['Nominal_SNR_dB']:.1f} dB | {r['Silent_Temp_Error_C']:.2f}°C | {r['Silent_SNR_dB']:.1f} dB | **{r['Shielding_Required']}** |\n")
            
        f.write("\n## 2. Recomendaciones de Blindaje Electromagnético (Mitigación EMI)\n\n")
        f.write("> [!WARNING]\n")
        f.write("> **Diagnóstico de Vulnerabilidades Físicas:**\n")
        f.write("> 1. **Sensor de CPU (Top)**: Es el nodo más expuesto a la interferencia por acoplamiento de RF debido a la cercanía con el Transmisor de Banda S/X (2.2 GHz, 2W). La rectificación de RF en el amplificador operacional de instrumentación induce una tensión continua parásita equivalente a un sesgo térmico de **" + f"{df_emc.loc[df_emc['Sensor'] == 'CPU', 'Nominal_Temp_Error_C'].values[0]:.2f}°C**. Requiere blindaje Faraday con pintura conductiva de níquel en la tapa superior.\n")
        f.write("> 2. **Sensor de Batería (Middle)**: Sufre picos capacitivos rápidos de **" + f"{df_emc.loc[df_emc['Sensor'] == 'Battery', 'Nominal_Temp_Error_C'].values[0]:.2f}°C** generados por los flancos de subida del Calefactor PWM a 1 kHz. Se recomienda rutear la señal del termistor en par trenzado apantallado (STP).\n")
        f.write("> 3. **Filtro de Rail de Alimentación**: Se debe instalar un condensador de desacoplo de $10\\mu\\text{F}$ en paralelo con un filtro de ferrita para eliminar los 100 kHz del regulador DC-DC en todos los nodos analógicos.\n\n")
        
        f.write("## 3. Formas de Onda y Acoplamiento Espectral\n")
        f.write("![ waveforms EMC](emc_noise_plot.png)\n")
        
    print(f"[+] Informe final de EMC guardado en: {report_path}")

if __name__ == "__main__":
    run_emc_study()
