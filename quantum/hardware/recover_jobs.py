import os
import json
import argparse
import math
from pathlib import Path
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.quantum_info import Statevector

# Importar build_circuits de qade_validation_v2
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from quantum.hardware.qade_validation_v2 import build_circuits

RESULTS_DIR = Path("benchmarks/results/hardware_real")

def compute_hellinger_fidelity(observed_counts: dict, ideal_probs: dict) -> float:
    """Calcula la fidelidad de Hellinger entre la distribución observada e ideal."""
    total_shots = sum(observed_counts.values())
    if total_shots == 0:
        return 0.0
    
    overlap = 0.0
    for outcome, count in observed_counts.items():
        obs_p = count / total_shots
        ideal_p = ideal_probs.get(outcome, 0.0)
        overlap += math.sqrt(obs_p * ideal_p)
        
    return overlap ** 2

def get_counts_from_pub_result(pub_result) -> dict:
    """Extrae de forma genérica el diccionario de cuentas del PrimitiveResult de SamplerV2."""
    data = pub_result.data
    # Atributos estándar a excluir
    exclude = {"keys", "values", "items", "ndim", "shape", "size"}
    for attr in dir(data):
        if attr.startswith("_") or attr in exclude:
            continue
        val = getattr(data, attr)
        if hasattr(val, "get_counts"):
            return val.get_counts()
    raise AttributeError("Could not find any BitArray in the result DataBin.")

def recover_results(job_ids_file):
    """Carga los jobs de IBM y recupera los resultados."""
    with open(job_ids_file, "r") as f:
        job_data = json.load(f)
        
    timestamp = job_data["timestamp"]
    backend_name = job_data["backend"]
    job_ids = job_data["job_ids"]
    
    print("=" * 60)
    print(f"RECOVERING IBM JOBS FOR BACKEND: {backend_name}")
    print(f"Job IDs File: {job_ids_file}")
    print("=" * 60)
    
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    # Intentar inicializar sin token si las credenciales están guardadas localmente
    try:
        if token:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        else:
            service = QiskitRuntimeService(channel="ibm_quantum_platform")
    except Exception as e:
        print(f"ERROR: Could not connect to IBM Quantum service: {e}")
        print("Please set your token: export IBM_QUANTUM_TOKEN=your_token")
        return
        
    # Reconstruir los circuitos ideales sin mediciones para la fidelidad ideal
    circuits = build_circuits()
    ideal_probs = {}
    print("\nSimulating ideal noiseless distributions using Statevector...")
    for name, qc in circuits.items():
        state = Statevector.from_instruction(qc)
        ideal_probs[name] = state.probabilities_dict()
        print(f"  Simulated {name} ({qc.num_qubits} qubits)")
        
    recovered_results = {}
    pending_jobs = False
    
    print("\nChecking job statuses on IBM Quantum:")
    for key, job_id in job_ids.items():
        if job_id.startswith("FAILED"):
            print(f"  {key}: Skip (Submission failed: {job_id})")
            recovered_results[key] = {
                "status": "SUBMISSION_FAILED",
                "counts": None,
                "fidelity": 0.0
            }
            continue
            
        print(f"  Retrieving job {job_id} for {key}...")
        try:
            job = service.job(job_id)
            if not job.in_final_state():
                print(f"    [Pending] Job is not complete. Status: {job.status()}")
                recovered_results[key] = {
                    "status": str(job.status()),
                    "counts": None,
                    "fidelity": None
                }
                pending_jobs = True
                continue
                
            status_str = str(job.status())
            if "DONE" in status_str or "JobStatus.DONE" in status_str:
                result = job.result()
                counts = get_counts_from_pub_result(result[0])
                
                # Encontrar el nombre del circuito base (ej. GHZ_5q_qiskit -> GHZ_5q)
                circuit_base_name = key.replace("_qiskit", "").replace("_qade", "")
                
                # Calcular fidelidad de Hellinger
                fidelity = compute_hellinger_fidelity(counts, ideal_probs[circuit_base_name])
                
                print(f"    [Complete] Success. Hellinger fidelity: {fidelity:.4f}")
                recovered_results[key] = {
                    "status": "DONE",
                    "counts": counts,
                    "fidelity": fidelity
                }
            else:
                print(f"    [Failed] Job ended with state: {job.status()}")
                recovered_results[key] = {
                    "status": f"FAILED: {job.status()}",
                    "counts": None,
                    "fidelity": 0.0
                }
        except Exception as e:
            print(f"    [Error] Failed to query job {job_id}: {e}")
            recovered_results[key] = {
                "status": f"QUERY_ERROR: {e}",
                "counts": None,
                "fidelity": 0.0
            }
            
    # Calcular deriva de calibración si hay snapshot guardado
    compile_snapshot = job_data.get("calibration_snapshot")
    drift_report = None
    if compile_snapshot and not pending_jobs:
        try:
            print("\nRetrieving active backend calibration for drift analysis...")
            backend = service.backend(backend_name)
            from quantum.hardware.calibration_drift_monitor import get_calibration_snapshot, compare_snapshots
            execute_snapshot = get_calibration_snapshot(backend)
            drift_report = compare_snapshots(compile_snapshot, execute_snapshot)
            print("  Drift analysis complete.")
            print(f"    Hours elapsed: {drift_report['hours_elapsed']:.2f}")
            print(f"    Max T1 Drift: {drift_report['max_t1_drift_pct']:.1f}%")
            print(f"    Max T2 Drift: {drift_report['max_t2_drift_pct']:.1f}%")
            print(f"    Max Gate Error Drift: {drift_report['max_gate_error_drift_pct']:.1f}%")
            if drift_report['drift_exceeds_threshold']:
                print(f"    [Warning] Calibration drift exceeds threshold ({drift_report['threshold_pct']}%)!")
        except Exception as e:
            print(f"  [Warning] Failed to calculate calibration drift: {e}")

    # Guardar resultados finales
    output_path = RESULTS_DIR / f"hardware_results_{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "backend": backend_name,
            "results": recovered_results,
            "pending_jobs": pending_jobs,
            "drift_report": drift_report
        }, f, indent=2)
        
    print("\n" + "=" * 60)
    print(f"Results saved to: {output_path}")
    if pending_jobs:
        print("WARNING: Some jobs are still pending. Run recover_jobs.py again later to collect them.")
    else:
        print("All jobs completed. Run analysis script:")
        print(f"  python quantum/hardware/analyze_hardware_results.py --results {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-ids", type=str, required=True, help="Path to job_ids_TIMESTAMP.json file")
    args = parser.parse_args()
    
    recover_results(args.job_ids)
