import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
import numpy as np
from quantum.optimization.calibration_model import get_fake_backend
from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter

logging.basicConfig(level=logging.INFO)
backend = get_fake_backend("FakeFez")
coupling_map = list(backend.coupling_map) if backend.coupling_map else None

qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i+1)
qc.name = "GHZ_5q"

transpiled_in = transpile(qc, backend=backend, optimization_level=1)
qade_json = qiskit_to_qade_json(transpiled_in)

placer = QubitPlacement(qade_json.get("qubits"), coupling_map, backend=backend)
initial_layout = placer.place(qade_json, method="fidelity_aware")

router = AdvancedRouter(coupling_map, backend=backend)
routed_json, final_layout = router.route(qade_json, method="sabre", initial_layout=initial_layout)

# Let's verify equivalence using the new mapped equivalence check
def test_verify_equivalence(original_qc, optimized_json, layout):
    # Find active qubits in original_qc
    active_qs_in = set()
    for instr in original_qc.data:
        if instr.operation.name != 'measure':
            for q in instr.qubits:
                active_qs_in.add(original_qc.find_bit(q).index)
    
    num_qubits = len(active_qs_in)
    print("Number of active qubits:", num_qubits)
    print("Active input qubits:", sorted(list(active_qs_in)))
    
    # We want to map original_qc's active qubits using layout
    orig_mapped = QuantumCircuit(num_qubits)
    for instr in original_qc.data:
        if instr.operation.name != 'measure':
            qubits = [original_qc.find_bit(q).index for q in instr.qubits]
            mapped_qubits = [layout[q] for q in qubits if q in layout]
            if len(mapped_qubits) == len(qubits) and all(q < num_qubits for q in mapped_qubits):
                orig_mapped.append(instr.operation, [orig_mapped.qubits[q] for q in mapped_qubits])
                
    # Create clean optimized circuit on num_qubits
    opt_qc = QuantumCircuit(num_qubits)
    for gate in optimized_json.get("gates", []):
        g_type = gate.get("type", "").upper()
        q = gate.get("qubits", [])
        if all(idx < num_qubits for idx in q):
            # Apply to opt_qc
            if g_type == "H":
                opt_qc.h(q[0])
            elif g_type == "X":
                opt_qc.x(q[0])
            elif g_type == "Y":
                opt_qc.y(q[0])
            elif g_type == "Z":
                opt_qc.z(q[0])
            elif g_type == "SX":
                opt_qc.sx(q[0])
            elif g_type in ("RX", "RY", "RZ"):
                theta = float(gate.get("theta", 0.0))
                if g_type == "RX":
                    opt_qc.rx(theta, q[0])
                elif g_type == "RY":
                    opt_qc.ry(theta, q[0])
                elif g_type == "RZ":
                    opt_qc.rz(theta, q[0])
            elif g_type == "CNOT":
                opt_qc.cx(q[0], q[1])
            elif g_type == "CZ":
                opt_qc.cz(q[0], q[1])
            elif g_type == "SWAP":
                opt_qc.swap(q[0], q[1])
                
    op_orig = Operator(orig_mapped)
    op_opt = Operator(opt_qc)
    
    fidelity = abs(np.trace(op_orig.data.conj().T @ op_opt.data)) / (2 ** num_qubits)
    return fidelity

fid = test_verify_equivalence(transpiled_in, routed_json, final_layout)
print("Mapped Equivalence Fidelity:", fid)
