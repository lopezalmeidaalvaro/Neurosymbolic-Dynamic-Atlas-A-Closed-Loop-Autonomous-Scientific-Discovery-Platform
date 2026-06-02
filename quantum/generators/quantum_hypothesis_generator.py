import random
from typing import Dict, Any
from core.abstractions.base_hypothesis_generator import BaseHypothesisGenerator

class QuantumHypothesisGenerator(BaseHypothesisGenerator):
    """
    Generador de hipótesis científicas para el dominio cuántico.
    Genera y muta circuitos cuánticos simples representados en JSON puro.
    """
    
    def propose(self, context: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """
        Propone una nueva hipótesis cuántica con un circuito candidato.
        """
        qubits = 2
        gates = [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
        
        circuit = {
            "qubits": qubits,
            "gates": gates
        }
        
        return {
            "hypothesis_text": f"Un estado entrelazado GHZ de {qubits} qubits se puede preparar con profundidad <= 2.",
            "prediction": "depth <= 2",
            "variables_involved": ["qubits", "depth"],
            "confidence_prior": 0.9,
            "circuit": circuit
        }

    def mutate(self, hypothesis: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """
        Muta una hipótesis cuántica agregando o alterando puertas en el circuito.
        """
        circuit = hypothesis.get("circuit", {"qubits": 2, "gates": []})
        gates = list(circuit.get("gates", []))
        qubits = circuit.get("qubits", 2)
        
        gate_types = ["H", "X", "RX", "RY", "CNOT"]
        g_type = random.choice(gate_types)
        
        if g_type == "CNOT":
            gates.append({"type": "CNOT", "qubits": [0, 1]})
        elif g_type in ["RX", "RY"]:
            gates.append({
                "type": g_type, 
                "qubits": [random.randint(0, qubits - 1)], 
                "theta": round(random.uniform(0, 3.1415), 4)
            })
        else:
            gates.append({"type": g_type, "qubits": [random.randint(0, qubits - 1)]})
            
        mutated_circuit = {
            "qubits": qubits,
            "gates": gates
        }
        
        return {
            "hypothesis_text": hypothesis.get("hypothesis_text", "") + " (mutated)",
            "prediction": f"depth <= {len(gates)}",
            "variables_involved": hypothesis.get("variables_involved", ["qubits", "depth"]),
            "confidence_prior": round(max(0.1, hypothesis.get("confidence_prior", 0.9) - 0.05), 2),
            "circuit": mutated_circuit
        }
