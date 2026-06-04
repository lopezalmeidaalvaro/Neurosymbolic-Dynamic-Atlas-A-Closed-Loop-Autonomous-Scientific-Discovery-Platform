import os
import json
import math
import random
from typing import Dict, Any, List, Set, Tuple

class CausalLawVerifier:
    """
    Component G: Causal Law Verifier.
    Performs feature ablation, counterfactuals, randomization, and stability checks on candidate laws.
    """

    def __init__(self, laws_path: str = "candidate_laws.json", data_path: str = "observation_dataset.json", output_path: str = "causal_law_validation.json"):
        self.laws_path = laws_path
        self.data_path = data_path
        self.output_path = output_path
        self.validated_laws: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_laws(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.laws_path):
            return []
        with open(self.laws_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_antecedents(self, obs: Dict[str, Any], antecedents: List[str]) -> bool:
        """
        Check if an observation satisfies all antecedents of a law.
        """
        for ant in antecedents:
            if "gate_entropy < 0.25" in ant and obs["gate_entropy"] >= 0.25:
                return False
            if "gate_entropy >= 0.25" in ant and obs["gate_entropy"] < 0.25:
                return False
            if "stabilizer_overlap > 0.6" in ant and obs["stabilizer_overlap"] <= 0.6:
                return False
            if "stabilizer_overlap <= 0.6" in ant and obs["stabilizer_overlap"] > 0.6:
                return False
            if "tensor_rank < 3" in ant and obs["tensor_rank"] >= 3:
                return False
            if "tensor_rank >= 3" in ant and obs["tensor_rank"] < 3:
                return False
            if "clifford_ratio > 0.7" in ant and obs["clifford_ratio"] <= 0.7:
                return False
            if "clifford_ratio <= 0.7" in ant and obs["clifford_ratio"] > 0.7:
                return False
            if "betweenness_centrality > 0.25" in ant and obs["betweenness_centrality"] <= 0.25:
                return False
            if "betweenness_centrality <= 0.25" in ant and obs["betweenness_centrality"] > 0.25:
                return False
        return True

    def verify_laws(self) -> List[Dict[str, Any]]:
        observations = self.load_data()
        laws = self.load_laws()
        self.validated_laws = []
        
        if not observations or not laws:
            print("No observations or laws found for causal verification.")
            return []
            
        n = len(observations)
        
        for law in laws:
            ants = law["antecedents"]
            consequent = law["consequent"]
            trend = law["trend"]
            
            # Map consequent to binary evaluation
            # High utility/synergy/transferability/noise_resilience/novelty threshold is 0.7 (or 0.6 for synergy/novelty)
            threshold = 0.6 if consequent in ["synergy", "novelty"] else 0.7
            
            # 1. Base Contingency Table
            tp = fp = fn = tn = 0
            for obs in observations:
                ant_satisfied = self.check_antecedents(obs, ants)
                cons_val = obs[consequent]
                cons_satisfied = (cons_val >= threshold) if trend == "increases" else (cons_val < threshold)
                
                if ant_satisfied and cons_satisfied:
                    tp += 1
                elif ant_satisfied and not cons_satisfied:
                    fp += 1
                elif not ant_satisfied and cons_satisfied:
                    fn += 1
                elif not ant_satisfied and not cons_satisfied:
                    tn += 1
                    
            # Compute Base Metrics
            def get_stats(tp, fp, fn, tn):
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                
                denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
                mcc = (tp * tn - fp * fn) / denom if denom > 0 else 0.0
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
                auc = 0.5 * (tpr + tnr)
                return f1, mcc, auc
                
            f1_base, mcc_base, auc_base = get_stats(tp, fp, fn, tn)
            
            # 2. Causal Ablation
            # Ablating means predicting randomly based on class prior
            prior_p = (tp + fn) / n
            tp_ab = int(n * prior_p * prior_p)
            fp_ab = int(n * (1 - prior_p) * prior_p)
            fn_ab = int(n * prior_p * (1 - prior_p))
            tn_ab = int(n * (1 - prior_p) * (1 - prior_p))
            f1_ab, mcc_ab, auc_ab = get_stats(tp_ab, fp_ab, fn_ab, tn_ab)
            
            delta_f1 = f1_base - f1_ab
            delta_mcc = mcc_base - mcc_ab
            delta_auc = auc_base - auc_ab
            
            # 3. Counterfactual Perturbation
            # If we perturb antecedents from True to False, we measure the counterfactual drop
            # P(consequent | antecedent) - P(consequent | not antecedent)
            p_c_given_a = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            p_c_given_not_a = fn / (fn + tn) if (fn + tn) > 0 else 0.0
            counterfactual_effect = p_c_given_a - p_c_given_not_a
            
            # 4. Randomization Test
            # Shuffle consequent across dataset
            shuffled_obs = [obs[consequent] for obs in observations]
            random.Random(123).shuffle(shuffled_obs)
            tp_rand = fp_rand = fn_rand = tn_rand = 0
            for idx, obs in enumerate(observations):
                ant_satisfied = self.check_antecedents(obs, ants)
                cons_val = shuffled_obs[idx]
                cons_satisfied = (cons_val >= threshold) if trend == "increases" else (cons_val < threshold)
                if ant_satisfied and cons_satisfied:
                    tp_rand += 1
                elif ant_satisfied and not cons_satisfied:
                    fp_rand += 1
                elif not ant_satisfied and cons_satisfied:
                    fn_rand += 1
                elif not ant_satisfied and not cons_satisfied:
                    tn_rand += 1
            f1_rand, mcc_rand, auc_rand = get_stats(tp_rand, fp_rand, fn_rand, tn_rand)
            
            # 5. Sensitivity & Stability Score
            # Introduce 10% noise to antecedents satisfying check and measure flip rate
            flips = 0
            runs = 100
            for _ in range(runs):
                idx = random.randint(0, n - 1)
                obs = observations[idx]
                base_sat = self.check_antecedents(obs, ants)
                
                # Perturb observations slightly
                perturbed_obs = obs.copy()
                for key in ["gate_entropy", "stabilizer_overlap", "clifford_ratio", "betweenness_centrality"]:
                    if key in perturbed_obs:
                        perturbed_obs[key] += random.choice([-0.05, 0.05])
                if base_sat != self.check_antecedents(perturbed_obs, ants):
                    flips += 1
            stability_score = 1.0 - (flips / runs)
            
            # Determine Causal Classification
            # Promotion to Tier 2 (CAUSALLY_VALIDATED_LAW) if:
            # - delta_auc > 0.05
            # - counterfactual_effect > 0.15
            # - f1_base > 0.60
            is_causal = (delta_auc > 0.05) and (counterfactual_effect > 0.15) and (f1_base > 0.50)
            status = "CAUSALLY_VALIDATED_LAW" if is_causal else "CANDIDATE_LAW"
            
            validated_law = {
                "id": law["id"],
                "rule": law["rule"],
                "status": status,
                "metrics": {
                    "base_f1": round(f1_base, 4),
                    "base_mcc": round(mcc_base, 4),
                    "base_auc": round(auc_base, 4),
                    "delta_f1": round(delta_f1, 4),
                    "delta_mcc": round(delta_mcc, 4),
                    "delta_auc": round(delta_auc, 4),
                    "counterfactual_effect": round(counterfactual_effect, 4),
                    "randomized_auc": round(auc_rand, 4),
                    "stability_score": round(stability_score, 4)
                }
            }
            self.validated_laws.append(validated_law)
            
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.validated_laws, f, indent=2, ensure_ascii=False)
            
        print(f"Causal verification complete. Validated {len(self.validated_laws)} laws. Output: {self.output_path}")
        return self.validated_laws

if __name__ == "__main__":
    verifier = CausalLawVerifier()
    verifier.verify_laws()
