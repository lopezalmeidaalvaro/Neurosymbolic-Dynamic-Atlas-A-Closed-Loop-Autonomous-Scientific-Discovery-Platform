import os
import sys
import csv
import logging
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.circuit.library import QFT

# Set up paths
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.optimization.calibration_model import get_fake_backend
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.optimization.hardware_cost_model_v2 import predict_hellinger_fidelity

def configure_logging():
    # Configure quantum logger specifically to avoid Qiskit's verbosity
    quantum_logger = logging.getLogger("quantum")
    quantum_logger.setLevel(logging.DEBUG)
    quantum_logger.propagate = False
    
    # Clean formatter to only print the message itself in the log file
    file_handler = logging.FileHandler('gate_overhead_debug.log', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(file_formatter)
    quantum_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    quantum_logger.addHandler(console_handler)

def make_ghz(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i+1)
    return qc

def make_quantum_kernel(num_qubits: int) -> QuantumCircuit:
    qk = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qk.h(i)
        qk.rz(0.5, i)
    for i in range(num_qubits - 1):
        qk.cx(i, i+1)
        qk.rz(0.3, i+1)
    for i in range(num_qubits):
        qk.h(i)
        qk.rz(0.5, i)
    for i in range(num_qubits - 1):
        qk.cx(i, i+1)
    return qk

def make_qft(num_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits)
    qc.compose(QFT(num_qubits), inplace=True)
    return qc

def make_vqe(num_qubits: int) -> QuantumCircuit:
    vqe = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        vqe.ry(0.3 * i, i)
    for i in range(num_qubits - 1):
        vqe.cx(i, i+1)
    for i in range(num_qubits):
        vqe.ry(0.2 * i, i)
    return vqe

def get_1q_2q_counts(qc: QuantumCircuit) -> tuple[int, int]:
    count_1q = 0
    count_2q = 0
    for instr in qc.data:
        op_name = instr.operation.name
        if op_name in ("measure", "barrier"):
            continue
        num_q = len(instr.qubits)
        if num_q == 1:
            count_1q += 1
        elif num_q == 2:
            count_2q += 1
    return count_1q, count_2q

def run_diagnostics():
    configure_logging()
    
    backend = get_fake_backend("FakeFez")
    
    circuits_to_test = [
        ("GHZ_5q", make_ghz(5)),
        ("QFT_5q", make_qft(5)),
        ("Quantum_Kernel_5q", make_quantum_kernel(5)),
        ("Quantum_Kernel_8q", make_quantum_kernel(8)),
        ("VQE_5q", make_vqe(5)),
    ]
    
    csv_rows = []
    
    print("\n" + "="*80)
    print(f"GATE OVERHEAD DIAGNOSTIC RUN - Target Backend: {backend.name}")
    print("="*80)
    
    for name, qc in circuits_to_test:
        qc.name = name
        
        print(f"\nProcessing circuit: {name} ...")
        
        # 1. Compile with Qiskit L3
        qiskit_base = qc.copy()
        qiskit_base.measure_all()
        qiskit_compiled = transpile(qiskit_base, backend=backend, optimization_level=3)
        
        # 2. Compile with QADE
        qade_input = qc.copy()
        qade_input.measure_all()
        transpiled_in = transpile(qade_input, backend=backend, optimization_level=1)
        
        qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm = PassManager(qade_pass)
        qade_compiled = pm.run(transpiled_in)
        
        # 3. Compile with QADE (L3 input)
        qade_l3_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
        pm_l3 = PassManager(qade_l3_pass)
        qade_l3_compiled = pm_l3.run(qiskit_compiled)
        
        # Gate counts
        qiskit_1q, qiskit_2q = get_1q_2q_counts(qiskit_compiled)
        qade_1q, qade_2q = get_1q_2q_counts(qade_compiled)
        qade_l3_1q, qade_l3_2q = get_1q_2q_counts(qade_l3_compiled)
        
        qiskit_depth = qiskit_compiled.depth()
        qade_depth = qade_compiled.depth()
        qade_l3_depth = qade_l3_compiled.depth()
        
        qiskit_fid = predict_hellinger_fidelity(qiskit_compiled, backend)
        qade_fid = predict_hellinger_fidelity(qade_compiled, backend)
        qade_l3_fid = predict_hellinger_fidelity(qade_l3_compiled, backend)
        
        delta_1q = qade_1q - qiskit_1q
        delta_2q = qade_2q - qiskit_2q
        delta_l3_1q = qade_l3_1q - qiskit_1q
        delta_l3_2q = qade_l3_2q - qiskit_2q
        
        csv_rows.append({
            "circuit_name": name,
            "qiskit_1q_count": qiskit_1q,
            "qade_1q_count": qade_1q,
            "qade_l3_1q_count": qade_l3_1q,
            "delta_1q": delta_1q,
            "delta_l3_1q": delta_l3_1q,
            "qiskit_2q_count": qiskit_2q,
            "qade_2q_count": qade_2q,
            "qade_l3_2q_count": qade_l3_2q,
            "delta_2q": delta_2q,
            "delta_l3_2q": delta_l3_2q,
            "qiskit_total_depth": qiskit_depth,
            "qade_total_depth": qade_depth,
            "qade_l3_total_depth": qade_l3_depth,
            "qiskit_fidelity": round(qiskit_fid, 6),
            "qade_fidelity": round(qade_fid, 6),
            "qade_l3_fidelity": round(qade_l3_fid, 6),
        })
        
        # Print side-by-side comparison of gates by type
        qiskit_ops = qiskit_compiled.count_ops()
        qade_ops = qade_compiled.count_ops()
        qade_l3_ops = qade_l3_compiled.count_ops()
        all_keys = sorted(list(set(qiskit_ops.keys()) | set(qade_ops.keys()) | set(qade_l3_ops.keys())))
        
        print(f"Gate count breakdown by type for {name}:")
        print(f"{'Gate Type':<15} | {'Qiskit L3':<10} | {'QADE (L1)':<10} | {'QADE (L3)':<10} | {'Delta L1':<10} | {'Delta L3':<10}")
        print("-" * 79)
        for k in all_keys:
            qis_val = qiskit_ops.get(k, 0)
            qad_val = qade_ops.get(k, 0)
            qad_l3_val = qade_l3_ops.get(k, 0)
            diff_l1 = qad_val - qis_val
            diff_l3 = qad_l3_val - qis_val
            print(f"{k:<15} | {qis_val:<10} | {qad_val:<10} | {qad_l3_val:<10} | {diff_l1:<+10} | {diff_l3:<+10}")
            
    # Write to CSV
    csv_fields = [
        "circuit_name", "qiskit_1q_count", "qade_1q_count", "qade_l3_1q_count", "delta_1q", "delta_l3_1q",
        "qiskit_2q_count", "qade_2q_count", "qade_l3_2q_count", "delta_2q", "delta_l3_2q",
        "qiskit_total_depth", "qade_total_depth", "qade_l3_total_depth",
        "qiskit_fidelity", "qade_fidelity", "qade_l3_fidelity"
    ]
    csv_path = "gate_overhead_debug_results_v2.csv"
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"\nCSV exported to {csv_path}")
    print("\n" + "="*110)
    print("COMPILATION SUMMARY TABLE:")
    print("="*110)
    print(f"{'Circuit':<20} | {'1Q (Qis/QA1/QA3)':<20} | {'2Q (Qis/QA1/QA3)':<20} | {'Depth (Qis/QA1/QA3)':<20} | {'Fidelity (Qis/QA1/QA3)':<25}")
    print("-" * 115)
    for r in csv_rows:
        q1 = f"{r['qiskit_1q_count']}/{r['qade_1q_count']}/{r['qade_l3_1q_count']}"
        q2 = f"{r['qiskit_2q_count']}/{r['qade_2q_count']}/{r['qade_l3_2q_count']}"
        dep = f"{r['qiskit_total_depth']}/{r['qade_total_depth']}/{r['qade_l3_total_depth']}"
        fid = f"{r['qiskit_fidelity']:.4f}/{r['qade_fidelity']:.4f}/{r['qade_l3_fidelity']:.4f}"
        print(f"{r['circuit_name']:<20} | {q1:<20} | {q2:<20} | {dep:<20} | {fid:<25}")
    print("="*115)

if __name__ == "__main__":
    run_diagnostics()
