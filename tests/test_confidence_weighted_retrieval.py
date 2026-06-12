import math
import pytest
from quantum.memory.quantum_memory import QuantumMemory
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.critics.quantum_critic import QuantumCritic


def test_confidence_weighted_retrieval_memory():
    memory = QuantumMemory()

    # Store patterns
    patterns = [
        {
            "pattern_id": "pat_high",
            "sequence": ["H", "CNOT"],
            "frequency": 12,
            "avg_score": 0.9,
            "representation": "H->CNOT",
        },
        {
            "pattern_id": "pat_toxic",
            "sequence": ["H(q0)", "CNOT(q0,q1)"],
            "frequency": 8,
            "avg_score": 0.5,
            "representation": "H(q0)->CNOT(q0,q1)",
        },
        {
            "pattern_id": "pat_noise",
            "sequence": ["X(q0)", "X(q0)"],
            "frequency": 4,
            "avg_score": 0.2,
            "representation": "X(q0)->X(q0)",
        },
        {
            "pattern_id": "pat_neutral",
            "sequence": ["CNOT", "H"],
            "frequency": 3,
            "avg_score": 0.6,
            "representation": "CNOT->H",
        },
    ]
    memory.store("quantum:distillation:patterns", patterns)

    # Store causal records
    causal_records = [
        {"pattern": "H->CNOT", "delta_score": 0.15, "survival_status": True},
        {"pattern": "H->CNOT", "delta_score": 0.25, "survival_status": True},
        {
            "pattern": "H(q0)->CNOT(q0,q1)",
            "delta_score": -0.2,
            "survival_status": False,
        },
    ]
    memory.store("quantum:distillation:causal_records", causal_records)

    # Store knowledge graph nodes and edges to satisfy PatternValuationEngine
    knowledge_graph = {
        "nodes": {
            "pattern_pat_high": {
                "type": "Pattern",
                "attributes": {
                    "sequence": ["H", "CNOT"],
                    "type": "repeated_subsequence",
                },
            },
            "pattern_pat_toxic": {
                "type": "Pattern",
                "attributes": {
                    "sequence": ["H(q0)", "CNOT(q0,q1)"],
                    "type": "entanglement_motif",
                },
            },
            "pattern_pat_noise": {
                "type": "Pattern",
                "attributes": {
                    "sequence": ["X(q0)", "X(q0)"],
                    "type": "repeated_subsequence",
                },
            },
            "pattern_pat_neutral": {
                "type": "Pattern",
                "attributes": {
                    "sequence": ["CNOT", "H"],
                    "type": "repeated_subsequence",
                },
            },
            "circ_1": {
                "type": "Circuit",
                "attributes": {"raw": True, "score": 0.98, "fidelity": 1.0},
            },
        },
        "edges": [
            {
                "source": "circ_1",
                "target": "pattern_pat_high",
                "type": "contains_pattern",
            }
        ],
    }
    memory.store("quantum:distillation:knowledge_graph", knowledge_graph)

    # Retrieve active patterns
    active = memory.get_active_patterns()

    # Must filter out TOXIC (pat_toxic) and NOISE/JUNK (pat_noise)
    active_representations = {p["representation"] for p in active}
    assert "H->CNOT" in active_representations
    assert "CNOT->H" in active_representations
    assert "H(q0)->CNOT(q0,q1)" not in active_representations
    assert "X(q0)->X(q0)" not in active_representations

    # Check weight of pat_high ("H->CNOT"):
    # frequency = 12 >= 10. confidence_factor = 1.0 + log10(12/10) = 1.07918
    # p_conv = 1.0 (since circ_1 containing it has fidelity = 1.0 >= 0.99)
    # survival_prob = 1.0 (2 out of 2 causal records survived)
    # base_weight = 1.0 * 1.0 = 1.0
    # weight = 1.07918
    pat_high_weight = next(
        p["weight"] for p in active if p["representation"] == "H->CNOT"
    )
    assert pytest.approx(pat_high_weight, rel=1e-4) == (
        1.0 * 1.0 * (1.0 + math.log10(1.2))
    )

    # Check weight of pat_neutral ("CNOT->H"):
    # frequency = 3 < 10. confidence_factor = 3 / 10 = 0.3
    # P_conv = 0.0, survival_prob = 0.0 (no circuits/records) -> base_weight = 1e-4
    # weight = 1e-4 * 0.3 = 3e-5
    pat_neutral_weight = next(
        p["weight"] for p in active if p["representation"] == "CNOT->H"
    )
    assert pytest.approx(pat_neutral_weight, rel=1e-4) == 3e-5


def test_evolution_engine_kdi_calculation():
    population_manager = QuantumPopulationManager(
        qubits=2, population_size=5, max_gates=8, seed=10
    )
    memory = QuantumMemory()

    engine = EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=[1.0, 0, 0, 0],
        memory=memory,
        elitism=1,
        pattern_injection_rate=0.0,
    )

    # Mock some pending injections of previous generation
    engine.pending_injections_this_gen = [
        {
            "pattern": "H->CNOT",
            "child_hash": "h1",
            "generation": 0,
            "discarded_in_loop": False,
        },
        {
            "pattern": "H->CNOT",
            "child_hash": "h2",
            "generation": 0,
            "discarded_in_loop": False,
        },
        {
            "pattern": "X->H",
            "child_hash": "h3",
            "generation": 0,
            "discarded_in_loop": False,
        },
        {
            "pattern": "X->H",
            "child_hash": "h4",
            "generation": 0,
            "discarded_in_loop": True,
        },  # Discarded, shouldn't count in KDI
    ]

    # Run evolve_generation (this calls evaluate_population, checks survival, calculates KDI, and clears pending)
    report = engine.evolve_generation()

    # Shannon entropy of: 2 "H->CNOT", 1 "X->H". Total = 3.
    # p1 = 2/3, p2 = 1/3
    # KDI = - (2/3 * log2(2/3) + 1/3 * log2(1/3))
    expected_kdi = -((2 / 3) * math.log2(2 / 3) + (1 / 3) * math.log2(1 / 3))

    assert pytest.approx(engine.last_generation_kdi) == expected_kdi
