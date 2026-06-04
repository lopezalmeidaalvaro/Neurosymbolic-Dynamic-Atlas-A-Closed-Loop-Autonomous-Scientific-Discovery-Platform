import os
import time
from typing import List, Dict, Any

class ExperimentLogger:
    @staticmethod
    def log_benchmark_run(
        benchmark_name: str,
        seed_values: List[int],
        convergence_metrics: Dict[str, Any],
        transfer_learning_outcomes: Dict[str, Any],
        discovered_motifs: List[str],
        output_path: str = "docs/EXPERIMENT_LOG.md"
    ) -> None:
        """
        Formats and appends a benchmark run to docs/EXPERIMENT_LOG.md.
        Ensures the file is created with default headers if it does not exist.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if file exists to determine if we should write header
        file_exists = os.path.exists(output_path)
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the seeds list
        seeds_str = ", ".join(map(str, seed_values))
        
        # Format the convergence metrics and transfer outcomes
        cold_avg = convergence_metrics.get("cold_avg_generations", "N/A")
        warm_avg = convergence_metrics.get("warm_avg_generations", "N/A")
        speedup = transfer_learning_outcomes.get("average_speedup", "N/A")
        utilization = transfer_learning_outcomes.get("average_utilization", "N/A")
        
        # Format discovered/reused motifs
        motifs_str = ", ".join([f"`{m}`" for m in discovered_motifs]) if discovered_motifs else "None"
        
        entry = f"""
## Run: {benchmark_name} - {timestamp}
- **Timestamp:** {timestamp}
- **Seeds Evaluated:** [{seeds_str}]
- **Convergence Metrics:**
  - Average Generations (Cold Start): {cold_avg}
  - Average Generations (Warm Start): {warm_avg}
- **Transfer Learning Outcomes:**
  - Average Speedup: {speedup if isinstance(speedup, str) else f"{speedup:.4f}x"}
  - Avg Knowledge Utilization Rate: {utilization if isinstance(utilization, str) else f"{utilization:.4f}"}
- **Discovered & Reused Motifs:** {motifs_str}
- **Status:** SUCCESS

---
"""
        
        mode = "a" if file_exists else "w"
        
        with open(output_path, mode, encoding="utf-8") as f:
            if not file_exists:
                f.write(f"""# Scientific Experiment Log

This file acts as a chronological, immutable ledger of all scientific experiments, benchmark executions, and training runs.

---
""")
            f.write(entry)
            
        print(f"[INFO] ExperimentLogger: Appended experiment details to {output_path}")
