import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from quantum.evolution.population_manager import Circuit, Gate, QuantumPopulationManager


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
        self.elitism = min(elitism, population_manager.population_size)
        self.selection_fraction = selection_fraction
        self.mutation_rate = mutation_rate
        self.random_injection_rate = random_injection_rate
        self.diversity_threshold = diversity_threshold
        self.generation = 0
        self.history: List[Dict[str, Any]] = []
        self.historical_best: List[Dict[str, Any]] = []
        self.mutation_history: List[Dict[str, Any]] = []
        self.last_evaluations: List[QuantumCircuitEvaluation] = []

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

        operation = self._choose_mutation_operation(child)
        before_hash = self._circuit_hash(parent)

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

        self.mutation_history.append(
            {
                "generation": self.generation,
                "operation": operation,
                "parent_hash": before_hash,
                "child_hash": self._circuit_hash(child),
                "parent_gate_count": len(parent.get("gates", [])),
                "child_gate_count": len(child.get("gates", [])),
            }
        )
        return child

    def evolve_generation(self) -> Dict[str, Any]:
        evaluations = self.evaluate_population()
        report = self._build_report(evaluations)
        self._store_generation_report(report)

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
            child_evaluation = self.evaluate_circuit(child)
            if (
                child_evaluation.score + 1e-12 < parent_evaluation.score
                and self.population_manager.rng.random() < 0.85
            ):
                child = copy.deepcopy(parent)
            next_population.append(child)

        next_population = self._preserve_diversity(next_population)
        self.population_manager.set_population(next_population)
        self.generation += 1
        return report.to_dict()

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
