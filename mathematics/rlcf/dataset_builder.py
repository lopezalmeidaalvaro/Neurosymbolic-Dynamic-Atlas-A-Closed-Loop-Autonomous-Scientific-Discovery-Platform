import json
from collections import defaultdict
from pathlib import Path
from mathematics.knowledge_base.library_manager import FormalKnowledgeBase


class DPODatasetGenerator:
    """Generates DPO (Direct Preference Optimization) training datasets

    from proof step trajectories stored in the FormalKnowledgeBase.
    """

    def __init__(self, kb: FormalKnowledgeBase) -> None:
        self.kb = kb

    def generate_dpo_jsonl(self, output_path: str | Path) -> int:
        """Extracts trajectories, pairs them relatively by reward, and writes a DPO JSONL dataset.

        Returns the number of DPO pairs generated.
        """
        # Ensure parent directory exists
        out_path = Path(output_path)
        if out_path.parent:
            out_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Retrieve all trajectories
        trajectories = self.kb.get_all_trajectories()

        # 2. Group by state_context
        grouped = defaultdict(list)
        for traj in trajectories:
            grouped[traj["state_context"]].append(traj)

        # 3. Generate DPO pairs
        pair_count = 0
        seen_pairs = set()
        with open(out_path, "w", encoding="utf-8") as f:
            for state_context, steps in grouped.items():
                n = len(steps)
                # Compare all pairs (step A, step B) within this context
                for i in range(n):
                    for j in range(n):
                        if i == j:
                            continue
                        step_a = steps[i]
                        step_b = steps[j]
                        # chosen (tactic_A) must have STRICTLY higher reward than rejected (tactic_B)
                        # and tactics must be different to form a valid preference pair
                        if (
                            step_a["reward"] > step_b["reward"]
                            and step_a["tactic_applied"] != step_b["tactic_applied"]
                        ):
                            pair_key = (
                                state_context,
                                step_a["tactic_applied"],
                                step_b["tactic_applied"],
                            )
                            if pair_key not in seen_pairs:
                                seen_pairs.add(pair_key)
                                dpo_pair = {
                                    "prompt": state_context,
                                    "chosen": step_a["tactic_applied"],
                                    "rejected": step_b["tactic_applied"],
                                }
                                f.write(json.dumps(dpo_pair) + "\n")
                                pair_count += 1

        return pair_count
