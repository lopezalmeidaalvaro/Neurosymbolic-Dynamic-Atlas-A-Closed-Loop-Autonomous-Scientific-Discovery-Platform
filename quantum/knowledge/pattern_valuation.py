import statistics
from typing import Dict, Any, List, Optional

class PatternValuationEngine:
    """
    Engine to evaluate the epistemic quality of quantum patterns discovered/reused.
    Classifies patterns into HIGH_VALUE, NEUTRAL, TOXIC, and NOISE/JUNK.
    """

    def __init__(self, memory: Any):
        self.memory = memory

    def evaluate_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Processes memory contents and returns valuation metrics for every unique pattern.
        """
        patterns = self.memory.query_patterns() or []
        causal_records = self.memory.retrieve("quantum:distillation:causal_records") or []
        knowledge_graph = self.memory.get_knowledge_graph() or {"nodes": {}, "edges": []}

        nodes = knowledge_graph.get("nodes", {})
        edges = knowledge_graph.get("edges", [])

        # Group causal records by pattern representation
        causal_by_pattern = {}
        for record in causal_records:
            pat = record.get("pattern") or record.get("pattern_repr")
            if pat:
                causal_by_pattern.setdefault(pat, []).append(record)

        # Map pattern representations to matching Pattern nodes in the knowledge graph
        # and trace their Circuit connections
        graph_patterns = {}
        for nid, ndata in nodes.items():
            if ndata.get("type") == "Pattern":
                seq = ndata.get("attributes", {}).get("sequence", [])
                if seq:
                    rep = "->".join(seq)
                    graph_patterns.setdefault(rep, []).append(nid)

        evaluated = {}
        for p in patterns:
            rep = p.get("representation")
            if not rep:
                continue

            # 1. Frequency
            freq = p.get("frequency", 1)

            # 2. Get circuits containing this pattern from the knowledge graph
            matching_pattern_nodes = graph_patterns.get(rep, [])
            scores = []
            fidelities = []
            generations_present = set()

            # Find Circuit nodes that contain this pattern
            circuits_containing = set()
            for edge in edges:
                if edge.get("type") == "contains_pattern" and edge.get("target") in matching_pattern_nodes:
                    circuits_containing.add(edge.get("source"))

            for cid in circuits_containing:
                cnode = nodes.get(cid)
                if cnode and cnode.get("type") == "Circuit":
                    attrs = cnode.get("attributes", {})
                    # We check if raw=True to ensure it was evaluated and has metrics
                    if attrs.get("raw", False):
                        scores.append(attrs.get("score", 0.0))
                        fidelities.append(attrs.get("fidelity", 0.0))

            # Trace generations present
            for cid in circuits_containing:
                for edge in edges:
                    if edge.get("type") == "discovered_in_generation" and edge.get("source") == cid:
                        gen_node_id = edge.get("target")
                        gen_node = nodes.get(gen_node_id)
                        if gen_node and gen_node.get("type") == "Generation":
                            gen_num = gen_node.get("attributes", {}).get("number")
                            if gen_num is not None:
                                generations_present.add(gen_num)

            mean_score = statistics.mean(scores) if scores else float(p.get("avg_score", 0.0))
            mean_fidelity = statistics.mean(fidelities) if fidelities else 0.0

            # 3. P(convergence | pattern)
            total_circuits = len(fidelities)
            converged_circuits = sum(1 for f in fidelities if f >= 0.99)
            p_convergence = converged_circuits / total_circuits if total_circuits > 0 else 0.0

            # 4. mean_delta_score
            pat_causal = causal_by_pattern.get(rep, [])
            delta_scores = [r.get("delta_score") for r in pat_causal if r.get("delta_score") is not None]
            mean_delta = statistics.mean(delta_scores) if delta_scores else 0.0

            # 5. survival_probability
            if pat_causal:
                survived_count = sum(1 for r in pat_causal if r.get("survival_status", False))
                survival_prob = survived_count / len(pat_causal)
            elif generations_present:
                gens = sorted(list(generations_present))
                survived_generations = sum(1 for g in gens if (g + 1) in generations_present)
                survival_prob = survived_generations / len(gens)
            else:
                survival_prob = 0.0

            # 6. Classification
            category = self.classify_pattern(rep, freq, mean_score, mean_fidelity, survival_prob, p_convergence, mean_delta)

            evaluated[rep] = {
                "pattern_id": p.get("pattern_id"),
                "sequence": p.get("sequence", []),
                "representation": rep,
                "frequency": freq,
                "mean_score": round(mean_score, 4),
                "mean_fidelity": round(mean_fidelity, 4),
                "survival_probability": round(survival_prob, 4),
                "P_convergence": round(p_convergence, 4),
                "mean_delta_score": round(mean_delta, 4),
                "category": category
            }

        return evaluated

    @staticmethod
    def classify_pattern(
        representation: str,
        frequency: int,
        mean_score: float,
        mean_fidelity: float,
        survival_probability: float,
        P_convergence: float,
        mean_delta_score: float
    ) -> str:
        """
        Categorizes a pattern into HIGH_VALUE, TOXIC, NOISE/JUNK, or NEUTRAL.
        """
        # Rule 1: Redundant self-inverse gates (e.g., X->X, H->H) -> NOISE/JUNK
        parts = representation.split("->")
        has_self_inverse = False
        for i in range(len(parts) - 1):
            p1 = parts[i].split("(")[0].strip()
            p2 = parts[i+1].split("(")[0].strip()
            if p1 == p2 and p1 in ("H", "X"):
                q1 = parts[i].split("(")[1].rstrip(")") if "(" in parts[i] else None
                q2 = parts[i+1].split("(")[1].rstrip(")") if "(" in parts[i+1] else None
                if q1 == q2:
                    has_self_inverse = True
                    break
        
        if has_self_inverse:
            return "NOISE/JUNK"

        # Rule 2: TOXIC - Negative delta score and zero survival probability
        if mean_delta_score < 0.0 and survival_probability == 0.0:
            return "TOXIC"

        # Rule 3: NOISE/JUNK - High frequency but zero contribution and zero convergence probability
        if mean_delta_score <= 0.0 and P_convergence == 0.0 and frequency >= 5:
            return "NOISE/JUNK"

        # Rule 4: HIGH_VALUE - Positive delta score OR non-zero survival/convergence probability
        if mean_delta_score > 0.0 or (survival_probability > 0.1 and P_convergence > 0.1):
            return "HIGH_VALUE"

        # Rule 5: NEUTRAL - Default
        return "NEUTRAL"
