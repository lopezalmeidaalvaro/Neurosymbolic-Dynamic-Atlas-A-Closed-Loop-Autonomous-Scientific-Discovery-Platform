import os
import sys
import time
import json
import logging
from pathlib import Path
import qiskit
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.circuit.library import QFT

# Ensure quantum module is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.optimization.calibration_model import get_fake_backend

def build_qaoa_3regular(num_qubits: int, layers: int = 2) -> QuantumCircuit:
    """Builds a Max-Cut QAOA circuit on a 3-regular Möbius ladder graph."""
    qc = QuantumCircuit(num_qubits)
    for q in range(num_qubits):
        qc.h(q)
        
    # Generate 3-regular graph edges (Möbius ladder)
    edges = []
    for i in range(num_qubits):
        edges.append((i, (i + 1) % num_qubits))
        if i < num_qubits // 2:
            edges.append((i, i + num_qubits // 2))
            
    for layer in range(layers):
        for u, v in edges:
            qc.cx(u, v)
            qc.rz(0.08 * (layer + 1), v)
            qc.cx(u, v)
        for q in range(num_qubits):
            qc.rx(0.12 * (layer + 1), q)
    return qc

def build_vqe_hea(num_qubits: int, depth: int = 3) -> QuantumCircuit:
    """Builds a hardware-efficient RY-RZ ansatz VQE circuit."""
    qc = QuantumCircuit(num_qubits)
    for d in range(depth):
        for i in range(num_qubits):
            qc.ry(0.1 * (d + 1) * (i + 1), i)
            qc.rz(0.2 * (d + 1) * (i + 1), i)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
    return qc

def build_quantum_kernel(num_qubits: int) -> QuantumCircuit:
    """Builds a 20-qubit Quantum Kernel circuit extending the standard pattern."""
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.h(i)
        qc.rz(0.5, i)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
        qc.rz(0.3, i + 1)
    for i in range(num_qubits):
        qc.h(i)
        qc.rz(0.5, i)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    return qc

def run_suite():
    print("=" * 60)
    print("QADE SCALE VALIDATION SUITE (20-50 QUBITS)")
    print("=" * 60)
    
    backend = get_fake_backend("FakeFez")
    print(f"Loaded backend: {backend.name} ({backend.num_qubits} qubits)")
    
    # 1. Build circuits
    circuits = {
        "GHZ_20q": QuantumCircuit(20),
        "GHZ_30q": QuantumCircuit(30),
        "QAOA_20q": build_qaoa_3regular(20, layers=2),
        "VQE_25q": build_vqe_hea(25, depth=3),
        "Quantum_Kernel_20q": build_quantum_kernel(20)
    }
    
    # Build GHZ circuits
    circuits["GHZ_20q"].h(0)
    for i in range(19):
        circuits["GHZ_20q"].cx(i, i + 1)
        
    circuits["GHZ_30q"].h(0)
    for i in range(29):
        circuits["GHZ_30q"].cx(i, i + 1)
        
    results = {}
    
    # Configure logging to capture stdout/stderr details from QADE
    logger = logging.getLogger("quantum.optimization.qiskit_plugin")
    logger.setLevel(logging.INFO)
    from io import StringIO
    
    for name, qc in circuits.items():
        print(f"\nProcessing circuit: {name}...")
        
        # Qiskit Level 3 baseline
        qc_measure = qc.copy()
        qc_measure.measure_all()
        
        t0 = time.time()
        qiskit_l3 = transpile(qc_measure, backend=backend, optimization_level=3)
        t_qiskit = time.time() - t0
        
        qiskit_gates = len(qiskit_l3.data)
        qiskit_2q = sum(1 for inst in qiskit_l3.data if len(inst.qubits) == 2 and inst.operation.name != "barrier")
        qiskit_depth = qiskit_l3.depth()
        
        # QADE transpilation (using Qiskit L3 as input)
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger.addHandler(handler)
        
        t0 = time.time()
        qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm = PassManager(qade_pass)
        try:
            qade_optimized = pm.run(qiskit_l3)
            t_qade = time.time() - t0
            success = True
        except Exception as e:
            t_qade = time.time() - t0
            print(f"  ERROR compiling with QADE: {e}")
            success = False
            qade_optimized = None
            
        logger.removeHandler(handler)
        log_output = log_capture.getvalue()
        
        if success:
            qade_gates = len(qade_optimized.data)
            qade_2q = sum(1 for inst in qade_optimized.data if len(inst.qubits) == 2 and inst.operation.name != "barrier")
            qade_depth = qade_optimized.depth()
            
            # Analyze logs for details
            bypass_evolution = "Bypassing" in log_output or "bypassing" in log_output
            dense_fallback = "[Placement Fallback] Dense circuit detected" in log_output or "Dense circuit detected" in log_output
            gate_guard_triggered = "Falling back to routed input" in log_output or "Falling back" in log_output or "did not reduce gates" in log_output
            
            # Determine active qubits
            active_qs = set()
            for inst in qade_optimized.data:
                if inst.operation.name not in ("measure", "barrier"):
                    for q in inst.qubits:
                        active_qs.add(qade_optimized.find_bit(q).index)
            num_active = len(active_qs)
            
            results[name] = {
                "success": True,
                "qiskit_l3": {
                    "gates": qiskit_gates,
                    "gates_2q": qiskit_2q,
                    "depth": qiskit_depth,
                    "time_s": t_qiskit
                },
                "qade": {
                    "gates": qade_gates,
                    "gates_2q": qade_2q,
                    "depth": qade_depth,
                    "time_s": t_qade
                },
                "active_qubits": num_active,
                "bypass_evolution": bypass_evolution,
                "dense_fallback": dense_fallback,
                "gate_guard_triggered": gate_guard_triggered,
                "log": log_output
            }
            
            # Print summary of comparison
            print(f"  Qiskit L3: {qiskit_gates} gates (2Q: {qiskit_2q}), depth={qiskit_depth}, time={t_qiskit:.2f}s")
            print(f"  QADE     : {qade_gates} gates (2Q: {qade_2q}), depth={qade_depth}, time={t_qade:.2f}s")
            print(f"  Active Qubits: {num_active} | Bypass Evolution: {bypass_evolution} | Dense Fallback: {dense_fallback} | Gate Guard: {gate_guard_triggered}")
        else:
            results[name] = {
                "success": False,
                "time_s": t_qade,
                "error": str(sys.exc_info()[1])
            }
            
    # Save validation results to JSON
    out_path = Path(__file__).resolve().parent / "results" / "scale_validation_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved scaling results to {out_path}")
    
    # Generate Markdown Table for terminal stdout
    print("\n" + "=" * 60)
    print("SCALE VALIDATION RESULTS SUMMARY TABLE")
    print("=" * 60)
    print("| Circuit | Active Qubits | Qiskit L3 2Q (Total) | QADE 2Q (Total) | Bypass Evolution? | Dense Fallback? | Gate Guard? | QADE Time |")
    print("|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    for name, r in results.items():
        if r["success"]:
            q_3 = f"{r['qiskit_l3']['gates_2q']} ({r['qiskit_l3']['gates']})"
            qade_g = f"{r['qade']['gates_2q']} ({r['qade']['gates']})"
            bypass = "YES" if r["bypass_evolution"] else "NO"
            dense = "YES" if r["dense_fallback"] else "NO"
            guard = "YES" if r["gate_guard_triggered"] else "NO"
            t_q = f"{r['qade']['time_s']:.2f}s"
            print(f"| {name} | {r['active_qubits']} | {q_3} | {qade_g} | {bypass} | {dense} | {guard} | {t_q} |")
        else:
            print(f"| {name} | FAILED | N/A | N/A | N/A | N/A | N/A | {r['time_s']:.2f}s |")

if __name__ == "__main__":
    run_suite()
