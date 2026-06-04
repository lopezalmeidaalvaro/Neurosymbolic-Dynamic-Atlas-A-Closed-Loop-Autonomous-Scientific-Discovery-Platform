import logging
from typing import Dict, Any, Optional
from qiskit.transpiler import TransformationPass
from qiskit.dagcircuit import DAGCircuit
from qiskit.converters import dag_to_circuit, circuit_to_dag
from qiskit import QuantumCircuit

from quantum.integration.qiskit_adapter import qiskit_to_qade_json, qade_json_to_qiskit
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.evolution.evolution_engine import EvolutionEngine, route_circuit
from quantum.optimization.pyzx_optimizer import PyZXOptimizer

logger = logging.getLogger(__name__)

class QADEOptimizerPass(TransformationPass):
    """
    Standard Qiskit compiler pass wrapping the QADE Evolutionary Search, 
    ZX-calculus reduction, and layout SWAP routing optimization pipeline.
    """

    def __init__(self, backend: Optional[Any] = None, generations: int = 5, population_size: int = 8):
        super().__init__()
        self.backend = backend
        self.generations = generations
        self.population_size = population_size

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        """
        Runs the QADE compiler pipeline on the input DAG representation.
        """
        # 1. Convert DAG to QuantumCircuit
        qc = dag_to_circuit(dag)
        
        # 2. Perform QADE + PyZX optimization pipeline
        try:
            optimized_qc = self.optimize_circuit(qc)
            return circuit_to_dag(optimized_qc)
        except Exception as e:
            logger.error(f"QADE optimization pass failed: {e}. Returning original circuit.")
            return dag

    def optimize_circuit(self, qc: QuantumCircuit) -> QuantumCircuit:
        # Check for zero qubits or empty circuits
        if qc.num_qubits == 0:
            return qc

        # A. Translate Qiskit Circuit -> QADE JSON representation
        qade_json = qiskit_to_qade_json(qc)

        # B. Retrieve coupling map from target Qiskit Backend
        coupling_map = None
        if self.backend is not None:
            if hasattr(self.backend, "coupling_map") and self.backend.coupling_map is not None:
                # BackendV2 standard coupling map query
                coupling_map = list(self.backend.coupling_map)

        # C. Initial SWAP routing layer to ensure input is physically executable
        routed_json = route_circuit(qade_json, coupling_map)

        # E. Core evolutionary optimization search
        num_pop_qubits = qc.num_qubits
        if coupling_map is not None and len(coupling_map) > 0:
            max_q = max(max(edge) for edge in coupling_map) + 1
            num_pop_qubits = max(num_pop_qubits, max_q)

        # D. Statevector target definition using the sandbox
        # Pad unrouted circuit to backend size to prevent statevector dimension mismatch
        target_qade_json = {
            "qubits": num_pop_qubits,
            "gates": qade_json.get("gates", [])
        }
        sandbox = QiskitQuantumSandbox()
        initial_sim = sandbox.execute(target_qade_json)
        if not initial_sim.get("success", False):
            # If simulation fails, return original circuit
            return qc
            
        target_statevector = initial_sim["result"]["statevector"]

        # Calculate a safe max_gates limit based on the routed input size to prevent truncation
        safe_max_gates = max(80, len(routed_json.get("gates", [])) + 20)

        pop_manager = QuantumPopulationManager(
            qubits=num_pop_qubits,
            population_size=self.population_size,
            seed_circuits=[routed_json],
            coupling_map=coupling_map,
            max_gates=safe_max_gates
        )
        
        critic = QuantumCritic(alpha=0.01, beta=0.001)
        engine = EvolutionEngine(
            population_manager=pop_manager,
            sandbox=sandbox,
            critic=critic,
            target_state=target_statevector,
            elitism=1,
            selection_fraction=0.5
        )
        
        reports = engine.run(generations=self.generations)
        best_evolved_circuit = reports[-1]["best_circuit"] if reports else routed_json

        # F. ZX Calculus symbolic simplification
        pyzx_opt = PyZXOptimizer()
        zx_reduced_circuit, _ = pyzx_opt.optimize_circuit(best_evolved_circuit)

        # G. Re-route output to guarantee physical execution constraints
        final_routed_circuit = route_circuit(zx_reduced_circuit, coupling_map)

        # H. Translate QADE JSON -> Qiskit QuantumCircuit
        optimized_qc = qade_json_to_qiskit(final_routed_circuit)
        
        return optimized_qc
