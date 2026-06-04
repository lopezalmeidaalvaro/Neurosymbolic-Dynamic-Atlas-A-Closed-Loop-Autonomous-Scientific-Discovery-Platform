import os
import pytest
from quantum.reality_native.theory_reconstruction import TheoryReconstructor

@pytest.fixture
def temp_export_file(tmp_path):
    export_file = tmp_path / "RTHEORY_001_EXPORT.md"
    content = """
# Independent Theory Specification — RTHEORY_001

## 4. Parameter Specification
- **a (Gate Error Coefficient)**: `-1.2345`
- **b (Readout Error Coefficient)**: `-2.3456`
- **c (Intrinsic Calibration Offset)**: `-0.0123`
"""
    export_file.write_text(content, encoding="utf-8")
    return str(export_file)

def test_theory_reconstruction_parsing(temp_export_file):
    reconstructor = TheoryReconstructor(export_path=temp_export_file)
    assert abs(reconstructor.a - (-1.2345)) < 1e-6
    assert abs(reconstructor.b - (-2.3456)) < 1e-6
    assert abs(reconstructor.c - (-0.0123)) < 1e-6

def test_theory_reconstruction_predict(temp_export_file):
    reconstructor = TheoryReconstructor(export_path=temp_export_file)
    # Gap = -1.2345 * 0.01 + -2.3456 * 0.02 + -0.0123 = -0.012345 - 0.046912 - 0.0123 = -0.071557
    # predicted_corrected = 0.50 + gap = 0.428443
    pred = reconstructor.predict(0.50, 0.01, 0.02)
    assert abs(pred - 0.428443) < 1e-5
