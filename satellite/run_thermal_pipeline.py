#!/usr/bin/env python3
"""
Satellite Thermal Pipeline Orchestrator
Executes all core spacecraft digital twin simulator stages sequentially.
Author: Alvaro Lopez Almeida
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Add project root and register config paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

# Pipeline mapping
STAGES = {
    "T9": "thermal/multi_node_thermal_network.py",
    "T11": "thermal/geometry_topology_optimizer.py",
    "T17": "thermal/hardware_in_the_loop.py",
    "T21": "thermal/train_thermal_pinn.py",
    "T22": "thermal/train_thermal_neural_ode.py",
    "T23": "thermal/closed_loop_thermal_control.py",
    "T24": "thermal/constellation_modeler.py",
    "T25": "thermal/material_aging.py",
    "T26": "thermal/tvac_integration.py",
    "T27": "thermal/ecss_compliance.py",
    "T28": "thermal/hpc_acceleration.py"
}

def print_step(step):
    print("\n" + "=" * 70)
    print(f"🚀 EXECUTING STAGE {step}: {STAGES[step]}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Satellite Thermal Digital Twin Pipeline Orchestrator")
    parser.add_argument("--from-stage", type=str, default="T9", choices=list(STAGES.keys()), help="Stage to start execution from")
    parser.add_argument("--to-stage", type=str, default="T28", choices=list(STAGES.keys()), help="Stage to end execution at")
    args = parser.parse_args()
    
    stages_keys = list(STAGES.keys())
    start_idx = stages_keys.index(args.from_stage)
    end_idx = stages_keys.index(args.to_stage)
    
    active_stages = stages_keys[start_idx:end_idx + 1]
    
    print(f"[*] Pipeline initiated. Running stages: {active_stages}")
    
    times = {}
    
    for stage in active_stages:
        print_step(stage)
        script_relative_path = STAGES[stage]
        script_absolute_path = config.SATELLITE_DIR / script_relative_path
        
        # Determine working directory context (satellite/)
        cwd = str(config.SATELLITE_DIR)
        
        t_start = time.time()
        
        # Execute script
        try:
            # Under local executions, run the scripts with the virtual environment python interpreter
            result = subprocess.run(
                [sys.executable, str(script_absolute_path)],
                cwd=cwd,
                check=True
            )
            elapsed = time.time() - t_start
            times[stage] = {"status": "SUCCESS", "time_sec": elapsed}
            print(f"\n✅ STAGE {stage} COMPLETED SUCCESSFULY IN {elapsed:.2f} SECONDS.")
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - t_start
            print(f"\n❌ STAGE {stage} FAILED WITH EXIT CODE {e.returncode}. ABORTING PIPELINE.")
            sys.exit(1)
            
    print("\n" + "=" * 70)
    print("🏁 PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    for stage, data in times.items():
        print(f" -> Stage {stage:4s}: {data['status']:8s} | Elapsed: {data['time_sec']:6.2f}s")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
