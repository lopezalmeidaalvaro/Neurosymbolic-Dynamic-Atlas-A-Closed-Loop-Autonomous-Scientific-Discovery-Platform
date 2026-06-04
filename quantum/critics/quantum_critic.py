from typing import Dict, Any, List
from core.abstractions.base_critic import BaseCritic

class QuantumCriticVerdict(dict):
    """
    Clase de veredicto que actúa como diccionario y objeto para máxima compatibilidad.
    """
    @property
    def valid(self) -> bool:
        return self.get("valid", False)

    @property
    def score(self) -> float:
        return self.get("score", 0.0)

    @property
    def reason(self) -> str:
        return self.get("reason", "")

    @property
    def fidelity(self) -> float:
        return self.get("fidelity", 0.0)

    @property
    def depth(self) -> int:
        return self.get("depth", 0)

    @property
    def gate_count(self) -> int:
        return self.get("gate_count", 0)

    # Para compatibilidad con tests clásicos
    @property
    def verdict(self) -> str:
        return "ACCEPTED" if self.valid else "REJECTED"


def parse_statevector(sv: Any) -> List[complex]:
    """
    Convierte cualquier representación de vector de estado a una lista de números complejos.
    Soporta:
      - Números complejos directamente.
      - Cadenas complejas ("0.707+0j", "1j", etc.).
      - Listas/tuplas de tipo [real, imag].
      - Floats/ints para estados reales.
    """
    if not isinstance(sv, (list, tuple)):
        raise ValueError("El vector de estado debe ser una lista o tupla.")
    
    result = []
    for idx, item in enumerate(sv):
        if isinstance(item, complex):
            result.append(item)
        elif isinstance(item, (int, float)):
            result.append(complex(item, 0.0))
        elif isinstance(item, str):
            cleaned = item.replace(" ", "").replace("i", "j").replace("I", "j")
            result.append(complex(cleaned))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            result.append(complex(item[0], item[1]))
        else:
            raise ValueError(f"Formato de número complejo desconocido en la posición {idx}: {item}")
    return result


class QuantumCritic(BaseCritic):
    """
    Crítico de hipótesis para el dominio cuántico.
    Evalúa la validez estructural de los circuitos y calcula la fidelidad física
    frente a un estado objetivo, aplicando penalizaciones por profundidad y número de puertas.
    """

    def __init__(self, alpha: float = 0.01, beta: float = 0.001):
        """
        Inicializa el crítico con coeficientes de penalización configurables.
        alpha: penalización por cada unidad de profundidad (depth).
        beta: penalización por cada compuerta (gate_count).
        """
        self.alpha = alpha
        self.beta = beta

    def validate(self, hypothesis: Any, target_state: Any = None, *args, **kwargs) -> QuantumCriticVerdict:
        """
        Valida el circuito.
        Si se especifica target_state, realiza una evaluación física basada en la fidelidad
        y penalización por tamaño/profundidad.
        De lo contrario, realiza una validación estructural heredada de la hipótesis del circuito.
        """
        # 1. Determinar si se solicita evaluación física (presencia de target_state)
        if target_state is not None:
            return self._validate_physical(hypothesis, target_state, **kwargs)
        else:
            return self._validate_structural(hypothesis)

    def _validate_physical(self, candidate_result: Any, target_state: Any, **kwargs) -> QuantumCriticVerdict:
        """
        Calcula la fidelidad cuántica F = |<psi_target | psi_candidate>|^2 y evalúa el score físico.
        """
        # Extraer los datos reales del sandbox
        candidate_data = candidate_result
        if isinstance(candidate_result, dict):
            # Si contiene el envoltorio "success" / "result"
            if "result" in candidate_result and "success" in candidate_result:
                if not candidate_result["success"]:
                    return QuantumCriticVerdict({
                        "valid": False,
                        "fidelity": 0.0,
                        "depth": 0,
                        "gate_count": 0,
                        "score": 0.0,
                        "reason": f"La simulación del sandbox falló: {candidate_result.get('error', 'Error desconocido')}"
                    })
                candidate_data = candidate_result["result"]

        if not isinstance(candidate_data, dict):
            return QuantumCriticVerdict({
                "valid": False,
                "fidelity": 0.0,
                "depth": 0,
                "gate_count": 0,
                "score": 0.0,
                "reason": "El resultado candidato del sandbox no tiene un formato válido."
            })

        # Obtener métricas
        depth = candidate_data.get("depth", 0)
        gate_count = candidate_data.get("gate_count", 0)

        # Parsear vectores de estado
        try:
            statevector_candidate = candidate_data.get("statevector")
            if statevector_candidate is None:
                # Intentar fallback con statevector_complex
                statevector_candidate = candidate_data.get("statevector_complex")

            if statevector_candidate is None:
                return QuantumCriticVerdict({
                    "valid": False,
                    "fidelity": 0.0,
                    "depth": depth,
                    "gate_count": gate_count,
                    "score": 0.0,
                    "reason": "El candidato no contiene un vector de estado ('statevector')."
                })

            psi_cand = parse_statevector(statevector_candidate)
            psi_targ = parse_statevector(target_state)
        except Exception as e:
            return QuantumCriticVerdict({
                "valid": False,
                "fidelity": 0.0,
                "depth": depth,
                "gate_count": gate_count,
                "score": 0.0,
                "reason": f"Fallo al parsear vectores de estado: {str(e)}"
            })

        if len(psi_cand) != len(psi_targ):
            return QuantumCriticVerdict({
                "valid": False,
                "fidelity": 0.0,
                "depth": depth,
                "gate_count": gate_count,
                "score": 0.0,
                "reason": f"Dimensión del vector de estado candidato ({len(psi_cand)}) no coincide con el objetivo ({len(psi_targ)})."
            })

        # Calcular producto interno: <psi_target | psi_candidate> = sum(tc.conjugate() * cc)
        inner_product = 0.0 + 0.0j
        for tc, cc in zip(psi_targ, psi_cand):
            inner_product += tc.conjugate() * cc

        # Fidelidad = |inner_product|^2
        fidelity = abs(inner_product) ** 2
        # Acotar fidelidad en [0, 1]
        fidelity = max(0.0, min(1.0, fidelity))

        # Parámetros de penalización configurables dinámicamente
        alpha = kwargs.get("alpha", self.alpha)
        beta = kwargs.get("beta", self.beta)

        # Score = fidelity - alpha * depth - beta * gate_count
        # To prevent size/depth penalties from discarding high-fidelity circuits,
        # we apply a heavy penalty to low-fidelity configurations.
        if fidelity < 0.99:
            score = fidelity - 10.0
        else:
            score = fidelity - alpha * depth - beta * gate_count

        return QuantumCriticVerdict({
            "valid": True,
            "fidelity": float(fidelity),
            "depth": int(depth),
            "gate_count": int(gate_count),
            "score": float(score),
            "reason": f"Evaluación de fidelidad completada con éxito. Fidelidad: {fidelity:.6f}, Score: {score:.6f}."
        })

    def _validate_structural(self, hypothesis: Any) -> QuantumCriticVerdict:
        """
        Valida estructuralmente el circuito y calcula una puntuación basada en la eficiencia estructural (legacy).
        """
        # Si la hipótesis es un diccionario o un objeto
        if isinstance(hypothesis, dict):
            circuit = hypothesis.get("circuit")
        else:
            circuit = getattr(hypothesis, "circuit", None)

        if not circuit:
            return QuantumCriticVerdict({
                "valid": False,
                "score": 0.0,
                "reason": "La hipótesis no contiene una estructura de circuito válida."
            })

        qubits = circuit.get("qubits", 0)
        gates = circuit.get("gates", [])

        # 1. Validez estructural básica
        if qubits <= 0:
            return QuantumCriticVerdict({
                "valid": False,
                "score": 0.0,
                "reason": "El número de qubits debe ser mayor que 0."
            })

        allowed_gates = {"H", "X", "Y", "Z", "RX", "RY", "RZ", "CNOT", "CX", "CZ", "SWAP"}
        for idx, gate in enumerate(gates):
            g_type = gate.get("type")
            g_qubits = gate.get("qubits", [])

            if g_type not in allowed_gates:
                return QuantumCriticVerdict({
                    "valid": False,
                    "score": 0.0,
                    "reason": f"Puerta no permitida '{g_type}' en la posición {idx}."
                })

            for q in g_qubits:
                if q < 0 or q >= qubits:
                    return QuantumCriticVerdict({
                        "valid": False,
                        "score": 0.0,
                        "reason": f"Índice de qubit {q} fuera de rango [0, {qubits - 1}] en la posición {idx}."
                    })

        # 2. Calcular conteo de puertas y estimación de profundidad
        gate_count = len(gates)
        qubit_depths = [0] * qubits
        for gate in gates:
            g_qubits = gate.get("qubits", [])
            max_d = max([qubit_depths[q] for q in g_qubits]) if g_qubits else 0
            for q in g_qubits:
                qubit_depths[q] = max_d + 1
        depth = max(qubit_depths) if qubit_depths else 0

        # 3. Calcular heurística de puntuación estructural
        score = 1.0
        if gate_count > 10:
            score -= (gate_count - 10) * 0.05
        if depth > 5:
            score -= (depth - 5) * 0.1

        score = max(0.1, min(1.0, round(score, 2)))

        return QuantumCriticVerdict({
            "valid": True,
            "score": score,
            "reason": f"Circuito estructuralmente válido con {gate_count} puertas y profundidad {depth}."
        })
