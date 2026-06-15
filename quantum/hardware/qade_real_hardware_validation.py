import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.providers.fake_provider import GenericBackendV2

# Importar QADE
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import quantum
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.optimization.hardware_cost_model import estimate_physical_cost

SHOTS = 1024
RESULTS_DIR = Path("benchmarks/results/hardware_real")

def build_circuits():
    """Define los 4 circuitos de validación (sin mediciones para simulación ideal)."""
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
    
    return circuits

def compile_with_qiskit(circuit, backend):
    """Compilar con Qiskit Level 3 (baseline)."""
    # Hacer copia y añadir mediciones
    qc = circuit.copy()
    qc.measure_all()
    return transpile(qc, backend=backend, optimization_level=3)

def compile_with_qade(circuit, backend, raise_on_failure=False):
    """Compilar con QADE pipeline completo."""
    # Hacer copia y añadir mediciones
    qc = circuit.copy()
    qc.measure_all()
    
    # Primero transpile básico para enrutar inicialmente en el backend
    transpiled = transpile(qc, backend=backend, optimization_level=1)
    
    # Configurar el pase QADE
    qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
    pm = PassManager(qade_pass)
    
    try:
        optimized = pm.run(transpiled)
        return optimized
    except Exception as e:
        print(f"  [Error] QADE optimization failed: {e}")
        if raise_on_failure:
            raise RuntimeError(f"QADE optimization failed on circuit: {e}") from e
        print("  [Warning] Falling back to transpiled baseline.")
        return transpiled

def run_validation(backend_name=None, dry_run=True):
    """
    Ejecuta la validación en hardware real o simulado.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("QADE REAL HARDWARE VALIDATION")
    print(f"Timestamp: {timestamp}")
    print(f"Dry run mode: {dry_run}")
    print("=" * 60)
    
    # Cargar backend
    if dry_run:
        print("\nUsing mock GenericBackendV2 (5 qubits) for compilation dry-run...")
        backend = GenericBackendV2(num_qubits=5)
    else:
        token = os.environ.get("IBM_QUANTUM_TOKEN")
        if not token:
            print("ERROR: IBM_QUANTUM_TOKEN environment variable not set.")
            print("Export your token: export IBM_QUANTUM_TOKEN=your_token")
            return
        
        print("Connecting to IBM Quantum...")
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        
        if backend_name:
            backend = service.backend(backend_name)
        else:
            print("Auto-selecting operational backend with >= 5 qubits and shortest queue...")
            backends = service.backends(
                filters=lambda b: (
                    b.status().operational and
                    b.configuration().n_qubits >= 5 and
                    not b.configuration().simulator
                )
            )
            if not backends:
                print("ERROR: No operational real backends available.")
                return
            backend = min(backends, key=lambda b: b.status().pending_jobs)
            
        print(f"\nUsing real backend: {backend.name}")
        print(f"Backend qubits: {backend.configuration().n_qubits}")
        print(f"Queue depth: {backend.status().pending_jobs} jobs")
        
        # Confirmación de coste
        print("\n" + "=" * 40)
        print("COST WARNING:")
        print("This run will submit 8 jobs (4 circuits x 2 compilation methods).")
        print("Each job runs 1024 shots.")
        print("Confirm submission? [y/N]: ", end="")
        response = input()
        if response.lower() != 'y':
            print("Aborted by user.")
            return

    # Construir y compilar circuitos
    circuits = build_circuits()
    job_ids = {}
    compilation_metrics = {}
    
    for name, circuit in circuits.items():
        print(f"\nProcessing circuit: {name}")
        
        # 1. Compilar
        print("  Compiling with Qiskit L3...")
        qiskit_compiled = compile_with_qiskit(circuit, backend)
        
        print("  Compiling with QADE...")
        qade_compiled = compile_with_qade(circuit, backend, raise_on_failure=not dry_run)
        
        # 2. Registrar métricas
        try:
            qiskit_cost = estimate_physical_cost(qiskit_compiled, backend)
            qiskit_pred_fid = qiskit_cost["estimated_fidelity"]
        except Exception as e:
            print(f"  [Warning] Qiskit cost estimation failed: {e}")
            qiskit_pred_fid = 0.0

        try:
            qade_cost = estimate_physical_cost(qade_compiled, backend)
            qade_pred_fid = qade_cost["estimated_fidelity"]
        except Exception as e:
            print(f"  [Warning] QADE cost estimation failed: {e}")
            qade_pred_fid = 0.0

        metrics = {
            "qiskit": {
                "gate_count": qiskit_compiled.size(),
                "depth": qiskit_compiled.depth(),
                "two_qubit_count": sum(1 for inst in qiskit_compiled.data if len(inst.qubits) == 2),
                "estimated_fidelity": qiskit_pred_fid
            },
            "qade": {
                "gate_count": qade_compiled.size(),
                "depth": qade_compiled.depth(),
                "two_qubit_count": sum(1 for inst in qade_compiled.data if len(inst.qubits) == 2),
                "estimated_fidelity": qade_pred_fid
            }
        }
        compilation_metrics[name] = metrics
        
        print(f"  Metrics - Qiskit: Gates={metrics['qiskit']['gate_count']}, Depth={metrics['qiskit']['depth']}, 2Q={metrics['qiskit']['two_qubit_count']}, Pred Fid={qiskit_pred_fid:.4f}")
        print(f"  Metrics - QADE:   Gates={metrics['qade']['gate_count']}, Depth={metrics['qade']['depth']}, 2Q={metrics['qade']['two_qubit_count']}, Pred Fid={qade_pred_fid:.4f}")
        
        # 3. Enviar
        if not dry_run:
            sampler = SamplerV2(backend)
            
            # Submit Qiskit job
            try:
                print("  Submitting Qiskit job...")
                job_qiskit = sampler.run([qiskit_compiled], shots=SHOTS)
                job_ids[f"{name}_qiskit"] = job_qiskit.job_id()
                print(f"    Qiskit Job ID: {job_qiskit.job_id()}")
            except Exception as e:
                print(f"    [Error] Qiskit submission failed: {e}")
                job_ids[f"{name}_qiskit"] = f"FAILED: {e}"
                
            # Submit QADE job
            try:
                print("  Submitting QADE job...")
                job_qade = sampler.run([qade_compiled], shots=SHOTS)
                job_ids[f"{name}_qade"] = job_qade.job_id()
                print(f"    QADE Job ID: {job_qade.job_id()}")
            except Exception as e:
                print(f"    [Error] QADE submission failed: {e}")
                job_ids[f"{name}_qade"] = f"FAILED: {e}"
                
            # Pequeña pausa entre solicitudes
            time.sleep(2)
            
    # Guardar resultados
    compilation_path = RESULTS_DIR / f"compilation_metrics_{timestamp}.json"
    with open(compilation_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "backend": backend.name,
            "compilation_metrics": compilation_metrics
        }, f, indent=2)
    print(f"\nCompilation metrics saved to: {compilation_path}")
    
    if not dry_run:
        job_ids_path = RESULTS_DIR / f"job_ids_{timestamp}.json"
        with open(job_ids_path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "backend": backend.name,
                "job_ids": job_ids
            }, f, indent=2)
        print(f"Job IDs saved to: {job_ids_path}")
        print("Jobs submitted successfully. Monitor status at: https://quantum.ibm.com/jobs")
        print(f"Once complete, run: python quantum/hardware/recover_jobs.py --job-ids {job_ids_path}")
    else:
        print("\nDry-run complete. No real jobs submitted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=str, default=None, help="Name of the IBM Quantum backend")
    parser.add_argument("--run", action="store_true", help="Submit real jobs to IBM Quantum QPUs")
    args = parser.parse_args()
    
    run_validation(backend_name=args.backend, dry_run=not args.run)
