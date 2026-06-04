import os
import pytest
from quantum.reality_native.false_discovery_control import FalseDiscoveryControl

def test_false_discovery_control():
    # Run FDR control
    fdr_control = FalseDiscoveryControl(n_control_domains=10, seed=99)
    results = fdr_control.run_fdr_control()

    # Assertions
    assert results["control_domains_tested"] == 10
    assert "false_discoveries_count" in results
    assert "false_discovery_rate" in results
    assert results["false_discovery_rate"] < 5.0, "False Discovery Rate must be < 5%"
    assert results["status"] == "PASSED"
    assert os.path.exists("docs/FALSE_DISCOVERY_REPORT.md"), "False discovery report should exist"
