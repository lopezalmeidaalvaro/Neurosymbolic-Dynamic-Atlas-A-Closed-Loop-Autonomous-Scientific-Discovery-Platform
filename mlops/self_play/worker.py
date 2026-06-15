import time
from mathematics import MathEngine, QuantumEquivalenceIR


class SelfPlayWorker:
    """Orchestrates self-play sessions by verifying synthetic motifs against the MathEngine."""

    def __init__(self, math_engine: MathEngine) -> None:
        self.math_engine = math_engine

    def run_self_play_session(self, motifs: list[QuantumEquivalenceIR]) -> dict:
        """Verifies all input motifs and collects session execution statistics."""
        start_time = time.perf_counter()
        success_count = 0
        failure_count = 0

        for motif in motifs:
            # Run verification loop/MCTS via MathEngine facade
            res = self.math_engine.verify_discovery(motif)
            if res.get("success", False):
                success_count += 1
            else:
                failure_count += 1

        elapsed = time.perf_counter() - start_time

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "total_time_seconds": elapsed,
            "total_processed": len(motifs),
        }
