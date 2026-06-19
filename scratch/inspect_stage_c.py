import sys
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantum.optimization.calibration_model import get_fake_backend
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter

def inspect_stage_c():
    backend = get_fake_backend("FakeFez")
    
    # Build GHZ
    ghz = QuantumCircuit(5)
    ghz.h(0)
    for i in range(4):
        ghz.cx(i, i+1)
    ghz.measure_all()
    
    # Transpile level 1
    transpiled = transpile(ghz, backend=backend, optimization_level=1)
    
    # 1. Qiskit L1 layout
    active_in = sorted(list(set(transpiled.find_bit(q).index for instr in transpiled.data for q in instr.qubits if instr.operation.name != 'measure')))
    print(f"Qiskit L1 active physical qubits: {active_in}")
    
    # 2. QADE JSON
    qade_json = qiskit_to_qade_json(transpiled)
    print(f"qade_json qubits: {qade_json.get('qubits')}")
    
    # 3. Placement
    placer = QubitPlacement(qade_json.get("qubits", 0), list(backend.coupling_map), backend=backend)
    
    # Let's inspect physical scores
    qualities = {}
    max_t1 = 1e-15
    max_t2 = 1e-15
    from quantum.optimization.hardware_cost_model import get_qubit_quality
    for p in range(placer.num_physical):
        quality = get_qubit_quality(backend, p)
        quality["avg_gate_error"] = placer._physical_avg_gate_error(p)
        quality["degree"] = len(placer.adj.get(p, ()))
        qualities[p] = quality
        max_t1 = max(max_t1, quality["t1"])
        max_t2 = max(max_t2, quality["t2"])

    w1, w2, w3, w4 = 0.35, 0.35, 0.15, 0.15
    physical_scores = []
    for p, quality in qualities.items():
        score = (
            w1 * (quality["t1"] / max_t1)
            + w2 * (quality["t2"] / max_t2)
            - w3 * quality["readout_error"]
            - w4 * quality["avg_gate_error"]
            + 0.01 * quality["degree"]
        )
        physical_scores.append((p, score))
    physical_scores.sort(key=lambda item: item[1], reverse=True)
    print(f"Top 10 physical scores: {physical_scores[:10]}")
    
    initial_layout = placer.place(qade_json, method="fidelity_aware")
    
    # Filter only the mapping of active_in qubits to see where they are mapped
    active_layout = {k: v for k, v in initial_layout.items() if k in active_in}
    print(f"initial_layout (fidelity_aware) for active qubits: {active_layout}")
    
    # 4. Routing
    router = AdvancedRouter(list(backend.coupling_map), backend=backend)
    routed_json, final_layout_from_router = router.route(
        qade_json,
        method="coherence_aware_sabre",
        initial_layout=initial_layout
    )
    
    # Filter final layout
    final_active_layout = {k: v for k, v in final_layout_from_router.items() if k in active_in}
    print(f"final_layout_from_router for active qubits: {final_active_layout}")
    
    # Check physical qubits used in routed_json
    routed_active_qubits = sorted(list(set(q for g in routed_json.get("gates", []) for q in g.get("qubits", []))))
    print(f"routed_json active qubits: {routed_active_qubits}")
    
    # Is it physically executable?
    from quantum.optimization.qiskit_plugin import is_physically_executable
    executable = is_physically_executable(routed_json, list(backend.coupling_map))
    print(f"Is routed_json physically executable? {executable}")

if __name__ == "__main__":
    inspect_stage_c()
