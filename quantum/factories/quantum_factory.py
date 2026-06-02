import json
import math
from typing import Dict, Any
from core.orchestration.scientific_container import ScientificContainer
from quantum.generators.quantum_hypothesis_generator import QuantumHypothesisGenerator
from quantum.critics.quantum_critic import QuantumCritic
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.memory.quantum_memory import QuantumMemory
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.evolution.population_manager import QuantumPopulationManager

class QuantumLLMReasoner:
    """
    Stub LLM Reasoner específico para el dominio cuántico.
    Evita interactuar con LLMs externos o caer en el mock clásico del orquestador.
    """
    
    def generate_hypothesis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "hypothesis_text": "Un estado entrelazado Bell de 2 qubits se puede preparar con profundidad <= 2 usando H y CNOT.",
            "prediction": "depth <= 2",
            "variables_involved": ["qubits", "depth"],
            "confidence_prior": 0.9,
            "circuit": {
                "qubits": 2,
                "gates": [
                    {"type": "H", "qubits": [0]},
                    {"type": "CNOT", "qubits": [0, 1]}
                ]
            }
        }

    def design_experiment(self, hypothesis: Dict[str, Any], available_data: Any, available_methods: Any) -> Dict[str, Any]:
        circuit = hypothesis.get("circuit", {
            "qubits": 2,
            "gates": [
                {"type": "H", "qubits": [0]},
                {"type": "CNOT", "qubits": [0, 1]}
            ]
        })
        return {
            "experiment_description": "Validación de la profundidad del circuito cuántico de preparación Bell mediante sandbox cuántico.",
            "dataset": "bell_state",
            "method": "circuit_ansatz",
            "metrics": ["gate_count", "depth"],
            "falsification_criterion": "depth > 2",
            "python_code": json.dumps(circuit)
        }

    def interpret_results(self, hypothesis: Dict[str, Any], experiment: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        depth = results.get("depth", 0)
        verdict = "validated" if depth <= 2 else "rejected"
        return {
            "verdict": verdict,
            "confidence_posterior": 0.95 if verdict == "validated" else 0.1,
            "reasoning": f"La ejecución del circuito confirmó una profundidad real de {depth}, lo que cumple el límite de <= 2.",
            "refined_hypothesis": "El circuito de preparación Bell de 2 qubits es óptimo en profundidad 2.",
            "next_steps": "Expandir la hipótesis a la preparación de estados W."
        }


def create_quantum_container() -> ScientificContainer:
    """
    Ensambla y configura los componentes cuánticos en un ScientificContainer.
    """
    container = ScientificContainer()
    
    # Registrar componentes cuánticos
    generator = QuantumHypothesisGenerator()
    critic = QuantumCritic()
    sandbox = QiskitQuantumSandbox()
    memory = QuantumMemory()

    container.register_generator(generator)
    container.register_critic(critic)
    container.register_sandbox(sandbox)
    container.register_memory(memory)
    container.register_llm_reasoner(QuantumLLMReasoner())

    bell_target = [1.0 / math.sqrt(2), 0.0, 0.0, 1.0 / math.sqrt(2)]
    population_manager = QuantumPopulationManager(
        qubits=2,
        population_size=40,
        max_gates=8,
        seed=42,
    )
    container.register_evolution_engine(
        EvolutionEngine(
            population_manager=population_manager,
            sandbox=sandbox,
            critic=critic,
            target_state=bell_target,
            memory=memory,
        )
    )
    
    return container
