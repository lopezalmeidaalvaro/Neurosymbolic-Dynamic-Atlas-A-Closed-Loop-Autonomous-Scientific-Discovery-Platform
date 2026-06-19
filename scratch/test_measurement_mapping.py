import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from quantum.optimization.calibration_model import get_fake_backend
from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter
from quantum.optimization.pyzx_optimizer import PyZXOptimizer

logging.basicConfig(level=logging.INFO)
backend = get_fake_backend("FakeFez")
coupling_map = list(backend.coupling_map) if backend.coupling_map else None

# Let's test with GHZ_5q first as it's simpler
qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i+1)
qc.name = "GHZ_5q"

# 1. Compile with Qiskit Level 3 to get target statevector
qiskit_base = qc.copy()
qiskit_base.measure_all()
qiskit_compiled = transpile(qiskit_base, backend=backend, optimization_level=3)

# 2. QADE manual simulation
transpiled_in = transpile(qc, backend=backend, optimization_level=1)
qade_json = qiskit_to_qade_json(transpiled_in)

placer = QubitPlacement(qade_json.get("qubits"), coupling_map, backend=backend)
initial_layout = placer.place(qade_json, method="fidelity_aware")

router = AdvancedRouter(coupling_map, backend=backend)
routed_json, final_layout = router.route(qade_json, method="sabre", initial_layout=initial_layout)

pyzx_opt = PyZXOptimizer()
zx_reduced_circuit, _ = pyzx_opt.optimize_circuit(routed_json)

# Trivial routing for Stage G
trivial_layout = {i: i for i in range(zx_reduced_circuit.get("qubits", 0))}
final_routed, final_layout_stage_g = router.route(zx_reduced_circuit, method="sabre", initial_layout=trivial_layout)

# Translate to Qiskit
optimized_unitary = qade_json_to_qiskit(final_routed)

# Re-add classical registers and measurements (with mapped measurements!)
measures = []
for instr in transpiled_in.data:
    if instr.operation.name == "measure":
        q_idx = transpiled_in.find_bit(instr.qubits[0]).index
        c_idx = transpiled_in.find_bit(instr.clbits[0]).index
        measures.append((q_idx, c_idx))

final_qc = QuantumCircuit(*optimized_unitary.qregs, *transpiled_in.cregs)
for instr in optimized_unitary.data:
    qubits = [final_qc.qubits[optimized_unitary.find_bit(q).index] for q in instr.qubits]
    clbits = [final_qc.clbits[optimized_unitary.find_bit(c).index] for c in instr.clbits]
    final_qc.append(instr.operation, qubits, clbits)

for q_idx, c_idx in measures:
    measured_qubit = final_layout[q_idx]  # Use final_layout from router
    final_qc.measure(final_qc.qubits[measured_qubit], final_qc.clbits[c_idx])

# Run final transpile at level 1
final_qc_opt = transpile(final_qc, backend=backend, optimization_level=1)

# Predict fidelity
from quantum.optimization.hardware_cost_model_v2 import predict_hellinger_fidelity
qis_fid = predict_hellinger_fidelity(qiskit_compiled, backend)
qade_fid = predict_hellinger_fidelity(final_qc_opt, backend)

print("Qiskit Fidelity:", qis_fid)
print("QADE Fidelity:", qade_fid)
print("QADE 1Q count:", len([inst for inst in final_qc_opt.data if len(inst.qubits) == 1 and inst.operation.name not in ('measure', 'barrier')]))
print("QADE 2Q count:", len([inst for inst in final_qc_opt.data if len(inst.qubits) == 2]))
