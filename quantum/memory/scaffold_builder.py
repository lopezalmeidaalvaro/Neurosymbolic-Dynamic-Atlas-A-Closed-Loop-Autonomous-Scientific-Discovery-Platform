import time
import copy
from typing import List, Dict, Any, Optional
from quantum.knowledge.context_schema import Context
from quantum.memory.context_compatibility import ContextCompatibilityEngine
from quantum.knowledge.knowledge_graph import QuantumKnowledgeGraph
from quantum.optimization.pyzx_optimizer import PyZXOptimizer

class ContextAwareScaffoldBuilder:
    """
    Composes compatible context-aware patterns from memory into higher-order reusable structures.
    """

    def __init__(self, memory: Any, compatibility_engine: Optional[ContextCompatibilityEngine] = None):
        self.memory = memory
        self.compatibility_engine = compatibility_engine or ContextCompatibilityEngine()
        self.pyzx_optimizer = PyZXOptimizer()

    def compute_confidence(self, support_count: int, successful_reuses: int, successful_transfers: int) -> float:
        """
        Computes an evidence-weighted confidence score between 0.1 and 1.0.
        """
        if support_count == 0:
            return 0.1
        support_factor = min(1.0, support_count / 5.0)
        reuse_rate = successful_reuses / support_count
        transfer_rate = successful_transfers / support_count
        return round(0.1 + 0.9 * support_factor * (0.5 * reuse_rate + 0.5 * transfer_rate), 4)

    def build_scaffolds(self, target_context: Context, threshold: float = 0.75) -> List[Dict[str, Any]]:
        patterns = self.memory.retrieve("quantum:distillation:patterns") or []
        existing_scaffolds = self.memory.retrieve("quantum:distillation:scaffolds") or []
        
        # Filter patterns compatible with the target context
        compatible_patterns = []
        for p in patterns:
            ctx_data = p.get("context")
            if not ctx_data:
                continue
            if self.compatibility_engine.are_compatible(ctx_data, target_context, threshold):
                compatible_patterns.append(p)
                
        new_scaffolds = {s["representation"]: s for s in existing_scaffolds}
        
        # Retrieve graph once for batching
        graph_dict = self.memory.retrieve("quantum:distillation:knowledge_graph") or {"nodes": {}, "edges": []}
        graph = QuantumKnowledgeGraph()
        graph.nodes = graph_dict.get("nodes", {})
        graph.edges = graph_dict.get("edges", [])
        graph_modified = False
        
        # Compose compatible pairs
        n = len(compatible_patterns)
        for i in range(n):
            for j in range(i + 1, n):
                p_a = compatible_patterns[i]
                p_b = compatible_patterns[j]
                
                seq_a = p_a.get("sequence", [])
                seq_b = p_b.get("sequence", [])
                
                if len(seq_a) + len(seq_b) > 5:
                    continue
                    
                composed_seq = seq_a + seq_b
                
                # PyZX optimize
                optimized_seq, opt_metrics = self.pyzx_optimizer.optimize_sequence(composed_seq)
                rep = "->".join(optimized_seq)
                
                # If already exists, we increase support count
                if rep in new_scaffolds:
                    new_scaffolds[rep]["support_count"] += 1
                    # Recalculate confidence
                    sc = new_scaffolds[rep]
                    new_scaffolds[rep]["confidence_score"] = self.compute_confidence(
                        sc["support_count"], sc["successful_reuses"], sc["successful_transfers"]
                    )
                else:
                    p_conv = round((p_a.get("P_convergence", 0.0) + p_b.get("P_convergence", 0.0)) / 2, 4)
                    surv_prob = round((p_a.get("survival_probability", 0.5) + p_b.get("survival_probability", 0.5)) / 2, 4)
                    mean_delta = round((p_a.get("mean_delta_score", 0.0) + p_b.get("mean_delta_score", 0.0)) / 2, 4)
                    
                    sc_id = f"scaffold_{abs(hash(rep)) & 0xffffffff}"
                    confidence = self.compute_confidence(1, 0, 0)
                    
                    new_scaffolds[rep] = {
                        "pattern_id": sc_id,
                        "sequence": optimized_seq,
                        "representation": rep,
                        "context": target_context.to_dict(),
                        "source_patterns": [p_a["representation"], p_b["representation"]],
                        "source_contexts": [p_a.get("context"), p_b.get("context")],
                        "generation_time": time.time(),
                        "confidence_score": confidence,
                        "support_count": 1,
                        "successful_reuses": 0,
                        "successful_transfers": 0,
                        "P_convergence": p_conv,
                        "survival_probability": surv_prob,
                        "mean_delta_score": mean_delta,
                        "is_scaffold": True,
                        "type": "COMPOSITE",
                        # Metrics from PyZX optimization
                        "compression_ratio": opt_metrics["compression_ratio"],
                        "gate_reduction": opt_metrics["gate_reduction"],
                        "depth_reduction": opt_metrics["depth_reduction"],
                        "utility_preservation": opt_metrics["utility_preservation"]
                    }
                    
                    # Batch update knowledge graph
                    sc_node_id = f"scaffold_{sc_id}"
                    graph.add_node(
                        sc_node_id, 
                        "CompositeScaffold", 
                        sequence=optimized_seq,
                        confidence=confidence
                    )
                    
                    pat_a_id = f"pattern_{p_a.get('pattern_id')}"
                    pat_b_id = f"pattern_{p_b.get('pattern_id')}"
                    
                    if pat_a_id in graph.nodes:
                        graph.add_edge(sc_node_id, pat_a_id, "composed_from")
                    if pat_b_id in graph.nodes:
                        graph.add_edge(sc_node_id, pat_b_id, "composed_from")
                    graph_modified = True

        scaffold_list = list(new_scaffolds.values())
        self.memory.store("quantum:distillation:scaffolds", scaffold_list)
        
        if graph_modified:
            self.memory.store("quantum:distillation:knowledge_graph", graph.to_dict())
            
        return scaffold_list
