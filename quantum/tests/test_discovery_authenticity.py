import os
import json
import pytest
from quantum.audits.novel_structure_audit import run_novel_structure_audit
from quantum.audits.optimization_removal_audit import run_optimization_removal_audit
from quantum.audits.random_evolution_control import run_random_evolution_control
from quantum.audits.cross_domain_discovery_audit import run_cross_domain_discovery_audit
from quantum.audits.discovery_compression_audit import run_discovery_compression_audit
from quantum.audits.lineage_reconstruction import run_lineage_reconstruction
from quantum.audits.discovery_authenticity_verdict import run_authenticity_aggregator

def test_novel_structure_audit():
    report = run_novel_structure_audit(output_path="test_novel_structure_report.json")
    assert "novelty_score" in report
    assert "classification" in report
    assert os.path.exists("test_novel_structure_report.json")
    os.remove("test_novel_structure_report.json")

def test_optimization_removal_audit():
    report = run_optimization_removal_audit(output_path="test_optimization_removal_report.json")
    assert "deltas" in report
    assert "verdict" in report
    assert os.path.exists("test_optimization_removal_report.json")
    os.remove("test_optimization_removal_report.json")

def test_random_evolution_control():
    report = run_random_evolution_control(num_seeds=2, output_path="test_random_evolution_report.json")
    assert report["num_seeds"] == 2
    assert "statistics" in report
    assert os.path.exists("test_random_evolution_report.json")
    os.remove("test_random_evolution_report.json")

def test_cross_domain_discovery_audit():
    report = run_cross_domain_discovery_audit(output_path="test_cross_domain_discovery_report.json")
    assert "results" in report
    assert os.path.exists("test_cross_domain_discovery_report.json")
    os.remove("test_cross_domain_discovery_report.json")

def test_discovery_compression_audit():
    report = run_discovery_compression_audit(output_path="test_discovery_compression_report.json")
    assert "cases" in report
    assert "classification" in report
    assert os.path.exists("test_discovery_compression_report.json")
    os.remove("test_discovery_compression_report.json")

def test_lineage_reconstruction():
    report = run_lineage_reconstruction(output_path="test_lineage_report.json")
    assert "metrics" in report
    assert "graph" in report
    assert os.path.exists("test_lineage_report.json")
    os.remove("test_lineage_report.json")

def test_authenticity_aggregator():
    # Write test reports first
    run_novel_structure_audit(output_path="test_novel_structure_report.json")
    run_optimization_removal_audit(output_path="test_optimization_removal_report.json")
    run_random_evolution_control(num_seeds=2, output_path="test_random_evolution_report.json")
    run_cross_domain_discovery_audit(output_path="test_cross_domain_discovery_report.json")
    run_discovery_compression_audit(output_path="test_discovery_compression_report.json")
    run_lineage_reconstruction(output_path="test_lineage_report.json")
    
    test_files = {
        "novel_structure": "test_novel_structure_report.json",
        "optimization_removal": "test_optimization_removal_report.json",
        "random_evolution": "test_random_evolution_report.json",
        "cross_domain": "test_cross_domain_discovery_report.json",
        "discovery_compression": "test_discovery_compression_report.json",
        "lineage": "test_lineage_report.json"
    }
    
    report = run_authenticity_aggregator(
        input_files=test_files,
        output_report_path="test_DISCOVERY_AUTHENTICITY_REPORT.md"
    )
    assert "verdict" in report
    assert "novelty_score" in report
    assert os.path.exists("test_DISCOVERY_AUTHENTICITY_REPORT.md")
    
    # Cleanup
    for f in list(test_files.values()) + ["test_DISCOVERY_AUTHENTICITY_REPORT.md"]:
        if os.path.exists(f):
            os.remove(f)
