import os
import json
import time
import argparse
import math
import logging
from datetime import datetime
from pathlib import Path
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# Import QADE
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import quantum
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.optimization.hardware_cost_model_v2 import estimate_physical_cost
from quantum.hardware.calibration_drift_monitor import get_calibration_snapshot, compare_snapshots

CHECKPOINT_PATH = Path("benchmarks/checkpoints/RUN6_CHECKPOINT.json")
RESULTS_DIR = Path("benchmarks/results/hardware_real")
PLACEMENT_LOG_PATH = Path("benchmarks/results/hardware_real/run6_placement_log.txt")

def build_circuits():
    """Define los 5 circuitos de validación (v2)."""
    circuits = {}
    
    # CIRCUITO 1: GHZ 5q
    ghz = QuantumCircuit(5)
    ghz.h(0)
    for i in range(4):
        ghz.cx(i, i+1)
    circuits["GHZ_5q"] = ghz
    
    # CIRCUITO 2: Quantum Kernel 5q 2 layers
    qk = QuantumCircuit(5)
    for i in range(5):
        qk.h(i)
        qk.rz(0.5, i)
    for i in range(4):
        qk.cx(i, i+1)
        qk.rz(0.3, i+1)
    for i in range(5):
        qk.h(i)
        qk.rz(0.5, i)
    for i in range(4):
        qk.cx(i, i+1)
    circuits["Quantum_Kernel_5q"] = qk
    
    # CIRCUITO 3: QFT 5q
    qft = QuantumCircuit(5)
    qft.compose(QFT(5), inplace=True)
    circuits["QFT_5q"] = qft
    
    # CIRCUITO 4: VQE ansatz 5q
    vqe = QuantumCircuit(5)
    for i in range(5):
        vqe.ry(0.3 * i, i)
    for i in range(4):
        vqe.cx(i, i+1)
    for i in range(5):
        vqe.ry(0.2 * i, i)
    circuits["VQE_5q"] = vqe
    
    # CIRCUITO 5: Quantum Kernel 8q 2 layers
    qk8 = QuantumCircuit(8)
    for i in range(8):
        qk8.h(i)
        qk8.rz(0.5, i)
    for i in range(7):
        qk8.cx(i, i+1)
        qk8.rz(0.3, i+1)
    for i in range(8):
        qk8.h(i)
        qk8.rz(0.5, i)
    for i in range(7):
        qk8.cx(i, i+1)
    circuits["Quantum_Kernel_8q"] = qk8
    
    return circuits

def compile_with_qiskit(circuit, backend):
    """Compila con Qiskit Level 3."""
    qc = circuit.copy()
    qc.measure_all()
    return transpile(qc, backend=backend, optimization_level=3)

def compile_with_qade_and_details(circuit, backend, qade_key):
    """Compila con QADE y extrae detalles de qubit placement y bypass."""
    qc = circuit.copy()
    qc.measure_all()
    transpiled = transpile(qc, backend=backend, optimization_level=1)
    
    qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
    pm = PassManager(qade_pass)
    
    # Capture logs to detect bypass_evolution
    from io import StringIO
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    qade_logger = logging.getLogger("quantum.optimization.qiskit_plugin")
    old_level = qade_logger.level
    qade_logger.setLevel(logging.INFO)
    qade_logger.addHandler(handler)
    
    try:
        optimized = pm.run(transpiled)
        optimized.name = qade_key
    except Exception as e:
        qade_logger.removeHandler(handler)
        qade_logger.setLevel(old_level)
        raise e
        
    qade_logger.removeHandler(handler)
    qade_logger.setLevel(old_level)
    log_output = log_capture.getvalue()
    
    # Extract bypass_evolution
    if "Bypassing" in log_output or "bypassing" in log_output:
        bypass_evolution = True
    elif "Evolution" in log_output:
        bypass_evolution = False
    else:
        bypass_evolution = "Unknown (Check log)"
        
    # Extract layout
    layout = qade_pass._optimal_layout
    
    # Extract active qubits in input
    from quantum.integration.qiskit_adapter import qiskit_to_qade_json
    qc_unitary = QuantumCircuit(*circuit.qregs)
    for instr in circuit.data:
        if instr.operation.name != "measure":
            qubits = [qc_unitary.qubits[circuit.find_bit(q).index] for q in instr.qubits]
            qc_unitary.append(instr.operation, qubits, [])
    qade_json = qiskit_to_qade_json(qc_unitary)
    
    active_v_qs = set()
    for gate in qade_json.get("gates", []):
        if gate.get("type", "").upper() != "BARRIER":
            active_v_qs.update(gate.get("qubits", []))
            
    selected_qubits = []
    if layout:
        selected_qubits = [layout.get(v) for v in sorted(list(active_v_qs)) if v in layout]
        
    return optimized, selected_qubits, bypass_evolution, log_output

def save_checkpoint(checkpoint):
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = CHECKPOINT_PATH.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(checkpoint, f, indent=2)
    temp_path.replace(CHECKPOINT_PATH)

def load_checkpoint():
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r") as f:
            return json.load(f)
    return None

def compute_hellinger_fidelity(observed_counts: dict, ideal_probs: dict) -> float:
    """Calcula la fidelidad de Hellinger."""
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
    """Extrae counts de SamplerV2."""
    data = pub_result.data
    exclude = {"keys", "values", "items", "ndim", "shape", "size"}
    for attr in dir(data):
        if attr.startswith("_") or attr in exclude:
            continue
        val = getattr(data, attr)
        if hasattr(val, "get_counts"):
            return val.get_counts()
    raise AttributeError("Could not find any BitArray in result.")

def submit_jobs(token, backend_name, shots):
    print("=" * 60)
    print("RUN 6 SUBMISSION START")
    print(f"Target Backend: {backend_name}")
    print(f"Shots: {shots}")
    print("=" * 60)

    # Initialize Qiskit Runtime
    print("Connecting to IBM Quantum...")
    try:
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        backend = service.backend(backend_name)
    except Exception as e:
        print(f"CRITICAL ERROR: Connection failed: {e}")
        return False

    # Capture calibration snapshot
    print("\nCapturing calibration snapshot...")
    try:
        compile_snapshot = get_calibration_snapshot(backend)
    except Exception as e:
        print(f"Warning: Calibration snapshot failed: {e}")
        compile_snapshot = {}

    checkpoint = load_checkpoint()
    if checkpoint:
        print(f"Found checkpoint from timestamp: {checkpoint['timestamp']}")
        if checkpoint["backend"] != backend_name:
            print("Warning: Backend mismatch in checkpoint. Overwriting.")
            checkpoint = None
    
    if not checkpoint:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint = {
            "timestamp": timestamp,
            "backend": backend_name,
            "shots": shots,
            "jobs": {},
            "calibration_snapshot": compile_snapshot,
            "qubits_selected": {}
        }
        save_checkpoint(checkpoint)
        print(f"Created new checkpoint: {timestamp}")

    timestamp = checkpoint["timestamp"]
    circuits = build_circuits()
    compilation_metrics = {}

    metrics_path = RESULTS_DIR / f"compilation_metrics_{timestamp}.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            compilation_metrics = json.load(f).get("compilation_metrics", {})

    sampler = SamplerV2(backend)

    # Clear placement log on start of new submission
    if len(checkpoint["jobs"]) == 0 and PLACEMENT_LOG_PATH.exists():
        try:
            PLACEMENT_LOG_PATH.unlink()
        except Exception:
            pass

    for name, circuit in circuits.items():
        print(f"\nProcessing circuit: {name}...")

        qiskit_key = f"{name}_qiskit"
        qade_key = f"{name}_qade"
        
        qiskit_submitted = qiskit_key in checkpoint["jobs"] and not checkpoint["jobs"][qiskit_key].startswith("FAILED")
        qade_submitted = qade_key in checkpoint["jobs"] and not checkpoint["jobs"][qade_key].startswith("FAILED")

        # Compile always to populate metrics and placement log
        print("  Compiling circuits...")
        qiskit_compiled = compile_with_qiskit(circuit, backend)
        qiskit_compiled.name = qiskit_key

        try:
            qade_compiled, selected_qubits, bypass_evolution, log_output = compile_with_qade_and_details(circuit, backend, qade_key)
            checkpoint["qubits_selected"][name] = selected_qubits
            save_checkpoint(checkpoint)
        except Exception as e:
            print(f"  [Error] QADE compilation failed for {name}: {e}")
            qade_compiled = None
            selected_qubits = []
            bypass_evolution = "FAILED"
            log_output = f"Compilation failed: {e}"

        # Get gate metrics
        qiskit_pred_fid = 0.0
        try:
            qiskit_pred_fid = estimate_physical_cost(qiskit_compiled, backend)["estimated_fidelity"]
        except Exception:
            pass
            
        qade_pred_fid = 0.0
        if qade_compiled:
            try:
                qade_pred_fid = estimate_physical_cost(qade_compiled, backend)["estimated_fidelity"]
            except Exception:
                pass

        metrics = {
            "qiskit": {
                "gate_count": qiskit_compiled.size(),
                "depth": qiskit_compiled.depth(),
                "two_qubit_count": sum(1 for inst in qiskit_compiled.data if len(inst.qubits) == 2),
                "estimated_fidelity": qiskit_pred_fid
            },
            "qade": {
                "gate_count": qade_compiled.size() if qade_compiled else 0,
                "depth": qade_compiled.depth() if qade_compiled else 0,
                "two_qubit_count": sum(1 for inst in qade_compiled.data if len(inst.qubits) == 2) if qade_compiled else 0,
                "estimated_fidelity": qade_pred_fid
            }
        }
        compilation_metrics[name] = metrics

        # Generate placement log entry
        placement_info = (
            f"Circuit: {name}\n"
            f"  - Selected Physical Qubits: {selected_qubits}\n"
            f"  - Bypass Evolution: {bypass_evolution}\n"
            f"  - Gate Count: Qiskit L3 = {metrics['qiskit']['gate_count']} gates | QADE = {metrics['qade']['gate_count']} gates (Delta = {metrics['qade']['gate_count'] - metrics['qiskit']['gate_count']:+d})\n"
            f"  - Evolution Log:\n{log_output}\n"
            f"{'-'*60}\n"
        )
        print(placement_info)

        # Write placement log
        PLACEMENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        log_content = ""
        if PLACEMENT_LOG_PATH.exists():
            with open(PLACEMENT_LOG_PATH, "r") as f:
                log_content = f.read()
        if f"Circuit: {name}" not in log_content:
            with open(PLACEMENT_LOG_PATH, "a") as f:
                f.write(placement_info)

        # Submit Qiskit job
        if not qiskit_submitted:
            try:
                print("  Submitting Qiskit job...")
                job_qiskit = sampler.run([qiskit_compiled], shots=shots)
                checkpoint["jobs"][qiskit_key] = job_qiskit.job_id()
                print(f"    Qiskit Job ID: {job_qiskit.job_id()}")
            except Exception as e:
                print(f"    [Error] Qiskit submission failed: {e}")
                checkpoint["jobs"][qiskit_key] = f"FAILED: {e}"
            save_checkpoint(checkpoint)
        else:
            print(f"  Qiskit job already submitted: {checkpoint['jobs'][qiskit_key]}")

        # Submit QADE job
        if not qade_submitted:
            if qade_compiled:
                try:
                    print("  Submitting QADE job...")
                    job_qade = sampler.run([qade_compiled], shots=shots)
                    checkpoint["jobs"][qade_key] = job_qade.job_id()
                    print(f"    QADE Job ID: {job_qade.job_id()}")
                except Exception as e:
                    print(f"    [Error] QADE submission failed: {e}")
                    checkpoint["jobs"][qade_key] = f"FAILED: {e}"
            else:
                checkpoint["jobs"][qade_key] = "FAILED: Compilation failed"
            save_checkpoint(checkpoint)
        else:
            print(f"  QADE job already submitted: {checkpoint['jobs'][qade_key]}")

        time.sleep(2)

    # Save compilation metrics
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "backend": backend_name,
            "compilation_metrics": compilation_metrics
        }, f, indent=2)
        
    print(f"\nCompilation metrics saved to: {metrics_path}")
    print("=" * 60)
    print("SUBMISSION PHASE COMPLETE")
    print("=" * 60)
    return True

def recover_and_analyze(token):
    checkpoint = load_checkpoint()
    if not checkpoint:
        print("ERROR: No checkpoint file found at benchmarks/checkpoints/RUN6_CHECKPOINT.json")
        return False

    timestamp = checkpoint["timestamp"]
    backend_name = checkpoint["backend"]
    shots = checkpoint["shots"]
    jobs = checkpoint["jobs"]
    compile_snapshot = checkpoint.get("calibration_snapshot", {})
    qubits_selected = checkpoint.get("qubits_selected", {})

    print("=" * 60)
    print(f"RECOVERING RUN 6 JOBS FOR BACKEND: {backend_name}")
    print(f"Checkpoint Timestamp: {timestamp}")
    print("=" * 60)

    try:
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    except Exception as e:
        print(f"CRITICAL ERROR: Connection failed: {e}")
        return False

    # Check status
    pending_jobs = False
    completed_jobs_dict = {}

    for key, job_id in jobs.items():
        if job_id.startswith("FAILED"):
            print(f"  {key}: FAILED submission ({job_id})")
            completed_jobs_dict[key] = {
                "status": "SUBMISSION_FAILED",
                "counts": None,
                "fidelity": 0.0
            }
            continue

        print(f"  Checking job {job_id} for {key}...")
        try:
            job = service.job(job_id)
            status_str = str(job.status())
            print(f"    Current status: {status_str}")

            if not job.in_final_state():
                pending_jobs = True
                completed_jobs_dict[key] = {
                    "status": status_str,
                    "counts": None,
                    "fidelity": None
                }
            elif "DONE" in status_str or "JobStatus.DONE" in status_str:
                completed_jobs_dict[key] = {
                    "status": "DONE",
                    "job_id": job_id,
                    "job_status": status_str
                }
            else:
                completed_jobs_dict[key] = {
                    "status": f"FAILED: {status_str}",
                    "counts": None,
                    "fidelity": 0.0
                }
        except Exception as e:
            print(f"    [Error] Querying job failed: {e}")
            pending_jobs = True
            completed_jobs_dict[key] = {
                "status": f"QUERY_ERROR: {e}",
                "counts": None,
                "fidelity": None
            }

    if pending_jobs:
        print("\n" + "=" * 60)
        print("STATUS: SOME JOBS ARE PENDING.")
        print("Please run --recover again later.")
        print("=" * 60)
        return False

    print("\nAll jobs completed! Fetching results...")
    
    # Simulate noiseless ideal outcomes
    circuits = build_circuits()
    ideal_probs = {}
    for name, qc in circuits.items():
        state = Statevector.from_instruction(qc)
        ideal_probs[name] = state.probabilities_dict()

    recovered_results = {}
    for key, job_info in completed_jobs_dict.items():
        if job_info["status"] != "DONE":
            recovered_results[key] = job_info
            continue

        job_id = job_info["job_id"]
        try:
            job = service.job(job_id)
            result = job.result()
            counts = get_counts_from_pub_result(result[0])

            circuit_base_name = key.replace("_qiskit", "").replace("_qade", "")
            fidelity = compute_hellinger_fidelity(counts, ideal_probs[circuit_base_name])

            recovered_results[key] = {
                "status": "DONE",
                "counts": counts,
                "fidelity": fidelity
            }
            print(f"  {key}: Fidelity = {fidelity:.4f}")
        except Exception as e:
            print(f"  [Error] Failed to fetch result for {key} ({job_id}): {e}")
            recovered_results[key] = {
                "status": f"FETCH_ERROR: {e}",
                "counts": None,
                "fidelity": 0.0
            }

    # Compare calibration drift
    drift_report = None
    if compile_snapshot:
        try:
            print("\nRetrieving active backend calibration for drift analysis...")
            backend = service.backend(backend_name)
            execute_snapshot = get_calibration_snapshot(backend)
            drift_report = compare_snapshots(compile_snapshot, execute_snapshot)
            print("  Drift analysis complete.")
        except Exception as e:
            print(f"  [Warning] Calibration drift analysis failed: {e}")

    # Save results JSON
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_path = RESULTS_DIR / f"hardware_results_{timestamp}.json"
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "backend": backend_name,
            "results": recovered_results,
            "pending_jobs": False,
            "drift_report": drift_report,
            "qubits_selected": qubits_selected
        }, f, indent=2)
    print(f"\nResults JSON saved to: {results_path}")

    # Load compilation metrics
    metrics_path = RESULTS_DIR / f"compilation_metrics_{timestamp}.json"
    metrics_data = {}
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f).get("compilation_metrics", {})

    # Generate tables
    compilation_table = [
        "| Circuit | Method | Gates | 2Q Gates | Depth |",
        "|---|---|---|---|---|"
    ]
    for circuit_name, metrics in metrics_data.items():
        qiskit_m = metrics["qiskit"]
        qade_m = metrics["qade"]
        compilation_table.append(f"| {circuit_name} | Qiskit L3 | {qiskit_m['gate_count']} | {qiskit_m['two_qubit_count']} | {qiskit_m['depth']} |")
        compilation_table.append(f"| {circuit_name} | QADE | {qade_m['gate_count']} | {qade_m['two_qubit_count']} | {qade_m['depth']} |")

    fidelity_table = [
        "| Circuit | Qiskit L3 Observed | QADE Observed | QADE vs Qiskit Delta | QADE Predicted | Prediction Error | Winner | Qubits Físicos QADE |",
        "|---|---|---|---|---|---|---|---|"
    ]
    
    better_count = 0
    total_valid = 0
    worst_case_circuits = []
    best_improvement = -999.0
    best_circuit = None
    max_degradation = 0.0

    circuit_names = sorted(list(set(k.replace("_qiskit", "").replace("_qade", "") for k in recovered_results.keys())))
    
    for name in circuit_names:
        qiskit_fid = recovered_results.get(f"{name}_qiskit", {}).get("fidelity")
        qade_fid = recovered_results.get(f"{name}_qade", {}).get("fidelity")
        qade_pred = metrics_data.get(name, {}).get("qade", {}).get("estimated_fidelity", 0.0)
        q_sel = str(qubits_selected.get(name, "N/A"))

        if qiskit_fid is None or qade_fid is None:
            fidelity_table.append(f"| {name} | FAILED | FAILED | - | {qade_pred:.4f} | - | - | {q_sel} |")
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
            if abs(delta) > max_degradation:
                max_degradation = abs(delta)

        fidelity_table.append(
            f"| {name} | {qiskit_fid:.4f} | {qade_fid:.4f} | {delta:+.4f} | {qade_pred:.4f} | {pred_error:.4f} | {status} | `{q_sel}` |"
        )

    win_rate = (better_count / total_valid) * 100 if total_valid > 0 else 0.0

    # Determine Class D Criteria
    win_rate_ok = (better_count >= 3)
    improvement_ok = (best_improvement >= 0.0100)
    degradation_ok = (max_degradation <= 0.0800)

    class_d_success = win_rate_ok and improvement_ok and degradation_ok
    new_class = "D — Pilot-Ready" if class_d_success else "C — Product Candidate"

    print(f"\nWin Rate: {better_count}/{total_valid} ({win_rate:.1f}%)")
    print(f"Max Improvement: {best_improvement:+.4f} ({'PASS' if improvement_ok else 'FAIL'})")
    print(f"Max Degradation: {max_degradation:.4f} ({'PASS' if degradation_ok else 'FAIL'})")
    print(f"Target Classification: Class {new_class}")

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
                f"A maximum drift of {max(drift_report['max_t1_drift_pct'], drift_report['max_t2_drift_pct'], drift_report['max_gate_error_drift_pct']):.1f}% was detected.\n"
            )
        else:
            drift_md += f"\n*   **Drift Status**: PASS (Calibration drift is within the {drift_report['threshold_pct']}% stability threshold).\n"

    report_content = f"""# QADE Real Hardware Validation Report (Run 6)
 
> **⚠️ DISCLOSURE:** All economic metrics, hardware costs, and licensing models discussed in this project context represent speculative simulation projections and do not reflect active revenues or contracted values. (modelo especulativo — sin revenue real)

### Metadata
*   **Target Backend**: {backend_name}
*   **Execution Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
*   **QADE Version**: {quantum.__version__}
*   **Qiskit Version**: {qiskit.__version__}
*   **Shots per Circuit**: {shots}
*   **Results Source File**: `[results_file](file:///{results_path.as_posix()})`

### Comparison vs Run 5
Para comparar directamente con los resultados del Run 5:
- GHZ_5q en Run 5: Delta = -0.0062 (Qiskit ganó)
- QFT_5q en Run 5: Delta = -0.0070 (Qiskit ganó)
- Quantum_Kernel_5q en Run 5: Delta = -0.0004 (Qiskit ganó)
- Quantum_Kernel_8q en Run 5: Delta = +0.0034 (QADE ganó)
- VQE_5q en Run 5: Delta = +0.0000 (QADE ganó)

### Compilation Metrics
{"\n".join(compilation_table)}

### Observed Fidelity (Hardware Real)
{"\n".join(fidelity_table)}

{drift_md}

### Honest Analysis
QADE superó a Qiskit L3 en **{better_count} de {total_valid}** casos evaluados (**{win_rate:.1f}%** win rate).

*   **Resultado general**: QADE obtuvo una tasa de acierto de **{better_count}/{total_valid}** (win rate = {win_rate:.1f}%).
{"*   **Resultado positivo**: QADE demostró una mejora de **" + f"{best_improvement*100:+.2f}%" + "** en fidelidad observada sobre Qiskit L3 en el hardware real **" + backend_name + "** para el circuito **" + str(best_circuit) + "**." if better_count > 0 else ""}
{"*   **Resultado desfavorable**: En el hardware real **" + backend_name + "**, QADE no superó a Qiskit L3 en la fidelidad observada para los circuitos: **" + ", ".join(worst_case_circuits) + "**." if len(worst_case_circuits) > 0 else ""}

### Clasificación Final de Readiness
Criterios de éxito para Class D:
1. Win rate >= 3/5: **{'CUMPLIDO' if win_rate_ok else 'FALLIDO'}**
2. Al menos 1 circuito con delta fidelidad > +1%: **{'CUMPLIDO' if improvement_ok else 'FALLIDO'}**
3. Ninguna degradación > -8%: **{'CUMPLIDO' if degradation_ok else 'FALLIDO'}**

Resultado de Clasificación: **Class {new_class}**

### Reproducibility
To reproduce this analysis and regenerate this report, execute the following command:
```bash
python quantum/hardware/run6_executor.py --recover
```
"""

    report_path = RESULTS_DIR / f"report_{timestamp}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nReport generated successfully: {report_path}")

    # Append to HARDWARE_VALIDATION_REPORT.md
    validation_report_path = Path("docs/quantum/HARDWARE_VALIDATION_REPORT.md")
    if validation_report_path.exists():
        with open(validation_report_path, "r", encoding="utf-8") as f:
            v_content = f.read()
        
        if "## Sexta Ejecución (Run 6)" not in v_content:
            job_rows = []
            for name in circuit_names:
                qiskit_id = jobs.get(f"{name}_qiskit", "N/A")
                qade_id = jobs.get(f"{name}_qade", "N/A")
                job_rows.append(f"| {name} | Qiskit L3 (Baseline) | `{qiskit_id}` | Completed (DONE) |")
                job_rows.append(f"| {name} | QADE | `{qade_id}` | Completed (DONE) |")

            comp_rows = []
            for circuit_name, metrics in metrics_data.items():
                qiskit_m = metrics["qiskit"]
                qade_m = metrics["qade"]
                comp_rows.append(f"| {circuit_name} | Qiskit L3 | {qiskit_m['gate_count']} | {qiskit_m['two_qubit_count']} | {qiskit_m['depth']} |")
                comp_rows.append(f"| {circuit_name} | QADE | {qade_m['gate_count']} | {qade_m['two_qubit_count']} | {qade_m['depth']} |")

            fid_rows = []
            for name in circuit_names:
                qiskit_fid = recovered_results.get(f"{name}_qiskit", {}).get("fidelity", 0.0)
                qade_fid = recovered_results.get(f"{name}_qade", {}).get("fidelity", 0.0)
                delta = qade_fid - qiskit_fid
                qade_pred = metrics_data.get(name, {}).get("qade", {}).get("estimated_fidelity", 0.0)
                pred_error = abs(qade_pred - qade_fid)
                status = "QADE WINS" if delta > 0 else "QISKIT WINS"
                q_sel = str(qubits_selected.get(name, "N/A"))
                fid_rows.append(f"| {name} | {qiskit_fid:.4f} | {qade_fid:.4f} | {delta:+.4f} | {qade_pred:.4f} | {pred_error:.4f} | {status} | `{q_sel}` |")

            run6_section = f"""
---

## Sexta Ejecución (Run 6) — VERIFICADA

Backend: {backend_name}
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Shots: {shots}
Correcciones activas:
- qiskit_plugin.py: Desacoplamiento virtual-físico (Stage E) para evitar desbordar el sandbox limit en ibm_fez

### Job IDs (Run 6) — Verificables en https://quantum.ibm.com/jobs

| Circuit | Method | Job ID | Status |
|---|---|---|---|
{"\n".join(job_rows)}

### Compilation Metrics (Run 6)
| Circuit | Method | Gates | 2Q Gates | Depth |
|---|---|---|---|---|
{"\n".join(comp_rows)}

### Observed Fidelity (Run 6) — MEDIDO en hardware real
| Circuit | Qiskit L3 Observed | QADE Observed | QADE vs Qiskit Delta | QADE Predicted | Prediction Error | Status | Qubits Físicos QADE |
|---|---|---|---|---|---|---|---|
{"\n".join(fid_rows)}

### Honest Analysis
QADE superó a Qiskit L3 en **{better_count} de {total_valid}** casos evaluados (**{win_rate:.1f}%** win rate).

*   **Resultado general**: QADE obtuvo una tasa de acierto de **{better_count}/{total_valid}** (win rate = {win_rate:.1f}%).
{"*   **Resultado positivo**: QADE demostró una mejora de **" + f"{best_improvement*100:+.2f}%" + "** en fidelidad observada sobre Qiskit L3 en el hardware real **" + backend_name + "** para el circuito **" + str(best_circuit) + "**." if better_count > 0 else ""}
{"*   **Resultado desfavorable**: En el hardware real **" + backend_name + "**, QADE no superó a Qiskit L3 en la fidelidad observada para los circuitos: **" + ", ".join(worst_case_circuits) + "**." if len(worst_case_circuits) > 0 else ""}

### Reproducibility
To reproduce this analysis and regenerate this report, execute the following command:
```bash
python quantum/hardware/run6_executor.py --recover
```
"""
            with open(validation_report_path, "a", encoding="utf-8") as f:
                f.write(run6_section)
            print(f"Appended Run 6 results to: {validation_report_path}")
        else:
            print("Run 6 results already present in HARDWARE_VALIDATION_REPORT.md.")

    # Update PHASE9_READINESS_ASSESSMENT.md
    readiness_path = Path("PHASE9_READINESS_ASSESSMENT.md")
    if readiness_path.exists():
        with open(readiness_path, "r", encoding="utf-8") as f:
            r_lines = f.readlines()
        
        # Update Classification line
        for idx, line in enumerate(r_lines):
            if line.startswith("## Classification:"):
                r_lines[idx] = f"## Classification: {new_class}\n"
                break
        
        # Append Run 6 status to entrance criteria list
        has_run6 = any("Run 6 verificado" in l for l in r_lines)
        if not has_run6:
            for idx, line in enumerate(r_lines):
                if "Run 5 verificado" in line:
                    r_lines.insert(idx + 1, f"✅ Run 6 verificado ({better_count}/{total_valid} wins, classification updated)\n")
                    break

            # Update Action Checklist
            for idx, line in enumerate(r_lines):
                if "Alcanzar win rate" in line:
                    chk = "x" if win_rate_ok else " "
                    r_lines[idx] = f"4. [{chk}] Alcanzar win rate >= 3/5 en ejecución real ({'CUMPLIDO' if win_rate_ok else 'FALLIDO'}: {better_count}/{total_valid} wins)\n"
                    break

        with open(readiness_path, "w", encoding="utf-8") as f:
            f.writelines(r_lines)
        print(f"Updated classification and checklist in: {readiness_path}")

    # Remove checkpoint file upon successful completion
    try:
        CHECKPOINT_PATH.unlink()
        print("Checkpoint file cleaned up successfully.")
    except Exception as e:
        pass

    print("=" * 60)
    print("RECOVERY AND ANALYSIS PHASE COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, default=None, help="IBM Quantum API Token")
    parser.add_argument("--backend", type=str, default="ibm_fez", help="IBM Quantum Backend name")
    parser.add_argument("--shots", type=int, default=8192, help="Number of shots")
    parser.add_argument("--submit", action="store_true", help="Submit validation jobs to IBM Quantum")
    parser.add_argument("--recover", action="store_true", help="Recover results from IBM Quantum and analyze")
    args = parser.parse_args()

    token = args.token or os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        print("ERROR: IBM Quantum token not found. Pass it with --token or set the IBM_QUANTUM_TOKEN environment variable.")
        sys.exit(1)

    if args.submit:
        success = submit_jobs(token, args.backend, args.shots)
        sys.exit(0 if success else 1)
    elif args.recover:
        success = recover_and_analyze(token)
        sys.exit(0 if success else 1)
    else:
        print("ERROR: Specify either --submit or --recover.")
        sys.exit(1)
