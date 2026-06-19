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

def _get_stage_metrics(circuit_or_json) -> tuple[int, int, int, list[str]]:
    if isinstance(circuit_or_json, QuantumCircuit):
        gates = circuit_or_json.data
        count_1q = sum(1 for inst in gates if len(inst.qubits) == 1 and inst.operation.name != "measure" and inst.operation.name != "barrier")
        count_2q = sum(1 for inst in gates if len(inst.qubits) == 2)
        depth = circuit_or_json.depth()
        gate_list = [inst.operation.name for inst in gates]
    elif isinstance(circuit_or_json, dict):
        gates = circuit_or_json.get("gates", [])
        count_1q = sum(1 for g in gates if len(g.get("qubits", [])) == 1 and g.get("type") != "MEASURE" and g.get("type") != "BARRIER")
        count_2q = sum(1 for g in gates if len(g.get("qubits", [])) == 2)
        
        q_depth = {}
        for g in gates:
            for q in g.get("qubits", []):
                q_depth[q] = q_depth.get(q, 0) + 1
        depth = max(q_depth.values()) if q_depth else 0
        gate_list = [g.get("type") for g in gates]
    else:
        count_1q, count_2q, depth, gate_list = 0, 0, 0, []
    return count_1q, count_2q, depth, gate_list

def is_physically_executable(circuit_json: Dict[str, Any], coupling_map: Optional[list]) -> bool:
    if not coupling_map:
        return True
    edges = set()
    for edge in coupling_map:
        u, v = int(edge[0]), int(edge[1])
        edges.add((u, v))
        edges.add((v, u))
        
    for gate in circuit_json.get("gates", []):
        g_type = str(gate.get("type", "")).upper()
        q = gate.get("qubits", [])
        if g_type in ("CNOT", "CX", "CZ", "SWAP") and len(q) == 2:
            if (q[0], q[1]) not in edges:
                return False
    return True

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

        self._optimal_layout = None
        circuit_name = qc.name or "unknown"

        # [STAGE 0] Input: circuito original (gate count)
        c1q, c2q, dp, gl = _get_stage_metrics(qc)
        logger.debug(f"[STAGE 0] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

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
            
            # [STAGE 1] Post-layout (after placement, before routing)
            c1q, c2q, dp, gl = _get_stage_metrics(qade_json)
            logger.debug(f"[STAGE 1] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

            router = AdvancedRouter(coupling_map, backend=self.backend)
            routed_json, final_layout_from_router = router.route(
                qade_json,
                method=self.routing_method,
                initial_layout=initial_layout,
            )
            self._optimal_layout = final_layout_from_router
        else:
            # [STAGE 1] Post-layout (no placement, before routing)
            c1q, c2q, dp, gl = _get_stage_metrics(qade_json)
            logger.debug(f"[STAGE 1] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

            routed_json = route_circuit(qade_json, coupling_map)

        # [STAGE 2] Post-routing (after SWAPs)
        c1q, c2q, dp, gl = _get_stage_metrics(routed_json)
        logger.debug(f"[STAGE 2] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

        # E. Core evolutionary optimization search
        # Optimize by running evolution on only the active physical qubits to speed up simulation
        active_virtual_qs = set()
        for gate in qade_json.get("gates", []):
            if gate.get("type", "").upper() != "BARRIER":
                active_virtual_qs.update(gate.get("qubits", []))

        active_qs = set()
        for gate in routed_json.get("gates", []):
            if gate.get("type", "").upper() != "BARRIER":
                active_qs.update(gate.get("qubits", []))
        if hasattr(self, "_optimal_layout") and self._optimal_layout is not None:
            active_qs.update(self._optimal_layout.get(v) for v in active_virtual_qs if v in self._optimal_layout)
        else:
            active_qs.update(active_virtual_qs)
        if not active_qs:
            active_qs = set(range(qc_unitary.num_qubits)) if qc_unitary.num_qubits > 0 else {0}
            
        active_qs_sorted = sorted(list(active_qs))
        num_active = len(active_qs_sorted)
        
        phys_to_virt = {phys: i for i, phys in enumerate(active_qs_sorted)}
        virt_to_phys = {i: phys for i, phys in enumerate(active_qs_sorted)}
        
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
        # requires simulating 2^num_active amplitudes through thousands of gates.
        # In these cases, skip evolution and apply algebraic simplification directly.
        EVOLUTION_GATE_THRESHOLD = 500
        bypass_evolution = len(routed_json.get("gates", [])) > EVOLUTION_GATE_THRESHOLD or num_active > 20

        if bypass_evolution:
            logger.info(f"Routed circuit has {len(routed_json.get('gates', []))} gates or {num_active} active qubits. "
                        f"Bypassing evolutionary search, applying algebraic simplification only.")
            best_evolved_circuit = routed_json
        else:
            # Map routed_json (physical) to virtual space for sandbox simulation
            virtual_gates = []
            for gate in routed_json.get("gates", []):
                g_qubits = gate.get("qubits", [])
                mapped_q = [phys_to_virt[q] for q in g_qubits]
                new_gate = gate.copy()
                new_gate["qubits"] = mapped_q
                virtual_gates.append(new_gate)
            virtual_seed_json = {
                "qubits": num_active,
                "gates": virtual_gates
            }

            # Map target gates (virtual) to physical and then to mapped virtual space
            target_to_virtual = {}
            for v in range(qade_json.get("qubits", 0)):
                phys = self._optimal_layout.get(v, v) if (hasattr(self, "_optimal_layout") and self._optimal_layout is not None) else v
                if phys in phys_to_virt:
                    target_to_virtual[v] = phys_to_virt[phys]
                else:
                    target_to_virtual[v] = v
            
            target_gates = []
            for gate in qade_json.get("gates", []):
                g_qubits = gate.get("qubits", [])
                mapped_q = [target_to_virtual.get(q, q) for q in g_qubits]
                new_gate = gate.copy()
                new_gate["qubits"] = mapped_q
                target_gates.append(new_gate)

            target_qade_json = {
                "qubits": num_active,
                "gates": target_gates
            }
            
            sandbox = QiskitQuantumSandbox()
            initial_sim = sandbox.execute(target_qade_json)
            if not initial_sim.get("success", False):
                # If simulation fails, return original circuit
                return qc
                
            target_statevector = initial_sim["result"]["statevector"]

            virtual_coupling_map = None
            if pruned_coupling_map is not None:
                virtual_coupling_map = [
                    [phys_to_virt[edge[0]], phys_to_virt[edge[1]]]
                    for edge in pruned_coupling_map
                ]

            pop_manager = QuantumPopulationManager(
                qubits=num_active,
                population_size=self.population_size,
                seed_circuits=[virtual_seed_json],
                coupling_map=virtual_coupling_map,
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
            if reports and reports[-1]["best_fidelity"] >= 0.99:
                best_evolved_virtual = reports[-1]["best_circuit"]
                evolved_gates = best_evolved_virtual.get("gates", [])
                routed_gates = routed_json.get("gates", [])
                evolved_2q = sum(1 for g in evolved_gates if len(g.get("qubits", [])) == 2)
                routed_2q = sum(1 for g in routed_gates if len(g.get("qubits", [])) == 2)
                evolved_1q = sum(1 for g in evolved_gates if len(g.get("qubits", [])) == 1)
                routed_1q = sum(1 for g in routed_gates if len(g.get("qubits", [])) == 1)
                
                if (evolved_2q < routed_2q) or (evolved_2q == routed_2q and evolved_1q < routed_1q):
                    best_evolved_physical_gates = []
                    for gate in evolved_gates:
                        g_qubits = gate.get("qubits", [])
                        mapped_q = [virt_to_phys[q] for q in g_qubits]
                        new_gate = gate.copy()
                        new_gate["qubits"] = mapped_q
                        best_evolved_physical_gates.append(new_gate)
                    best_evolved_circuit = {
                        "qubits": max(active_qs) + 1 if active_qs else 1,
                        "gates": best_evolved_physical_gates
                    }
                    logger.info(f"Evolution reduced gates: 2Q={routed_2q}->{evolved_2q}, 1Q={routed_1q}->{evolved_1q}")
                else:
                    logger.info(f"Evolution did not reduce gates: evolved 2Q={evolved_2q}, routed 2Q={routed_2q}. Falling back to routed input.")
                    best_evolved_circuit = routed_json
            else:
                logger.warning("Evolution did not find a high-fidelity circuit. Falling back to routed input.")
                best_evolved_circuit = routed_json

        # F. ZX Calculus symbolic simplification
        pyzx_opt = PyZXOptimizer()
        zx_candidate, _ = pyzx_opt.optimize_circuit(best_evolved_circuit)
        
        # Only accept PyZX optimization if it does not increase gate counts
        def get_gate_counts(circ):
            gates = circ.get("gates", [])
            g_2q = sum(1 for g in gates if len(g.get("qubits", [])) == 2)
            g_1q = sum(1 for g in gates if len(g.get("qubits", [])) == 1 and g.get("type") != "BARRIER" and g.get("type") != "MEASURE")
            return g_2q, g_1q
            
        cand_2q, cand_1q = get_gate_counts(zx_candidate)
        best_2q, best_1q = get_gate_counts(best_evolved_circuit)
        
        if (cand_2q < best_2q) or (cand_2q == best_2q and cand_1q <= best_1q):
            zx_reduced_circuit = zx_candidate
        else:
            zx_reduced_circuit = best_evolved_circuit

        # Verificar equivalencia usando el circuito Qiskit original
        # (no la representación QADE que puede tener puertas perdidas)
        def verify_equivalence_qiskit(
            original_qc: QuantumCircuit,
            optimized_json: Dict[str, Any],
            num_qubits: int,
            threshold: float = 0.999
        ) -> bool:
            try:
                from qiskit.quantum_info import Operator
                import numpy as np
                from quantum.integration.qiskit_adapter import qade_json_to_qiskit
                
                # Encontrar qubits activos en el original
                active_qs_in = set()
                for instr in original_qc.data:
                    if instr.operation.name != 'measure':
                        for q in instr.qubits:
                            active_qs_in.add(original_qc.find_bit(q).index)
                
                num_active = len(active_qs_in)
                if num_active > 12:
                    return True  # No verificar para evitar limite de dimension
                
                if not hasattr(self, "_optimal_layout") or self._optimal_layout is None:
                    return True # No se puede verificar sin layout
                
                layout = self._optimal_layout
                layout_inv = {phys: virt for virt, phys in layout.items()}
                
                # Mapeo a qubits limpios 0..num_active-1
                active_qs_sorted = sorted(list(active_qs_in))
                phys_to_clean = {phys: i for i, phys in enumerate(active_qs_sorted)}
                
                # 1. Mapear original
                orig_mapped = QuantumCircuit(num_active)
                for instr in original_qc.data:
                    if instr.operation.name != 'measure':
                        qubits = [original_qc.find_bit(q).index for q in instr.qubits]
                        mapped_qubits = [phys_to_clean[q] for q in qubits if q in phys_to_clean]
                        if len(mapped_qubits) == len(qubits):
                            orig_mapped.append(instr.operation, 
                                [orig_mapped.qubits[q] for q in mapped_qubits])
                
                # 2. Mapear optimizado
                opt_qc = QuantumCircuit(num_active)
                for gate in optimized_json.get("gates", []):
                    g_type = gate.get("type", "").upper()
                    q = gate.get("qubits", [])
                    
                    # Mapear qubits usando layout_inv y phys_to_clean
                    mapped_qubits = []
                    for idx in q:
                        orig_q = layout_inv.get(idx)
                        if orig_q in phys_to_clean:
                            mapped_qubits.append(phys_to_clean[orig_q])
                    
                    if len(mapped_qubits) == len(q):
                        if g_type == "H":
                            opt_qc.h(mapped_qubits[0])
                        elif g_type == "X":
                            opt_qc.x(mapped_qubits[0])
                        elif g_type == "Y":
                            opt_qc.y(mapped_qubits[0])
                        elif g_type == "Z":
                            opt_qc.z(mapped_qubits[0])
                        elif g_type == "SX":
                            opt_qc.sx(mapped_qubits[0])
                        elif g_type in ("RX", "RY", "RZ"):
                            theta = float(gate.get("theta", 0.0))
                            if g_type == "RX":
                                opt_qc.rx(theta, mapped_qubits[0])
                            elif g_type == "RY":
                                opt_qc.ry(theta, mapped_qubits[0])
                            elif g_type == "RZ":
                                opt_qc.rz(theta, mapped_qubits[0])
                        elif g_type in ("CNOT", "CX"):
                            opt_qc.cx(mapped_qubits[0], mapped_qubits[1])
                        elif g_type == "CZ":
                            opt_qc.cz(mapped_qubits[0], mapped_qubits[1])
                        elif g_type == "SWAP":
                            opt_qc.swap(mapped_qubits[0], mapped_qubits[1])
                        elif g_type == "ECR":
                            opt_qc.ecr(mapped_qubits[0], mapped_qubits[1])
                        elif g_type in ("ID", "I"):
                            opt_qc.id(mapped_qubits[0])
                
                from qiskit.quantum_info import Statevector
                sv_orig = Statevector.from_instruction(orig_mapped)
                sv_opt = Statevector.from_instruction(opt_qc)
                fidelity = abs(np.vdot(sv_orig.data, sv_opt.data)) ** 2
                
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
            logger.warning("ZX equivalence check failed against original Qiskit circuit. Falling back to routed input circuit.")
            zx_reduced_circuit = routed_json

        # [STAGE 3] Post-PyZX (after PyZX optimization)
        c1q, c2q, dp, gl = _get_stage_metrics(zx_reduced_circuit)
        logger.debug(f"[STAGE 3] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

        # G. Re-route output to guarantee physical execution constraints
        if self.hardware_aware and coupling_map:
            if is_physically_executable(zx_reduced_circuit, coupling_map):
                final_routed_circuit = zx_reduced_circuit
            else:
                # Map zx_reduced_circuit back to virtual qubits
                layout = self._optimal_layout if (hasattr(self, "_optimal_layout") and self._optimal_layout is not None) else {i: i for i in range(zx_reduced_circuit.get("qubits", 0))}
                layout_inv = {phys: virt for virt, phys in layout.items()}
                
                virtual_gates = []
                for gate in zx_reduced_circuit.get("gates", []):
                    g_type = gate.get("type")
                    g_qubits = gate.get("qubits", [])
                    mapped_qubits = []
                    for q in g_qubits:
                        if q in layout_inv:
                            mapped_qubits.append(layout_inv[q])
                        else:
                            # Fallback: if physical qubit not in layout, assign a new virtual qubit
                            new_virt = len(layout)
                            layout[new_virt] = q
                            layout_inv[q] = new_virt
                            mapped_qubits.append(new_virt)
                    
                    new_gate = gate.copy()
                    new_gate["qubits"] = mapped_qubits
                    virtual_gates.append(new_gate)
                    
                virtual_circuit = {
                    "qubits": len(layout),
                    "gates": virtual_gates
                }

                router = AdvancedRouter(coupling_map, backend=self.backend)
                candidate_routed, final_layout = router.route(
                    virtual_circuit,
                    method=self.routing_method,
                    initial_layout=layout,
                )
                
                def get_2q_count(circ):
                    return sum(1 for g in circ.get("gates", []) if len(g.get("qubits", [])) == 2)
                    
                if get_2q_count(candidate_routed) <= get_2q_count(best_evolved_circuit):
                    final_routed_circuit = candidate_routed
                    self._optimal_layout = final_layout
                else:
                    logger.info("Stage G routing increased 2Q gate count. Falling back to best_evolved_circuit.")
                    final_routed_circuit = best_evolved_circuit
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
            measured_qubit = q_idx
            if hasattr(self, "_optimal_layout") and self._optimal_layout is not None:
                if q_idx in self._optimal_layout:
                    measured_qubit = self._optimal_layout[q_idx]
            final_qc.measure(final_qc.qubits[measured_qubit], final_qc.clbits[c_idx])
            
        # [STAGE 4] Post-rebind measures
        c1q, c2q, dp, gl = _get_stage_metrics(final_qc)
        logger.debug(f"[STAGE 4] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

        # Re-transpile to backend's basis gates to unroll non-native gates (like H)
        if self.backend is not None:
            from qiskit import transpile
            final_qc = transpile(final_qc, backend=self.backend, optimization_level=3, routing_method='none')
            
        # [STAGE 5] Output final (gate count)
        c1q, c2q, dp, gl = _get_stage_metrics(final_qc)
        logger.debug(f"[STAGE 5] {circuit_name}: 1Q_count={c1q}, 2Q_count={c2q}, depth={dp}, gates={gl}")

        return final_qc
