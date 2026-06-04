import os
from typing import Dict, Any, List
from quantum.novel_physics.physics_baseline_library import PhysicsBaselineLibrary

class ResidualFrontierEngine:
    """
    Phase 4B: Residual Frontier Discovery.
    Calculates physical anomalies by subtracting standard physics baseline expectations from observations.
    """

    def __init__(self):
        self.baseline_lib = PhysicsBaselineLibrary()

    def discover_residuals(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        residuals = []
        baselines = self.baseline_lib.get_baseline_predictions(observations)

        for obs, base_pred in zip(observations, baselines):
            observed_gap = obs.get("observed_gap", 0.0)
            # Residual gap = observed gap - standard prediction (base_pred is 0.0)
            residual_gap = observed_gap - base_pred

            residuals.append({
                "id": obs.get("id"),
                "device": obs.get("device"),
                "vendor": obs.get("vendor"),
                "paradigm": obs.get("paradigm"),
                "gate_error": obs.get("gate_error"),
                "readout_error": obs.get("readout_error"),
                "observed_gap": observed_gap,
                "standard_prediction": base_pred,
                "residual_gap": round(residual_gap, 6)
            })

        self._write_markdown_report(residuals)
        return residuals

    def _write_markdown_report(self, residuals: List[Dict[str, Any]]) -> None:
        lines = [
            "# Residual Frontier Report — Phase 4B",
            "",
            "Documents the residual physical deviations that survive subtraction of standard physics models.",
            "",
            "| ID | Device | Vendor | Paradigm | Gate Error | Readout Error | Observed Gap | Std Prediction | Residual Gap |",
            "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |"
        ]

        for r in residuals[:15]:  # show sample
            lines.append(
                f"| `{r['id']}` | `{r['device']}` | `{r['vendor']}` | `{r['paradigm']}` | `{r['gate_error']}` | `{r['readout_error']}` | `{r['observed_gap']:.6f}` | `{r['standard_prediction']:.6f}` | **`{r['residual_gap']:.6f}`** |"
            )

        if len(residuals) > 15:
            lines.append(f"| ... | ... | ... | ... | ... | ... | ... | ... | ... |")

        lines.append("")
        os.makedirs("docs", exist_ok=True)
        with open("docs/RESIDUAL_FRONTIER_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
