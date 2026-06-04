import os
import json
import pytest
from quantum.audits.label_shuffle_audit import run_label_shuffle_audit
from quantum.audits.domain_holdout_audit import run_domain_holdout_audit
from quantum.audits.adversarial_feature_audit import run_adversarial_feature_audit
from quantum.audits.counterfactual_scaffold_audit import run_counterfactual_scaffold_audit
from quantum.audits.leakage_forensics import run_leakage_forensics
from quantum.audits.realism_audit import run_realism_audit
from quantum.audits.scientific_verdict import run_scientific_verdict_aggregator

def test_label_shuffle_audit():
    # Run with small seed count for speed
    report = run_label_shuffle_audit(num_seeds=2, output_path="test_label_shuffle_report.json")
    assert report["num_seeds"] == 2
    assert "results" in report
    assert "verdict" in report
    assert os.path.exists("test_label_shuffle_report.json")
    # Clean up test output
    if os.path.exists("test_label_shuffle_report.json"):
        os.remove("test_label_shuffle_report.json")

def test_domain_holdout_audit():
    report = run_domain_holdout_audit(num_seeds=2, output_path="test_domain_holdout_report.json")
    assert report["num_seeds"] == 2
    assert "metrics" in report
    assert "verdict" in report
    assert os.path.exists("test_domain_holdout_report.json")
    if os.path.exists("test_domain_holdout_report.json"):
        os.remove("test_domain_holdout_report.json")

def test_adversarial_feature_audit():
    report = run_adversarial_feature_audit(num_seeds=2, output_path="test_adversarial_feature_report.json")
    assert report["num_seeds"] == 2
    assert "predictor_robustness" in report
    assert "rule_robustness" in report
    assert os.path.exists("test_adversarial_feature_report.json")
    if os.path.exists("test_adversarial_feature_report.json"):
        os.remove("test_adversarial_feature_report.json")

def test_counterfactual_scaffold_audit():
    report = run_counterfactual_scaffold_audit(num_seeds=2, output_path="test_counterfactual_scaffold_report.json")
    assert report["num_seeds"] == 2
    assert "perturbation_impact" in report
    assert os.path.exists("test_counterfactual_scaffold_report.json")
    if os.path.exists("test_counterfactual_scaffold_report.json"):
        os.remove("test_counterfactual_scaffold_report.json")

def test_leakage_forensics():
    report = run_leakage_forensics(output_path="test_leakage_forensics_report.json")
    assert "dataset_statistics" in report
    assert "target_leakage" in report
    assert "correlation_matrix" in report
    assert "mutual_information" in report
    assert os.path.exists("test_leakage_forensics_report.json")
    if os.path.exists("test_leakage_forensics_report.json"):
        os.remove("test_leakage_forensics_report.json")

def test_realism_audit():
    # Make a dummy label shuffle and domain holdout test report for the realism audit to read
    run_label_shuffle_audit(num_seeds=2, output_path="test_label_shuffle_report.json")
    run_domain_holdout_audit(num_seeds=2, output_path="test_domain_holdout_report.json")
    
    report = run_realism_audit(
        output_path="test_realism_audit_report.json",
        label_shuffle_path="test_label_shuffle_report.json",
        domain_holdout_path="test_domain_holdout_report.json"
    )
    assert "scaling_audit" in report
    assert "metrics_audit" in report
    assert "fidelity_realism" in report
    assert os.path.exists("test_realism_audit_report.json")
    
    # Cleanup
    for f in ["test_label_shuffle_report.json", "test_domain_holdout_report.json", "test_realism_audit_report.json"]:
        if os.path.exists(f):
            os.remove(f)

def test_scientific_verdict_aggregator():
    # Generate test-specific input reports
    run_label_shuffle_audit(num_seeds=2, output_path="test_label_shuffle_report.json")
    run_domain_holdout_audit(num_seeds=2, output_path="test_domain_holdout_report.json")
    run_adversarial_feature_audit(num_seeds=2, output_path="test_adversarial_feature_report.json")
    run_counterfactual_scaffold_audit(num_seeds=2, output_path="test_counterfactual_scaffold_report.json")
    run_leakage_forensics(output_path="test_leakage_forensics_report.json")
    run_realism_audit(
        output_path="test_realism_audit_report.json",
        label_shuffle_path="test_label_shuffle_report.json",
        domain_holdout_path="test_domain_holdout_report.json"
    )
    
    test_files = {
        "label_shuffle": "test_label_shuffle_report.json",
        "domain_holdout": "test_domain_holdout_report.json",
        "adversarial_feature": "test_adversarial_feature_report.json",
        "counterfactual_scaffold": "test_counterfactual_scaffold_report.json",
        "leakage_forensics": "test_leakage_forensics_report.json",
        "realism_audit": "test_realism_audit_report.json"
    }
    
    report = run_scientific_verdict_aggregator(
        report_files=test_files,
        output_report_path="test_SCIENTIFIC_VALIDATION_REPORT.md"
    )
    assert "verdict" in report
    assert "feature_significance" in report
    assert "cohen_effects" in report
    assert os.path.exists("test_SCIENTIFIC_VALIDATION_REPORT.md")
    
    # Cleanup all test files
    for f in list(test_files.values()) + ["test_SCIENTIFIC_VALIDATION_REPORT.md"]:
        if os.path.exists(f):
            os.remove(f)
