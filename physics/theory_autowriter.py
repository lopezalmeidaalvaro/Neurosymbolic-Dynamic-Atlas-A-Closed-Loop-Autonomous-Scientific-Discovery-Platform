from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import sympy as sp

try:
    from physics.core.base_module import ScientificModule
    from physics.physics_sanity_engine import PhysicsSanityEngine
    from physics.scientific_guard import assign_claim_level, sanitize_hypothesis
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from physics_sanity_engine import PhysicsSanityEngine
    from scientific_guard import assign_claim_level, sanitize_hypothesis


class TheoryAutowriter(ScientificModule):
    """MVP. Solo campos escalares, sin cuantización, sin loops."""

    def generate_lagrangian_family(self, variables: list[str], symmetries: list[str], max_terms: int = 10) -> dict[str, Any]:
        warnings = []
        omitted = 0
        if len(variables) > 2:
            omitted += len(variables) - 2
            variables = variables[:2]
            warnings.append("Truncated to max 2 scalar fields.")
        max_terms = min(max_terms, 10)
        t = sp.Symbol("t")
        terms = []
        for name in variables:
            phi = sp.Function(name)(t)
            dphi = sp.diff(phi, t)
            m = sp.Symbol(f"m_{name}", positive=True)
            lam = sp.Symbol(f"lambda_{name}", positive=True)
            candidate_terms = [sp.Rational(1, 2) * dphi**2, -sp.Rational(1, 2) * m**2 * phi**2, -lam * phi**4 / 24]
            if "shift" not in symmetries:
                g = sp.Symbol(f"g_{name}")
                candidate_terms.append(-g * phi)
            for term in candidate_terms:
                dimension = _term_dimension(term)
                if dimension <= 4 and len(terms) < max_terms:
                    terms.append(term)
                else:
                    omitted += 1
        if omitted:
            warnings.append(f"WARNING: omitted_terms={omitted} due to max_terms/dimension/search limits.")
        lagrangian = sp.simplify(sum(terms))
        return {"lagrangian": lagrangian, "variables": variables, "warnings": warnings, "omitted_terms": omitted}

    def derive_equations_of_motion(self, lagrangian, variables: list[str]) -> dict[str, str]:
        t = sp.Symbol("t")
        equations = {}
        for name in variables:
            phi = sp.Function(name)(t)
            dphi = sp.diff(phi, t)
            eom = sp.simplify(sp.diff(lagrangian, phi) - sp.diff(sp.diff(lagrangian, dphi), t))
            equations[name] = str(eom)
        return equations

    def check_consistency(self, lagrangian, symmetries: list[str]) -> dict[str, Any]:
        text = str(lagrangian)
        stability = "lambda" in text and "-lambda" in text
        symmetry_ok = True
        if "z2" in [item.lower() for item in symmetries]:
            symmetry_ok = all(power not in text for power in ["**3", "g_"])
        return {
            "stability": stability,
            "symmetry_ok": symmetry_ok,
            "minimum_action_form": bool(lagrangian != 0),
            "passed": bool(stability and symmetry_ok and lagrangian != 0),
        }

    def derive_predictions(self, equations: dict[str, str]) -> list[dict[str, Any]]:
        predictions = []
        for field, equation in equations.items():
            predictions.append(
                {
                    "field": field,
                    "prediction": f"Small oscillation residual for {field} should remain below 0.1 under normalized perturbation.",
                    "falsification_test": "residual_mse > 0.1",
                    "equation": equation,
                }
            )
        return predictions

    def validate_theory(self, hypothesis: dict[str, Any]) -> dict[str, Any]:
        sanity = PhysicsSanityEngine().validate_hypothesis(hypothesis)
        claim = assign_claim_level(hypothesis.get("hypothesis", ""), "symbolic MVP theory generation only")
        valid = bool(sanity.get("accepted") and claim["level"] <= 2)
        return {"valid": valid, "sanity": sanity, "claim_level": claim}

    def run(self, domain: str = "scalar_field", **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        family = self.generate_lagrangian_family(["phi", "chi"], ["z2"], max_terms=10)
        equations = self.derive_equations_of_motion(family["lagrangian"], family["variables"])
        consistency = self.check_consistency(family["lagrangian"], ["z2"])
        predictions = self.derive_predictions(equations)
        hypothesis = {
            "hypothesis": sanitize_hypothesis("Generated scalar-field MVP theory has falsable small-oscillation predictions."),
            "equation": next(iter(equations.values())) if equations else "0",
            "variables": family["variables"][:2],
            "falsification_test": "residual_mse > 0.1",
            "confidence_prior": 0.3,
            "system_type": "unknown",
            "variable_ranges": {name: (-1.0, 1.0) for name in family["variables"]},
        }
        validation = self.validate_theory(hypothesis)
        theory_status = "valid" if validation["valid"] and consistency["passed"] else "invalid"
        metrics = {
            "domain": domain,
            "terms": len(sp.Add.make_args(family["lagrangian"])),
            "omitted_terms": family["omitted_terms"],
            "theory_status": theory_status,
            "predictions": len(predictions),
        }
        report_path = self._write_theory_demo(family, equations, consistency, predictions, validation, metrics)
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": domain},
            results={**metrics, "report_path": report_path},
            status=theory_status,
        )
        return {"metrics": metrics, "report_path": report_path}

    def _write_theory_demo(self, family, equations, consistency, predictions, validation, metrics) -> str:
        lines = [
            "# Theory Autowriter Demo",
            "",
            "## Lagrangian",
            "",
            f"`{sp.sstr(family['lagrangian'])}`",
            "",
            "## Equations Of Motion",
            "",
        ]
        for field, equation in equations.items():
            lines.append(f"- `{field}`: `{equation}`")
        lines.extend(["", "## Consistency", "", "```json", json.dumps(consistency, indent=2), "```", "", "## Predictions", ""])
        for prediction in predictions:
            lines.append(f"- {prediction['prediction']} Falsification: `{prediction['falsification_test']}`")
        lines.extend(
            [
                "",
                "## Validation",
                "",
                "```json",
                json.dumps(validation, indent=2, default=str),
                "```",
                "",
                "## Limitations",
                "",
                "- MVP only.",
                "- Solo campos escalares.",
                "- Sin cuantización.",
                "- Sin loops.",
                "- No claims beyond simulation-supported symbolic consistency.",
            ]
        )
        output = Path(__file__).resolve().parent / "artifacts" / "theory_demo.md"
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.report_manager.generate_phase_report("Theory Autowriter", metrics, "theory_autowriter_report.md")
        return str(output)


def _term_dimension(term) -> int:
    text = str(term)
    return max([int(power) for power in ["4", "3", "2"] if f"**{power}" in text] or [2])


if __name__ == "__main__":
    print(json.dumps(TheoryAutowriter().run(), indent=2, default=str))
