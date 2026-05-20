"""
core/validation/confidence_certifier.py
Phase 3.3B — Persistence & Scientific Consistency Audit

Certifies the statistical validity of a system-level analysis block
produced by analyze_massive_sweep().

Design contracts
----------------
* Backend is the SOLE authority for labelling scientific validity.
* Mathematical arrays (noise, mean_drift, velocity, acceleration) are
  NEVER modified — only read.
* get_reproducibility_status() is the single source of truth for tiers;
  no caller-side overrides exist here.
* Output structure: ONE certification block per system embedded directly
  inside the certified_results list — no duplicate top-level "certification" key.

confidence_score method: confidence_v2
--------------------------------------
Formula:
    seed_factor      = min(seed_count / 10.0, 1.0)
    stability_factor = 1.0 / (1.0 + acceleration_std)
    confidence_score = seed_factor * stability_factor

Rationale:
  * seed_factor captures reproducibility coverage: how many independent
    random initializations confirmed the result.  Saturates at 1.0 for
    seed_count >= 10 (the 'validated' tier threshold).
  * stability_factor captures geometric stability: how consistent the
    second derivative of drift is across noise levels.  A low std means
    the attractor collapses at a predictable, reproducible rate.
    The factor is bounded (0, 1] via the inverse formula.
  * The product is non-circular: it does NOT depend on critical_score,
    so it remains informative even when acceleration vectors are near zero
    (e.g., stable systems or sparse data).
  * Example values:
      seed=1,  acc_std=0.0  -> 0.1 * 1.0  = 0.1   (uncertain, trivially stable)
      seed=3,  acc_std=5.0  -> 0.3 * 0.17 = 0.051 (preliminary, high variance)
      seed=3,  acc_std=0.5  -> 0.3 * 0.67 = 0.2   (preliminary, moderate)
      seed=10, acc_std=0.1  -> 1.0 * 0.91 = 0.91  (validated, very stable)

Schema version: 1.2.0
"""

from __future__ import annotations

from typing import Any, Dict, List

from .reproducibility import get_reproducibility_status


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _safe_mean(values: List[float]) -> float:
    """Return the arithmetic mean, or 0.0 for empty lists."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _safe_std(values: List[float]) -> float:
    """
    Population standard deviation, or 0.0 for empty/singleton lists.
    Dependency-free — avoids importing numpy in this module.
    """
    n = len(values)
    if n < 2:
        return 0.0
    mean = _safe_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / n
    return variance ** 0.5


def _compute_critical_score(acceleration: List[float], acceleration_std: float) -> float:
    """
    critical_score = |mean(acceleration)| / max(acceleration_std, 1e-8)

    Measures the signal-to-noise ratio of the geometric collapse:
    - numerator  = mean absolute second derivative of drift over noise axis
    - denominator = spread of that derivative (floored to 1e-8 to avoid ÷0)

    Interpretation: > 3 → strong regime change; > 2 → moderate; else → none.
    """
    mean_acc = abs(_safe_mean(acceleration))
    denom = max(acceleration_std, 1e-8)
    return mean_acc / denom


def _assign_critical_level(score: float) -> str:
    if score > 3.0:
        return "strong"
    if score > 2.0:
        return "moderate"
    return "none"


def _compute_confidence_score(seed_count: int, acceleration_std: float) -> float:
    """
    confidence_score = seed_factor * stability_factor    [confidence_v2]

    seed_factor      = min(seed_count / 10.0, 1.0)
    stability_factor = 1.0 / (1.0 + acceleration_std)

    Both factors are bounded in (0, 1], so the product is in (0, 1].
    See module docstring for full mathematical justification and example values.
    """
    seed_factor: float = min(seed_count / 10.0, 1.0)
    stability_factor: float = 1.0 / (1.0 + acceleration_std)
    return round(seed_factor * stability_factor, 6)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def certify_session(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Certify the statistical quality of the analysis block returned by
    ``analyze_massive_sweep()``.

    Parameters
    ----------
    analysis_data:
        The full dict returned by ``analyze_massive_sweep()``.  Expected shape::

            {
              "metadata": {"systems": [...], "noise_levels": [...], "seeds": [...]},
              "results":  {<system_name>: {<per-system-vectors>}, ...}
            }

    Returns
    -------
    dict
        Preserves ``"metadata"`` and ``"results"`` unchanged.
        Adds ``"certified_results"`` — a list of objects, one per system,
        each containing the original result vectors PLUS an inline
        ``"certification"`` sub-dict.

        There is NO separate top-level ``"certification"`` key.
        ``"certified_results"`` is the SINGLE source of truth.

    Design contracts
    ----------------
    * Reproducibility tier comes exclusively from get_reproducibility_status();
      no override logic exists in this function.
    * confidence_method is stored in every certification block so JSON
      consumers can detect methodology changes across schema versions.
    """
    import copy

    certified = copy.deepcopy(analysis_data)

    meta = certified.get("metadata", {})
    seeds: List[int] = meta.get("seeds", [])
    seed_count: int = len(seeds)

    repro_status: str = get_reproducibility_status(seed_count)
    # confidence_score is computed per-system inside the loop (requires acceleration_std)

    results: Dict[str, Any] = certified.get("results", {})
    certified_results: List[Dict[str, Any]] = []

    for sys_name, sys_data in results.items():
        acceleration: List[float] = sys_data.get("acceleration", [])
        std_drift: List[float] = sys_data.get("std_drift", [])

        # acceleration_std: spread of the second-derivative vector.
        # When only 1 seed is available std_drift≡0; we fall back to
        # the std of the acceleration vector itself (also 0 in that case,
        # but consistent with the data available).
        acceleration_std: float = (
            _safe_std(acceleration) if len(acceleration) > 1
            else _safe_mean(std_drift)
        )

        mean_acceleration: float = _safe_mean(acceleration)
        critical_score: float = _compute_critical_score(acceleration, acceleration_std)
        critical_level: str = _assign_critical_level(critical_score)
        confidence_score: float = _compute_confidence_score(seed_count, acceleration_std)

        cert_block: Dict[str, Any] = {
            "version": "1.2.0",
            "critical_level": critical_level,
            "critical_score": round(critical_score, 8),
            "confidence_score": confidence_score,
            "confidence_method": "confidence_v2",
            "reproducibility_status": repro_status,
            "evidence": {
                "acceleration": round(mean_acceleration, 8),
                "acceleration_std": round(acceleration_std, 8),
                "seed_count": float(seed_count),
            },
        }

        # Single source of truth: certification lives inside certified_results
        certified_results.append({
            "system": sys_name,
            **sys_data,
            "certification": cert_block,
        })

    # Remove any legacy duplicate key if present from a prior run
    certified.pop("certification", None)

    certified["certified_results"] = certified_results

    return certified
