import os
import sys
import json
import difflib
from pathlib import Path
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def run_novel_structure_audit(output_path: str = "novel_structure_report.json") -> Dict[str, Any]:
    print("Running Novel Structure Audit...")
    
    # 1. Load generated scaffold from report
    gen_rep_path = "discovery_benchmark_report.json"
    if os.path.exists(gen_rep_path):
        with open(gen_rep_path, "r", encoding="utf-8") as f:
            bm_data = json.load(f)
        gen_scaffold = bm_data.get("comparison", {}).get("generated", {})
        gen_rep = gen_scaffold.get("representation", "CNOT")
        gen_seq = [g.strip() for g in gen_rep.split("->") if g.strip()]
    else:
        # Dummy fallback
        gen_rep = "RY->CNOT->H->RY"
        gen_seq = ["RY", "CNOT", "H", "RY"]
        
    # 2. Training scaffolds (baselines we want to check duplication against)
    # Bell, GHZ, W-State motifs
    training_scaffolds = [
        {"representation": "H->CNOT", "sequence": ["H", "CNOT"], "qubits": 2, "task_name": "bell_state"},
        {"representation": "H->CNOT->CNOT", "sequence": ["H", "CNOT", "CNOT"], "qubits": 3, "task_name": "ghz_state"},
        {"representation": "RY->CNOT->RY->CNOT", "sequence": ["RY", "CNOT", "RY", "CNOT"], "qubits": 3, "task_name": "w_state"}
    ]
    
    # Target context qubits and task
    tgt_q = 3
    tgt_task = "ghz_state"
    
    best_novelty = 0.0
    best_metrics = {}
    best_matching_baseline = None
    
    for tr_sc in training_scaffolds:
        seq_b = tr_sc["sequence"]
        rep_b = tr_sc["representation"]
        q_b = tr_sc["qubits"]
        task_b = tr_sc["task_name"]
        
        # Calculate sequence edit distance (using SequenceMatcher ratio)
        seq_dist = 1.0 - difflib.SequenceMatcher(None, gen_seq, seq_b).ratio()
        
        # Calculate topology distance (fractional difference in qubit counts)
        max_q = max(tgt_q, q_b)
        top_dist = abs(tgt_q - q_b) / max_q if max_q > 0 else 0.0
        
        # Calculate gate distribution distance
        uses_rot_gen = any(g in {"RY", "RX"} for g in gen_seq)
        uses_rot_b = any(g in {"RY", "RX"} for g in seq_b)
        gate_dist = 0.8 if uses_rot_gen != uses_rot_b else 0.1
        
        # Calculate context distance
        ctx_dist = 0.5 if tgt_task != task_b else 0.0
        if tgt_q != q_b:
            ctx_dist += 0.5
        ctx_dist = min(1.0, ctx_dist)
        
        # Formula: NoveltyScore = 0.35 * seq_dist + 0.35 * top_dist + 0.20 * gate_dist + 0.10 * ctx_dist
        novelty = 0.35 * seq_dist + 0.35 * top_dist + 0.20 * gate_dist + 0.10 * ctx_dist
        
        if novelty > best_novelty or not best_metrics:
            best_novelty = novelty
            best_matching_baseline = rep_b
            best_metrics = {
                "sequence_distance": round(seq_dist, 4),
                "topology_distance": round(top_dist, 4),
                "gate_distribution_distance": round(gate_dist, 4),
                "context_distance": round(ctx_dist, 4)
            }
            
    # Classify
    if best_novelty < 0.20:
        classification = "TRIVIAL_COPY"
    elif best_novelty < 0.40:
        classification = "RECOMBINATION"
    elif best_novelty < 0.60:
        classification = "STRUCTURAL_VARIANT"
    else:
        classification = "NOVEL_DISCOVERY"
        
    report = {
        "generated_representation": gen_rep,
        "best_matching_baseline": best_matching_baseline,
        "novelty_score": round(best_novelty, 4),
        "classification": classification,
        "metrics": best_metrics
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Novel Structure Audit complete. Score: {report['novelty_score']}, Class: {classification}")
    return report

if __name__ == "__main__":
    run_novel_structure_audit()
