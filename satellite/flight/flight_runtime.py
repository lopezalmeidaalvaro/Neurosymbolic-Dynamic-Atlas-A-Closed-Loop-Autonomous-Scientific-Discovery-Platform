#!/usr/bin/env python3
"""
Phase T31: Flight Software Runtime (PyTorch-Free)
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import time
import pickle
import numpy as np
import pandas as pd
import onnxruntime as ort
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

def main():
    print("======================================================================")
    print("         Phase T31: Embedded Flight Software Control Loop (ONNX)       ")
    print("======================================================================\n")
    
    # Paths
    flight_dir = Path("satellite/flight")
    models_dir = Path("satellite/models")
    
    onnx_path = flight_dir / "surrogate.onnx"
    scaler_X_path = models_dir / "scaler_X.pkl"
    scaler_y_path = models_dir / "scaler_y.pkl"
    
    if not onnx_path.exists():
        raise FileNotFoundError(f"ONNX model not found at {onnx_path}. Run export_to_onnx.py first.")
        
    # 1. Load ONNX model using ONNX Runtime (No PyTorch)
    print("[*] Cargando modelo de vuelo ONNX (Sin PyTorch)...")
    ort_session = ort.InferenceSession(str(onnx_path))
    
    # Load scalers to scale/unscale inputs and outputs
    with open(scaler_X_path, "rb") as f:
        scaler_X = pickle.load(f)
    with open(scaler_y_path, "rb") as f:
        scaler_y = pickle.load(f)
        
    print("[+] Modelo ONNX cargado exitosamente.")
    print(f"    Inputs del modelo: {[i.name for i in ort_session.get_inputs()]}")
    print(f"    Outputs del modelo: {[o.name for o in ort_session.get_outputs()]}\n")
    
    # 2. Simulate OBC Control Loop
    # Telemetry configurations
    radiator_area = 0.15      # m2 (fixed design)
    radiator_eps = 0.85       # nominal emissivity
    nominal_power = 30.0      # W (Standard operation)
    throttled_power = 5.0     # W (Safe mode)
    
    current_power = nominal_power
    cpu_temp_measured = 25.0  # Initial measured CPU temperature (°C)
    
    telemetry_logs = []
    
    # Loop duration: 60 cycles (simulating 60s total, 1s per cycle)
    cycles = 60
    
    print("--- INICIANDO BUCLE DE CONTROL EN TIEMPO REAL OBC (FP32) ---")
    print("Ciclo | Temp Medida | Potencia OBC | Pred Max Temp | Pred T_Critical | Acción")
    print("---------------------------------------------------------------------------------")
    
    for c in range(1, cycles + 1):
        t_cycle_start = time.perf_counter()
        
        # Simulating thermal plant physics step:
        # If power is high (30W), CPU temperature rises. If power is low (5W), CPU cools down.
        # Add a bit of realistic system noise.
        heating_rate = 1.8 if current_power == nominal_power else -1.2
        noise = np.random.normal(0, 0.2)
        cpu_temp_measured = max(20.0, cpu_temp_measured + heating_rate + noise)
        
        # a) Prepare inputs for ONNX model: [power, area, emissivity]
        # In flight, we feed current parameters to the neural networks to predict thermal limits
        raw_input = np.array([[current_power, radiator_area, radiator_eps]], dtype=np.float32)
        
        # Scale inputs using the pre-saved training scaler
        scaled_input = scaler_X.transform(raw_input).astype(np.float32)
        
        # b) Run ONNX inference
        onnx_outputs = ort_session.run(None, {"input": scaled_input})[0]
        
        # Unscale output to get predictions in Celsius and seconds
        unscaled_outputs = scaler_y.inverse_transform(onnx_outputs)[0]
        pred_max_temp = float(unscaled_outputs[0])
        pred_time_to_crit = float(unscaled_outputs[1])
        
        # c) Throttling Decision Logic (Predictive Safety)
        # If predicted max temperature > 75C or predicted time to critical limit is less than 30 seconds
        # Or if the current measured temperature is getting dangerously high (> 70C)
        action = "NOMINAL"
        if pred_max_temp > 75.0 or pred_time_to_crit < 30.0 or cpu_temp_measured > 70.0:
            current_power = throttled_power
            action = "THROTTLE"
        else:
            current_power = nominal_power
            action = "NOMINAL"
            
        t_cycle = (time.perf_counter() - t_cycle_start) * 1000.0 # ms
        
        print(f"{c:5d} | {cpu_temp_measured:10.2f}°C | {current_power:10.1f}W | {pred_max_temp:11.2f}°C | {pred_time_to_crit:13.1f}s | {action:8s}")
        
        telemetry_logs.append({
            "cycle": c,
            "measured_temp": cpu_temp_measured,
            "power_w": current_power,
            "pred_max_temp": pred_max_temp,
            "pred_time_to_crit": pred_time_to_crit,
            "action": action,
            "cycle_time_ms": t_cycle
        })
        
        # Small delay to simulate real OBC time steps
        time.sleep(0.01)
        
    # Write flight telemetry to CSV
    df = pd.DataFrame(telemetry_logs)
    csv_path = flight_dir / "flight_telemetry_simulation.csv"
    df.to_csv(str(csv_path), index=False)
    
    avg_cycle_time = df["cycle_time_ms"].mean()
    max_cycle_time = df["cycle_time_ms"].max()
    
    print("\n---------------------------------------------------------------------------------")
    print(f"[+] Simulación de vuelo completada. Telemetría guardada en: {csv_path}")
    print(f"[+] Rendimiento de Ciclo OBC:")
    print(f"    - Tiempo de ciclo promedio: {avg_cycle_time:.4f} ms")
    print(f"    - Tiempo de ciclo máximo: {max_cycle_time:.4f} ms")
    print(f"    - Frecuencia equivalente: {1000.0 / avg_cycle_time:.1f} Hz")
    
if __name__ == "__main__":
    main()
