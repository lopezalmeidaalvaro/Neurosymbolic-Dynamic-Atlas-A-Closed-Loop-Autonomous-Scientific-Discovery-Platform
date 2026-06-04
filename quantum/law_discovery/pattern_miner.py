import os
import json
from typing import Dict, Any, List, Set, Tuple

class PatternMiner:
    """
    Component B: Pattern Mining Engine.
    Discretizes continuous observation metrics and mines frequent association rules.
    """

    def __init__(self, input_path: str = "observation_dataset.json", output_path: str = "pattern_rules.json"):
        self.input_path = input_path
        self.output_path = output_path
        self.rules: List[Dict[str, Any]] = []

    def load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Observation dataset not found at: {self.input_path}")
        with open(self.input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def discretize_observation(self, obs: Dict[str, Any]) -> Set[str]:
        """
        Discretizes continuous metrics to create categorical items.
        """
        items = set()
        
        # Discretize input metrics
        if obs["gate_entropy"] < 0.25:
            items.add("gate_entropy < 0.25")
        else:
            items.add("gate_entropy >= 0.25")
            
        if obs["stabilizer_overlap"] > 0.6:
            items.add("stabilizer_overlap > 0.6")
        else:
            items.add("stabilizer_overlap <= 0.6")
            
        if obs["tensor_rank"] < 3:
            items.add("tensor_rank < 3")
        else:
            items.add("tensor_rank >= 3")
            
        if obs["clifford_ratio"] > 0.7:
            items.add("clifford_ratio > 0.7")
        else:
            items.add("clifford_ratio <= 0.7")
            
        if obs["betweenness_centrality"] > 0.25:
            items.add("betweenness_centrality > 0.25")
        else:
            items.add("betweenness_centrality <= 0.25")
            
        # Target variables (consequents)
        if obs["transferability"] >= 0.7:
            items.add("transferability_high")
        else:
            items.add("transferability_low")
            
        if obs["synergy"] >= 0.6:
            items.add("synergy_high")
        else:
            items.add("synergy_low")
            
        if obs["noise_resilience"] >= 0.7:
            items.add("noise_resilience_high")
        else:
            items.add("noise_resilience_low")
            
        if obs["novelty"] >= 0.6:
            items.add("novelty_high")
        else:
            items.add("novelty_low")
            
        return items

    def mine_rules(self, min_support: float = 0.05, min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Pure Python Apriori-based rule miner designed for target predictions.
        Supports single item and pair item antecedents.
        """
        observations = self.load_data()
        n = len(observations)
        
        # Discretize all observations
        transactions = [self.discretize_observation(obs) for obs in observations]
        
        # Count frequency of single items
        item_counts: Dict[str, int] = {}
        for trans in transactions:
            for item in trans:
                item_counts[item] = item_counts.get(item, 0) + 1
                
        # Count frequency of pairs
        pair_counts: Dict[Tuple[str, str], int] = {}
        for trans in transactions:
            sorted_trans = sorted(list(trans))
            for i in range(len(sorted_trans)):
                for j in range(i + 1, len(sorted_trans)):
                    pair_counts[(sorted_trans[i], sorted_trans[j])] = pair_counts.get((sorted_trans[i], sorted_trans[j]), 0) + 1
                    
        targets = ["transferability_high", "synergy_high", "noise_resilience_high", "novelty_high"]
        candidate_rules = []
        
        # Helper to compute rule metrics
        def add_rule(antecedent: List[str], consequent: str, support_count: int):
            support = support_count / n
            
            # Antecedent support
            if len(antecedent) == 1:
                ant_count = item_counts.get(antecedent[0], 0)
            else:
                key = tuple(sorted(antecedent))
                ant_count = pair_counts.get(key, 0)
                
            if ant_count == 0:
                return
                
            confidence = support_count / ant_count
            cons_support = item_counts.get(consequent, 0) / n
            if cons_support == 0:
                return
            lift = confidence / cons_support
            
            if support >= min_support and confidence >= min_confidence:
                candidate_rules.append({
                    "antecedent": antecedent,
                    "consequent": consequent,
                    "support": round(support, 4),
                    "confidence": round(confidence, 4),
                    "lift": round(lift, 4)
                })

        # Mine 1-to-1 rules
        # e.g., IF [gate_entropy < 0.25] THEN [transferability_high]
        for pair, count in pair_counts.items():
            item1, item2 = pair
            
            # Check item1 -> item2 where item2 is a target
            if item2 in targets and not item1.endswith("_high") and not item1.endswith("_low"):
                add_rule([item1], item2, count)
            # Check item2 -> item1 where item1 is a target
            if item1 in targets and not item2.endswith("_high") and not item2.endswith("_low"):
                add_rule([item2], item1, count)
                
        # Mine 2-to-1 rules
        # e.g., IF [stabilizer_overlap > 0.6, tensor_rank < 3] THEN [synergy_high]
        # Count frequency of triples (antecedent pair + consequent)
        triple_counts: Dict[Tuple[str, str, str], int] = {}
        for trans in transactions:
            sorted_trans = sorted(list(trans))
            for i in range(len(sorted_trans)):
                for j in range(i + 1, len(sorted_trans)):
                    for k in range(j + 1, len(sorted_trans)):
                        triple_counts[(sorted_trans[i], sorted_trans[j], sorted_trans[k])] = triple_counts.get((sorted_trans[i], sorted_trans[j], sorted_trans[k]), 0) + 1
                        
        for triple, count in triple_counts.items():
            # Check subsets to find if two items predict a target
            for consequent in targets:
                if consequent in triple:
                    antecedent = [item for item in triple if item != consequent]
                    # Filter out other targets from antecedent
                    if any(ant in targets for ant in antecedent):
                        continue
                    add_rule(antecedent, consequent, count)
                    
        # Sort rules by confidence and lift
        candidate_rules.sort(key=lambda x: (x["confidence"], x["lift"]), reverse=True)
        self.rules = candidate_rules
        
        # Save patterns
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
            
        print(f"Mined {len(self.rules)} rules and saved to: {self.output_path}")
        return self.rules

if __name__ == "__main__":
    miner = PatternMiner()
    miner.mine_rules()
