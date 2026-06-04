import os
import pytest
from quantum.novel_physics.physics_impact_assessor import PhysicsImpactAssessor

def test_physics_impact_strong_candidate():
    assessor = PhysicsImpactAssessor()
    classification = assessor.classify_impact(
        novel_effects_count=10,
        verification_rate=1.0,
        elimination_rate=1.0,
        replication_equivalence=1.0
    )
    assert classification == "STRONG_NEW_PHYSICS_CANDIDATE"
    assert os.path.exists("docs/NOVEL_PHYSICS_IMPACT.md")

def test_physics_impact_potential():
    assessor = PhysicsImpactAssessor()
    classification = assessor.classify_impact(
        novel_effects_count=5,
        verification_rate=0.80,
        elimination_rate=0.75,
        replication_equivalence=0.50  # below 0.90 threshold
    )
    assert classification == "POTENTIAL_NEW_PHYSICS"

def test_physics_impact_known():
    assessor = PhysicsImpactAssessor()
    classification = assessor.classify_impact(
        novel_effects_count=0,
        verification_rate=0.0,
        elimination_rate=0.0,
        replication_equivalence=0.0
    )
    assert classification == "KNOWN_PHYSICS"
