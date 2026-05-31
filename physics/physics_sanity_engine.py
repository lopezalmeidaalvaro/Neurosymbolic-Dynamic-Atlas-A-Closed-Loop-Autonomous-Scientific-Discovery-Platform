from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

try:
    from physics.core.base_module import ScientificModule
    from physics.scientific_guard import sanitize_hypothesis, validate_hypothesis_structure
    from physics.symbolic_discovery import safe_parse_sympy
    from physics.synthetic_systems import get_ground_truth_equations
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from scientific_guard import sanitize_hypothesis, validate_hypothesis_structure
    from symbolic_discovery import safe_parse_sympy
    from synthetic_systems import get_ground_truth_equations


ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


class PhysicsSanityEngine(ScientificModule):
    """Physics consistency checks for discovered equations and hypotheses."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_path = ARTIFACTS_DIR / "sanity_cache.json"
        self.cache = self._load_cache()

    def check_dimensional_consistency(self, equation_str: str, variable_units: dict[str, Any]) -> dict[str, Any]:
        lhs, rhs = _split_equation(equation_str)
        unit_map = {name: _parse_unit(unit) for name, unit in (variable_units or {}).items()}
        try:
            lhs_dim = _dimension_of(safe_parse_sympy(lhs, variables=list(unit_map)), unit_map)
            rhs_dim = _dimension_of(safe_parse_sympy(rhs, variables=list(unit_map)), unit_map)
            consistent = lhs_dim == rhs_dim
            return {"passed": consistent, "lhs_dimension": lhs_dim, "rhs_dimension": rhs_dim, "warnings": []}
        except Exception as exc:
            return {"passed": False, "lhs_dimension": {}, "rhs_dimension": {}, "warnings": [str(exc)]}

    def check_boundedness(
        self,
        equation_str: str,
        variable_ranges: dict[str, tuple[float, float]],
        n_samples: int = 100,
    ) -> dict[str, Any]:
        lhs, rhs = _split_equation(equation_str)
        variables = list(variable_ranges or {})
        expr = safe_parse_sympy(rhs if rhs else lhs, variables=variables)
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        values = []
        warnings = []
        for _ in range(max(1, n_samples)):
            sample = {sp.Symbol(name): rng.uniform(bounds[0], bounds[1]) for name, bounds in variable_ranges.items()}
            try:
                value = float(expr.evalf(subs=sample))
            except Exception as exc:
                warnings.append(f"evaluation_error: {exc}")
                continue
            values.append(value)
            if not np.isfinite(value):
                warnings.append("non_finite_value")
            if value < 0 or value > 1.0e6:
                warnings.append("temperature_or_state_out_of_safe_range")
        passed = bool(values) and not warnings
        return {
            "passed": passed,
            "min": float(np.min(values)) if values else None,
            "max": float(np.max(values)) if values else None,
            "warnings": sorted(set(warnings)),
        }

    def check_conservation_laws(self, equation_str: str, system_type: str) -> dict[str, Any]:
        try:
            ground_truth = get_ground_truth_equations(system_type)
        except Exception:
            return {"passed": True, "warnings": [f"unknown_system_type: {system_type}"], "overlap": None}
        _, rhs = _split_equation(equation_str)
        discovered = str(safe_parse_sympy(rhs or equation_str, variables=ground_truth.get("variables", [])))
        truth_exprs = [str(safe_parse_sympy(expr, variables=ground_truth.get("variables", []))) for expr in ground_truth["equations_sympy"].values()]
        discovered_symbols = {str(sym) for sym in safe_parse_sympy(discovered, variables=ground_truth.get("variables", [])).free_symbols}
        truth_symbols = set().union(*[{str(sym) for sym in safe_parse_sympy(expr, variables=ground_truth.get("variables", [])).free_symbols} for expr in truth_exprs])
        overlap = len(discovered_symbols & truth_symbols) / max(1, len(truth_symbols))
        warnings = [] if overlap > 0 else ["no_symbol_overlap_with_known_system"]
        return {"passed": overlap > 0, "warnings": warnings, "overlap": overlap}

    def check_mathematical_consistency(self, equation_str: str) -> dict[str, Any]:
        lhs, rhs = _split_equation(equation_str)
        warnings = []
        try:
            if rhs:
                lhs_expr = safe_parse_sympy(lhs)
                rhs_expr = safe_parse_sympy(rhs)
                residual = sp.simplify(lhs_expr - rhs_expr)
                expr = residual
            else:
                expr = safe_parse_sympy(lhs)
                residual = sp.simplify(expr)
            if residual == 0:
                warnings.append("trivial_identity")
            denom = sp.denom(expr)
            if denom != 1 and denom.free_symbols:
                warnings.append("possible_singularity")
            return {"passed": "trivial_identity" not in warnings, "simplified": str(residual), "warnings": warnings}
        except Exception as exc:
            return {"passed": False, "simplified": None, "warnings": [str(exc)]}

    def validate_hypothesis(self, hypothesis_dict: dict[str, Any]) -> dict[str, Any]:
        cache_key = _hash_payload(hypothesis_dict)
        if cache_key in self.cache:
            return self.cache[cache_key]

        structure_ok, structure_errors = validate_hypothesis_structure(hypothesis_dict)
        equation = hypothesis_dict.get("equation") or hypothesis_dict.get("prediction") or "0"
        system_type = hypothesis_dict.get("system_type") or hypothesis_dict.get("system") or "unknown"
        variable_units = hypothesis_dict.get("variable_units", {})
        variable_ranges = hypothesis_dict.get("variable_ranges", {name: (-1.0, 1.0) for name in hypothesis_dict.get("variables", [])})
        checks = {
            "structure": {"passed": structure_ok, "warnings": structure_errors},
            "math": self.check_mathematical_consistency(equation),
            "dimensions": self.check_dimensional_consistency(equation, variable_units) if variable_units else {"passed": True, "warnings": ["no_units_provided"]},
            "boundedness": self.check_boundedness(equation, variable_ranges) if variable_ranges else {"passed": True, "warnings": ["no_ranges_provided"]},
            "conservation": self.check_conservation_laws(equation, system_type),
        }
        passed_count = sum(1 for item in checks.values() if item.get("passed"))
        score = passed_count / len(checks)
        result = {
            "hypothesis": sanitize_hypothesis(hypothesis_dict.get("hypothesis") or hypothesis_dict.get("hypothesis_text") or ""),
            "score": score,
            "accepted": score >= 0.5,
            "checks": checks,
        }
        self.cache[cache_key] = result
        self._save_cache()
        return result

    def run(self, hypotheses: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        if hypotheses is None:
            hypotheses = [
                {
                    "hypothesis": "The harmonic oscillator derivative follows velocity.",
                    "equation": "dx = v",
                    "variables": ["x", "v"],
                    "variable_units": {"dx": "m/s", "v": "m/s"},
                    "variable_ranges": {"v": (-10.0, 10.0)},
                    "falsification_test": "MSE > 0.1",
                    "confidence_prior": 0.5,
                    "system_type": "duffing",
                }
            ]
        results = [self.validate_hypothesis(item) for item in hypotheses]
        accepted = sum(1 for item in results if item["accepted"])
        self.artifact_manager.save_json("sanity_log.json", results)
        metrics = {
            "hypotheses_checked": len(results),
            "accepted": accepted,
            "rejected": len(results) - accepted,
            "cache_entries": len(self.cache),
        }
        report_path = self.log_result(metrics, "sanity_report.md")
        return {"metrics": metrics, "report_path": report_path, "results": results}

    def _load_cache(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {}
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _save_cache(self) -> None:
        self.cache_path.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")


def _split_equation(equation_str: str) -> tuple[str, str]:
    text = str(equation_str).replace("$", "").strip()
    if "=" in text:
        lhs, rhs = text.split("=", 1)
        return lhs.strip(), rhs.strip()
    return text, ""


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_unit(unit: Any) -> dict[str, float]:
    if isinstance(unit, dict):
        return {str(key): float(value) for key, value in unit.items() if value}
    text = str(unit).strip()
    aliases = {"m": "length", "s": "time", "kg": "mass", "k": "temperature", "K": "temperature"}
    if not text or text == "1":
        return {}
    dims: dict[str, float] = {}
    numerator, *denominators = text.split("/")
    for token in numerator.split("*"):
        _add_unit_token(dims, token, 1.0, aliases)
    for denominator in denominators:
        for token in denominator.split("*"):
            _add_unit_token(dims, token, -1.0, aliases)
    return {key: value for key, value in dims.items() if abs(value) > 1e-12}


def _add_unit_token(dims: dict[str, float], token: str, sign: float, aliases: dict[str, str]) -> None:
    token = token.strip()
    if not token:
        return
    if "^" in token:
        name, power = token.split("^", 1)
        exponent = float(power)
    else:
        name, exponent = token, 1.0
    dims[aliases.get(name, name)] = dims.get(aliases.get(name, name), 0.0) + sign * exponent


def _dimension_of(expr, unit_map: dict[str, dict[str, float]]) -> dict[str, float]:
    if expr.is_Number:
        return {}
    if expr.is_Symbol:
        return dict(unit_map.get(str(expr), {}))
    if expr.is_Add:
        dims = [_dimension_of(arg, unit_map) for arg in expr.args]
        first = dims[0]
        if any(dim != first for dim in dims[1:]):
            raise ValueError(f"additive terms have incompatible dimensions: {dims}")
        return first
    if expr.is_Mul:
        result: dict[str, float] = {}
        for arg in expr.args:
            for key, value in _dimension_of(arg, unit_map).items():
                result[key] = result.get(key, 0.0) + value
        return {key: value for key, value in result.items() if abs(value) > 1e-12}
    if expr.is_Pow:
        base, exponent = expr.args
        if not exponent.is_number:
            raise ValueError("symbolic powers are not dimensionally supported")
        base_dims = _dimension_of(base, unit_map)
        return {key: value * float(exponent) for key, value in base_dims.items()}
    return {}


if __name__ == "__main__":
    print(json.dumps(PhysicsSanityEngine().run(), indent=2))
