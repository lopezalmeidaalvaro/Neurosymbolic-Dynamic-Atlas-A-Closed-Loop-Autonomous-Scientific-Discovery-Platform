import io
import sys

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from core.autonomous import (
    run_noise_sweep,
    analyze_noise_drift,
    evaluate_hypotheses,
    save_research_report
)

def main():
    print("=" * 60)
    print("🚀 INICIANDO BARRIDO AUTOMATIZADO DE RUIDO (AUTOMATED SWEEP)")
    print("=" * 60)
    
    # Noise grid levels (short sweep for testing as specified by user)
    noise_levels = [0.0, 0.2, 0.5]
    base_experiment = "lorenz"
    
    # 1. Scheduler runs the grid of noise levels
    session_ids = run_noise_sweep(base_experiment, noise_levels)
    
    if not session_ids:
        print("❌ Error: No se generaron sesiones en el barrido.")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("📊 ANALIZANDO SESIONES GENERADAS Y GEOMETRIC DRIFT")
    print("=" * 60)
    
    # 2. Analyze the sessions
    analysis_results = analyze_noise_drift(session_ids)
    
    # 3. Evaluate scientific hypotheses
    hypotheses_results = evaluate_hypotheses(analysis_results)
    
    # 4. Export consolidated research report
    report_path = save_research_report(analysis_results, hypotheses_results)
    
    # 5. Print a console summary showing: noise level, accuracy, and average Delta drift
    print("\n" + "=" * 60)
    print("🏆 RESUMEN DEL ANÁLISIS DE RESISTENCIA AL RUIDO")
    print("=" * 60)
    print(f"Base Experiment: {base_experiment.upper()}")
    print(f"Sistemas Analizados: {', '.join(analysis_results.get('systems_analyzed', []))}")
    print("-" * 60)
    print(f"{'Noise Level (σ)':<16} | {'Accuracy (V2)':<15} | {'Geometric Drift (Δ)':<20}")
    print("-" * 60)
    
    for run in analysis_results.get("runs", []):
        noise = run["noise_level"]
        acc = run["accuracy"]
        drift = run["average_drift"]
        print(f"{noise:<16.2f} | {acc * 100:<13.2f}% | {drift:<20.4f}")
        
    print("-" * 60)
    print("\nEvaluación de Hipótesis:")
    for h_id, h_data in hypotheses_results.items():
        print(f"  • {h_id}: Status={h_data['status']} | {h_data['evidence']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
