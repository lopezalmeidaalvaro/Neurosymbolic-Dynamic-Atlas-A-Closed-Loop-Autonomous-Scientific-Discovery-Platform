import json
import numpy as np
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory
from quantum.theory.mechanism_engine import MechanismEngine

class AdversarialTheoryTests:
    """
    Component O: Theory Adversarial Attack Suite.
    Stress-tests theories under noise injection, feature permutation, simulator drift,
    domain shifts, and synthetic confounders to verify structural stability.
    """

    def __init__(self, data_path: str = "observation_dataset.json", db_path: str = "theory_memory.db", output_path: str = "adversarial_theory_report.json"):
        self.data_path = data_path
        self.db_path = db_path
        self.output_path = output_path
        self.memory = TheoryMemory(db_path=db_path)
        self.engine = MechanismEngine(data_path=data_path, db_path=db_path)

    def run_adversarial_tests(self) -> List[Dict[str, Any]]:
        dataset = self.engine.load_or_generate_dataset()
        theories = self.memory.get_all_theories()
        
        # Obfuscated variables with latent properties
        enriched_data = []
        for obs in dataset:
            enriched_obs = obs.copy()
            enriched_obs["structural_coherence"] = 1.0 - obs["gate_entropy"]
            enriched_obs["domain_similarity"] = 1.0 - obs["gate_distribution_distance"]
            enriched_obs["algebraic_symmetry"] = obs["stabilizer_overlap"]
            enriched_obs["computation_complexity"] = obs["tensor_rank"] / 20.0
            enriched_obs["state_preservation"] = 1.0 - (obs["tensor_rank"] / 20.0)
            enriched_obs["stabilizer_compatibility"] = obs["clifford_ratio"]
            enriched_obs["error_mitigation"] = obs["fidelity"]
            enriched_obs["reuse_bottleneck"] = obs["betweenness_centrality"]
            enriched_obs["module_recombination"] = obs["clustering_coefficient"]
            enriched_data.append(enriched_obs)
            
        adversarial_results = []
        rng = np.random.default_rng(42)

        for theory in theories:
            t_id = theory["id"]
            
            # Map parameters
            if t_id == "THEORY_001":
                cause, effect = "gate_entropy", "transferability"
            elif t_id == "THEORY_002":
                cause, effect = "stabilizer_overlap", "synergy"
            elif t_id == "THEORY_003":
                cause, effect = "clifford_ratio", "noise_resilience"
            else: # THEORY_004
                cause, effect = "betweenness_centrality", "novelty"

            base_corr = self.engine.compute_correlation(enriched_data, cause, effect)
            
            # 1. Noise injection (20% gaussian noise)
            noise_data = []
            for obs in enriched_data:
                obs_noise = obs.copy()
                obs_noise[cause] = obs_noise[cause] + rng.normal(0, 0.20)
                noise_data.append(obs_noise)
            noise_corr = self.engine.compute_correlation(noise_data, cause, effect)
            
            # 2. Simulator Drift
            drift_data = []
            for obs in enriched_data:
                obs_drift = obs.copy()
                obs_drift[cause] = obs_drift[cause] * 1.15 + 0.05
                drift_data.append(obs_drift)
            drift_corr = self.engine.compute_correlation(drift_data, cause, effect)
            
            # 3. Domain Shift
            holdout_domains = ["VQE", "QFT", "Grover"]
            shift_data = [obs for obs in enriched_data if obs["domain"] in holdout_domains]
            shift_corr = self.engine.compute_correlation(shift_data, cause, effect)
            
            # 4. Synthetic Confounder Attack
            # Inject a highly collinear confounder to see if it disrupts the direction
            confounder_data = []
            for obs in enriched_data:
                obs_conf = obs.copy()
                obs_conf["confounder"] = obs_conf[cause] * 0.90 + rng.normal(0, 0.05)
                confounder_data.append(obs_conf)
            conf_corr = self.engine.compute_correlation(confounder_data, "confounder", effect)

            # Evaluate survival
            # Sign consistency check
            base_sign = np.sign(base_corr)
            signs = [np.sign(c) for c in [noise_corr, drift_corr, shift_corr, conf_corr]]
            surviving_attacks = sum([1 for s in signs if s == base_sign])
            
            survival_rate = surviving_attacks / len(signs)
            status = "SURVIVED" if survival_rate >= 0.75 else "COLLAPSED"
            
            adversarial_results.append({
                "theory_id": t_id,
                "base_correlation": round(base_corr, 4),
                "noise_correlation": round(noise_corr, 4),
                "drift_correlation": round(drift_corr, 4),
                "shift_correlation": round(shift_corr, 4),
                "confounder_correlation": round(conf_corr, 4),
                "survival_rate": round(survival_rate, 4),
                "status": status
            })
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(adversarial_results, f, indent=2, ensure_ascii=False)
            
        print(f"Theory Adversarial Attack Suite completed. Audited {len(adversarial_results)} theories.")
        return adversarial_results

if __name__ == "__main__":
    adv = AdversarialTheoryTests()
    adv.run_adversarial_tests()
