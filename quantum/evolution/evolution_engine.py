import copy
import math
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from quantum.evolution.population_manager import Circuit, Gate, QuantumPopulationManager
from quantum.knowledge.canonicalizer import QuantumCircuitCanonicalizer
from quantum.knowledge.quantum_pattern_extractor import QuantumPatternExtractor
from quantum.knowledge.knowledge_graph import QuantumKnowledgeGraph


@dataclass(frozen=True)
class QuantumCircuitEvaluation:
    circuit: Circuit
    sandbox_result: Dict[str, Any]
    valid: bool
    fidelity: float
    score: float
    depth: int
    gate_count: int
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "circuit": copy.deepcopy(self.circuit),
            "valid": self.valid,
            "fidelity": self.fidelity,
            "score": self.score,
            "depth": self.depth,
            "gate_count": self.gate_count,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class GenerationReport:
    generation: int
    best_circuit: Circuit
    best_fidelity: float
    best_score: float
    average_population_score: float
    diversity_metric: float
    best_depth: int
    best_gate_count: int
    population_size: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "best_circuit": copy.deepcopy(self.best_circuit),
            "best_fidelity": self.best_fidelity,
            "best_score": self.best_score,
            "average_population_score": self.average_population_score,
            "diversity_metric": self.diversity_metric,
            "best_depth": self.best_depth,
            "best_gate_count": self.best_gate_count,
            "population_size": self.population_size,
        }


class EvolutionEngine:
    """
    Population-based evolutionary optimizer for quantum circuits.
    """

    def __init__(
        self,
        population_manager: QuantumPopulationManager,
        sandbox: Any,
        critic: Any,
        target_state: Any,
        memory: Optional[Any] = None,
        elitism: int = 2,
        selection_fraction: float = 0.3,
        mutation_rate: float = 0.9,
        random_injection_rate: float = 0.1,
        diversity_threshold: float = 0.25,
        pattern_injection_rate: float = 0.2,
        scaffold_injection_rate: float = 0.1,
        compatibility_threshold: float = 0.75,
    ):
        if not 0.0 < selection_fraction <= 1.0:
            raise ValueError("selection_fraction must be in (0, 1].")
        if elitism < 0:
            raise ValueError("elitism must be non-negative.")

        self.population_manager = population_manager
        self.sandbox = sandbox
        self.critic = critic
        self.target_state = target_state
        self.memory = memory
        
        # Initialize context-aware memory active context
        if self.memory is not None:
            task_name = "bell_state" if len(target_state) == 4 else "ghz_state"
            qubits = 2 if len(target_state) == 4 else 3
            from quantum.knowledge.context_schema import Context
            current_context = Context(task_name=task_name, qubit_count=qubits, converged=False)
            if hasattr(self.memory, "set_current_context"):
                self.memory.set_current_context(current_context)
                
        self.elitism = min(elitism, population_manager.population_size)
        self.selection_fraction = selection_fraction
        self.mutation_rate = mutation_rate
        self.random_injection_rate = random_injection_rate
        self.diversity_threshold = diversity_threshold
        self.pattern_injection_rate = pattern_injection_rate
        self.scaffold_injection_rate = scaffold_injection_rate
        self.compatibility_threshold = compatibility_threshold
        self.generation = 0
        self.history: List[Dict[str, Any]] = []
        self.historical_best: List[Dict[str, Any]] = []
        self.mutation_history: List[Dict[str, Any]] = []
        self.last_evaluations: List[QuantumCircuitEvaluation] = []
        self.knowledge_graph = QuantumKnowledgeGraph()
        self.discovered_patterns_archive = set()
        self.patterns_injected = 0
        self.successful_injections = 0
        self.reused_patterns = set()
        self.pending_injections_this_gen = []
        self.patterns_selected_from_memory = 0
        self.pattern_injection_attempts = 0
        self.patterns_survived = 0
        self.patterns_improved_score = 0
        self.injected_patterns_records = []
        self.last_generation_kdi = 0.0

    def evaluate_population(self) -> List[QuantumCircuitEvaluation]:
        evaluations = [
            self.evaluate_circuit(circuit)
            for circuit in self.population_manager.copy_population()
        ]
        evaluations.sort(key=lambda item: item.score, reverse=True)
        self.last_evaluations = evaluations
        return evaluations

    def evaluate_circuit(self, circuit: Circuit) -> QuantumCircuitEvaluation:
        normalized = self.population_manager.normalize_circuit(circuit)
        if not self.population_manager.is_valid_circuit(normalized):
            return QuantumCircuitEvaluation(
                circuit=normalized,
                sandbox_result={"success": False, "error": "Invalid circuit syntax."},
                valid=False,
                fidelity=0.0,
                score=float("-inf"),
                depth=0,
                gate_count=len(normalized.get("gates", [])),
                reason="Invalid circuit syntax.",
            )

        sandbox_result = self.sandbox.execute(normalized)
        verdict = self.critic.validate(sandbox_result, self.target_state)
        return QuantumCircuitEvaluation(
            circuit=normalized,
            sandbox_result=sandbox_result,
            valid=bool(self._verdict_field(verdict, "valid", False)),
            fidelity=float(self._verdict_field(verdict, "fidelity", 0.0)),
            score=float(self._verdict_field(verdict, "score", 0.0)),
            depth=int(self._verdict_field(verdict, "depth", 0)),
            gate_count=int(self._verdict_field(verdict, "gate_count", 0)),
            reason=str(self._verdict_field(verdict, "reason", "")),
        )

    def select_top_k(
        self, k: int, evaluations: Optional[List[QuantumCircuitEvaluation]] = None
    ) -> List[QuantumCircuitEvaluation]:
        evaluations = evaluations if evaluations is not None else self.last_evaluations
        if not evaluations:
            evaluations = self.evaluate_population()
        return sorted(evaluations, key=lambda item: item.score, reverse=True)[:k]

    def mutate(self, circuit: Circuit) -> Circuit:
        parent = self.population_manager.normalize_circuit(circuit)
        child = copy.deepcopy(parent)
        gates = child.setdefault("gates", [])
        gates[:] = self._simplify_gates(gates)

        injected = False
        pattern_repr = None
        pattern_id = None
        rng_state = self.population_manager.rng.getstate()

        if (
            self.memory is not None
            and self.population_manager.rng.random() < self.pattern_injection_rate
        ):
            self.pattern_injection_attempts += 1
            injection_result = self._mutate_pattern_injection(child)
            if injection_result is not None:
                injected_gates, pattern_repr, pattern_id, source_context = injection_result
                gates_copy = copy.deepcopy(gates)
                if gates_copy:
                    insert_idx = self.population_manager.rng.randint(0, len(gates_copy))
                else:
                    insert_idx = 0
                new_gates = gates_copy[:insert_idx] + injected_gates + gates_copy[insert_idx:]
                
                candidate_child = copy.deepcopy(child)
                candidate_child["gates"] = self._simplify_gates(new_gates)
                candidate_child = self.population_manager.normalize_circuit(candidate_child)
                
                if self.population_manager.is_valid_circuit(candidate_child):
                    child = candidate_child
                    injected = True

        if not injected:
            self.population_manager.rng.setstate(rng_state)
            operation = self._choose_mutation_operation(child)
            if operation == "gate_removal":
                self._mutate_gate_removal(gates)
            elif operation == "gate_insertion":
                self._mutate_gate_insertion(gates)
            elif operation == "qubit_reassignment":
                self._mutate_qubit_reassignment(gates)
            else:
                self._mutate_gate_replacement(gates)
                
            gates[:] = self._simplify_gates(gates)
            child = self.population_manager.normalize_circuit(child)
            
            if not self.population_manager.is_valid_circuit(child):
                child = copy.deepcopy(parent)
                
            operation_used = operation
        else:
            operation_used = "inject_pattern"

        child_hash = self._circuit_hash(child)
        parent_hash = self._circuit_hash(parent)

        if injected and child_hash != parent_hash:
            parent_score = float("-inf")
            for ev in self.last_evaluations:
                if self._circuit_hash(ev.circuit) == parent_hash:
                    parent_score = ev.score
                    break
            
            self.patterns_injected += 1
            if not hasattr(self, "pending_injections_this_gen"):
                self.pending_injections_this_gen = []
            self.pending_injections_this_gen.append({
                "pattern_id": pattern_id,
                "pattern": pattern_repr,
                "source_context": source_context,
                "pre_mutation_score": parent_score,
                "child_hash": child_hash,
                "post_mutation_score": None,
                "delta_score": None,
                "survival_status": False,
                "generation": self.generation,
                "discarded_in_loop": False,
                "is_scaffold": "scaffold" in str(pattern_id)
            })
        elif injected:
            self.population_manager.rng.setstate(rng_state)
            operation = self._choose_mutation_operation(child)
            if operation == "gate_removal":
                self._mutate_gate_removal(gates)
            elif operation == "gate_insertion":
                self._mutate_gate_insertion(gates)
            elif operation == "qubit_reassignment":
                self._mutate_qubit_reassignment(gates)
            else:
                self._mutate_gate_replacement(gates)
                
            gates[:] = self._simplify_gates(gates)
            child = self.population_manager.normalize_circuit(child)
            
            if not self.population_manager.is_valid_circuit(child):
                child = copy.deepcopy(parent)
                
            operation_used = operation
            child_hash = self._circuit_hash(child)

        self.mutation_history.append(
            {
                "generation": self.generation,
                "operation": operation_used,
                "parent_hash": parent_hash,
                "child_hash": child_hash,
                "parent_gate_count": len(parent.get("gates", [])),
                "child_gate_count": len(child.get("gates", [])),
            }
        )
        return child

    def _mutate_pattern_injection(self, child: Circuit) -> Optional[Any]:
        if self.memory is None:
            return None
            
        if hasattr(self.memory, "get_active_patterns"):
            patterns = self.memory.get_active_patterns()
            is_weighted = True
        else:
            patterns = self.memory.query_patterns()
            is_weighted = False

        scaffolds = []
        if hasattr(self.memory, "get_active_scaffolds"):
            scaffolds = self.memory.get_active_scaffolds(
                context=self.memory.current_context,
                threshold=getattr(self, "compatibility_threshold", 0.75)
            )

        valid_patterns = [p for p in patterns if len(p.get("sequence", [])) <= 3]
        valid_scaffolds = [s for s in scaffolds if len(s.get("sequence", [])) <= 5]
        
        candidates = valid_patterns + valid_scaffolds
        if not candidates:
            return None
            
        if is_weighted:
            weights = []
            sc_rate = getattr(self, "scaffold_injection_rate", 0.1)
            for c in candidates:
                if c.get("is_scaffold", False):
                    weights.append(c.get("weight", 1e-4))
                else:
                    weights.append(c.get("weight", 1e-4) * (1.0 - sc_rate))
            selected = self.population_manager.rng.choices(candidates, weights=weights, k=1)[0]
        else:
            selected = self.population_manager.rng.choice(candidates)
            
        self.patterns_selected_from_memory += 1
        
        pattern_seq = selected.get("sequence", [])
        pattern_repr = selected.get("representation", "")
        
        relative_qubits = []
        for g_str in pattern_seq:
            if '(' in g_str and ')' in g_str:
                _, qubits_part = g_str.split('(')
                qubits_part = qubits_part.rstrip(')')
                for q_rel in qubits_part.split(','):
                    q_rel = q_rel.strip()
                    if q_rel not in relative_qubits:
                        relative_qubits.append(q_rel)
                        
        num_physical_qubits = self.population_manager.qubits
        num_rel_qubits = len(relative_qubits)
        if num_rel_qubits > num_physical_qubits:
            return None
            
        if num_rel_qubits > 0:
            physical_indices = self.population_manager.rng.sample(range(num_physical_qubits), num_rel_qubits)
            qubit_mapping = {rel: phys for rel, phys in zip(relative_qubits, physical_indices)}
        else:
            qubit_mapping = {}
            
        injected_gates = []
        for g_str in pattern_seq:
            if '(' in g_str and ')' in g_str:
                gate_type, qubits_part = g_str.split('(')
                qubits_part = qubits_part.rstrip(')')
                rel_qs = [q.strip() for q in qubits_part.split(',')]
                phys_qs = [qubit_mapping[rq] for rq in rel_qs]
            else:
                gate_type = g_str
                if gate_type == "CNOT":
                    if num_physical_qubits < 2:
                        continue
                    phys_qs = self.population_manager.rng.sample(range(num_physical_qubits), 2)
                else:
                    phys_qs = [self.population_manager.rng.randrange(num_physical_qubits)]
                    
            gate = {"type": gate_type, "qubits": phys_qs}
            if gate_type in ("RX", "RY"):
                gate["theta"] = self.population_manager._sample_angle()
            injected_gates.append(gate)
            
        return injected_gates, pattern_repr, selected.get("pattern_id"), selected.get("context")

    def evolve_generation(self) -> Dict[str, Any]:
        evaluations = self.evaluate_population()

        # Check survival of pending injections from the previous generation
        if hasattr(self, "pending_injections_this_gen") and self.pending_injections_this_gen:
            survivor_count = max(
                self.elitism + 1,
                int(self.population_manager.population_size * self.selection_fraction),
            )
            temp_survivors = self.select_top_k(survivor_count, evaluations)
            survivor_hashes = {self._circuit_hash(s.circuit) for s in temp_survivors}
            
            current_population_hashes = {self._circuit_hash(ev.circuit) for ev in evaluations}
            
            for pending in self.pending_injections_this_gen:
                child_hash = pending["child_hash"]
                
                in_current_population = child_hash in current_population_hashes
                in_top_k = child_hash in survivor_hashes
                
                if in_current_population and in_top_k:
                    pending["survival_status"] = True
                    self.patterns_survived += 1
                    self.successful_injections += 1
                    self.reused_patterns.add(pending["pattern"])
                
                if pending.get("delta_score") is not None and pending["delta_score"] > 0:
                    self.patterns_improved_score += 1
                    
                self.injected_patterns_records.append(pending)

            # Update scaffold stats in memory
            if self.memory is not None and hasattr(self.memory, "query_scaffolds"):
                scaffolds = self.memory.query_scaffolds()
                if scaffolds:
                    updated = False
                    for pending in self.pending_injections_this_gen:
                        pat_id = pending.get("pattern_id", "")
                        if "scaffold" in str(pat_id):
                            for sc in scaffolds:
                                if sc["pattern_id"] == pat_id or sc["representation"] == pending["pattern"]:
                                    sc["support_count"] += 1
                                    if pending.get("survival_status", False):
                                        sc["successful_reuses"] += 1
                                    if pending.get("delta_score") is not None and pending["delta_score"] > 0:
                                        sc["successful_transfers"] += 1
                                    
                                    from quantum.memory.scaffold_builder import ContextAwareScaffoldBuilder
                                    builder = ContextAwareScaffoldBuilder(self.memory)
                                    sc["confidence_score"] = builder.compute_confidence(
                                        sc["support_count"], sc["successful_reuses"], sc["successful_transfers"]
                                    )
                                    updated = True
                    if updated:
                        self.memory.store("quantum:distillation:scaffolds", scaffolds)
            
            # Calculate KDI (Knowledge Diversity Index) for the previous generation
            injected_non_discarded = [p["pattern"] for p in self.pending_injections_this_gen if not p.get("discarded_in_loop", False)]
            if not injected_non_discarded:
                self.last_generation_kdi = 0.0
            else:
                counts = {}
                for pat in injected_non_discarded:
                    counts[pat] = counts.get(pat, 0) + 1
                total = len(injected_non_discarded)
                self.last_generation_kdi = -sum((c / total) * math.log2(c / total) for c in counts.values())
                
            self.pending_injections_this_gen = []

        # --- Capa de Destilación de Conocimiento Cuántico (Fase 1B.4) ---
        rng_state = self.population_manager.rng.getstate()
        
        try:
            top_k = min(10, len(evaluations))
            top_evaluations = self.select_top_k(top_k, evaluations)
            raw_circuits = [e.circuit for e in top_evaluations]
            canonical_circuits = [QuantumCircuitCanonicalizer.canonicalize(c) for c in raw_circuits]
            
            extractor = QuantumPatternExtractor(score_threshold=0.3)
            discovered_patterns = extractor.extract_patterns(top_evaluations)
            
            pattern_count = len(discovered_patterns)
            unique_pattern_count = len({p["representation"] for p in discovered_patterns})
            
            total_raw_gates = sum(len(c.get("gates", [])) for c in raw_circuits)
            total_canonical_gates = sum(len(c.get("gates", [])) for c in canonical_circuits)
            compression_ratio = total_raw_gates / total_canonical_gates if total_canonical_gates > 0 else 1.0
            
            new_patterns_count = 0
            for pattern in discovered_patterns:
                pat_repr = pattern["representation"]
                if pat_repr not in self.discovered_patterns_archive:
                    self.discovered_patterns_archive.add(pat_repr)
                    new_patterns_count += 1
            knowledge_growth = new_patterns_count

            # Actualizar grafo de conocimiento
            gen_node_id = f"generation_{self.generation}"
            self.knowledge_graph.add_node(gen_node_id, "Generation", number=self.generation)
            
            for e, canonical_c in zip(top_evaluations, canonical_circuits):
                raw_c = e.circuit
                raw_hash = self._circuit_hash(raw_c)
                canonical_hash = self._circuit_hash(canonical_c)
                
                self.knowledge_graph.add_node(raw_hash, "Circuit", raw=True, score=e.score, fidelity=e.fidelity)
                self.knowledge_graph.add_node(canonical_hash, "Circuit", raw=False)
                
                self.knowledge_graph.add_edge(raw_hash, gen_node_id, "discovered_in_generation")
                self.knowledge_graph.add_edge(canonical_hash, gen_node_id, "discovered_in_generation")
                self.knowledge_graph.add_edge(raw_hash, canonical_hash, "equivalent_to")
                
                for pattern in discovered_patterns:
                    seq_str = pattern["representation"]
                    gate_types = [g.get("type") for g in raw_c.get("gates", []) if g.get("type")]
                    gate_types_str = "->".join(gate_types)
                    
                    rel_gates = []
                    qubit_map = {}
                    for g in raw_c.get("gates", []):
                        g_type = g.get("type")
                        g_qubits = g.get("qubits", [])
                        mapped_qubits = [qubit_map.setdefault(q, f"q{len(qubit_map)}") for q in g_qubits]
                        if mapped_qubits:
                            rel_gates.append(f"{g_type}({','.join(mapped_qubits)})")
                        else:
                            rel_gates.append(g_type)
                    rel_gates_str = "->".join(rel_gates)
                    
                    if seq_str in gate_types_str or seq_str in rel_gates_str:
                        pat_node_id = f"pattern_{pattern['pattern_id']}"
                        self.knowledge_graph.add_node(pat_node_id, "Pattern", sequence=pattern["sequence"], type=pattern["type"])
                        self.knowledge_graph.add_edge(raw_hash, pat_node_id, "contains_pattern")
                        self.knowledge_graph.add_edge(canonical_hash, pat_node_id, "contains_pattern")

            for mut in self.mutation_history:
                if mut["generation"] == self.generation:
                    parent_h = mut["parent_hash"]
                    child_h = mut["child_hash"]
                    if parent_h in self.knowledge_graph.nodes and child_h in self.knowledge_graph.nodes:
                        self.knowledge_graph.add_edge(child_h, parent_h, "mutation_of")
                        parent_score = self.knowledge_graph.nodes[parent_h]["attributes"].get("score", -1.0)
                        child_score = self.knowledge_graph.nodes[child_h]["attributes"].get("score", -1.0)
                        if child_score > parent_score:
                            self.knowledge_graph.add_edge(child_h, parent_h, "improves")

            if self.patterns_injected > 0:
                knowledge_utilization_rate = self.successful_injections / self.patterns_injected
            else:
                knowledge_utilization_rate = 0.0

            # Actualizar memoria
            if self.memory is not None:
                self.memory.store("quantum:distillation:canonical_circuits", canonical_circuits)
                
                # Derive current context
                task_name = "bell_state" if len(self.target_state) == 4 else "ghz_state"
                qubits = 2 if len(self.target_state) == 4 else 3
                is_converged = any(e.fidelity >= 0.99 for e in evaluations)
                from quantum.knowledge.context_schema import Context
                current_context = Context(task_name=task_name, qubit_count=qubits, converged=is_converged)
                if hasattr(self.memory, "set_current_context"):
                    self.memory.set_current_context(current_context)

                # Merge patterns to preserve transfer learning knowledge across tasks/seeds
                existing_patterns = self.memory.retrieve("quantum:distillation:patterns") or []
                
                # Group existing patterns by (representation, task_name, qubit_count, converged)
                pattern_map = {}
                for p in existing_patterns:
                    p_ctx_dict = p.get("context")
                    if p_ctx_dict:
                        p_ctx = Context.from_dict(p_ctx_dict)
                    else:
                        p_ctx = Context(task_name="bell_state", qubit_count=2, converged=True)
                    
                    key = (p["representation"], p_ctx.task_name, p_ctx.qubit_count, p_ctx.converged)
                    pattern_map[key] = p
                
                # Add/Merge discovered patterns with current_context
                for p in discovered_patterns:
                    repr_str = p["representation"]
                    key = (repr_str, current_context.task_name, current_context.qubit_count, current_context.converged)
                    
                    if key in pattern_map:
                        prev = pattern_map[key]
                        pattern_map[key] = {
                            "pattern_id": p["pattern_id"],
                            "sequence": p["sequence"],
                            "frequency": p["frequency"] + prev["frequency"],
                            "avg_score": round((p["avg_score"] + prev["avg_score"]) / 2, 4),
                            "type": p["type"],
                            "representation": repr_str,
                            "context": current_context.to_dict()
                        }
                    else:
                        p_with_context = copy.deepcopy(p)
                        p_with_context["context"] = current_context.to_dict()
                        pattern_map[key] = p_with_context
                
                # Update per-context statistics for each pattern
                causal_records = self.injected_patterns_records
                for key, p in pattern_map.items():
                    repr_str = p["representation"]
                    p_ctx_dict = p.get("context")
                    p_ctx = Context.from_dict(p_ctx_dict) if p_ctx_dict else current_context
                    
                    # Filter causal records matching this pattern and context
                    matching_records = []
                    for r in causal_records:
                        rec_pat = r.get("pattern", "")
                        rec_clean = "->".join(part.split("(")[0].strip() for part in rec_pat.split("->"))
                        
                        # Match record context if present
                        rec_ctx_data = r.get("source_context")
                        rec_ctx = Context.from_dict(rec_ctx_data) if rec_ctx_data else None
                        
                        # Match context task_name and qubit_count if context is present
                        context_match = True
                        if rec_ctx:
                            context_match = (rec_ctx.task_name == p_ctx.task_name and 
                                             rec_ctx.qubit_count == p_ctx.qubit_count)
                        
                        if rec_clean == repr_str and context_match:
                            matching_records.append(r)
                            
                    if matching_records:
                        survived_count = sum(1 for r in matching_records if r.get("survival_status", False))
                        survival_prob = survived_count / len(matching_records)
                        deltas = [r.get("delta_score") for r in matching_records if r.get("delta_score") is not None]
                        mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
                    else:
                        survival_prob = p.get("survival_probability", 0.0)
                        mean_delta = p.get("mean_delta_score", 0.0)
                    
                    # P(convergence) is 1.0 if this context is converged, otherwise 0.0
                    p_conv = 1.0 if p_ctx.converged else 0.0
                    
                    p["survival_probability"] = round(survival_prob, 4)
                    p["P_convergence"] = round(p_conv, 4)
                    p["mean_delta_score"] = round(mean_delta, 4)

                merged_patterns = list(pattern_map.values())
                merged_patterns.sort(key=lambda x: (x["frequency"], x["avg_score"]), reverse=True)
                self.memory.store("quantum:distillation:patterns", merged_patterns)
                self.memory.store("quantum:distillation:knowledge_graph", self.knowledge_graph.to_dict())
                
                metrics_history = self.memory.retrieve("quantum:distillation:metrics_history") or []
                metrics_history.append({
                    "generation": self.generation,
                    "pattern_count": pattern_count,
                    "unique_pattern_count": unique_pattern_count,
                    "canonical_compression_ratio": round(compression_ratio, 4),
                    "knowledge_growth": knowledge_growth,
                    "patterns_injected": self.patterns_injected,
                    "successful_injections": self.successful_injections,
                    "knowledge_utilization_rate": round(knowledge_utilization_rate, 4),
                    "patterns_selected_from_memory": self.patterns_selected_from_memory,
                    "pattern_injection_attempts": self.pattern_injection_attempts,
                    "patterns_survived": self.patterns_survived,
                    "patterns_improved_score": self.patterns_improved_score,
                    "knowledge_diversity_index": round(getattr(self, "last_generation_kdi", 0.0), 4),
                })
                self.memory.store("quantum:distillation:metrics_history", metrics_history)
                self.memory.store("quantum:distillation:causal_records", self.injected_patterns_records)
                
                task_patterns = []
                for pattern in discovered_patterns:
                    task_patterns.append({
                        "task": task_name,
                        "pattern": pattern["representation"],
                        "frequency": pattern["frequency"],
                        "avg_score": pattern["avg_score"],
                        "context": current_context.to_dict()
                    })
                self.memory.store(f"quantum:distillation:task:{task_name}:patterns", task_patterns)
                
                # Build new scaffolds (Fase 1E Component A)
                from quantum.memory.scaffold_builder import ContextAwareScaffoldBuilder
                builder = ContextAwareScaffoldBuilder(self.memory)
                builder.build_scaffolds(target_context=current_context, threshold=getattr(self, "compatibility_threshold", 0.75))

            # Crear y almacenar el reporte
            report = self._build_report(evaluations)
            self._store_generation_report(report)

            # Inyectar métricas de destilación en el reporte
            report_dict = report.to_dict()
            report_dict["patterns_discovered"] = unique_pattern_count
            report_dict["canonical_compression_ratio"] = round(compression_ratio, 4)
            report_dict["knowledge_growth"] = knowledge_growth
            report_dict["patterns_injected"] = self.patterns_injected
            report_dict["successful_injections"] = self.successful_injections
            report_dict["knowledge_utilization_rate"] = round(knowledge_utilization_rate, 4)
            report_dict["patterns_selected_from_memory"] = self.patterns_selected_from_memory
            report_dict["pattern_injection_attempts"] = self.pattern_injection_attempts
            report_dict["patterns_survived"] = self.patterns_survived
            report_dict["patterns_improved_score"] = self.patterns_improved_score
            report_dict["knowledge_diversity_index"] = round(getattr(self, "last_generation_kdi", 0.0), 4)
            
            # Reemplazar la última entrada en el historial local y sincronizar la memoria
            if self.history:
                self.history[-1] = report_dict
                if self.memory is not None:
                    self.memory.store("quantum:evolution:history", copy.deepcopy(self.history))
                    self.memory.store(f"quantum:evolution:generation:{report.generation}", report_dict)
                    
        finally:
            # Restaurar el estado del RNG para mantener la reproducibilidad exacta
            self.population_manager.rng.setstate(rng_state)

        # --- Fin de Capa de Destilación ---

        survivor_count = max(
            self.elitism + 1,
            int(self.population_manager.population_size * self.selection_fraction),
        )
        survivors = self.select_top_k(survivor_count, evaluations)

        next_population = [
            copy.deepcopy(item.circuit) for item in survivors[: self.elitism]
        ]
        parent_pool = survivors or evaluations

        while len(next_population) < self.population_manager.population_size:
            if (
                self.population_manager.rng.random() < self.random_injection_rate
                or self._diversity(next_population) < self.diversity_threshold
            ):
                next_population.append(self.population_manager.random_circuit())
                continue

            parent_evaluation = self._select_parent(parent_pool)
            parent = parent_evaluation.circuit
            if self.population_manager.rng.random() <= self.mutation_rate:
                child = self.mutate(parent)
            else:
                child = copy.deepcopy(parent)
                
            child_hash = self._circuit_hash(child)
            child_evaluation = self.evaluate_circuit(child)
            
            # Fill in evaluation details for pending injections of the current generation
            for pending in self.pending_injections_this_gen:
                if pending["child_hash"] == child_hash and pending["generation"] == self.generation:
                    pending["post_mutation_score"] = child_evaluation.score
                    pending["delta_score"] = child_evaluation.score - pending["pre_mutation_score"]
            
            if (
                child_evaluation.score + 1e-12 < parent_evaluation.score
                and self.population_manager.rng.random() < 0.85
            ):
                for pending in self.pending_injections_this_gen:
                    if pending["child_hash"] == child_hash and pending["generation"] == self.generation:
                        pending["discarded_in_loop"] = True
                child = copy.deepcopy(parent)
            next_population.append(child)

        next_population = self._preserve_diversity(next_population)
        self.population_manager.set_population(next_population)
        self.generation += 1
        return report_dict

    def run(self, generations: int) -> List[Dict[str, Any]]:
        reports = []
        for _ in range(generations):
            reports.append(self.evolve_generation())
        return reports

    def _build_report(
        self, evaluations: List[QuantumCircuitEvaluation]
    ) -> GenerationReport:
        if not evaluations:
            raise ValueError("Cannot build a generation report from an empty population.")

        best = evaluations[0]
        finite_scores = [item.score for item in evaluations if item.score != float("-inf")]
        average_score = sum(finite_scores) / len(finite_scores) if finite_scores else 0.0

        return GenerationReport(
            generation=self.generation,
            best_circuit=copy.deepcopy(best.circuit),
            best_fidelity=best.fidelity,
            best_score=best.score,
            average_population_score=average_score,
            diversity_metric=self._diversity([item.circuit for item in evaluations]),
            best_depth=best.depth,
            best_gate_count=best.gate_count,
            population_size=len(evaluations),
        )

    def _verdict_field(self, verdict: Any, field: str, default: Any) -> Any:
        if isinstance(verdict, dict):
            return verdict.get(field, default)
        return getattr(verdict, field, default)

    def _store_generation_report(self, report: GenerationReport) -> None:
        report_dict = report.to_dict()
        self.history.append(report_dict)
        self.historical_best.append(
            {
                "generation": report.generation,
                "circuit": copy.deepcopy(report.best_circuit),
                "score": report.best_score,
                "fidelity": report.best_fidelity,
            }
        )
        self.historical_best.sort(key=lambda item: item["score"], reverse=True)

        if self.memory is None:
            return

        self.memory.store(f"quantum:evolution:generation:{report.generation}", report_dict)
        self.memory.store("quantum:evolution:history", copy.deepcopy(self.history))
        self.memory.store(
            "quantum:evolution:historical_best",
            copy.deepcopy(self.historical_best),
        )
        self.memory.store("quantum:evolution:best_circuit", copy.deepcopy(report.best_circuit))
        self.memory.store("quantum:evolution:best_score", report.best_score)
        self.memory.store(
            "quantum:evolution:best_score_by_domain",
            {"quantum": report.best_score},
        )
        self.memory.store("quantum:best_score:quantum", report.best_score)
        self.memory.store(
            "quantum:evolution:mutation_history",
            copy.deepcopy(self.mutation_history),
        )

    def _select_parent(
        self, parent_pool: List[QuantumCircuitEvaluation]
    ) -> QuantumCircuitEvaluation:
        tournament_size = min(3, len(parent_pool))
        competitors = self.population_manager.rng.sample(parent_pool, tournament_size)
        return max(competitors, key=lambda item: item.score)

    def _choose_mutation_operation(self, circuit: Circuit) -> str:
        gate_count = len(circuit.get("gates", []))
        depth = self._estimate_depth(circuit.get("gates", []))
        has_entanglement = self._entangling_gate_count(circuit.get("gates", [])) > 0
        ideal_gate_budget = max(2, self.population_manager.qubits + 1)
        ideal_depth_budget = max(2, self.population_manager.qubits)

        operations = [
            "gate_replacement",
            "gate_insertion",
            "gate_removal",
            "qubit_reassignment",
        ]

        if gate_count == 0:
            weights = [0.0, 0.85, 0.0, 0.15]
        elif gate_count > ideal_gate_budget or depth > ideal_depth_budget:
            weights = [0.25, 0.10, 0.50, 0.15]
        elif not has_entanglement and self.population_manager.qubits >= 2:
            weights = [0.35, 0.45, 0.05, 0.15]
        else:
            weights = [0.35, 0.25, 0.20, 0.20]

        return self.population_manager.rng.choices(operations, weights=weights, k=1)[0]

    def _mutate_gate_replacement(self, gates: List[Gate]) -> None:
        if not gates:
            self._mutate_gate_insertion(gates)
            return

        idx = self.population_manager.rng.randrange(len(gates))
        prefer_entangling = (
            self.population_manager.qubits >= 2 and self._entangling_gate_count(gates) == 0
        )
        gates[idx] = self.population_manager.random_gate(prefer_entangling=prefer_entangling)

    def _mutate_gate_insertion(self, gates: List[Gate]) -> None:
        if len(gates) >= self.population_manager.max_gates:
            self._mutate_gate_replacement(gates)
            return

        prefer_entangling = (
            self.population_manager.qubits >= 2
            and self._entangling_efficiency(gates) < 0.35
        )
        new_gate = self.population_manager.random_gate(prefer_entangling=prefer_entangling)
        idx = self.population_manager.rng.randrange(len(gates) + 1)
        gates.insert(idx, new_gate)

    def _mutate_gate_removal(self, gates: List[Gate]) -> None:
        if not gates:
            return

        removable_indices = self._redundant_gate_indices(gates)
        if not removable_indices:
            removable_indices = list(range(len(gates)))

        if self._entangling_gate_count(gates) <= 1 and self.population_manager.qubits >= 2:
            protected = {
                idx for idx, gate in enumerate(gates) if gate.get("type") == "CNOT"
            }
            filtered = [idx for idx in removable_indices if idx not in protected]
            if filtered:
                removable_indices = filtered

        idx = self.population_manager.rng.choice(removable_indices)
        del gates[idx]

    def _mutate_qubit_reassignment(self, gates: List[Gate]) -> None:
        if not gates:
            self._mutate_gate_insertion(gates)
            return

        idx = self.population_manager.rng.randrange(len(gates))
        gate = gates[idx]
        gate_type = gate.get("type")
        if gate_type == "CNOT" and self.population_manager.qubits >= 2:
            control, target = self.population_manager.rng.sample(
                range(self.population_manager.qubits), 2
            )
            gate["qubits"] = [control, target]
        else:
            gate["qubits"] = [self.population_manager.rng.randrange(self.population_manager.qubits)]

    def _simplify_gates(self, gates: List[Gate]) -> List[Gate]:
        simplified: List[Gate] = []

        for gate in gates:
            gate_type = gate.get("type")
            if gate_type in ("RX", "RY") and abs(float(gate.get("theta", 0.0))) < 1e-12:
                continue

            if simplified and self._are_self_inverse_pair(simplified[-1], gate):
                simplified.pop()
                continue

            simplified.append(copy.deepcopy(gate))

        return simplified[: self.population_manager.max_gates]

    def _are_self_inverse_pair(self, first: Gate, second: Gate) -> bool:
        if first.get("type") != second.get("type"):
            return False
        if first.get("qubits") != second.get("qubits"):
            return False
        return first.get("type") in {"H", "X", "CNOT"}

    def _redundant_gate_indices(self, gates: List[Gate]) -> List[int]:
        redundant = []
        for idx, gate in enumerate(gates):
            if gate.get("type") in ("RX", "RY") and abs(float(gate.get("theta", 0.0))) < 1e-12:
                redundant.append(idx)
            if idx > 0 and self._are_self_inverse_pair(gates[idx - 1], gate):
                redundant.extend([idx - 1, idx])
        return sorted(set(redundant))

    def _preserve_diversity(self, population: List[Circuit]) -> List[Circuit]:
        target_size = self.population_manager.population_size
        deduped: List[Circuit] = []
        seen = set()
        for circuit in population:
            key = self._circuit_hash(circuit)
            if key in seen and self.population_manager.rng.random() < 0.75:
                continue
            seen.add(key)
            deduped.append(circuit)
            if len(deduped) == target_size:
                break

        while len(deduped) < target_size:
            deduped.append(self.population_manager.random_circuit())
        return deduped

    def _diversity(self, population: List[Circuit]) -> float:
        if not population:
            return 0.0
        unique = {self._circuit_hash(circuit) for circuit in population}
        return len(unique) / len(population)

    def _circuit_hash(self, circuit: Circuit) -> str:
        normalized = self.population_manager.normalize_circuit(circuit)
        payload = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _entangling_gate_count(self, gates: List[Gate]) -> int:
        return sum(1 for gate in gates if gate.get("type") == "CNOT")

    def _entangling_efficiency(self, gates: List[Gate]) -> float:
        if not gates:
            return 0.0
        return self._entangling_gate_count(gates) / len(gates)

    def _estimate_depth(self, gates: List[Gate]) -> int:
        qubit_depths = [0] * self.population_manager.qubits
        for gate in gates:
            gate_qubits = gate.get("qubits", [])
            if not gate_qubits:
                continue
            max_depth = max(qubit_depths[q] for q in gate_qubits)
            for qubit in gate_qubits:
                qubit_depths[qubit] = max_depth + 1
        return max(qubit_depths) if qubit_depths else 0
