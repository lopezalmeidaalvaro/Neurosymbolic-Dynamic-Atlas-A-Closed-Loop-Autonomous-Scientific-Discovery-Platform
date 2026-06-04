import json
import statistics
import time
from typing import List, Dict, Any
from quantum.memory.context_compatibility import ContextCompatibilityEngine
from quantum.analysis.interaction_classifier import InteractionClassifier
from quantum.analysis.novelty_metrics import NoveltyMetrics

class PairwiseSynergyAuditor:
    """
    Audits pairwise interactions between context-aware patterns to find synergy.
    """

    def __init__(self, memory: Any):
        self.memory = memory
        self.compatibility_engine = ContextCompatibilityEngine()
        self.classifier = InteractionClassifier()
        self.novelty_calculator = NoveltyMetrics(memory)

    def audit_pairwise_interactions(self, causal_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = self.memory.retrieve("quantum:distillation:patterns") or []
        target_context = self.memory.current_context
        
        # Filter patterns compatible with target context
        compatible_patterns = []
        for p in patterns:
            ctx = p.get("context")
            if ctx and self.compatibility_engine.are_compatible(ctx, target_context, 0.75):
                compatible_patterns.append(p)

        n = len(compatible_patterns)
        pairwise_records = []
        
        # Calculate utility of components from causal records
        comp_utilities = {}
        for p in compatible_patterns:
            rep = p["representation"]
            p_id = p.get("pattern_id")
            deltas = [r["delta_score"] for r in causal_records if (r.get("pattern") == rep or r.get("pattern_id") == p_id) and r.get("delta_score") is not None]
            comp_utilities[rep] = statistics.mean(deltas) if deltas else 0.0

        # We will also evaluate the composed pairs
        # Find records of composed scaffolds in the causal records
        scaffolds = self.memory.query_scaffolds() or []
        scaffold_map = {s["representation"]: s for s in scaffolds}

        for i in range(n):
            for j in range(i + 1, n):
                p_a = compatible_patterns[i]
                p_b = compatible_patterns[j]
                
                rep_a = p_a["representation"]
                rep_b = p_b["representation"]
                
                composed_rep = f"{rep_a}->{rep_b}"
                composed_seq = p_a.get("sequence", []) + p_b.get("sequence", [])
                
                # Check if we have this scaffold in memory
                sc = scaffold_map.get(composed_rep)
                sc_id = sc["pattern_id"] if sc else f"scaffold_pair_{abs(hash(composed_rep)) & 0xffffffff}"
                
                # Calculate utility(pair) from causal records
                pair_deltas = [r["delta_score"] for r in causal_records if (r.get("pattern") == composed_rep or r.get("pattern_id") == sc_id) and r.get("delta_score") is not None]
                utility_pair = statistics.mean(pair_deltas) if pair_deltas else 0.0
                
                # Calculate survival probability for the pair
                pair_injections = [r for r in causal_records if (r.get("pattern") == composed_rep or r.get("pattern_id") == sc_id)]
                if pair_injections:
                    survived = sum(1 for r in pair_injections if r.get("survival_status", False))
                    survival_rate = survived / len(pair_injections)
                else:
                    survival_rate = 0.0

                # Synergy Score = utility(pair) - max(utility(a), utility(b))
                utility_a = comp_utilities.get(rep_a, 0.0)
                utility_b = comp_utilities.get(rep_b, 0.0)
                max_comp_utility = max(utility_a, utility_b)
                
                synergy_score = utility_pair - max_comp_utility

                # Interaction Type
                interaction_type = self.classifier.classify_sequence(composed_seq)

                # Novelty
                # We construct a temp scaffold dict to compute similarity
                temp_scaffold = {
                    "sequence": composed_seq,
                    "representation": composed_rep,
                    "context": target_context.to_dict() if hasattr(target_context, "to_dict") else target_context,
                    "survival_probability": survival_rate,
                    "confidence_score": 0.1
                }
                
                # Novelty similarity against other scaffolds/patterns
                max_sim = 0.0
                for other_p in compatible_patterns:
                    other_rep = other_p["representation"]
                    if other_rep == rep_a or other_rep == rep_b:
                        continue
                    # simple similarity
                    seq_a = composed_seq
                    seq_b = other_p.get("sequence", [])
                    sim = difflib.SequenceMatcher(None, seq_a, seq_b).ratio() if seq_a and seq_b else 0.0
                    if sim > max_sim:
                        max_sim = sim
                        
                novelty_score = round(1.0 - max_sim, 4)
                
                record = {
                    "pattern_a": rep_a,
                    "pattern_b": rep_b,
                    "context_a": p_a.get("context"),
                    "context_b": p_b.get("context"),
                    "interaction_type": interaction_type,
                    "synergy_score": round(synergy_score, 4),
                    "utility_pair": round(utility_pair, 4),
                    "max_component_utility": round(max_comp_utility, 4),
                    "fitness": round(utility_pair + survival_rate, 4),
                    "survival": round(survival_rate, 4),
                    "novelty": novelty_score
                }
                pairwise_records.append(record)
                
        # Save to pairwise_synergy_dataset.json
        with open("pairwise_synergy_dataset.json", "w", encoding="utf-8") as f:
            json.dump(pairwise_records, f, indent=2, ensure_ascii=False)

        return pairwise_records

import difflib
