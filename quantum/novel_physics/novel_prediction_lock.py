import hashlib
import json
import os
from typing import Dict, Any, List

class NovelPredictionLock:
    """
    Phase 4F: Blind Novel Physics Challenge - Cryptographic prediction locker.
    Calculates SHA-256 hashes of predictions to prevent retrospective adjustments.
    """

    def lock_predictions(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        locked_records = []
        
        for p in predictions:
            # We serialize the prediction inputs and prediction values
            serial_data = json.dumps({
                "case_id": p.get("case_id"),
                "theory_id": p.get("theory_id"),
                "standard_prediction": p.get("standard_prediction"),
                "rtheory_prediction": p.get("rtheory_prediction")
            }, sort_keys=True)
            
            sha = hashlib.sha256(serial_data.encode("utf-8")).hexdigest()
            
            locked_records.append({
                "case_id": p.get("case_id"),
                "theory_id": p.get("theory_id"),
                "sha256": sha,
                "frozen_record": p
            })

        self._write_markdown_report(locked_records)
        return {"status": "LOCKED", "records": locked_records}

    def _write_markdown_report(self, locked_records: List[Dict[str, Any]]) -> None:
        lines = [
            "# Novel Prediction Cryptographic Lock Registry — Phase 4F",
            "",
            "Registers cryptographic hashes of predictions prior to execution on independent physical quantum hardware.",
            "",
            "| Case ID | Theory ID | Cryptographic Hash (SHA-256) | Frozen Standard Model | Frozen RTHEORY |",
            "| :--- | :--- | :--- | :---: | :---: |"
        ]

        for r in locked_records:
            lines.append(
                f"| `{r['case_id']}` | `{r['theory_id']}` | `{r['sha256'][:24]}...` | `{r['frozen_record']['standard_prediction']:.6f}` | `{r['frozen_record']['rtheory_prediction']:.6f}` |"
            )

        lines.append("")
        os.makedirs("docs", exist_ok=True)
        with open("docs/NOVEL_PREDICTION_LOCK.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
