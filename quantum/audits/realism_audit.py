import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.simulation.simulation_manager import SimulationManager

def run_realism_audit(output_path: str = "realism_audit_report.json", label_shuffle_path: str = "label_shuffle_report.json", domain_holdout_path: str = "domain_holdout_report.json") -> Dict[str, Any]:
    print("Running Realism and Scaling Audit...")
    
    # 1. Scaling Check
    manager = SimulationManager(use_gpu=False)
    qubit_sizes = [5, 10, 15, 20]
    runtimes = []
    memories = []
    
    for q in qubit_sizes:
        # Construct simple GHZ-like circuit
        gates = [{"type": "H", "qubits": [0]}]
        for i in range(1, q):
            gates.append({"type": "CNOT", "qubits": [i-1, i]})
        spec = {"qubits": q, "gates": gates}
        
        start = time.time()
        res = manager.run_simulation(spec)
        elapsed = time.time() - start
        
        runtimes.append(elapsed)
        memories.append(float(res.get("result", {}).get("estimated_memory_mb", 0.0)))
        
    # Check if runtimes are completely flat/zero
    runtime_is_flat = len(set([round(r, 4) for r in runtimes])) <= 1 and runtimes[0] == 0.0
    # Check if memory grows with qubits
    mem_grows = all(memories[i] < memories[i+1] for i in range(len(memories)-1)) if memories else False
    
    runtime_scaling_passed = not runtime_is_flat
    memory_scaling_passed = mem_grows
    
    # 2. Check for impossible perfect metrics & zero variance in label shuffle / domain holdout reports
    impossible_perfect = False
    zero_variance = False
    details_perfect = []
    details_variance = []
    
    # Check label shuffle report
    if os.path.exists(label_shuffle_path):
        with open(label_shuffle_path, "r", encoding="utf-8") as f:
            ls_data = json.load(f)
        results = ls_data.get("results", {})
        for model_name, metrics in results.items():
            # In a label shuffle, mean ROC-AUC should be around 0.5.
            # If it's 1.0 or 0.0, something is highly suspect.
            mean_auc = metrics.get("mean_roc_auc", 0.5)
            var_auc = metrics.get("var_roc_auc", 0.0)
            
            if mean_auc > 0.95 or mean_auc < 0.05:
                impossible_perfect = True
                details_perfect.append(f"Label shuffle mean ROC-AUC for {model_name} is abnormally high/low: {mean_auc}")
            if var_auc == 0.0 and ls_data.get("num_seeds", 100) > 1:
                zero_variance = True
                details_variance.append(f"Label shuffle ROC-AUC variance for {model_name} is exactly 0.0 across seeds")
                
    # Check domain holdout report
    if os.path.exists(domain_holdout_path):
        with open(domain_holdout_path, "r", encoding="utf-8") as f:
            dh_data = json.load(f)
        metrics = dh_data.get("metrics", {})
        mean_auc = metrics.get("mean_roc_auc", 0.5)
        var_auc = metrics.get("var_roc_auc", 0.0)
        
        if mean_auc == 1.0:
            impossible_perfect = True
            details_perfect.append(f"Domain holdout mean ROC-AUC is exactly 1.0")
        if var_auc == 0.0 and dh_data.get("num_seeds", 100) > 1:
            zero_variance = True
            details_variance.append(f"Domain holdout ROC-AUC variance is exactly 0.0 across seeds")
            
    # 3. Fidelity realism check
    # Check if quantum simulation produces physically realistic fidelities (not exactly 1.0 under noise)
    # We query the simulator with a noise model if possible
    fidelity_is_realistic = True
    try:
        from quantum.noise.noise_model import NoiseModel
        noise = NoiseModel(thermal_relaxation=True)
        # run a small simulation with noise and verify state fidelity is less than 1.0
        gates_noise = [{"type": "H", "qubits": [0]}, {"type": "CNOT", "qubits": [0, 1]}]
        spec_noise = {"qubits": 2, "gates": gates_noise, "noise_model": noise.to_dict() if hasattr(noise, "to_dict") else {}}
        res_noise = manager.run_simulation(spec_noise)
        state_fidelity = res_noise.get("result", {}).get("fidelity", 1.0)
        # If fidelity is exactly 1.0 even with noise, it's not realistic
        if state_fidelity == 1.0:
            fidelity_is_realistic = False
    except ImportError:
        # Noise module not available, or simulator does not compute fidelity
        pass

    verdict = "REALISM_VERIFIED"
    if not runtime_scaling_passed or not memory_scaling_passed or impossible_perfect or zero_variance or not fidelity_is_realistic:
        verdict = "REALISM_VIOLATIONS_FLAGGED"
        
    report = {
        "scaling_audit": {
            "qubit_sizes": qubit_sizes,
            "runtimes_sec": [round(r, 6) for r in runtimes],
            "memories_mb": memories,
            "runtime_scaling_passed": runtime_scaling_passed,
            "memory_scaling_passed": memory_scaling_passed
        },
        "metrics_audit": {
            "impossible_perfect_metrics": impossible_perfect,
            "impossible_perfect_details": details_perfect,
            "zero_variance_metrics": zero_variance,
            "zero_variance_details": details_variance
        },
        "fidelity_realism": {
            "fidelity_is_realistic": fidelity_is_realistic
        },
        "verdict": verdict
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Realism and Scaling Audit complete. Verdict: {verdict}")
    return report

if __name__ == "__main__":
    run_realism_audit()
