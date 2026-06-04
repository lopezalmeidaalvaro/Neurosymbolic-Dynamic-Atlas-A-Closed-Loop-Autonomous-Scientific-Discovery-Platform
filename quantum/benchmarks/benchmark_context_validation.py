import os
import sys
import math
import random
import statistics
import copy
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.critics.quantum_critic import QuantumCritic
from quantum.evolution.evolution_engine import EvolutionEngine
from quantum.evolution.population_manager import QuantumPopulationManager
from quantum.memory.quantum_memory import QuantumMemory
from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
from quantum.knowledge.representation_analyzer import RepresentationAnalyzer
from quantum.knowledge.context_schema import Context

def get_bell_target():
    return [1.0 / math.sqrt(2), 0.0, 0.0, 1.0 / math.sqrt(2)]

def get_ghz_target():
    return [1.0 / math.sqrt(2), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0 / math.sqrt(2)]

def check_convergence(report):
    return report["best_fidelity"] >= 0.99 and report["best_score"] > 0.0

def clone_memory(source_memory):
    new_memory = QuantumMemory()
    new_memory._store = copy.deepcopy(source_memory._store)
    return new_memory

def pretrain_bell(seed, max_gens=50):
    memory = QuantumMemory()
    population_size = 10
    seed_circuits_bell = [{"qubits": 2, "gates": []} for _ in range(population_size)]
    population_manager_bell = QuantumPopulationManager(
        qubits=2,
        population_size=population_size,
        max_gates=12,
        seed=seed,
        seed_circuits=seed_circuits_bell
    )
    engine_bell = EvolutionEngine(
        population_manager=population_manager_bell,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=get_bell_target(),
        memory=memory,
        elitism=2,
        random_injection_rate=0.0,
        diversity_threshold=0.0,
        pattern_injection_rate=0.2,
    )
    
    historical_evals = []
    task_name = "bell_state"
    qubits = 2
    
    for gen in range(max_gens):
        report = engine_bell.evolve_generation()
        for ev in engine_bell.last_evaluations:
            historical_evals.append({
                "circuit": copy.deepcopy(ev.circuit),
                "fidelity": ev.fidelity,
                "score": ev.score,
                "generation": engine_bell.generation,
                "task": task_name,
                "qubits": qubits,
                "converged": ev.fidelity >= 0.99
            })
            
        if check_convergence(report):
            break
            
    return memory, historical_evals

def run_ghz_engine(seed, memory, max_gens=50):
    population_size = 10
    seed_circuits_ghz = [{"qubits": 3, "gates": []} for _ in range(population_size)]
    population_manager_ghz = QuantumPopulationManager(
        qubits=3,
        population_size=population_size,
        max_gates=12,
        seed=seed,
        seed_circuits=seed_circuits_ghz
    )
    engine_ghz = EvolutionEngine(
        population_manager=population_manager_ghz,
        sandbox=QiskitQuantumSandbox(),
        critic=QuantumCritic(alpha=0.01, beta=0.001),
        target_state=get_ghz_target(),
        memory=memory,
        elitism=2,
        random_injection_rate=0.0,
        diversity_threshold=0.0,
        pattern_injection_rate=0.2,
    )
    
    historical_evals = []
    task_name = "ghz_state"
    qubits = 3
    
    for gen in range(max_gens):
        report = engine_ghz.evolve_generation()
        for ev in engine_ghz.last_evaluations:
            historical_evals.append({
                "circuit": copy.deepcopy(ev.circuit),
                "fidelity": ev.fidelity,
                "score": ev.score,
                "generation": engine_ghz.generation,
                "task": task_name,
                "qubits": qubits,
                "converged": ev.fidelity >= 0.99
            })
            
        if check_convergence(report):
            break
            
    return engine_ghz, historical_evals

def perform_cross_validation():
    seeds = [1, 42, 123, 999, 2025]
    all_evals = []
    all_records = []
    
    print("Harvesting evaluations for cross-validation...")
    for seed in seeds:
        bell_memory, bell_evals = pretrain_bell(seed)
        all_evals.extend(bell_evals)
        
        ghz_mem = clone_memory(bell_memory)
        engine_ghz, ghz_evals = run_ghz_engine(seed, ghz_mem)
        all_evals.extend(ghz_evals)
        all_records.extend(engine_ghz.injected_patterns_records)
        
    print(f"Harvested {len(all_evals)} evaluations, {len(all_records)} causal records.")
    
    # 80/20 train/test split (RNG isolated split)
    random.seed(42)
    random.shuffle(all_evals)
    random.shuffle(all_records)
    
    split_eval_idx = int(len(all_evals) * 0.8)
    train_evals = all_evals[:split_eval_idx]
    test_evals = all_evals[split_eval_idx:]
    
    split_rec_idx = int(len(all_records) * 0.8)
    train_records = all_records[:split_rec_idx]
    test_records = all_records[split_rec_idx:]
    
    analyzer = RepresentationAnalyzer()
    
    # Analyze train set to discover top patterns for each level
    train_analysis = analyzer.analyze(train_evals, train_records)
    
    levels_to_test = [
        "LEVEL_1_RAW_PATTERN",
        "LEVEL_2_MOTIF",
        "LEVEL_4_SCAFFOLD",
        "LEVEL_5_CONTEXT_AWARE"
    ]
    
    results = {}
    for lvl in levels_to_test:
        train_results = train_analysis.get(lvl, [])
        if not train_results:
            results[lvl] = {
                "ig": 0.0,
                "p_conv": 0.0,
                "transfer_utility": 0.0
            }
            continue
            
        # Select top pattern based on train set information gain
        best_pattern_repr = train_results[0]["representation"]
        
        # 1. Compute Out-of-Sample Information Gain
        ig_oos = analyzer.compute_information_gain(best_pattern_repr, lvl, test_evals)
        
        # 2. Compute Out-of-Sample Conditional Convergence Probability
        matching_evals = [e for e in test_evals if analyzer.circuit_contains(e, lvl, best_pattern_repr)]
        if matching_evals:
            p_conv_oos = sum(1 for e in matching_evals if e.get("converged", False)) / len(matching_evals)
        else:
            p_conv_oos = 0.0
            
        # 3. Compute Out-of-Sample Transfer Utility (delta score)
        matching_records = [r for r in test_records if analyzer.does_record_match(r, lvl, best_pattern_repr)]
        deltas = [r.get("delta_score") for r in matching_records if r.get("delta_score") is not None]
        utility_oos = statistics.mean(deltas) if deltas else 0.0
        
        results[lvl] = {
            "best_pattern": best_pattern_repr,
            "ig": round(ig_oos, 4),
            "p_conv": round(p_conv_oos, 4),
            "transfer_utility": round(utility_oos, 4)
        }
        
    print("\n======================================================================")
    print("CROSS-VALIDATION RESULTS (OUT-OF-SAMPLE)")
    print("======================================================================")
    for lvl, metrics in results.items():
        print(f"{lvl}:")
        print(f"  Best Pattern (Train): {metrics['best_pattern']}")
        print(f"  OOS Info Gain:        {metrics['ig']:.4f}")
        print(f"  OOS P(convergence):   {metrics['p_conv']:.4f}")
        print(f"  OOS Transfer Utility: {metrics['transfer_utility']:.4f}")
    print("======================================================================\n")
    
    return results

if __name__ == "__main__":
    perform_cross_validation()
