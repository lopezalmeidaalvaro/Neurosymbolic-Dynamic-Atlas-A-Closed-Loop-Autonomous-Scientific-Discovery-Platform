import os
import json
import argparse
import qiskit
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import quantum

SHOTS = 1024
RESULTS_DIR = Path("benchmarks/results/hardware_real")

def analyze_results(results_file):
    results_path = Path(results_file)
    if not results_path.exists():
        print(f"ERROR: Results file {results_file} does not exist.")
        return
        
    # Resolver la ruta de las métricas de compilación asociadas
    metrics_name = results_path.name.replace("hardware_results_", "compilation_metrics_")
    metrics_path = results_path.parent / metrics_name
    
    if not metrics_path.exists():
        print(f"WARNING: Compilation metrics file {metrics_path} not found. Attempting to run without metrics data.")
        metrics_data = {}
    else:
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f).get("compilation_metrics", {})
            
    with open(results_path, "r") as f:
        job_results = json.load(f)
        
    timestamp = job_results["timestamp"]
    backend_name = job_results["backend"]
    results = job_results["results"]
    drift_report = job_results.get("drift_report")
    
    # Determinar dinámicamente shots por circuito a partir de las cuentas reales
    shots_per_circuit = 1024
    for key, res in results.items():
        if res.get("counts"):
            shots_per_circuit = sum(res["counts"].values())
            break
            
    print("=" * 60)
    print(f"ANALYZING REAL HARDWARE RESULTS FOR: {backend_name}")
    print(f"Timestamp: {timestamp}")
    print(f"Shots per Circuit: {shots_per_circuit}")
    print("=" * 60)
    
    # 1. Generar la tabla de métricas de compilación
    compilation_table = []
    compilation_table.append("| Circuit | Method | Gates | 2Q Gates | Depth |")
    compilation_table.append("|---|---|---|---|---|")
    
    for circuit_name, metrics in metrics_data.items():
        qiskit_m = metrics["qiskit"]
        qade_m = metrics["qade"]
        compilation_table.append(f"| {circuit_name} | Qiskit L3 | {qiskit_m['gate_count']} | {qiskit_m['two_qubit_count']} | {qiskit_m['depth']} |")
        compilation_table.append(f"| {circuit_name} | QADE | {qade_m['gate_count']} | {qade_m['two_qubit_count']} | {qade_m['depth']} |")

    # 2. Generar la tabla de fidelidades
    fidelity_table = []
    fidelity_table.append("| Circuit | Qiskit L3 Observed | QADE Observed | QADE vs Qiskit Delta | QADE Predicted | Prediction Error | Status |")
    fidelity_table.append("|---|---|---|---|---|---|---|")
    
    better_count = 0
    total_valid = 0
    worst_case_circuits = []
    best_improvement = -999.0
    best_circuit = None
    
    # Encontrar circuitos únicos (ej. GHZ_5q_qiskit y GHZ_5q_qade -> GHZ_5q)
    circuit_names = sorted(list(set(k.replace("_qiskit", "").replace("_qade", "") for k in results.keys())))
    
    for name in circuit_names:
        qiskit_res = results.get(f"{name}_qiskit", {})
        qade_res = results.get(f"{name}_qade", {})
        
        qiskit_fid = qiskit_res.get("fidelity")
        qade_fid = qade_res.get("fidelity")
        
        # Recuperar predicción si está disponible en las métricas de compilación
        qade_pred = metrics_data.get(name, {}).get("qade", {}).get("estimated_fidelity", 0.0)
        
        if qiskit_fid is None or qade_fid is None:
            print(f"  [Warning] Circuit {name} has missing/pending job results. Skipping in table.")
            fidelity_table.append(f"| {name} | PENDING | PENDING | - | {qade_pred:.4f} | - | PENDING |")
            continue
            
        total_valid += 1
        delta = qade_fid - qiskit_fid
        pred_error = abs(qade_pred - qade_fid)
        
        if delta > 0:
            better_count += 1
            status = "QADE WINS"
            if delta > best_improvement:
                best_improvement = delta
                best_circuit = name
        else:
            status = "QISKIT WINS"
            worst_case_circuits.append(name)
            
        fidelity_table.append(
            f"| {name} | {qiskit_fid:.4f} | {qade_fid:.4f} | {delta:+.4f} | {qade_pred:.4f} | {pred_error:.4f} | {status} |"
        )

    # 3. Construir el reporte honesto
    honest_analysis = []
    honest_analysis.append("### Honest Analysis")
    if total_valid > 0:
        win_rate = (better_count / total_valid) * 100
        honest_analysis.append(f"QADE superó a Qiskit L3 en **{better_count} de {total_valid}** casos evaluados (**{win_rate:.1f}%** win rate).\n")
        
        if win_rate > 0:
            pct_gain = best_improvement * 100
            honest_analysis.append(
                f"*   **Resultado positivo**: QADE demostró una mejora de **{pct_gain:+.2f}%** en fidelidad observada "
                f"sobre Qiskit L3 en el hardware real **{backend_name}** para el circuito **{best_circuit}**.\n"
            )
            
        if win_rate < 100:
            worst_circuits_str = ", ".join(worst_case_circuits)
            honest_analysis.append(
                f"*   **Resultado desfavorable**: En el hardware real **{backend_name}**, QADE no superó a Qiskit L3 "
                f"en la fidelidad observada para los circuitos: **{worst_circuits_str}**.\n"
                f"    *   *Hipótesis técnica*: Esto puede deberse a la degradación por coherencia/dephasing temporal (latencia de 429ms) "
                f"o a la deriva de calibración física (calibration drift) de los qubits de IBM entre la lectura de propiedades y la ejecución del job. "
                f"Este resultado informa la siguiente iteración del modelo de costes de hardware (Phase IX)."
            )
    else:
        honest_analysis.append("No hay suficientes resultados completados para realizar el análisis físico.")

    # 4. Formatear la sección de deriva de calibración si existe
    drift_md = ""
    if drift_report:
        drift_md += "### Calibration Drift Monitor\n"
        drift_md += f"*   **Hours Elapsed**: {drift_report['hours_elapsed']:.2f} hours\n"
        drift_md += f"*   **Max T1 Drift**: {drift_report['max_t1_drift_pct']:.1f}%\n"
        drift_md += f"*   **Max T2 Drift**: {drift_report['max_t2_drift_pct']:.1f}%\n"
        drift_md += f"*   **Max Gate Error Drift**: {drift_report['max_gate_error_drift_pct']:.1f}%\n"
        if drift_report["drift_exceeds_threshold"]:
            drift_md += (
                f"\n> [!WARNING]\n"
                f"> **Calibration drift exceeds threshold ({drift_report['threshold_pct']}%)!** "
                f"A maximum drift of {max(drift_report['max_t1_drift_pct'], drift_report['max_t2_drift_pct'], drift_report['max_gate_error_drift_pct']):.1f}% was detected "
                f"between compilation and physical execution. Results may not accurately reflect compiler optimization quality."
            )
        else:
            drift_md += f"\n*   **Drift Status**: PASS (Calibration drift is within the {drift_report['threshold_pct']}% stability threshold).\n"

    # 5. Compilar informe final en markdown
    report_content = f"""# QADE Real Hardware Validation Report
 
> **⚠️ DISCLOSURE:** All economic metrics, hardware costs, and licensing models discussed in this project context represent speculative simulation projections and do not reflect active revenues or contracted values. (modelo especulativo — sin revenue real)

### Metadata
*   **Target Backend**: {backend_name}
*   **Execution Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
*   **QADE Version**: {quantum.__version__}
*   **Qiskit Version**: {qiskit.__version__}
*   **Shots per Circuit**: {shots_per_circuit}
*   **Results Source File**: `[results_file](file:///{results_path.as_posix()})`

### Compilation Metrics
{"\n".join(compilation_table)}

### Observed Fidelity (Hardware Real)
{"\n".join(fidelity_table)}

{drift_md}

{"\n".join(honest_analysis)}

### Reproducibility
To reproduce this analysis and regenerate this report, execute the following command:
```bash
python quantum/hardware/analyze_hardware_results.py --results {results_path.as_posix()}
```
"""

    # Guardar reporte
    report_path = RESULTS_DIR / f"report_{timestamp}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("\n" + "=" * 60)
    print(f"Report generated successfully: {report_path}")
    print("=" * 60)
    try:
        print(report_content)
    except UnicodeEncodeError:
        print(report_content.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=str, required=True, help="Path to hardware_results_TIMESTAMP.json file")
    args = parser.parse_args()
    
    analyze_results(args.results)
