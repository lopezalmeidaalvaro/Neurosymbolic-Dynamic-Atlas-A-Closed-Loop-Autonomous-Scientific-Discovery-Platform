import os
import json
import random
from typing import Dict, Any, List
from quantum.law_discovery.scientific_observer import ScientificObserver
from quantum.law_discovery.pattern_miner import PatternMiner
from quantum.law_discovery.symbolic_law_generator import SymbolicLawGenerator

class SyntheticLawBenchmark:
    """
    Component F: Synthetic Law Recovery Benchmark.
    Injects hidden laws into a dataset and checks if the miner/generator can recover them.
    """

    def __init__(self, temp_data_path: str = "temp_synthetic_dataset.json", report_path: str = "synthetic_law_recovery_report.json"):
        self.temp_data_path = temp_data_path
        self.report_path = report_path

    def run_benchmark(self) -> Dict[str, Any]:
        print("Running Synthetic Law Recovery Benchmark...")
        rng = random.Random(99)
        
        # 1. Create a validation dataset with 500 records
        # Injected Laws:
        # Law 1: success_transfer = (gate_entropy < 0.25)
        # Law 2: success_synergy = (stabilizer_overlap > 0.6 and tensor_rank < 3)
        n_samples = 500
        synthetic_records = []
        
        for _ in range(n_samples):
            gate_entropy = rng.uniform(0.05, 0.8)
            stabilizer_overlap = rng.uniform(0.0, 1.0)
            tensor_rank = rng.randint(1, 20)
            clifford_ratio = rng.uniform(0.0, 1.0)
            betweenness_centrality = rng.uniform(0.01, 0.4)
            
            # Ground truth equations (with minor noise)
            is_transfer = (gate_entropy < 0.25)
            # Add minor noise (5% chance of flip)
            if rng.random() < 0.05:
                is_transfer = not is_transfer
                
            is_synergy = (stabilizer_overlap > 0.6 and tensor_rank < 3)
            if rng.random() < 0.05:
                is_synergy = not is_synergy
                
            is_resilience = (clifford_ratio > 0.7)
            if rng.random() < 0.05:
                is_resilience = not is_resilience
                
            is_novelty = (betweenness_centrality > 0.25)
            if rng.random() < 0.05:
                is_novelty = not is_novelty
                
            record = {
                "domain": "SyntheticDomain",
                "gate_entropy": round(gate_entropy, 4),
                "stabilizer_overlap": round(stabilizer_overlap, 4),
                "tensor_rank": tensor_rank,
                "clifford_ratio": round(clifford_ratio, 4),
                "betweenness_centrality": round(betweenness_centrality, 4),
                "transferability": 0.85 if is_transfer else 0.15,
                "synergy": 0.85 if is_synergy else 0.15,
                "noise_resilience": 0.85 if is_resilience else 0.15,
                "novelty": 0.85 if is_novelty else 0.15,
                # Other unused required keys
                "optimization_gain": 0.0, "graph_density": 0.0, "graph_diameter": 2,
                "clustering_coefficient": 0.0, "gate_distribution_distance": 0.0,
                "qubit_count": 2, "circuit_depth": 10, "entanglement_entropy": 0.0,
                "fidelity": 1.0, "runtime": 0.0, "memory_usage": 0.0
            }
            synthetic_records.append(record)
            
        # Write to temporary file
        with open(self.temp_data_path, "w", encoding="utf-8") as f:
            json.dump(synthetic_records, f, indent=2, ensure_ascii=False)
            
        # 2. Mine rules and generate laws on this synthetic dataset
        miner = PatternMiner(input_path=self.temp_data_path, output_path="temp_synthetic_rules.json")
        mined_rules = miner.mine_rules(min_support=0.01, min_confidence=0.5)
        
        generator = SymbolicLawGenerator(input_path="temp_synthetic_rules.json", output_path="temp_synthetic_laws.json")
        discovered_laws = generator.generate_laws()
        
        # 3. Assess recovery of the injected rules
        # Ground truths are:
        # 1. "gate_entropy < 0.25" -> transferability
        # 2. ["stabilizer_overlap > 0.6", "tensor_rank < 3"] -> synergy
        # 3. "clifford_ratio > 0.7" -> noise_resilience
        # 4. "betweenness_centrality > 0.25" -> novelty
        
        injected_ground_truths = [
            {"antecedents": ["gate_entropy < 0.25"], "consequent": "transferability"},
            {"antecedents": ["stabilizer_overlap > 0.6", "tensor_rank < 3"], "consequent": "synergy"},
            {"antecedents": ["clifford_ratio > 0.7"], "consequent": "noise_resilience"},
            {"antecedents": ["betweenness_centrality > 0.25"], "consequent": "novelty"}
        ]
        
        recovered_count = 0
        for gt in injected_ground_truths:
            gt_ants = set(gt["antecedents"])
            gt_cons = gt["consequent"]
            
            # Check if any discovered law matches
            for law in discovered_laws:
                law_ants = set(law["antecedents"])
                law_cons = law["consequent"]
                if law_cons == gt_cons and gt_ants.issubset(law_ants):
                    recovered_count += 1
                    break
                    
        # Calculate metrics
        total_injected = len(injected_ground_truths)
        recovery_recall = recovered_count / total_injected if total_injected > 0 else 0.0
        
        # Precision: how many discovered laws correspond to actual injected triggers?
        valid_discoveries = 0
        for law in discovered_laws:
            law_ants = set(law["antecedents"])
            law_cons = law["consequent"]
            
            is_valid = False
            for gt in injected_ground_truths:
                gt_ants = set(gt["antecedents"])
                gt_cons = gt["consequent"]
                if law_cons == gt_cons and law_ants.issubset(gt_ants):
                    is_valid = True
                    break
            if is_valid:
                valid_discoveries += 1
                
        recovery_precision = valid_discoveries / len(discovered_laws) if discovered_laws else 0.0
        
        if recovery_precision + recovery_recall > 0:
            recovery_f1 = (2 * recovery_precision * recovery_recall) / (recovery_precision + recovery_recall)
        else:
            recovery_f1 = 0.0
            
        discovery_confidence_score = (recovery_precision * 0.4) + (recovery_recall * 0.6)
        
        report = {
            "recovery_precision": round(recovery_precision, 4),
            "recovery_recall": round(recovery_recall, 4),
            "recovery_f1": round(recovery_f1, 4),
            "discovery_confidence_score": round(discovery_confidence_score, 4),
            "total_injected": total_injected,
            "recovered_count": recovered_count,
            "discovered_laws_count": len(discovered_laws)
        }
        
        # Save report
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Cleanup temporary files
        for temp_file in [self.temp_data_path, "temp_synthetic_rules.json", "temp_synthetic_laws.json"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        print(f"Synthetic Law Recovery Report saved: {report}")
        return report

if __name__ == "__main__":
    benchmark = SyntheticLawBenchmark()
    benchmark.run_benchmark()
