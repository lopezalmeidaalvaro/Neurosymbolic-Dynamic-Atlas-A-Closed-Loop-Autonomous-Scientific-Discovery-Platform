from typing import Union, Dict, Any
from quantum.knowledge.context_schema import Context

class ContextCompatibilityEngine:
    """
    Evaluates compatibility between source and target contexts for pattern composition and transfer.
    """

    def __init__(self, task_family_scores: Dict[tuple, float] = None, default_family_score: float = 0.5):
        # Configure task families. Pair format: (source_task, target_task)
        self.task_family_scores = task_family_scores or {
            ("bell_state", "ghz_state"): 0.9,
            ("bell_state", "ghz_extension"): 0.9,
            ("ghz_state", "ghz_extension"): 0.9,
        }
        self.default_family_score = default_family_score

    def _normalize_context(self, ctx: Union[Context, Dict[str, Any]]) -> Context:
        if isinstance(ctx, dict):
            return Context.from_dict(ctx)
        return ctx

    def calculate_compatibility(self, ctx_source: Union[Context, Dict[str, Any]], ctx_target: Union[Context, Dict[str, Any]]) -> float:
        src = self._normalize_context(ctx_source)
        tgt = self._normalize_context(ctx_target)

        # 1. Task similarity score
        if src.task_name == tgt.task_name:
            task_score = 1.0
        else:
            pair = (src.task_name, tgt.task_name)
            pair_rev = (tgt.task_name, src.task_name)
            if pair in self.task_family_scores:
                task_score = self.task_family_scores[pair]
            elif pair_rev in self.task_family_scores:
                task_score = self.task_family_scores[pair_rev]
            else:
                task_score = 0.0

        # 2. Qubit topology compatibility score
        if src.qubit_count == tgt.qubit_count:
            qubit_score = 1.0
        elif src.qubit_count < tgt.qubit_count:
            # Expandable topology
            qubit_score = 0.9
        else:
            qubit_score = 0.0

        # 3. Convergence history modifier
        conv_score = 1.0 if src.converged else 0.5

        return round(task_score * qubit_score * conv_score, 4)

    def are_compatible(self, ctx_source: Union[Context, Dict[str, Any]], ctx_target: Union[Context, Dict[str, Any]], threshold: float = 0.75) -> bool:
        return self.calculate_compatibility(ctx_source, ctx_target) >= threshold
