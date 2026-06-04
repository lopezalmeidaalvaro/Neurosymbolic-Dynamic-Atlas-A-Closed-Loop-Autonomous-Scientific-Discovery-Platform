import os
import json
import random
from typing import Dict, Any, List

class LawFalsificationEngine:
    """
    Component H: Autonomous Falsification Engine.
    Attempts to falsify candidate laws using adversarial samples, shifts, and permutations.
    """

    def __init__(self, validation_path: str = "causal_law_validation.json", data_path: str = "observation_dataset.json", output_path: str = "law_falsification_report.json"):
        self.validation_path = validation_path
        self.data_path = data_path
        self.output_path = output_path
        self.falsification_results: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.validation_path):
            return []
        with open(self.validation_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_antecedents_discretized(self, obs: Dict[str, Any], rule_str: str) -> bool:
        """
        Evaluate if antecedents are satisfied in the observation.
        """
        # Parsing basic antecedent substrings
        satisfied = True
        if "gate_entropy < 0.25" in rule_str and obs["gate_entropy"] >= 0.25:
            satisfied = False
        if "stabilizer_overlap > 0.6" in rule_str and obs["stabilizer_overlap"] <= 0.6:
            satisfied = False
        if "tensor_rank < 3" in rule_str and obs["tensor_rank"] >= 3:
            satisfied = False
        if "clifford_ratio > 0.7" in rule_str and obs["clifford_ratio"] <= 0.7:
            satisfied = False
        if "betweenness_centrality > 0.25" in rule_str and obs["betweenness_centrality"] <= 0.25:
            satisfied = False
        return satisfied

    def run_falsification(self) -> List[Dict[str, Any]]:
        observations = self.load_data()
        laws = self.load_laws()
        self.falsification_results = []
        
        if not observations or not laws:
            print("No observations or causal laws found for falsification.")
            return []
            
        n = len(observations)
        
        for law in laws:
            rule_str = law["rule"]
            law_id = law["id"]
            
            # Consequent details
            consequent = "transferability"
            if "synergy" in rule_str.lower():
                consequent = "synergy"
            elif "noise_resilience" in rule_str.lower():
                consequent = "noise_resilience"
            elif "novelty" in rule_str.lower():
                consequent = "novelty"
                
            threshold = 0.6 if consequent in ["synergy", "novelty"] else 0.7
            
            # Helper to calculate accuracy of the rule
            def get_precision(data):
                tp = fp = 0
                for obs in data:
                    if self.check_antecedents_discretized(obs, rule_str):
                        if obs[consequent] >= threshold:
                            tp += 1
                        else:
                            fp += 1
                return tp / (tp + fp) if (tp + fp) > 0 else 1.0

            # 1. Adversarial Feature Test
            # Filter observations where antecedent is satisfied, but we sort by lowest consequent
            satisfied_obs = [obs for obs in observations if self.check_antecedents_discretized(obs, rule_str)]
            satisfied_obs.sort(key=lambda x: x[consequent])
            # Adversarial set is the bottom 20% of satisfied observations (intentional counterexamples)
            adv_subset = satisfied_obs[:max(1, len(satisfied_obs)//5)]
            adversarial_precision = get_precision(adv_subset)
            
            # 2. Noise Injection Test (Add 15% noise to variables)
            noisy_obs = []
            for obs in observations:
                n_obs = obs.copy()
                for k in ["gate_entropy", "stabilizer_overlap", "clifford_ratio", "betweenness_centrality"]:
                    if k in n_obs:
                        n_obs[k] += random.gauss(0, 0.15)
                noisy_obs.append(n_obs)
            noise_precision = get_precision(noisy_obs)
            
            # 3. Distribution Shift / Holdout Domain Test
            # Filter observations belonging to holdout domains: "QAOA", "VQE", "QFT", "Grover"
            holdout_domains = ["QAOA", "VQE", "QFT", "Grover"]
            holdout_obs = [obs for obs in observations if obs["domain"] in holdout_domains]
            holdout_precision = get_precision(holdout_obs) if holdout_obs else 0.0
            
            # 4. Domain Shift (Evaluating strictly on Grover and QFT)
            shift_domains = ["Grover", "QFT"]
            shift_obs = [obs for obs in observations if obs["domain"] in shift_domains]
            shift_precision = get_precision(shift_obs) if shift_obs else 0.0
            
            # 5. Feature Permutation Test
            # Permute the antecedent columns randomly
            perm_obs = []
            features_to_permute = ["gate_entropy", "stabilizer_overlap", "clifford_ratio", "betweenness_centrality"]
            permuted_lists = {f: [obs[f] for obs in observations] for f in features_to_permute if f in observations[0]}
            for f in permuted_lists:
                random.Random(88).shuffle(permuted_lists[f])
                
            for idx, obs in enumerate(observations):
                p_obs = obs.copy()
                for f in permuted_lists:
                    p_obs[f] = permuted_lists[f][idx]
                perm_obs.append(p_obs)
            permutation_precision = get_precision(perm_obs)
            
            # Compute Falsification Survival Score
            # Expected behavior:
            # - Permutation precision should be low (e.g. < 0.5)
            # - Holdout precision should remain relatively high if law generalizes (e.g. > 0.55)
            # - Noise precision should remain stable (e.g. > 0.55)
            
            # Survival Score = (Holdout_Precision + Noise_Precision + (1.0 - Permutation_Precision)) / 3.0
            survival_score = (holdout_precision + noise_precision + (1.0 - permutation_precision)) / 3.0
            
            # Falsification verdict
            # Falsified if holdout_precision < 0.55 or survival_score < 0.50
            falsified = (holdout_precision < 0.55) or (survival_score < 0.50)
            verdict = "FALSIFIED" if falsified else "SURVIVED"
            
            falsification_report = {
                "id": law_id,
                "rule": rule_str,
                "verdict": verdict,
                "survival_score": round(survival_score, 4),
                "metrics": {
                    "adversarial_precision": round(adversarial_precision, 4),
                    "noise_precision": round(noise_precision, 4),
                    "holdout_precision": round(holdout_precision, 4),
                    "shift_precision": round(shift_precision, 4),
                    "permutation_precision": round(permutation_precision, 4)
                }
            }
            self.falsification_results.append(falsification_report)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.falsification_results, f, indent=2, ensure_ascii=False)
            
        print(f"Falsification testing completed. Saved report to: {self.output_path}")
        return self.falsification_results

if __name__ == "__main__":
    engine = LawFalsificationEngine()
    engine.run_falsification()
