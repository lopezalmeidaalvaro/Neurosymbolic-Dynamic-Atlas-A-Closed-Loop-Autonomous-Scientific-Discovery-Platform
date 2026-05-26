"""
core/validation/reproducibility.py
Phase 3.3A — Certification Consistency & Pipeline Verification

Single-path reproducibility tier classifier.  There is exactly ONE logical
route per input value; no caller-side overrides are required or permitted.

Tiers
-----
seed_count < 3   →  "uncertain"    (insufficient for any statistical claim)
seed_count >= 10 →  "validated"    (robust multi-seed consensus)
seed_count >= 5  →  "replicated"   (sufficient cross-seed agreement)
seed_count >= 3  →  "preliminary"  (minimum viable multi-seed coverage)
"""

from __future__ import annotations


def get_reproducibility_status(seed_count: int) -> str:
    """
    Return the reproducibility tier for a given seed count.

    The guard seed_count < 3 → "uncertain" is the FIRST check, ensuring that
    low-coverage sweeps are never promoted to a higher tier by later conditions.

    Parameters
    ----------
    seed_count:
        Number of independent random seeds used in the experiment sweep.

    Returns
    -------
    str
        One of ``"validated"``, ``"replicated"``, ``"preliminary"``,
        or ``"uncertain"``.
    """
    if seed_count < 3:
        return "uncertain"

    if seed_count >= 10:
        return "validated"

    if seed_count >= 5:
        return "replicated"

    return "preliminary"
