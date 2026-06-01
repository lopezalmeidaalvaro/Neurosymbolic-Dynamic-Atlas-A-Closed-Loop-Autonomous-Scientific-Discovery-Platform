#!/usr/bin/env python3
"""
Fase A — Diagnóstico Observacional de los Rechazos de TheoryCritic
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import json
import time
import argparse
import random
import re
import numpy as np
import torch
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from physics.benchmark.isolated_environment import create_isolated_benchmark_environment
from physics.agents.hypothesis_generator import HypothesisGenerator, Hypothesis
from physics.agents.theory_critic import TheoryCritic

def map_rejection_rule(verdict, metric_type):
    """
    Standardizes the TheoryCritic rejection cause into mandated categories.
    """
    if not verdict.singularities:
        return "unknown", "No explicit reason logged"
    
    primary_reason = verdict.singularities[0]
    
    if "Throat Closed" in primary_reason:
        return "boundary_condition", primary_reason
    elif "Flaring-out" in primary_reason:
        return "instability", primary_reason
    elif "Boundary conditions" in primary_reason:
        return "boundary_condition", primary_reason
    elif "Singularity at r=0" in primary_reason:
        return "singularity", primary_reason
    elif "Asymptotic limit" in primary_reason:
        return "boundary_condition", primary_reason
    elif "Curvature diverges" in primary_reason or "curvature divergence" in primary_reason:
        return "divergence", primary_reason
    elif "evaluation failed" in primary_reason or "Parse/Math Error" in primary_reason:
        return "numeric_failure", primary_reason
    elif "NaN/Inf" in primary_reason or "Infinity/NaN" in primary_reason:
        return "singularity", primary_reason
    else:
        return "unknown", primary_reason

def run_diagnostic_trace(seed=0, output_dir="physics/benchmark/diagnostic_logs/", batch_size=50):
    """
    Executes a purely observational diagnostic loop:
    1. Sets up isolated sandbox for the seed.
    2. Seeds random generators.
    3. Generates a batch of hypotheses per problem.
    4. Evaluates each hypothesis via TheoryCritic and logs exact results.
    """
    print(f"\n========================================================")
    # Ensure isolation sandbox starts fresh
    create_isolated_benchmark_environment(seed=seed)
    
    print(f"  INICIANDO DIAGNOSTICO CIEGO (SEMILLA: {seed})")
    print(f"========================================================\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Seed random number generators
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    problems = [
        {"key": "A", "metric_type": "wormhole", "label": "Wormhole"},
        {"key": "B", "metric_type": "warp", "label": "Warp Bubble"},
        {"key": "C", "metric_type": "black_hole", "label": "Quantum Gravity Black Hole"}
    ]
    
    trace_results = []
    
    for prob in problems:
        print(f"\n--- [PROBLEMA {prob['key']} - {prob['label']}] ---")
        
        # Initialize agents
        hypo_gen = HypothesisGenerator(exploration_rate=0.5, similarity_threshold=0.85)
        critic = TheoryCritic()
        
        context = {"exploration_history": []}
        
        for idx in range(batch_size):
            hypothesis = hypo_gen.propose(context, metric_type=prob["metric_type"])
            hypothesis_id = f"H_seed_{seed}_prob_{prob['key']}_{idx:03d}"
            
            # Analyze family
            eq = hypothesis.expression
            if prob["key"] == "A":
                family = "exponential" if "exp" in eq else ("tanh" if "tanh" in eq else "rational")
            elif prob["key"] == "B":
                family = "tanh" if "tanh" in eq else ("exponential" if "exp" in eq else "rational")
            else:
                family = "rational" if "/" in eq or "r**3" in eq else "exponential"
                
            # Validate via TheoryCritic
            verdict = critic.validate(hypothesis)
            
            accepted = (verdict.verdict == "ACCEPTED")
            
            if accepted:
                rule = "none"
                reason = "ACCEPTED"
                # To maintain exploration diversity check
                context["exploration_history"].append({
                    "equation": eq,
                    "exploring": False
                })
            else:
                rule, reason = map_rejection_rule(verdict, prob["metric_type"])
                
            entry = {
                "seed": seed,
                "problem": prob["key"],
                "hypothesis_id": hypothesis_id,
                "equation": eq,
                "family": family,
                "generation_timestamp": time.time(),
                "critic_result": {
                    "accepted": accepted,
                    "rule": rule,
                    "reason": reason
                }
            }
            trace_results.append(entry)
            
        print(f" [+] Completadas {batch_size} hipotesis para Problema {prob['key']}.")
        
    # Save output trace
    output_file = output_path / f"diagnostic_trace_seed_{seed}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(trace_results, f, indent=4)
        
    print(f"\n[+] Trace de diagnostico guardado en: {output_file}")
    return trace_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fase A — Diagnóstico Observacional de los Rechazos de TheoryCritic")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for generation")
    parser.add_argument("--output_dir", type=str, default="physics/benchmark/diagnostic_logs/", help="Directory to save logs")
    parser.add_argument("--batch_size", type=int, default=50, help="Number of hypotheses per problem to test")
    
    args = parser.parse_args()
    run_diagnostic_trace(seed=args.seed, output_dir=args.output_dir, batch_size=args.batch_size)
