import os
import sys
from pathlib import Path
from qiskit_ibm_runtime import QiskitRuntimeService

# Set up paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def analyze_properties():
    token = "U35_gPZ0AXsUm-xzxlYK5yyyPJfTqmSicVmOsvtICjmr"
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend("ibm_fez")
    
    ghz_qubits = [123, 124, 136, 142, 143]
    qft_qubits = [104, 105, 106, 107, 117]
    
    print("=== IBM_FEZ PROPERTIES FOR GHZ QUBITS ===")
    for q in ghz_qubits:
        t1 = backend.qubit_properties(q).t1
        t2 = backend.qubit_properties(q).t2
        # Readout error
        readout = backend.target.readout_error_with_qubit(q) if hasattr(backend.target, 'readout_error_with_qubit') else 0.01
        print(f"Qubit {q}: T1 = {t1*1e6:.2f}us, T2 = {t2*1e6:.2f}us, Readout Error = {readout*100:.3f}%")
        
    print("\n=== IBM_FEZ PROPERTIES FOR QFT QUBITS ===")
    for q in qft_qubits:
        t1 = backend.qubit_properties(q).t1
        t2 = backend.qubit_properties(q).t2
        readout = backend.target.readout_error_with_qubit(q) if hasattr(backend.target, 'readout_error_with_qubit') else 0.01
        print(f"Qubit {q}: T1 = {t1*1e6:.2f}us, T2 = {t2*1e6:.2f}us, Readout Error = {readout*100:.3f}%")

    # Let's check CNOT/ECR gate errors on edges
    ghz_edges = [(123, 124), (124, 136), (136, 142), (142, 143)]
    print("\n=== IBM_FEZ 2Q GATE ERRORS FOR GHZ EDGES ===")
    for u, v in ghz_edges:
        # Check cx or ecr
        props = {}
        for g_name in ('cx', 'ecr', 'cz'):
            try:
                err = backend.target[g_name][(u, v)].error
                print(f"Edge ({u}, {v}) {g_name.upper()} Error: {err*100:.3f}%")
            except Exception:
                try:
                    err = backend.target[g_name][(v, u)].error
                    print(f"Edge ({v}, {u}) {g_name.upper()} Error: {err*100:.3f}%")
                except Exception:
                    pass

if __name__ == "__main__":
    analyze_properties()
