import os
import json
import pytest
from quantum.discovery.autonomous_scaffold_generator import AutonomousScaffoldGenerator
from quantum.discovery.discovery_benchmark import run_discovery_benchmark

def test_similarity_and_novelty():
    generator = AutonomousScaffoldGenerator()
    
    # Test identical sequence similarity is 1.0
    sim = generator.compute_similarity(["H", "CNOT"], ["H", "CNOT"])
    assert sim == 1.0
    
    # Test dissimilar sequence similarity is low
    sim_low = generator.compute_similarity(["H", "CNOT"], ["RY", "T", "S"])
    assert sim_low < 0.5
    
    # Test novelty check against standard Bell motif
    # A sequence identical to Bell should be rejected (is_novel = False)
    assert not generator.is_novel(["H", "CNOT"])
    # A completely new sequence should be accepted (is_novel = True)
    assert generator.is_novel(["RY", "T", "S", "RY", "T"])

def test_pre_filter_transferable():
    generator = AutonomousScaffoldGenerator()
    
    # Same qubit sizes and same tasks -> should be accepted (True)
    assert generator.pre_filter_transferable(2, 2, "bell_state", "bell_state")
    
    # Different qubits but same task -> accepted (True)
    assert generator.pre_filter_transferable(2, 3, "bell_state", "ghz_state")
    
    # Different qubits AND different task families (e.g. Bell Clifford to Variational) -> rejected (False)
    # Bell is Clifford task, variational_ansatz is rotation task.
    # Qubit difference > 0, and gate distribution distance is estimated at 0.8 (> 0.5)
    assert not generator.pre_filter_transferable(2, 3, "bell_state", "variational_ansatz")

def test_evolutionary_operators():
    generator = AutonomousScaffoldGenerator()
    seq = ["H", "CNOT", "RY"]
    
    # Test mutation returns valid mutated sequence
    mutated = generator.mutate_sequence(seq)
    assert isinstance(mutated, list)
    assert len(mutated) > 0
    
    # Test crossover
    parent1 = ["H", "CNOT", "RY", "RX"]
    parent2 = ["RY", "T", "S", "H"]
    c1, c2 = generator.crossover_sequences(parent1, parent2)
    assert isinstance(c1, list)
    assert isinstance(c2, list)

def test_discovery_loop_small():
    generator = AutonomousScaffoldGenerator()
    # Run a small discovery loop to check execution
    discovered = generator.discover_scaffolds(generations=2, pop_size=4)
    assert len(discovered) > 0
    assert "sequence" in discovered[0]
    assert "utility" in discovered[0]
    assert "synergy_score" in discovered[0]

def test_discovery_benchmark():
    # Run the benchmark (with mock configurations inside)
    # We can temporarily patch the generations/pop_size or just let it run standard
    # Let's verify it executes successfully
    report = run_discovery_benchmark()
    assert "verdict" in report
    assert "comparison" in report
    assert "outperforms" in report
    assert os.path.exists("discovery_benchmark_report.json")
    assert os.path.exists("docs/AUTONOMOUS_DISCOVERY_REPORT.md")
