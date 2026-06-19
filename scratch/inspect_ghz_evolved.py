import sys
import logging
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
import numpy as np
from quantum.optimization.calibration_model import get_fake_backend
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit

logging.basicConfig(level=logging.INFO)
backend = get_fake_backend("FakeFez")

qc = QuantumCircuit(5)
qc.h(0)
for i in range(4):
    qc.cx(i, i+1)
qc.name = "GHZ_5q"
qc.measure_all()

# Transpiled input
transpiled_in = transpile(qc, backend=backend, optimization_level=1)

qade_pass = QADEOptimizerPass(backend=backend, hardware_aware=True)
qade_pass.generations = 5
qade_pass.population_size = 8

# Let's run a custom version of optimize_circuit that prints the mapped gates
qc_unitary = QuantumCircuit(*transpiled_in.qregs)
for instr in transpiled_in.data:
    if instr.operation.name != "measure":
        qubits = [qc_unitary.qubits[transpiled_in.find_bit(q).index] for q in instr.qubits]
        qc_unitary.append(instr.operation, qubits, [])

# Convert to JSON and route
qade_json = qiskit_to_qade_json(qc_unitary)
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter
placer = QubitPlacement(qade_json.get("qubits", 0), list(backend.coupling_map), backend=backend)
initial_layout = placer.place(qade_json, method="fidelity_aware")
router = AdvancedRouter(list(backend.coupling_map), backend=backend)
routed_json, final_layout = router.route(qade_json, method="sabre", initial_layout=initial_layout)

# Seed and evolve
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic

active_qs = set()
for gate in routed_json.get("gates", []):
    active_qs.update(gate.get("qubits", []))
num_pop_qubits = max(active_qs) + 1

target_qade_json = {
    "qubits": num_pop_qubits,
    "gates": qade_json.get("gates", [])
}
sandbox = QiskitQuantumSandbox()
initial_sim = sandbox.execute(target_qade_json)
target_statevector = initial_sim["result"]["statevector"]

pruned_coupling_map = [
    edge for edge in backend.coupling_map
    if edge[0] in active_qs and edge[1] in active_qs
]

pop_manager = QuantumPopulationManager(
    qubits=num_pop_qubits,
    population_size=8,
    seed_circuits=[routed_json],
    coupling_map=pruned_coupling_map,
    max_gates=80
)
critic = QuantumCritic(alpha=0.01, beta=0.001, apply_low_fidelity_penalty=True)
engine = EvolutionEngine(
    population_manager=pop_manager,
    sandbox=sandbox,
    critic=critic,
    target_state=target_statevector,
    elitism=1,
    selection_fraction=0.5
)
reports = engine.run(generations=5)
best_evolved = reports[-1]["best_circuit"]

# Print the evolved circuit gates
print("\n--- Evolved gates (QADE JSON) ---")
for g in best_evolved.get("gates", []):
    print(g)

# Map original and optimized
active_qs_in = set()
for instr in qc_unitary.data:
    for q in instr.qubits:
        active_qs_in.add(qc_unitary.find_bit(q).index)

num_active = len(active_qs_in)
layout = final_layout
layout_inv = {phys: virt for virt, phys in layout.items()}
active_qs_sorted = sorted(list(active_qs_in))
phys_to_clean = {phys: i for i, phys in enumerate(active_qs_sorted)}

# 1. Map original
orig_mapped = QuantumCircuit(num_active)
for instr in qc_unitary.data:
    qubits = [qc_unitary.find_bit(q).index for q in instr.qubits]
    mapped_qubits = [phys_to_clean[q] for q in qubits if q in phys_to_clean]
    if len(mapped_qubits) == len(qubits):
        orig_mapped.append(instr.operation, [orig_mapped.qubits[q] for q in mapped_qubits])

print("\n--- orig_mapped gates ---")
for inst in orig_mapped.data:
    print(inst.operation.name, [orig_mapped.find_bit(q).index for q in inst.qubits])

print("layout:", layout)
print("layout_inv:", layout_inv)
print("phys_to_clean:", phys_to_clean)

# 2. Map optimized
opt_qc = QuantumCircuit(num_active)
for gate in best_evolved.get("gates", []):
    g_type = gate.get("type", "").upper()
    q = gate.get("qubits", [])
    mapped_qubits = []
    for idx in q:
        orig_q = layout_inv.get(idx)
        if orig_q in phys_to_clean:
            mapped_qubits.append(phys_to_clean[orig_q])
    print(f"Gate {g_type} on physical {q} -> mapped to clean {mapped_qubits}")
    if len(mapped_qubits) == len(q):
        if g_type == "H":
            opt_qc.h(mapped_qubits[0])
        elif g_type == "X":
            opt_qc.x(mapped_qubits[0])
        elif g_type in ("CNOT", "CX"):
            opt_qc.cx(mapped_qubits[0], mapped_qubits[1])
        elif g_type == "CZ":
            opt_qc.cz(mapped_qubits[0], mapped_qubits[1])
        elif g_type == "SWAP":
            opt_qc.swap(mapped_qubits[0], mapped_qubits[1])

print("\n--- opt_qc gates ---")
for inst in opt_qc.data:
    print(inst.operation.name, [opt_qc.find_bit(q).index for q in inst.qubits])

# Compute statevector fidelity
from qiskit.quantum_info import Statevector
sv_orig = Statevector.from_instruction(orig_mapped)
sv_opt = Statevector.from_instruction(opt_qc)
fidelity = abs(np.vdot(sv_orig.data, sv_opt.data)) ** 2
print("\nStatevector Fidelity:", fidelity)
