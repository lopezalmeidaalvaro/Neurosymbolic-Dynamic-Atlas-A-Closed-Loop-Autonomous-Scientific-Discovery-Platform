import os
import pytest
from quantum.external_audit.independent_physics_review import IndependentPhysicsReview

def test_independent_physics_review():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    review = IndependentPhysicsReview(root)
    res = review.run_review()
    
    assert res["status"] == "PASSED"
    assert res["survival_rate"] >= 0.80  # Must be > 80%
    
    report_path = os.path.join(root, "docs", "INDEPENDENT_PHYSICS_REVIEW.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
