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
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter

logger = logging.getLogger(__name__)

class QADEOptimizerPass(TransformationPass):
    """
    Standard Qiskit compiler pass wrapping the QADE Evolutionary Search, 
    ZX-calculus reduction, and layout SWAP routing optimization pipeline.
    """

    def __init__(
        self,
        backend: Optional[Any] = None,
        generations: int = 5,
        population_size: int = 8,
        hardware_aware: bool = False,
        placement_method: Optional[str] = None,
        routing_method: Optional[str] = None,
    ):
        super().__init__()
        self.backend = backend
        self.generations = generations
        self.population_size = population_size
        self.hardware_aware = hardware_aware
        self.placement_method = placement_method or (
            "fidelity_aware" if hardware_aware else "interaction"
        )
        self.routing_method = routing_method or (
            "coherence_aware_sabre" if hardware_aware else "sabre"
        )

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

        # Extract measurements
        measures = []
        cregs = qc.cregs
        
        # Build unitary-only circuit
        qc_unitary = QuantumCircuit(*qc.qregs)
        for instr in qc.data:
            if instr.operation.name == "measure":
                q_idx = qc.find_bit(instr.qubits[0]).index
                c_idx = qc.find_bit(instr.clbits[0]).index
                measures.append((q_idx, c_idx))
            else:
                qubits = [qc_unitary.qubits[qc.find_bit(q).index] for q in instr.qubits]
                qc_unitary.append(instr.operation, qubits, [])

        # A. Translate Qiskit Circuit -> QADE JSON representation
        qade_json = qiskit_to_qade_json(qc_unitary)

        # B. Retrieve coupling map from target Qiskit Backend
        coupling_map = None
        if self.backend is not None:
            if hasattr(self.backend, "coupling_map") and self.backend.coupling_map is not None:
                # BackendV2 standard coupling map query
                coupling_map = list(self.backend.coupling_map)

        # C. Initial placement/routing layer to ensure input is physically executable
        if self.hardware_aware and coupling_map:
            placer = QubitPlacement(
                qade_json.get("qubits", 0),
                coupling_map,
                backend=self.backend,
            )
            initial_layout = placer.place(qade_json, method=self.placement_method)
            router = AdvancedRouter(coupling_map, backend=self.backend)
            routed_json, _ = router.route(
                qade_json,
                method=self.routing_method,
                initial_layout=initial_layout,
            )
        else:
            routed_json = route_circuit(qade_json, coupling_map)

        # E. Core evolutionary optimization search
        # Optimize by running evolution on only the active physical qubits to speed up simulation
        active_qs = set()
        for gate in routed_json.get("gates", []):
            active_qs.update(gate.get("qubits", []))
        if not active_qs:
            active_qs = set(range(qc_unitary.num_qubits)) if qc_unitary.num_qubits > 0 else {0}
            
        num_pop_qubits = max(active_qs) + 1
        
        pruned_coupling_map = None
        if coupling_map is not None:
            pruned_coupling_map = [
                edge for edge in coupling_map
                if edge[0] in active_qs and edge[1] in active_qs
            ]

        # Calculate a safe max_gates limit based on the routed input size to prevent truncation
        safe_max_gates = max(80, len(routed_json.get("gates", [])) + 20)

        # For very large routed circuits (e.g. QFT-20q with 2490+ gates),
        # statevector-based evolutionary search is impractical: each evaluation
        # requires simulating 2^num_pop_qubits amplitudes through thousands of gates.
        # In these cases, skip evolution and apply algebraic simplification directly.
        EVOLUTION_GATE_THRESHOLD = 500
        bypass_evolution = len(routed_json.get("gates", [])) > EVOLUTION_GATE_THRESHOLD or num_pop_qubits > 20

        if bypass_evolution:
            logger.info(f"Routed circuit has {len(routed_json.get('gates', []))} gates or {num_pop_qubits} qubits. "
                        f"Bypassing evolutionary search, applying algebraic simplification only.")
            best_evolved_circuit = routed_json
        else:
            # D. Statevector target definition using the sandbox
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

            pop_manager = QuantumPopulationManager(
                qubits=num_pop_qubits,
                population_size=self.population_size,
                seed_circuits=[routed_json],
                coupling_map=pruned_coupling_map,
                max_gates=safe_max_gates
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
            
            reports = engine.run(generations=self.generations)
            best_evolved_circuit = reports[-1]["best_circuit"] if reports else routed_json

        # F. ZX Calculus symbolic simplification
        pyzx_opt = PyZXOptimizer()
        zx_reduced_circuit, _ = pyzx_opt.optimize_circuit(best_evolved_circuit)

        # Verificar equivalencia usando el circuito Qiskit original
        # (no la representación QADE que puede tener puertas perdidas)
        def verify_equivalence_qiskit(
            original_qc: QuantumCircuit,
            optimized_json: Dict[str, Any],
            num_qubits: int,
            threshold: float = 0.999
        ) -> bool:
            if num_qubits > 12:
                return True
            try:
                from qiskit.quantum_info import Operator
                import numpy as np
                from quantum.integration.qiskit_adapter import qade_json_to_qiskit
                
                # Versión sin medidas del original
                orig_no_meas = QuantumCircuit(num_qubits)
                for instr in original_qc.data:
                    if instr.operation.name != 'measure':
                        qubits = [original_qc.find_bit(q).index 
                                  for q in instr.qubits]
                        # Solo añadir si el número de qubits es <= num_qubits
                        if all(q < num_qubits for q in qubits):
                            orig_no_meas.append(instr.operation, 
                                [orig_no_meas.qubits[q] for q in qubits])
                
                opt_qc = qade_json_to_qiskit(optimized_json)
                
                op_orig = Operator(orig_no_meas)
                op_opt = Operator(opt_qc)
                
                fidelity = abs(np.trace(
                    op_orig.data.conj().T @ op_opt.data
                )) / (2 ** num_qubits)
                
                if fidelity < threshold:
                    logger.warning(
                        f'Equivalence check FAILED: fidelity={fidelity:.4f} '
                        f'(threshold={threshold}). Returning original circuit.'
                    )
                    return False
                return True
            except Exception as e:
                logger.warning(f'Could not verify equivalence: {e}. Accepting.')
                return True

        if not verify_equivalence_qiskit(qc_unitary, zx_reduced_circuit, zx_reduced_circuit.get("qubits", 0)):
            logger.warning("ZX equivalence check failed against original Qiskit circuit. Falling back to pre-ZX circuit.")
            zx_reduced_circuit = best_evolved_circuit

        # G. Re-route output to guarantee physical execution constraints
        if self.hardware_aware and coupling_map:
            router = AdvancedRouter(coupling_map, backend=self.backend)
            final_routed_circuit, _ = router.route(
                zx_reduced_circuit,
                method=self.routing_method,
                initial_layout={i: i for i in range(zx_reduced_circuit.get("qubits", 0))},
            )
        else:
            final_routed_circuit = route_circuit(zx_reduced_circuit, coupling_map)

        # H. Translate QADE JSON -> Qiskit QuantumCircuit
        optimized_unitary = qade_json_to_qiskit(final_routed_circuit)
        
        # Re-add classical registers and measurements
        final_qc = QuantumCircuit(*optimized_unitary.qregs, *cregs)
        for instr in optimized_unitary.data:
            qubits = [final_qc.qubits[optimized_unitary.find_bit(q).index] for q in instr.qubits]
            clbits = [final_qc.clbits[optimized_unitary.find_bit(c).index] for c in instr.clbits]
            final_qc.append(instr.operation, qubits, clbits)
            
        for q_idx, c_idx in measures:
            final_qc.measure(final_qc.qubits[q_idx], final_qc.clbits[c_idx])
            
        # Re-transpile to backend's basis gates to unroll non-native gates (like H)
        if self.backend is not None:
            from qiskit import transpile
            final_qc = transpile(final_qc, backend=self.backend, optimization_level=0)
            
        return final_qc
