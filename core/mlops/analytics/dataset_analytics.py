import json
from pathlib import Path


class DatasetAnalytics:
    """Parses and analyzes properties of exported DPO JSONL datasets."""

    def analyze_dpo_jsonl(self, filepath: str) -> dict:
        """Counts total pairs, unique prompts, and density metrics of a versioned DPO dataset.

        Returns 0 counters if file is empty or does not exist.
        """
        default_stats = {
            "total_pairs": 0,
            "unique_prompts": 0,
            "avg_pairs_per_prompt": 0.0,
        }
        if not filepath:
            return default_stats

        path = Path(filepath)
        if not path.exists() or path.is_dir() or path.stat().st_size == 0:
            return default_stats

        total_pairs = 0
        unique_prompts = set()

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                    try:
                        record = json.loads(line_clean)
                        total_pairs += 1
                        prompt = record.get("prompt")
                        if prompt:
                            unique_prompts.add(prompt)
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue
        except Exception:
            return default_stats

        num_prompts = len(unique_prompts)
        avg = (total_pairs / num_prompts) if num_prompts > 0 else 0.0

        return {
            "total_pairs": total_pairs,
            "unique_prompts": num_prompts,
            "avg_pairs_per_prompt": avg,
        }
