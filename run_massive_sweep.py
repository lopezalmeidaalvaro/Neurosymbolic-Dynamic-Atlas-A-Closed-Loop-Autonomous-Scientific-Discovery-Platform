import io
import sys
import numpy as np
import argparse
from datetime import datetime, timezone

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from core.autonomous import (
    run_massive_sweep,
    analyze_massive_sweep,
    save_massive_sweep_report
)

def main():
    parser = argparse.ArgumentParser(description="Run Massive Topological Sweep Engine")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full sweep (25 noise levels x 4 systems x 3 seeds) instead of reduced test"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=None,
        help="Number of seeds to use (overrides --full default). Seeds will be [42, 1337, 9001, ...]"
    )
    parser.add_argument(
        "--noise-levels",
        type=int,
        default=None,
        dest="noise_levels",
        help="Number of noise levels (overrides --full default)."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 INICIANDO ENGINE DE BARRIDO MULTIDIMENSIONAL MASIVO")
    print("=" * 60)

    # Seed pool — deterministic, reproducible sequence
    SEED_POOL = [42, 1337, 9001, 2024, 777, 314, 99, 2718, 1618, 100]

    if args.full:
        print("[MODE] Production Sweep Mode Activated")
        noise_levels = np.linspace(0.0, 2.0, 25).tolist()
        systems = ["lorenz", "rossler", "chua", "duffing"]
        seeds = [42, 1337, 9001]
    else:
        print("[MODE] Reduced Test Sweep Mode (Default)")
        noise_levels = np.linspace(0.0, 1.0, 5).tolist()
        systems = ["lorenz", "rossler"]
        seeds = [42]

    # CLI overrides take precedence over mode defaults
    if args.seeds is not None:
        n = min(args.seeds, len(SEED_POOL))
        seeds = SEED_POOL[:n]
        print(f"[OVERRIDE] Seeds set to {seeds}")

    if args.noise_levels is not None:
        noise_levels = np.linspace(0.0, 2.0, args.noise_levels).tolist()
        print(f"[OVERRIDE] Noise levels count set to {args.noise_levels}")

    # Round noise levels to 4 decimal places for clean representation
    noise_levels = [round(x, 4) for x in noise_levels]

    print(f"Sistemas: {systems}")
    print(f"Semillas: {seeds}")
    print(f"Resolución de Ruido ({len(noise_levels)} niveles): {noise_levels}")
    print("-" * 60)

    # 1. Run parallel sweep
    session_ids = run_massive_sweep(systems, noise_levels, seeds)

    if not session_ids:
        print("❌ Error: No se generaron sesiones en el barrido masivo.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("📊 ANALIZANDO DERIVADAS DE ESTABILIDAD Y DERIVA GEOMÉTRICA")
    print("=" * 60)

    # 2. Analyze results
    analysis_results = analyze_massive_sweep(session_ids)

    # 3. Export massive sweep report
    report_path = save_massive_sweep_report(analysis_results)

    # 4. Print console summary of calculated derivatives
    print("\n" + "=" * 60)
    print("🏆 RESUMEN CINEMÁTICO DEL COLAPSO GEOMÉTRICO")
    print("=" * 60)
    
    for sys_name, data in analysis_results.get("results", {}).items():
        print(f"\nSistema Dinámico: {sys_name.upper()}")
        print("-" * 75)
        print(f"{'Noise (σ)':<10} | {'Mean Drift (Δ)':<15} | {'Std Drift':<10} | {'Velocity (dΔ/dσ)':<16} | {'Accel (d²Δ/dσ²)':<15}")
        print("-" * 75)
        
        noises = data["noise"]
        drifts = data["mean_drift"]
        stds = data["std_drift"]
        vels = data["velocity"]
        accs = data["acceleration"]
        
        for i in range(len(noises)):
            print(f"{noises[i]:<10.4f} | {drifts[i]:<15.6f} | {stds[i]:<10.6f} | {vels[i]:<16.6f} | {accs[i]:<15.6f}")
        print("-" * 75)

    print(f"\n✅ Sweep completado con éxito. Reporte guardado en {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
