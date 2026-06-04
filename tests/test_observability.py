import os
import shutil
import tempfile
import pytest
from core.observability.capability_registry import CapabilityRegistry
from core.observability.documentation_manager import DocumentationManager
from core.observability.experiment_logger import ExperimentLogger
from core.observability.dashboard import KnowledgeDashboard
from core.observability.snapshot_generator import ArchitectureSnapshotGenerator

@pytest.fixture
def temp_docs_dir():
    # Setup a temporary docs directory to test documentation writing safely
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_capability_registry():
    registry = CapabilityRegistry()
    
    # Test register capability
    registry.register_capability(
        name="TEST_CAPABILITY",
        phase_introduced="Phase Test",
        description="A test capability description.",
        validation_evidence="Unit test run."
    )
    
    cap = registry.get_capability("TEST_CAPABILITY")
    assert cap is not None
    assert cap.name == "TEST_CAPABILITY"
    assert cap.phase_introduced == "Phase Test"
    
    # Export markdown verification
    md = registry.export_capabilities_markdown()
    assert "# Emergent System Capabilities" in md
    assert "TEST_CAPABILITY" in md
    assert "Phase Test" in md

def test_experiment_logger(temp_docs_dir):
    log_file = os.path.join(temp_docs_dir, "EXPERIMENT_LOG.md")
    
    # Log first experiment
    ExperimentLogger.log_benchmark_run(
        benchmark_name="Test Benchmark 1",
        seed_values=[42],
        convergence_metrics={"cold_avg_generations": 5.0, "warm_avg_generations": 3.0},
        transfer_learning_outcomes={"average_speedup": 1.6667, "average_utilization": 0.25},
        discovered_motifs=["H->CNOT"],
        output_path=log_file
    )
    
    assert os.path.exists(log_file)
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "# Scientific Experiment Log" in content
    assert "Test Benchmark 1" in content
    assert "1.6667x" in content
    assert "`H->CNOT`" in content
    
    # Log second experiment (append check)
    ExperimentLogger.log_benchmark_run(
        benchmark_name="Test Benchmark 2",
        seed_values=[100],
        convergence_metrics={"cold_avg_generations": 8.0, "warm_avg_generations": 4.0},
        transfer_learning_outcomes={"average_speedup": 2.0, "average_utilization": 0.5},
        discovered_motifs=["CNOT->X"],
        output_path=log_file
    )
    
    with open(log_file, "r", encoding="utf-8") as f:
        content_after = f.read()
        
    assert "Test Benchmark 1" in content_after
    assert "Test Benchmark 2" in content_after
    assert "2.0000x" in content_after
    assert "`CNOT->X`" in content_after

def test_documentation_manager(temp_docs_dir):
    roadmap_path = os.path.join(temp_docs_dir, "ROADMAP.md")
    status_path = os.path.join(temp_docs_dir, "PHASE_STATUS.md")
    caps_path = os.path.join(temp_docs_dir, "CAPABILITIES.md")
    arch_path = os.path.join(temp_docs_dir, "ARCHITECTURE.md")
    
    # Log Phase 1D completion
    DocumentationManager.record_phase_completion(
        phase_id="Phase Test Phase",
        capabilities_enabled=["SCIENTIFIC_OBSERVABILITY", "TEST_CAPABILITY"],
        validation_results={"status": "PASS", "test_runs": 10},
        benchmark_outcomes={"speedup": "1.5x"},
        test_counts=10,
        docs_dir=temp_docs_dir
    )
    
    # Verify file existences
    assert os.path.exists(roadmap_path)
    assert os.path.exists(status_path)
    assert os.path.exists(caps_path)
    assert os.path.exists(arch_path)
    
    # Verify content in Roadmap (table row append)
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap_content = f.read()
    assert "| Phase Test Phase | COMPLETED |" in roadmap_content
    
    # Verify content in Phase Status
    with open(status_path, "r", encoding="utf-8") as f:
        status_content = f.read()
    assert "## [Phase Test Phase]" in status_content
    assert '"status": "PASS"' in status_content
    assert '"test_runs": 10' in status_content
    
    # Record another phase to verify append-only chronological integrity (Roadmap and Status)
    DocumentationManager.record_phase_completion(
        phase_id="Phase Second Test Phase",
        capabilities_enabled=["MULTI_DOMAIN_RUNTIME"],
        validation_results="All green.",
        benchmark_outcomes="Finished.",
        test_counts=20,
        docs_dir=temp_docs_dir
    )
    
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap_after = f.read()
    assert "Phase Test Phase" in roadmap_after
    assert "Phase Second Test Phase" in roadmap_after
    
    with open(status_path, "r", encoding="utf-8") as f:
        status_after = f.read()
    assert "## [Phase Test Phase]" in status_after
    assert "## [Phase Second Test Phase]" in status_after

def test_knowledge_dashboard(temp_docs_dir):
    # Mock memory object
    class MockMemory:
        def __init__(self):
            self.store_dict = {
                "quantum:distillation:patterns": [
                    {"pattern_id": "pat_1", "sequence": ["H", "CNOT"], "frequency": 10, "avg_score": 0.95, "representation": "H->CNOT"},
                    {"pattern_id": "pat_2", "sequence": ["X", "H"], "frequency": 5, "avg_score": 0.80, "representation": "X->H"}
                ],
                "quantum:distillation:metrics_history": [
                    {"patterns_injected": 6, "successful_injections": 3}
                ],
                "quantum:evolution:history": [
                    {"best_score": 0.95, "average_population_score": 0.70, "diversity_metric": 0.30},
                    {"best_score": 0.98, "average_population_score": 0.75, "diversity_metric": 0.35}
                ]
            }
            
        def query_patterns(self):
            return self.store_dict["quantum:distillation:patterns"]
            
        def retrieve(self, key):
            return self.store_dict.get(key)
            
    memory = MockMemory()
    dashboard = KnowledgeDashboard(memory=memory)
    
    json_path = os.path.join(temp_docs_dir, "metrics.json")
    report_path = os.path.join(temp_docs_dir, "REPORT.md")
    
    metrics = dashboard.generate_report(
        transfer_metrics={"cold_convergence_generations": 12, "warm_convergence_generations": 6, "speedup": 2.0},
        json_output_path=json_path,
        report_output_path=report_path
    )
    
    assert os.path.exists(json_path)
    assert os.path.exists(report_path)
    
    # Verify metrics dictionary calculations
    assert metrics["pattern_growth"]["total_patterns"] == 15
    assert metrics["pattern_growth"]["unique_patterns"] == 2
    assert metrics["knowledge_reuse"]["injected_patterns"] == 6
    assert metrics["knowledge_reuse"]["successful_injections"] == 3
    assert metrics["knowledge_reuse"]["utilization_rate"] == 0.5
    assert metrics["evolution_metrics"]["best_score"] == 0.98
    assert metrics["evolution_metrics"]["average_score"] == 0.725
    assert metrics["evolution_metrics"]["diversity"] == 0.325
    
    # Verify generated report file
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()
    assert "# Scientific Knowledge Observability Report" in report_content
    assert "Total Discovered Motifs** | 15" in report_content
    assert "Survival Utilization Rate:** 50.0000%" in report_content
