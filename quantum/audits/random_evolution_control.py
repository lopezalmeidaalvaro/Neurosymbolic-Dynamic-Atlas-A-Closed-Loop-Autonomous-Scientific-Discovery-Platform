import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from scipy.stats import ttest_ind, mannwhitneyu

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from quantum.discovery.autonomous_scaffold_generator import AutonomousScaffoldGenerator

def run_random_evolution_control(num_seeds: int = 100, output_path: str = "random_evolution_report.json") -> Dict[str, Any]:
    print(f"Running Random Evolution Control across {num_seeds} seeds...")
    
    generator = AutonomousScaffoldGenerator()
    
    law_guided_utilities = []
    law_guided_synergies = []
    random_search_utilities = []
    random_search_synergies = []
    
    source_ctx = {"task_name": "bell_state", "qubit_count": 2}
    target_ctx = {"task_name": "ghz_state", "qubit_count": 3}
    
    # We run 100 seeds
    for seed in range(1, num_seeds + 1):
        # We seed the generator random state
        generator.rng.seed(seed)
        
        # Group A: Law Guided Search (enforcing pre_filter_transferable)
        # We simulate a small discovery run (2 generations, pop_size=4)
        # Note: the discover_scaffolds already implements pre-filtering
        discovered_law = generator.discover_scaffolds(generations=2, pop_size=4, source_ctx=source_ctx, target_ctx=target_ctx)
        best_law = discovered_law[0] if discovered_law else {"utility": 0.5, "synergy_score": 0.0}
        
        law_guided_utilities.append(best_law["utility"])
        law_guided_synergies.append(best_law["synergy_score"])
        
        # Group B: Random Search (bypassing pre_filter_transferable)
        # To bypass pre-filtering, we patch the pre_filter_transferable method to always return True
        original_filter = generator.pre_filter_transferable
        generator.pre_filter_transferable = lambda *args, **kwargs: True
        
        discovered_rand = generator.discover_scaffolds(generations=2, pop_size=4, source_ctx=source_ctx, target_ctx=target_ctx)
        best_rand = discovered_rand[0] if discovered_rand else {"utility": 0.5, "synergy_score": 0.0}
        
        random_search_utilities.append(best_rand["utility"])
        random_search_synergies.append(best_rand["synergy_score"])
        
        # Restore pre-filter
        generator.pre_filter_transferable = original_filter
        
    law_util = np.array(law_guided_utilities)
    rand_util = np.array(random_search_utilities)
    
    # Calculate statistical metrics: t-test, Mann-Whitney U, Cohen's d, CI of difference
    # 1. t-test
    t_stat, p_val_t = ttest_ind(law_util, rand_util, equal_var=False)
    
    # 2. Mann-Whitney U
    m_stat, p_val_m = mannwhitneyu(law_util, rand_util, alternative='greater')
    
    # 3. Cohen's d
    mean_law = np.mean(law_util)
    mean_rand = np.mean(rand_util)
    var_law = np.var(law_util, ddof=1)
    var_rand = np.var(rand_util, ddof=1)
    # pool variance
    pooled_se = np.sqrt((var_law + var_rand) / 2.0)
    pooled_se = max(pooled_se, 1e-8)
    cohen_d_val = float((mean_law - mean_rand) / pooled_se)
    
    # 4. 95% Confidence Interval for the difference in means
    se_diff = np.sqrt(var_law / num_seeds + var_rand / num_seeds)
    mean_diff = mean_law - mean_rand
    ci_diff = [mean_diff - 1.96 * se_diff, mean_diff + 1.96 * se_diff]
    
    # Verdict: DISCOVERY_GUIDANCE_VERIFIED if law_guided > random with p < 0.05
    # Since we want to test if law_guided is statistically superior, we check the one-sided p-value
    # using Mann-Whitney U or a one-sided t-test.
    verdict = "DISCOVERY_GUIDANCE_VERIFIED" if (mean_law > mean_rand and p_val_m < 0.05) else "DISCOVERY_GUIDANCE_NOT_SIGNIFICANT"
    
    report = {
        "num_seeds": num_seeds,
        "law_guided": {
            "mean_utility": round(float(mean_law), 4),
            "mean_synergy": round(float(np.mean(law_guided_synergies)), 4)
        },
        "random_search": {
            "mean_utility": round(float(mean_rand), 4),
            "mean_synergy": round(float(np.mean(random_search_synergies)), 4)
        },
        "statistics": {
            "t_statistic": round(float(t_stat), 4),
            "t_test_p_value": round(float(p_val_t), 6),
            "mann_whitney_p_value": round(float(p_val_m), 6),
            "cohens_d": round(cohen_d_val, 4),
            "ci_95_difference": [round(float(ci_diff[0]), 4), round(float(ci_diff[1]), 4)]
        },
        "verdict": verdict
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Random Evolution Control complete. Verdict: {verdict}, Cohen's d: {cohen_d_val:.4f}, p-value: {p_val_m:.6f}")
    return report

if __name__ == "__main__":
    run_random_evolution_control()
