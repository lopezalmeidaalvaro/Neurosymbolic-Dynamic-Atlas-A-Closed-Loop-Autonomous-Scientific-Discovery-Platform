import os
import json
import pytest
from quantum.law_validation.synthetic_world_generator import SyntheticWorldGenerator

def test_synthetic_worlds():
    report_path = "test_synth_world_report.json"
    generator = SyntheticWorldGenerator(output_path=report_path)
    report = generator.run_challenge()
    
    assert "recovery_f1" in report
    assert "worlds" in report
    assert "World_A" in report["worlds"]
    assert os.path.exists(report_path)
    os.remove(report_path)
