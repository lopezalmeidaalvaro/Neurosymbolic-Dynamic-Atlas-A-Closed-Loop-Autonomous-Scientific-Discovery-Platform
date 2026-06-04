import copy
import math
import random
from typing import Any, Dict, Iterable, List, Optional


Circuit = Dict[str, Any]
Gate = Dict[str, Any]


class QuantumPopulationManager:
    """
    Maintains a population of syntactically valid quantum circuits in JSON format.
    """

    ALLOWED_GATES = ("H", "X", "Y", "Z", "RX", "RY", "RZ", "CNOT", "CX", "CZ", "SWAP")

    def __init__(
        self,
        qubits: int,
        population_size: int = 40,
        min_gates: int = 1,
        max_gates: Optional[int] = None,
        allowed_gates: Optional[Iterable[str]] = None,
        seed: Optional[int] = None,
        seed_circuits: Optional[List[Circuit]] = None,
        coupling_map: Optional[Iterable[Iterable[int]]] = None,
    ):
        if qubits <= 0:
            raise ValueError("qubits must be greater than zero.")
        if population_size <= 0:
            raise ValueError("population_size must be greater than zero.")

        self.qubits = qubits
        self.population_size = population_size
        self.min_gates = max(0, min_gates)
        self.max_gates = max_gates if max_gates is not None else max(4, qubits * 4)
        self.allowed_gates = tuple(allowed_gates or self.ALLOWED_GATES)
        self.rng = random.Random(seed)
        self.population: List[Circuit] = []

        self.coupling_map = None
        if coupling_map is not None:
            self.coupling_map = set()
            for edge in coupling_map:
                u, v = int(edge[0]), int(edge[1])
                self.coupling_map.add((u, v))
                self.coupling_map.add((v, u))

        if seed_circuits:
            for circuit in seed_circuits:
                normalized = self.normalize_circuit(circuit)
                if self.is_valid_circuit(normalized):
                    self.population.append(normalized)

        self.initialize_population()

    def initialize_population(self) -> List[Circuit]:
        while len(self.population) < self.population_size:
            self.population.append(self.random_circuit())
        self.population = self.population[: self.population_size]
        return self.copy_population()

    def copy_population(self) -> List[Circuit]:
        return [copy.deepcopy(circuit) for circuit in self.population]

    def set_population(self, population: List[Circuit]) -> None:
        normalized = [self.normalize_circuit(circuit) for circuit in population]
        invalid = [circuit for circuit in normalized if not self.is_valid_circuit(circuit)]
        if invalid:
            raise ValueError("population contains invalid circuits.")
        self.population = normalized[: self.population_size]

    def random_circuit(self) -> Circuit:
        if self.qubits >= 2 and self.rng.random() < 0.45:
            return self._random_entangling_circuit()

        gate_count = self.rng.randint(self.min_gates, self.max_gates)
        gates = [self.random_gate() for _ in range(gate_count)]
        return {"qubits": self.qubits, "gates": gates}

    def random_gate(self, prefer_entangling: bool = False) -> Gate:
        gate_type = self._sample_gate_type(prefer_entangling=prefer_entangling)
        return self.random_gate_of_type(gate_type)

    def random_gate_of_type(self, gate_type: str) -> Gate:
        if gate_type not in self.allowed_gates:
            raise ValueError(f"Unsupported gate type: {gate_type}")

        if gate_type in ("CNOT", "CX", "CZ", "SWAP"):
            if self.qubits < 2:
                return self.random_gate_of_type("H")
            if self.coupling_map:
                edge = self.rng.choice(list(self.coupling_map))
                if self.rng.random() < 0.5:
                    control, target = edge
                else:
                    target, control = edge
            else:
                control, target = self.rng.sample(range(self.qubits), 2)
            g_name = "CNOT" if gate_type == "CX" else gate_type
            return {"type": g_name, "qubits": [control, target]}

        qubit = self.rng.randrange(self.qubits)
        if gate_type in ("RX", "RY", "RZ"):
            return {
                "type": gate_type,
                "qubits": [qubit],
                "theta": self._sample_angle(),
            }
        return {"type": gate_type, "qubits": [qubit]}

    def normalize_circuit(self, circuit: Circuit) -> Circuit:
        qubits = int(circuit.get("qubits", self.qubits))
        qubits = self.qubits if qubits != self.qubits else qubits
        gates = []
        for gate in circuit.get("gates", []):
            normalized_gate = self.normalize_gate(gate, qubits)
            if normalized_gate is not None:
                gates.append(normalized_gate)
        return {"qubits": qubits, "gates": gates[: self.max_gates]}

    def normalize_gate(self, gate: Gate, qubits: Optional[int] = None) -> Optional[Gate]:
        qubits = qubits or self.qubits
        gate_type = gate.get("type", "").upper()
        if gate_type == "CX":
            gate_type = "CNOT"
        if gate_type not in self.allowed_gates:
            return None

        raw_qubits = gate.get("qubits", [])
        if gate_type in ("CNOT", "CZ", "SWAP"):
            if qubits < 2:
                return None
            if len(raw_qubits) == 2:
                control = int(raw_qubits[0]) % qubits
                target = int(raw_qubits[1]) % qubits
                if control == target:
                    target = (target + 1) % qubits
            else:
                if self.coupling_map:
                    edge = self.rng.choice(list(self.coupling_map))
                    control, target = edge
                else:
                    control, target = self.rng.sample(range(qubits), 2)
            return {"type": gate_type, "qubits": [control, target]}

        if len(raw_qubits) >= 1:
            gate_qubit = int(raw_qubits[0]) % qubits
        else:
            gate_qubit = self.rng.randrange(qubits)

        normalized = {"type": gate_type, "qubits": [gate_qubit]}
        if gate_type in ("RX", "RY", "RZ"):
            normalized["theta"] = float(gate.get("theta", self._sample_angle()))
        return normalized

    def is_valid_circuit(self, circuit: Circuit) -> bool:
        if not isinstance(circuit, dict):
            return False
        if circuit.get("qubits") != self.qubits:
            return False
        gates = circuit.get("gates", [])
        if not isinstance(gates, list):
            return False
        if len(gates) > self.max_gates:
            return False

        for gate in gates:
            if not self.is_valid_gate(gate):
                return False
        return True

    def is_valid_gate(self, gate: Gate) -> bool:
        if not isinstance(gate, dict):
            return False
        gate_type = gate.get("type")
        gate_qubits = gate.get("qubits")
        if gate_type not in self.allowed_gates:
            return False
        if not isinstance(gate_qubits, list):
            return False

        required_qubits = 2 if gate_type in ("CNOT", "CX", "CZ", "SWAP") else 1
        if len(gate_qubits) != required_qubits:
            return False
        if any(not isinstance(q, int) for q in gate_qubits):
            return False
        if any(q < 0 or q >= self.qubits for q in gate_qubits):
            return False
        if required_qubits == 2:
            if gate_qubits[0] == gate_qubits[1]:
                return False
            if self.coupling_map and (gate_qubits[0], gate_qubits[1]) not in self.coupling_map:
                return False
        if gate_type in ("RX", "RY", "RZ") and not isinstance(
            gate.get("theta"), (int, float)
        ):
            return False
        return True

    def _random_entangling_circuit(self) -> Circuit:
        gates: List[Gate] = []
        start = self.rng.randrange(self.qubits)
        gates.append({"type": "H", "qubits": [start]})

        if self.coupling_map:
            visited = {start}
            while len(visited) < self.qubits and len(gates) < self.max_gates:
                candidates = []
                for u, v in self.coupling_map:
                    if u in visited and v not in visited:
                        candidates.append((u, v))
                if not candidates:
                    break
                control, target = self.rng.choice(candidates)
                gates.append({"type": "CNOT", "qubits": [control, target]})
                visited.add(target)
        else:
            unused = [q for q in range(self.qubits) if q != start]
            self.rng.shuffle(unused)
            frontier = [start]
            while unused and len(gates) < self.max_gates:
                target = unused.pop()
                control = self.rng.choice(frontier)
                gates.append({"type": "CNOT", "qubits": [control, target]})
                frontier.append(target)

        while len(gates) < self.min_gates:
            gates.append(self.random_gate())

        if len(gates) < self.max_gates and self.rng.random() < 0.35:
            insertions = self.rng.randint(1, max(1, self.max_gates - len(gates)))
            for _ in range(insertions):
                gates.insert(self.rng.randrange(len(gates) + 1), self.random_gate())

        return {"qubits": self.qubits, "gates": gates[: self.max_gates]}

    def _sample_gate_type(self, prefer_entangling: bool = False) -> str:
        if self.qubits < 2:
            candidates = [gate for gate in self.allowed_gates if gate != "CNOT"]
        else:
            candidates = list(self.allowed_gates)

        if prefer_entangling and "CNOT" in candidates:
            if len(candidates) == 1:
                weights = [1.0]
            else:
                weights = [
                    0.45 if gate == "CNOT" else 0.55 / (len(candidates) - 1)
                    for gate in candidates
                ]
        else:
            base_weights = {
                "H": 0.28,
                "X": 0.14,
                "RX": 0.16,
                "RY": 0.18,
                "CNOT": 0.24,
            }
            weights = [base_weights.get(gate, 1.0) for gate in candidates]

        return self.rng.choices(candidates, weights=weights, k=1)[0]

    def _sample_angle(self) -> float:
        angle_pool = [0.0, math.pi / 2, -math.pi / 2, math.pi]
        if self.rng.random() < 0.8:
            return float(self.rng.choice(angle_pool))
        return round(self.rng.uniform(-math.pi, math.pi), 6)
