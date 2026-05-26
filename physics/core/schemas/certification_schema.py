"""
core/schemas/certification_schema.py
Phase 3.3 — Scientific Confidence & Validation Layer

Pydantic contract for the certification block attached to every
system's analysis results by ``core.validation.confidence_certifier``.
"""

from __future__ import annotations

from typing import Dict
from pydantic import BaseModel, Field


class CertificationEvidence(BaseModel):
    """
    Raw numerical evidence underpinning the certification verdict.
    All values are preserved at full floating-point precision.
    """

    acceleration: float = Field(
        ..., description="Mean of the d²Δ/dσ² (acceleration) vector across noise levels"
    )
    acceleration_std: float = Field(
        ...,
        description="Standard deviation of the acceleration vector; lower → steadier regime",
    )
    seed_count: float = Field(
        ..., description="Number of independent random seeds used in the sweep"
    )


class Certification(BaseModel):
    """
    Certification block produced by ``certify_session()`` for a single
    dynamical system within a massive-sweep analysis.

    Fields
    ------
    version:
        Schema version (semver).  Bump the minor/major when the contract
        changes in a breaking way so consumers can detect incompatibilities.
    critical_level:
        Qualitative verdict: ``"strong"`` (score > 3), ``"moderate"``
        (score > 2), or ``"none"``.
    critical_score:
        |mean(acceleration)| / max(acceleration_std, 1e-8).
        Measures signal-to-noise of the geometric collapse.
    confidence_score:
        Composite score ∈ [0, 1] combining critical_score and seed coverage.
    reproducibility_status:
        One of ``"validated"``, ``"replicated"``, ``"preliminary"``,
        ``"uncertain"``.  Forced to ``"uncertain"`` when seed_count < 3.
    evidence:
        Nested numerical provenance for full auditability.
    """

    version: str = Field(
        default="1.0.0", description="Certification schema version (semver)"
    )
    critical_level: str = Field(
        ..., description="Qualitative signal strength: 'strong', 'moderate', or 'none'"
    )
    critical_score: float = Field(
        ..., description="Signal-to-noise ratio of the acceleration vector"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Composite confidence score ∈ [0, 1]"
    )
    reproducibility_status: str = Field(
        ..., description="Reproducibility tier based on seed coverage"
    )
    evidence: CertificationEvidence = Field(
        ..., description="Raw numerical evidence supporting this certification verdict"
    )
