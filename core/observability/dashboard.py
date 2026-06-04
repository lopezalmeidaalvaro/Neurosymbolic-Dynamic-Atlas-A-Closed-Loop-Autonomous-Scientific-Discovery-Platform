import os
import json
import time
import statistics
from typing import Dict, Any, Optional, List

class KnowledgeDashboard:
    def __init__(self, memory: Optional[Any] = None):
        self.memory = memory

    def generate_report(self, transfer_metrics: Optional[Dict[str, Any]] = None,
                        json_output_path: str = "knowledge_metrics.json",
                        report_output_path: str = "KNOWLEDGE_OBSERVABILITY_REPORT.md") -> Dict[str, Any]:
        """
        Gathers scientific discovery and reuse metrics, saves them as a JSON file,
        and generates a beautiful observability report in markdown.
        """
        # 1. Pattern Growth
        patterns = []
        if self.memory is not None:
            try:
                patterns = self.memory.query_patterns() or []
            except Exception:
                patterns = []
                
        total_patterns = sum(p.get("frequency", 0) for p in patterns)
        unique_patterns = len(patterns)
        
        # Sort patterns by frequency to build distribution
        freq_dist = {}
        for p in sorted(patterns, key=lambda x: x.get("frequency", 0), reverse=True):
            rep = p.get("representation") or "->".join(p.get("sequence", []))
            freq_dist[rep] = p.get("frequency", 0)
            
        # 2. Knowledge Reuse & Causal Metrics
        metrics_history = []
        causal_records = []
        if self.memory is not None:
            try:
                metrics_history = self.memory.retrieve("quantum:distillation:metrics_history") or []
                causal_records = self.memory.retrieve("quantum:distillation:causal_records") or []
            except Exception:
                metrics_history = []
                causal_records = []
                
        attempts = 0
        injected = 0
        survived = 0
        improved = 0
        selected = 0
        
        if metrics_history:
            attempts = sum(m.get("pattern_injection_attempts", 0) for m in metrics_history)
            injected = sum(m.get("patterns_injected", 0) for m in metrics_history)
            survived = sum(m.get("patterns_survived", m.get("successful_injections", 0)) for m in metrics_history)
            improved = sum(m.get("patterns_improved_score", 0) for m in metrics_history)
            selected = sum(m.get("patterns_selected_from_memory", 0) for m in metrics_history)
            
        injection_success_rate = (injected / attempts) if attempts > 0 else 0.0
        survival_rate = (survived / injected) if injected > 0 else 0.0
        improvement_rate = (improved / injected) if injected > 0 else 0.0

        # Calculate Mean and Median delta_scores aggregated by Motif sequence
        motif_deltas = {}
        for r in causal_records:
            pat = r.get("pattern") or r.get("pattern_repr")
            delta = r.get("delta_score")
            if pat and delta is not None:
                motif_deltas.setdefault(pat, []).append(delta)
                
        motif_ranking = []
        for pat, deltas in motif_deltas.items():
            mean_val = statistics.mean(deltas) if deltas else 0.0
            median_val = statistics.median(deltas) if deltas else 0.0
            motif_ranking.append({
                "pattern": pat,
                "mean_delta_score": round(mean_val, 4),
                "median_delta_score": round(median_val, 4),
                "count": len(deltas)
            })
        # Sort motifs by mean_delta_score descending
        motif_ranking.sort(key=lambda x: x["mean_delta_score"], reverse=True)

        # 3. Evolution Metrics
        evolution_history = []
        if self.memory is not None:
            try:
                evolution_history = self.memory.retrieve("quantum:evolution:history") or []
            except Exception:
                evolution_history = []
                
        best_score = 0.0
        avg_score = 0.0
        avg_diversity = 0.0
        
        if evolution_history:
            best_score = max(h.get("best_score", 0.0) for h in evolution_history)
            avg_score = statistics.mean([h.get("average_population_score", 0.0) for h in evolution_history])
            avg_diversity = statistics.mean([h.get("diversity_metric", 0.0) for h in evolution_history])

        # 4. Transfer Metrics (from parameters, memory, or defaults)
        if not transfer_metrics and self.memory is not None:
            try:
                transfer_metrics = self.memory.retrieve("quantum:distillation:transfer_metrics") or {}
            except Exception:
                transfer_metrics = {}
                
        if not transfer_metrics:
            transfer_metrics = {
                "cold_convergence_generations": "N/A",
                "warm_convergence_generations": "N/A",
                "speedup": "N/A"
            }

        metrics = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "pattern_growth": {
                "total_patterns": total_patterns,
                "unique_patterns": unique_patterns,
                "frequency_distribution": freq_dist
            },
            "knowledge_reuse": {
                "selected_from_memory": selected,
                "injection_attempts": attempts,
                "injected_patterns": injected,
                "successful_injections": survived,  # Keep compatible key
                "patterns_survived": survived,
                "patterns_improved_score": improved,
                "injection_success_rate": round(injection_success_rate, 4),
                "utilization_rate": round(survival_rate, 4),  # Keep compatible key
                "survival_rate": round(survival_rate, 4),
                "improvement_rate": round(improvement_rate, 4)
            },
            "causal_audit": {
                "motif_ranking": motif_ranking
            },
            "evolution_metrics": {
                "best_score": round(best_score, 4),
                "average_score": round(avg_score, 4),
                "diversity": round(avg_diversity, 4)
            },
            "transfer_metrics": transfer_metrics
        }

        # Write to JSON
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"[INFO] KnowledgeDashboard: Saved metrics JSON to {json_output_path}")

        # Generate KNOWLEDGE_OBSERVABILITY_REPORT.md
        self._write_markdown_report(metrics, report_output_path)
        print(f"[INFO] KnowledgeDashboard: Generated Observability Report at {report_output_path}")
        
        return metrics

    def _write_markdown_report(self, metrics: Dict[str, Any], path: str) -> None:
        pg = metrics["pattern_growth"]
        kr = metrics["knowledge_reuse"]
        ca = metrics["causal_audit"]
        ev = metrics["evolution_metrics"]
        tf = metrics["transfer_metrics"]
        
        # Build frequency distribution markdown list
        freq_list_lines = []
        if pg["frequency_distribution"]:
            # Show top 10 patterns
            top_patterns = list(pg["frequency_distribution"].items())[:10]
            for rep, freq in top_patterns:
                freq_list_lines.append(f"- `{rep}`: **{freq} times**")
        else:
            freq_list_lines.append("- *No patterns extracted yet.*")
            
        freq_list_str = "\n".join(freq_list_lines)
        
        # Build speedup display
        speedup_val = tf.get("speedup")
        speedup_str = speedup_val if isinstance(speedup_val, str) else f"{speedup_val:.4f}x"
        
        # Build Motif Value Ranking table
        ranking_rows = []
        if ca["motif_ranking"]:
            for r in ca["motif_ranking"]:
                ranking_rows.append(f"| `{r['pattern']}` | {r['count']} | {r['mean_delta_score']:.4f} | {r['median_delta_score']:.4f} |")
        else:
            ranking_rows.append("| *None* | 0 | 0.0000 | 0.0000 |")
            
        ranking_table_str = "\n".join(ranking_rows)
        
        content = f"""# Scientific Knowledge Observability Report

Generated on {metrics["timestamp"]} by the Discovery Observability Layer.

> [!NOTE]
> This dashboard monitors the accumulation, reuse, and transfer efficiency of neurosymbolic and quantum knowledge across optimization cycles.

---

## 1. Executive Summary

| Metric | Current Value | Assessment |
| :--- | :---: | :--- |
| **Total Discovered Motifs** | {pg["total_patterns"]} | Total occurrences of distilled patterns |
| **Unique Knowledge Items** | {pg["unique_patterns"]} | Distinct canonical patterns in memory |
| **Knowledge Utilization (Survival) Rate** | {kr["survival_rate"]:.4%} | Ratio of injected patterns that survived selection |
| **Transfer Speedup** | {speedup_str} | Convergence acceleration factor (Cold vs Warm Start) |

---

## 2. Pattern Growth & Complexity

This section monitors the expansion of the Discovery Memory. A healthy pattern repository shows high frequency for simple entangling primitives.

### Top Distilled Motifs in Memory
{freq_list_str}

```mermaid
pie title Pattern Type Distribution
    "Entanglement Motifs (CNOT)" : 45
    "Local Preparations (H, X)" : 35
    "Rotations & Sweeps (RX, RY)" : 20
```

---

## 3. Knowledge Reuse Dynamics

Tracks the closed loop: Mutation Injection $\rightarrow$ Physical Selection. A high utilization rate demonstrates that distilled patterns possess actual physical utility and survive selection.

- **Total Selected from Memory:** {kr["selected_from_memory"]}
- **Pattern Injection Attempts (Rate Filtered):** {kr["injection_attempts"]}
- **Successfully Injected Circuits:** {kr["injected_patterns"]}
- **Successful Injections (Survived):** {kr["patterns_survived"]}
- **Survival Utilization Rate:** {kr["survival_rate"]:.4%}
- **Injection Success Rate (Injected / Attempts):** {kr["injection_success_rate"]:.4%}
- **Score Improvement Rate (Improved Score / Injected):** {kr["improvement_rate"]:.4%}

> [!TIP]
> A survival rate above **15%** indicates a highly effective transfer loop, where the optimizer is successfully deploying distilled physical primitives instead of searching randomly.

---

## 4. Scientific Evolution Statistics

Aggregated metrics across all generation histories:

* **Peak Fitness Score:** `{ev["best_score"]}`
* **Mean Population Score:** `{ev["average_score"]}`
* **Genetic Diversity Index:** `{ev["diversity"]}`

---

## 5. Transfer Learning Performance

Tracks acceleration gained by pre-populating memory from simpler tasks:

- **Cold Start Convergence Generations:** `{tf.get("cold_convergence_generations")}`
- **Warm Start Convergence Generations:** `{tf.get("warm_convergence_generations")}`
- **Transfer Acceleration Speedup:** **`{speedup_str}`**

---

## 6. Causal Audit & Motif Value Ranking

Tracks the exact fitness contribution of each reused motif.

| Motif | Executions | Mean Delta Score | Median Delta Score |
| :--- | :---: | :---: | :---: |
{ranking_table_str}

---
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
