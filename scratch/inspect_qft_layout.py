import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qiskit import QuantumCircuit, transpile
from quantum.optimization.calibration_model import get_fake_backend
from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter
from quantum.optimization.pyzx_optimizer import PyZXOptimizer

logging.basicConfig(level=logging.INFO)
backend = get_fake_backend("FakeFez")
coupling_map = list(backend.coupling_map) if backend.coupling_map else None

qc = QuantumCircuit(5)
from qiskit.circuit.library import QFT
qc.compose(QFT(5), inplace=True)
qc.name = "QFT_5q"

# Transpiled input first
transpiled_in = transpile(qc, backend=backend, optimization_level=1)
qade_json = qiskit_to_qade_json(transpiled_in)
active_in_qubits = set()
for g in qade_json.get("gates", []):
    active_in_qubits.update(g.get("qubits", []))
print("Active input qubits (Qiskit L1):", sorted(list(active_in_qubits)))

# 2. Placement
placer = QubitPlacement(qade_json.get("qubits"), coupling_map, backend=backend)
initial_layout = placer.place(qade_json, method="fidelity_aware")

# 3. Route (Stage C)
router = AdvancedRouter(coupling_map, backend=backend)
routed_json, final_layout = router.route(qade_json, method="sabre", initial_layout=initial_layout)

# 4. PyZX
pyzx_opt = PyZXOptimizer()
zx_reduced_circuit, _ = pyzx_opt.optimize_circuit(routed_json)

# 5. Route (Stage G) with Inverse Layout
inverse_layout = {phys: virt for virt, phys in final_layout.items()}
final_routed, final_layout_stage_g = router.route(zx_reduced_circuit, method="sabre", initial_layout=inverse_layout)

active_out_qubits = set()
for g in final_routed.get("gates", []):
    active_out_qubits.update(g.get("qubits", []))
print("Active output qubits (Stage G):", sorted(list(active_out_qubits)))

# Let's count how many SWAPs were added in Stage G
swaps_stage_g = sum(1 for g in final_routed.get("gates", []) if g.get("type") == "SWAP")
print("SWAPs added in Stage G:", swaps_stage_g)
