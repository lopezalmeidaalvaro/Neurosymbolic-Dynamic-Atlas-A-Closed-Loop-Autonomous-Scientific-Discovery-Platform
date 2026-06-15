import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics import MathEngine, DPODatasetGenerator, QuantumEquivalenceIR
from mlops.self_play.generators import SyntheticQuantumMotifGenerator
from mlops.self_play.worker import SelfPlayWorker
from mlops.pipeline.dpo_orchestrator import DPOPipelineOrchestrator
from mlops.bootstrap import bootstrap_mlops, run_training_cycle


def test_synthetic_motif_generator():
    """Verify that SyntheticQuantumMotifGenerator creates the requested number of valid motifs."""
    generator = SyntheticQuantumMotifGenerator()
    count = 10
    motifs = generator.generate_seed_motifs(count)

    assert len(motifs) == count
    for motif in motifs:
        assert isinstance(motif, QuantumEquivalenceIR)
        assert motif.motif_id.startswith("synth_")
        assert motif.source_system == "synthetic_generator"
        assert len(motif.lhs) > 0
        assert len(motif.rhs) > 0


def test_self_play_worker():
    """Verify that SelfPlayWorker processes motifs and compiles correct session statistics."""
    mock_engine = MagicMock(spec=MathEngine)
    # Mock verify_discovery to alternate success and failure
    mock_engine.verify_discovery.side_effect = [
        {"success": True, "status": "VERIFIED"},
        {"success": False, "status": "UNVERIFIED"},
        {"success": True, "status": "VERIFIED"},
    ]

    generator = SyntheticQuantumMotifGenerator()
    motifs = generator.generate_seed_motifs(3)

    worker = SelfPlayWorker(mock_engine)
    stats = worker.run_self_play_session(motifs)

    assert stats["success_count"] == 2
    assert stats["failure_count"] == 1
    assert stats["total_processed"] == 3
    assert stats["total_time_seconds"] >= 0.0
    assert mock_engine.verify_discovery.call_count == 3


def test_dpo_pipeline_orchestrator():
    """Verify that DPOPipelineOrchestrator generates datasets and metadata correctly."""
    mock_gen = MagicMock(spec=DPODatasetGenerator)

    def mock_generate(path):
        Path(path).write_text("dummy")
        return 5

    mock_gen.generate_dpo_jsonl.side_effect = mock_generate

    orchestrator = DPOPipelineOrchestrator(mock_gen)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path_str = orchestrator.export_versioned_dataset(output_dir=tmpdir)
        output_path = Path(output_path_str)

        # Verify dataset path and existence of files
        assert output_path.exists()
        assert output_path.name.endswith(".jsonl")

        meta_path = output_path.with_suffix(".meta.json")
        assert meta_path.exists()

        # Check metadata content
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        assert metadata["dataset_file"] == output_path.name
        assert metadata["pair_count"] == 5
        assert "extracted_at" in metadata
        assert metadata["version"] == "1.0"

        # Verify mock generator was called with correct path
        mock_gen.generate_dpo_jsonl.assert_called_once_with(output_path)


def test_bootstrap_mlops():
    """Verify that bootstrap_mlops correctly wires all pipeline components."""
    mock_engine = MagicMock(spec=MathEngine)
    mock_kb = MagicMock()
    mock_engine.get_rlcf_interface.return_value = mock_kb
    mock_engine._kb = mock_kb  # Simulate private attribute containing KB

    components = bootstrap_mlops(mock_engine)

    assert isinstance(components["generator"], SyntheticQuantumMotifGenerator)
    assert isinstance(components["worker"], SelfPlayWorker)
    assert isinstance(components["orchestrator"], DPOPipelineOrchestrator)
    assert components["worker"].math_engine == mock_engine
    assert components["orchestrator"].dataset_generator.kb == mock_kb


def test_run_training_cycle_integration():
    """Verify end-to-end integration of the training cycle function."""
    mock_engine = MagicMock(spec=MathEngine)
    mock_kb = MagicMock()
    mock_engine._kb = mock_kb

    # Mock the return values for self-play
    mock_engine.verify_discovery.return_value = {"success": True, "status": "VERIFIED"}

    # Mock the DPO dataset generator to return 10 pairs
    # Since we can't easily mock DPODatasetGenerator inside bootstrap_mlops (which instantiates it),
    # we can mock its generate_dpo_jsonl method using patch or mock the internal methods of KB if it runs.
    # Alternatively, let's use a real sqlite-based MathEngine bootstrapped in memory.
    from mathematics.knowledge_base.library_manager import FormalKnowledgeBase

    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        kb = FormalKnowledgeBase(db_path=db_file)
        mock_engine._kb = kb
        mock_engine.get_rlcf_interface.return_value = kb

        # Run training cycle
        # We will generate 4 motifs, and mock_engine returns success for all, which will log verification/trajectories
        # to the DB if we use a real orchestrator. Since mock_engine is a mock, its verify_discovery will be called.
        # But wait! DPODatasetGenerator reads from kb. If mock_engine doesn't actually log to kb,
        # kb will be empty and pair_count will be 0.
        # Let's populate the database manually or mock DPODatasetGenerator.generate_dpo_jsonl if we want to.
        # Let's write some trajectories to the database first so generate_dpo_jsonl produces pairs!
        kb.log_trajectory(
            run_id="run_1",
            state_context="Initial state",
            tactic_applied="exact H_squared",
            status="VERIFIED",
            reward=1.0,
        )
        kb.log_trajectory(
            run_id="run_1",
            state_context="Initial state",
            tactic_applied="sorry",
            status="TIMEOUT",
            reward=-1.0,
        )

        results = run_training_cycle(
            mock_engine, count=4, output_dir=Path(tmpdir) / "datasets"
        )

        assert "session_stats" in results
        assert "dataset_path" in results
        assert results["session_stats"]["total_processed"] == 4
        assert Path(results["dataset_path"]).exists()

        # Check metadata
        meta_path = Path(results["dataset_path"]).with_suffix(".meta.json")
        assert meta_path.exists()
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        # Because we added 2 trajectories for "Initial state" with different rewards (1.0 vs -1.0),
        # the generator will create 1 DPO pair.
        assert metadata["pair_count"] == 1
