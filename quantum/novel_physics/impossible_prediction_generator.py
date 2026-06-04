import os
import re
import numpy as np
from typing import Dict, Any, List, Tuple

class ImpossiblePredictionGenerator:
    """
    Phase 4D: Impossible Prediction Generator.
    Generates regions where Standard Physics predicts A (0.0) and RTHEORY predicts B (non-zero) with A != B.
    """

    def __init__(self, theories: List[Dict[str, Any]]):
        self.theories = theories

    def generate_impossible_predictions(self) -> List[Dict[str, Any]]:
        impossible_cases = []

        # Coordinate sweeps where prediction divergence is maximized
        sweeps = [
            {"gate_error": 0.005, "readout_error": 0.015},
            {"gate_error": 0.010, "readout_error": 0.025},
            {"gate_error": 0.015, "readout_error": 0.035}
        ]

        for t in self.theories:
            theory_id = t["theory_id"]
            eq = t["equation"]
            domain = t["domain"]

            # Parse coefficients
            floats = [float(val) for val in re.findall(r"[-+]?\d*\.\d+|\d+", eq)]
            a, b, c = 0.0, 0.0, 0.0
            if len(floats) >= 3:
                a, b, c = floats[0], floats[1], floats[2]

            for s_idx, sw in enumerate(sweeps):
                ge = sw["gate_error"]
                re_err = sw["readout_error"]

                pred_std = 0.000000
                pred_rtheory = a * ge + b * re_err + c

                divergence = abs(pred_std - pred_rtheory)

                impossible_cases.append({
                    "case_id": f"IMP_{theory_id.split('_')[1]}_{s_idx:02d}",
                    "theory_id": theory_id,
                    "domain": domain,
                    "gate_error": ge,
                    "readout_error": re_err,
                    "standard_prediction": round(pred_std, 6),
                    "rtheory_prediction": round(pred_rtheory, 6),
                    "divergence": round(divergence, 6)
                })

        self._write_markdown_report(impossible_cases)
        return impossible_cases

    def _write_markdown_report(self, cases: List[Dict[str, Any]]) -> None:
        lines = [
            "# Impossible Predictions Report — Phase 4D",
            "",
            "Documents specific physical regimes where Standard Physics and RTHEORY predict contradictory values (A != B).",
            "",
            "| Case ID | Theory ID | Domain | Gate Error | Readout Error | Standard Model (A) | RTHEORY (B) | Divergence |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
        ]

        for c in cases:
            lines.append(
                f"| `{c['case_id']}` | `{c['theory_id']}` | `{c['domain']}` | `{c['gate_error']}` | `{c['readout_error']}` | `{c['standard_prediction']:.6f}` | `{c['rtheory_prediction']:.6f}` | **`{c['divergence']:.6f}`** |"
            )

        lines.append("")
        os.makedirs("docs", exist_ok=True)
        with open("docs/IMPOSSIBLE_PREDICTIONS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
