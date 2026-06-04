import os
from typing import Dict, Any, List

class ExperimentDesigner:
    """
    Phase 4E: Experimental Design Engine.
    Designs physical experiments that maximize the divergence |A - B| between Standard Physics (A) and RTHEORY (B)
    to stress test and attempt to destroy the candidate theory.
    """

    def __init__(self, impossible_cases: List[Dict[str, Any]]):
        self.cases = impossible_cases

    def design_experiments(self) -> List[Dict[str, Any]]:
        designed_experiments = []

        # Group cases by theory and find the one with maximum divergence
        theory_max_div = {}
        for c in self.cases:
            t_id = c["theory_id"]
            if t_id not in theory_max_div or c["divergence"] > theory_max_div[t_id]["divergence"]:
                theory_max_div[t_id] = c

        for t_id, case in theory_max_div.items():
            # Stress testing strategy: probe higher error rates or lower error rates where RTHEORY extrapolation
            # might break down, maximizing the stress factor.
            opt_gate = case["gate_error"]
            opt_read = case["readout_error"]

            designed_experiments.append({
                "experiment_id": f"EXP_{t_id.split('_')[1]}",
                "theory_id": t_id,
                "domain": case["domain"],
                "target_gate_error": opt_gate,
                "target_readout_error": opt_read,
                "expected_divergence": case["divergence"],
                "required_shots": 10000,  # high precision shots
                "calibration_frequency": "Every 2 hours",
                "verification_devices": ["rigetti_aspen_m3", "ionq_aria", "quantinuum_h1"],
                "stress_mechanism": "Continuous execution at extreme gate/readout boundary grid coordinate."
            })

        self._write_markdown_report(designed_experiments)
        return designed_experiments

    def _write_markdown_report(self, experiments: List[Dict[str, Any]]) -> None:
        lines = [
            "# Experimental Stress Design Report — Phase 4E",
            "",
            "Designs physical experiment sweeps that maximize prediction divergence to falsify the RTHEORY model.",
            "",
            "| Experiment ID | Theory ID | Physical Domain | Target Gate Error | Target Readout Error | Expected Divergence | Min Shots | Verification Devices |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |"
        ]

        for e in experiments:
            lines.append(
                f"| `{e['experiment_id']}` | `{e['theory_id']}` | `{e['domain']}` | `{e['target_gate_error']}` | `{e['target_readout_error']}` | `{e['expected_divergence']:.6f}` | `{e['required_shots']}` | `{', '.join(e['verification_devices'])}` |"
            )

        lines.append("")
        os.makedirs("docs", exist_ok=True)
        with open("docs/NOVEL_EXPERIMENTAL_DESIGN.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
