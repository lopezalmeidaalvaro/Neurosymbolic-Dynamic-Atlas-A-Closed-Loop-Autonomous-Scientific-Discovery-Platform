import sys
from pathlib import Path
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantum.optimization.qiskit_plugin import QADEOptimizerPass
from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter

def inspect_placement_real():
    token = "U35_gPZ0AXsUm-xzxlYK5yyyPJfTqmSicVmOsvtICjmr"
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend("ibm_fez")
    
    # Build GHZ
    ghz = QuantumCircuit(5)
    ghz.h(0)
    for i in range(4):
        ghz.cx(i, i+1)
    ghz.measure_all()
    
    # Transpile level 1
    transpiled = transpile(ghz, backend=backend, optimization_level=1)
    
    # Qiskit L1 layout
    active_in = sorted(list(set(transpiled.find_bit(q).index for instr in transpiled.data for q in instr.qubits if instr.operation.name != 'measure')))
    print(f"Qiskit L1 active physical qubits: {active_in}")
    
    # QADE JSON
    qade_json = qiskit_to_qade_json(transpiled)
    
    # Placement
    placer = QubitPlacement(qade_json.get("qubits", 0), list(backend.coupling_map), backend=backend)
    initial_layout = placer.place(qade_json, method="fidelity_aware")
    
    # Filter only the mapping of active_in qubits to see where they are mapped
    active_layout = {k: v for k, v in initial_layout.items() if k in active_in}
    print(f"initial_layout (fidelity_aware) for active qubits: {active_layout}")

if __name__ == "__main__":
    inspect_placement_real()
