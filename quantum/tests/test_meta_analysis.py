import os
import pytest
from quantum.scientific_reproduction.meta_analysis import MetaAnalysisEngine

def test_meta_analysis():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    engine = MetaAnalysisEngine(root)
    
    cumulative = {
        "discovery_correlation": 0.9992,
        "mass_reproduction_rate": 1.0,
        "max_prediction_divergence": 0.104946,
        "hardware_validation_rate": 1.0,
        "leakage_score": 0.0,
        "red_team_equivalence": 1.0,
        "consensus_score": 1.0,
        "quality_grade": "VERY_HIGH",
        "readiness_score": 1.0
    }
    res = engine.run_meta_analysis(cumulative)
    
    assert res["status"] == "PASSED"
    assert "aggregated_metrics" in res
    assert res["aggregated_metrics"]["phase_3b_discovery_correlation"] == 0.9992
    
    report_path = os.path.join(root, "docs", "META_ANALYSIS_REPORT.md")
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 0
