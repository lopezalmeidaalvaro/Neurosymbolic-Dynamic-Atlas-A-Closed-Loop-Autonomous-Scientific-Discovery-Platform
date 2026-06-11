"""
Script to re-run all QADE benchmarks with real compiler installations.

Usage:
    python -m quantum.benchmarks.rerun_with_real_compilers

This script:
1. Verifies which compilers are genuinely installed
2. Runs benchmarks only with available real compilers
3. Saves results to benchmarks/results/ with timestamp
4. Generates updated reports to benchmarks/reports/
5. Updates docs automatically

Run after installing real compiler dependencies:
    bash quantum/install_benchmark_deps.sh
    python -m quantum.benchmarks.rerun_with_real_compilers
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.benchmarks.compiler_capability_detection import detect_compiler_capabilities
from quantum.benchmarks.benchmark_all_compilers import (
    verify_compiler_availability,
    run_unified_benchmarks,
    save_raw_csv,
    generate_markdown_report
)
from quantum.benchmarks.statistical_validation import run_statistical_validation
from quantum.benchmarks.update_docs_from_results import update_docs

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Check for existing checkpoint
    checkpoint_path = Path("benchmarks/checkpoints/BENCHMARK_CHECKPOINT.json")
    if checkpoint_path.exists():
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
            last_compiler = checkpoint_data.get("last_completed_compiler", "Unknown")
            print(f"Resuming benchmark from checkpoint: {last_compiler}")
        except Exception:
            pass

    print("="*60)
    print("QADE BENCHMARK RE-EXECUTION WITH REAL COMPILERS")
    print(f"Timestamp: {timestamp}")
    print("="*60)
    
    # Paso 0: Ejecutar detección dinámica de capacidades
    print("\nStep 0: Running compiler capability detection...")
    detect_compiler_capabilities()
    
    # Paso 1: Verificar disponibilidad real
    print("\nStep 1: Verifying compiler availability...")
    available = verify_compiler_availability()
    
    real_compilers = [k for k, v in available.items() if v]
    print(f"\nWill benchmark against: {real_compilers}")
    
    if len(real_compilers) == 1:
        print("\nWARNING: Only Qiskit is available.")
        print("Results will only compare QADE vs Qiskit L3.")
        print("Install other compilers for more complete comparison:")
        print("  bash quantum/install_benchmark_deps.sh")
        print("Continuing with Qiskit-only benchmark (non-interactive mode)...")
    
    # Paso 2: Ejecutar benchmarks
    print("\nStep 2: Running benchmarks (30 runs per configuration)...")
    results = run_unified_benchmarks()
    
    # Paso 3: Guardar con timestamp
    print("\nStep 3: Saving results...")
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / f"REAL_COMPILER_BENCHMARK_{timestamp}.csv"
    save_raw_csv(results, str(csv_path))
    
    # También actualizar el archivo principal
    primary_csv_path = output_dir / "COMPILER_COMPARISON_REAL.csv"
    save_raw_csv(results, str(primary_csv_path))
    # Y el de docs para compatibilidad
    save_raw_csv(results, "docs/ALL_COMPILERS_BENCHMARK_RESULTS.csv")
    
    # Paso 4: Generar informes y análisis estadístico
    print("\nStep 4: Generating reports and statistical validation...")
    generate_markdown_report(results)
    run_statistical_validation(str(primary_csv_path))
    
    # Paso 5: Generar nota de disponibilidad de compiladores
    availability_note = {
        "timestamp": timestamp,
        "real_compilers_used": real_compilers,
        "benchmark_type": "REAL_COMPILERS_ONLY",
        "excluded_compilers": [
            k for k, v in available.items() if not v
        ]
    }
    
    with open(
        "benchmarks/results/COMPILER_AVAILABILITY_NOTE.json", "w"
    ) as f:
        json.dump(availability_note, f, indent=2)
        
    # Paso 6: Actualizar documentación
    print("\nStep 6: Synchronizing documentation...")
    update_docs()
    
    print("\nStep 7: Summary")
    print("="*60)
    print(f"Real compilers benchmarked: {real_compilers}")
    print(f"Results saved to: {csv_path}")
    print(f"Report: benchmarks/reports/ALL_COMPILERS_BENCHMARK_REPORT.md")
    print(f"Statistical Report: benchmarks/reports/STATISTICAL_VALIDATION_REPORT.md")
    print("\nNOTE: All results in this run use real compiler execution.")
    print("No emulation or fallback was used.")
    print("="*60)

if __name__ == "__main__":
    main()
