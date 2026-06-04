import math
import sys
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.knowledge.canonicalizer import QuantumCircuitCanonicalizer
from quantum.knowledge.quantum_pattern_extractor import QuantumPatternExtractor
from quantum.knowledge.knowledge_graph import QuantumKnowledgeGraph
from quantum.memory.quantum_memory import QuantumMemory
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic


def test_canonicalizer_simplifications():
    """Valida que el canonicalizador simplifique de forma correcta pares autoinversos y combinaciones de ángulos."""
    # Caso 1: Cancelación directa H H
    circuit_1 = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "H", "qubits": [0]},
            {"type": "X", "qubits": [1]}
        ]
    }
    canonical_1 = QuantumCircuitCanonicalizer.canonicalize(circuit_1)
    assert len(canonical_1["gates"]) == 1
    assert canonical_1["gates"][0]["type"] == "X"
    assert canonical_1["gates"][0]["qubits"] == [1]

    # Caso 2: Cancelación a través de compuertas conmutativas en qubits disjuntos
    circuit_2 = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "X", "qubits": [1]},
            {"type": "H", "qubits": [0]}
        ]
    }
    canonical_2 = QuantumCircuitCanonicalizer.canonicalize(circuit_2)
    assert len(canonical_2["gates"]) == 1
    assert canonical_2["gates"][0]["type"] == "X"
    assert canonical_2["gates"][0]["qubits"] == [1]

    # Caso 3: Cancelación CNOT CNOT
    circuit_3 = {
        "qubits": 2,
        "gates": [
            {"type": "CNOT", "qubits": [0, 1]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    canonical_3 = QuantumCircuitCanonicalizer.canonicalize(circuit_3)
    assert len(canonical_3["gates"]) == 0

    # Caso 4: Fusión de ángulos de rotación continuos
    circuit_4 = {
        "qubits": 1,
        "gates": [
            {"type": "RX", "qubits": [0], "theta": 0.5},
            {"type": "RX", "qubits": [0], "theta": 0.3}
        ]
    }
    canonical_4 = QuantumCircuitCanonicalizer.canonicalize(circuit_4)
    assert len(canonical_4["gates"]) == 1
    assert canonical_4["gates"][0]["type"] == "RX"
    assert pytest.approx(canonical_4["gates"][0]["theta"]) == 0.8


def test_pattern_extractor():
    """Valida la extracción correcta de patrones basados en secuencias de compuertas y entrelazamiento."""
    extractor = QuantumPatternExtractor(min_length=2, max_length=3, score_threshold=0.5)

    class MockEvaluation:
        def __init__(self, circuit, score, valid=True):
            self.circuit = circuit
            self.score = score
            self.valid = valid

        def to_dict(self):
            return {"circuit": self.circuit, "score": self.score, "valid": self.valid}

    # Circuito 1: H -> CNOT
    c1 = {
        "qubits": 2,
        "gates": [
            {"type": "H", "qubits": [0]},
            {"type": "CNOT", "qubits": [0, 1]}
        ]
    }
    # Circuito 2: RY -> CNOT -> RY
    c2 = {
        "qubits": 2,
        "gates": [
            {"type": "RY", "qubits": [0], "theta": 0.5},
            {"type": "CNOT", "qubits": [0, 1]},
            {"type": "RY", "qubits": [0], "theta": 0.5}
        ]
    }

    evals = [MockEvaluation(c1, 0.98), MockEvaluation(c2, 0.95)]
    patterns = extractor.extract_patterns(evals)

    representations = {p["representation"] for p in patterns}
    # Debe haber motivos tipo-secuencia y motivos estructurales qubit-relativos
    assert "H->CNOT" in representations or "H(q0)->CNOT(q0,q1)" in representations
    assert "RY->CNOT->RY" in representations or "RY(q0)->CNOT(q0,q1)->RY(q0)" in representations

    # Validar que los objetos patrón tengan el formato y tipos esperados
    for p in patterns:
        assert "pattern_id" in p
        assert "frequency" in p
        assert "avg_score" in p
        assert p["frequency"] > 0
        assert p["type"] in ("repeated_subsequence", "entanglement_motif", "structural_motif")


def test_knowledge_graph_consistency():
    """Valida la consistencia estructural del grafo de conocimiento in-memory."""
    graph = QuantumKnowledgeGraph()
    
    graph.add_node("gen_0", "Generation", number=0)
    graph.add_node("c_opt", "Circuit", raw=True, score=0.98)
    graph.add_node("c_can", "Circuit", raw=False)
    
    graph.add_edge("c_opt", "gen_0", "discovered_in_generation")
    graph.add_edge("c_opt", "c_can", "equivalent_to")

    nodes = graph.get_nodes_by_type("Circuit")
    assert len(nodes) == 2
    assert "c_opt" in nodes
    assert "c_can" in nodes

    edges = graph.get_edges_by_type("equivalent_to")
    assert len(edges) == 1
    assert edges[0]["source"] == "c_opt"
    assert edges[0]["target"] == "c_can"


def test_memory_persistence():
    """Valida que los patrones destilados se almacenen y recuperen de forma estructurada y filtrable."""
    memory = QuantumMemory()
    
    patterns = [
        {"pattern_id": "pat_1", "sequence": ["H", "CNOT"], "frequency": 12, "avg_score": 0.98, "representation": "H->CNOT"}
    ]
    memory.store("quantum:distillation:patterns", patterns)
    memory.store("quantum:distillation:task:bell_state:patterns", [
        {"task": "bell_state", "pattern": "H->CNOT", "frequency": 12, "avg_score": 0.98}
    ])

    # Recuperación general
    pats = memory.query_patterns()
    assert len(pats) == 1
    assert pats[0]["pattern_id"] == "pat_1"

    # Recuperación filtrada por tarea
    pats_bell = memory.query_patterns(task="bell_state")
    assert len(pats_bell) == 1
    assert pats_bell[0]["task"] == "bell_state"
    assert pats_bell[0]["frequency"] == 12


def test_evolution_distillation_integration():
    """Valida la integración completa de la Capa de Destilación en el ciclo de EvolutionEngine."""
    bell_target = [1.0 / math.sqrt(2), 0.0, 0.0, 1.0 / math.sqrt(2)]
    memory = QuantumMemory()
    population_manager = QuantumPopulationManager(
        qubits=2,
        population_size=10,
        max_gates=8,
        seed=42,
    )
    engine = EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=bell_target,
        memory=memory,
        elitism=2
    )

    # Ejecutar una generación
    report = engine.evolve_generation()

    # Verificar que el reporte contenga las métricas de destilación de conocimiento
    assert "patterns_discovered" in report
    assert "canonical_compression_ratio" in report
    assert "knowledge_growth" in report

    # Verificar que se hayan actualizado las variables del motor
    assert len(engine.discovered_patterns_archive) > 0
    assert len(engine.knowledge_graph.nodes) > 0

    # Verificar almacenamiento en memoria
    assert memory.retrieve("quantum:distillation:canonical_circuits") is not None
    assert memory.retrieve("quantum:distillation:patterns") is not None
    
    graph_data = memory.get_knowledge_graph()
    assert len(graph_data["nodes"]) > 0
    assert len(graph_data["edges"]) > 0

    # Verificar que las métricas persistidas tengan el formato correcto
    metrics_history = memory.retrieve("quantum:distillation:metrics_history")
    assert len(metrics_history) == 1
    assert metrics_history[0]["generation"] == 0
    assert metrics_history[0]["canonical_compression_ratio"] >= 1.0


def test_knowledge_guided_mutation_logic():
    """Valida la inyección de patrones en el motor de mutación, el mapeo de qubits y el fallback."""
    # Configurar población y sandbox
    population_manager = QuantumPopulationManager(
        qubits=3,
        population_size=5,
        max_gates=8,
        seed=123,
    )
    
    # 1. Fallback: Memoria vacía
    memory_empty = QuantumMemory()
    engine_fallback = EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=[1.0, 0, 0, 0, 0, 0, 0, 0],
        memory=memory_empty,
        pattern_injection_rate=1.0, # Intentar siempre
    )
    
    parent = {"qubits": 3, "gates": [{"type": "H", "qubits": [0]}]}
    # Al no haber patrones en memoria, debe mutar usando fallback aleatorio estándar
    child = engine_fallback.mutate(parent)
    assert child is not None
    assert engine_fallback.patterns_injected == 0
    
    # 2. Con patrones en memoria: verificar inyección y mapeo
    memory_populated = QuantumMemory()
    patterns = [
        # Patrón válido de longitud <= 3
        {
            "pattern_id": "pat_cnot",
            "sequence": ["H(q0)", "CNOT(q0,q1)"],
            "frequency": 10,
            "avg_score": 0.95,
            "type": "entanglement_motif",
            "representation": "H(q0)->CNOT(q0,q1)"
        },
        # Patrón inválido de longitud > 3 (no debe inyectarse)
        {
            "pattern_id": "pat_long",
            "sequence": ["H(q0)", "CNOT(q0,q1)", "X(q2)", "H(q1)"],
            "frequency": 15,
            "avg_score": 0.99,
            "type": "structural_motif",
            "representation": "H(q0)->CNOT(q0,q1)->X(q2)->H(q1)"
        }
    ]
    memory_populated.store("quantum:distillation:patterns", patterns)
    
    engine_inject = EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=[1.0, 0, 0, 0, 0, 0, 0, 0],
        memory=memory_populated,
        pattern_injection_rate=1.0, # Intentar siempre
    )
    
    # Mutar varias veces para asegurar que se inyecta el patrón corto y no el largo
    # (el largo tiene mayor score, por lo que si no se filtrara, se elegiría primero)
    for _ in range(5):
        child = engine_inject.mutate(parent)
        assert child is not None
        
    # Verificar que al menos alguna inyección se haya registrado
    assert engine_inject.patterns_injected > 0
    
    # Verificar mapeo coherente y seguridad de índices
    # Buscamos en el historial de mutaciones las inyecciones exitosas
    injected_ops = [h for h in engine_inject.mutation_history if h["operation"] == "inject_pattern"]
    assert len(injected_ops) > 0
    
    # Vamos a realizar una mutación controlada para verificar el mapeo de qubits de H(q0) y CNOT(q0,q1)
    # H(q0) y CNOT(q0,q1) deben mapear q0 al mismo qubit físico y q1 a otro qubit físico diferente.
    # Además los índices físicos deben estar en [0, 2] (qubits = 3).
    test_parent = {"qubits": 3, "gates": []}
    child = engine_inject.mutate(test_parent)
    gates = child.get("gates", [])
    
    # Busquamos las compuertas correspondientes al patrón inyectado
    # El patrón es H -> CNOT. Dado que el padre estaba vacío, el hijo debe contener
    # exactamente un H y un CNOT inyectados.
    h_gates = [g for g in gates if g["type"] == "H"]
    cnot_gates = [g for g in gates if g["type"] == "CNOT"]
    
    assert len(h_gates) == 1
    assert len(cnot_gates) == 1
    
    h_qubit = h_gates[0]["qubits"][0]
    cnot_ctrl = cnot_gates[0]["qubits"][0]
    cnot_tgt = cnot_gates[0]["qubits"][1]
    
    # Coherencia del mapeo: q0 de H(q0) y CNOT(q0,q1) debe ser el mismo qubit físico.
    assert h_qubit == cnot_ctrl
    # q1 debe ser diferente
    assert cnot_tgt != h_qubit
    # Rango de qubits físicos
    assert 0 <= h_qubit < 3
    assert 0 <= cnot_tgt < 3
