import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.critics.quantum_critic import QuantumCritic
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.factories.quantum_factory import create_quantum_container
from quantum.memory.quantum_memory import QuantumMemory
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox


def bell_target():
    return [1.0 / math.sqrt(2), 0.0, 0.0, 1.0 / math.sqrt(2)]


def ghz_target():
    return [1.0 / math.sqrt(2), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0 / math.sqrt(2)]


def make_engine(qubits, target_state, seed, population_size=30):
    memory = QuantumMemory()
    population_manager = QuantumPopulationManager(
        qubits=qubits,
        population_size=population_size,
        max_gates=qubits * 4,
        seed=seed,
    )
    return EvolutionEngine(
        population_manager=population_manager,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=target_state,
        memory=memory,
        elitism=2,
        random_injection_rate=0.05,
    )


def test_population_manager_initializes_valid_circuits():
    manager = QuantumPopulationManager(
        qubits=3,
        population_size=25,
        max_gates=10,
        seed=7,
    )

    assert len(manager.population) == 25
    assert all(manager.is_valid_circuit(circuit) for circuit in manager.population)
    assert any(
        gate["type"] == "CNOT"
        for circuit in manager.population
        for gate in circuit["gates"]
    )


def test_bell_state_discovery_improves_average_fitness():
    engine = make_engine(qubits=2, target_state=bell_target(), seed=123)

    reports = engine.run(generations=8)

    assert reports[-1]["best_fidelity"] == pytest.approx(1.0, abs=1e-7)
    assert reports[-1]["best_score"] >= reports[0]["best_score"]
    assert (
        reports[-1]["average_population_score"]
        > reports[0]["average_population_score"]
    )
    assert reports[-1]["best_circuit"]["qubits"] == 2
    assert any(
        gate["type"] == "CNOT" for gate in reports[-1]["best_circuit"]["gates"]
    )


def test_ghz_convergence_reaches_high_fidelity():
    engine = make_engine(qubits=3, target_state=ghz_target(), seed=321)

    reports = engine.run(generations=8)

    assert reports[-1]["best_fidelity"] == pytest.approx(1.0, abs=1e-7)
    assert reports[-1]["best_score"] >= 0.95
    assert reports[-1]["average_population_score"] > reports[0]["average_population_score"]
    assert len(reports[-1]["best_circuit"]["gates"]) <= 4


def test_evolution_preserves_diversity_and_memory_history():
    engine = make_engine(qubits=2, target_state=bell_target(), seed=77)

    reports = engine.run(generations=6)

    assert min(report["diversity_metric"] for report in reports) >= 0.25
    assert engine.memory.retrieve("quantum:evolution:history") == reports
    assert engine.memory.retrieve("quantum:evolution:best_score") == reports[-1]["best_score"]
    assert engine.memory.retrieve("quantum:evolution:mutation_history")
    assert any(
        any(gate["type"] == "CNOT" for gate in circuit["gates"])
        for circuit in engine.population_manager.population
    )


def test_evolution_reproducible_across_equal_seeds():
    first = make_engine(qubits=2, target_state=bell_target(), seed=2026)
    second = make_engine(qubits=2, target_state=bell_target(), seed=2026)

    assert first.run(generations=5) == second.run(generations=5)


def test_quantum_container_exposes_plugin_compatible_evolution_engine():
    container = create_quantum_container()

    assert isinstance(container.evolution_engine, EvolutionEngine)
    report = container.evolution_engine.evolve_generation()
    assert report["best_fidelity"] >= 0.0
    assert "best_circuit" in report
