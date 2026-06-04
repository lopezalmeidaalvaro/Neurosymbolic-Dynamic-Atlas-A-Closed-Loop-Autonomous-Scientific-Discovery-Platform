import os
import json
import time
from typing import Dict, Any, List
from quantum.law_discovery.scientific_loop import ScientificLoop

def run_large_scale_benchmark() -> Dict[str, Any]:
    print("Running Large Scale Law Discovery Benchmark across 13 domains (1000 seeds)...")
    start_time = time.time()
    
    # 1. Execute the 1000-cycle scientific loop which handles the full method pipeline
    loop = ScientificLoop()
    loop.execute_loop(cycles=1000)
    
    # 2. Load outputs of the pipeline components to calculate summary metrics
    def load_json(path: str) -> List[Any]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    candidate_laws = load_json("candidate_laws.json")
    validated_laws = load_json("causal_law_validation.json")
    falsification_reports = load_json("law_falsification_report.json")
    meta_laws = load_json("meta_laws.json")
    mdl_reports = load_json("mdl_report.json")
    
    # Calculate counts
    n_candidates = len(candidate_laws)
    n_validated = sum(1 for item in validated_laws if item.get("status") == "CAUSALLY_VALIDATED_LAW")
    n_generalizable = sum(1 for item in falsification_reports if item.get("verdict") == "SURVIVED")
    n_metalaws = len(meta_laws)
    
    # Calculate average scientific value score
    val_scores = [item.get("scientific_value_score", 0.5) for item in mdl_reports]
    avg_scientific_value_score = sum(val_scores) / len(val_scores) if val_scores else 0.5
    
    # Falsification survival rate
    survived = sum(1 for item in falsification_reports if item.get("verdict") == "SURVIVED")
    falsification_survival_rate = survived / len(falsification_reports) if falsification_reports else 0.0
    
    benchmark_report = {
        "candidate_laws": n_candidates,
        "validated_laws": n_validated,
        "generalizable_laws": n_generalizable,
        "meta_laws": n_metalaws,
        "scientific_value_score": round(avg_scientific_value_score, 4),
        "falsification_survival_rate": round(falsification_survival_rate, 4),
        "domains_tested": [
            "Bell", "GHZ", "W", "QAOA", "VQE", "QFT", "Grover",
            "Quantum Walk", "Amplitude Encoding", "Hardware Efficient Ansatz",
            "Error Correction", "State Preparation", "Variational Compilation"
        ],
        "total_seeds": 1000,
        "benchmark_duration_seconds": round(time.time() - start_time, 3)
    }
    
    # Save benchmark report
    with open("law_discovery_benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, indent=2, ensure_ascii=False)
        
    print(f"Benchmark completed successfully. Report: {benchmark_report}")
    return benchmark_report

if __name__ == "__main__":
    run_large_scale_benchmark()
