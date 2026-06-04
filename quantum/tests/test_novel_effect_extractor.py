import os
import pytest
from quantum.novel_physics.novel_effect_extractor import NovelEffectExtractor

def test_novel_effect_extraction():
    extractor = NovelEffectExtractor()
    residuals = [
        {"id": "RUN_QUAN_TRAI_001", "device": "ibm_brisbane", "vendor": "IBM", "paradigm": "SC",
         "gate_error": 0.01, "readout_error": 0.02, "observed_gap": -0.04, "standard_prediction": 0.0, "residual_gap": -0.04},
        {"id": "RUN_QUAN_TRAI_002", "device": "ionq_aria", "vendor": "IonQ", "paradigm": "IT",
         "gate_error": 0.005, "readout_error": 0.01, "observed_gap": -0.02, "standard_prediction": 0.0, "residual_gap": -0.02},
    ]
    theories = [
        {"theory_id": "RTHEORY_001", "domain": "quantum_hardware_noise",
         "equation": "Gap = -1.49 * E_gate + -1.50 * E_readout + -0.002"}
    ]
    effects = extractor.extract_novel_effects(residuals, theories)
    assert len(effects) >= 1
    assert effects[0]["vendors_count"] >= 2
    assert os.path.exists("docs/NOVEL_EFFECT_REPORT.md")
