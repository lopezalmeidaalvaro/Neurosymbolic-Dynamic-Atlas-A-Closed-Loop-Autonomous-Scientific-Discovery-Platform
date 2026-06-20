import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.knowledge_base.library_manager import FormalKnowledgeBase
from core.mlops.analytics.trajectory_analytics import TrajectoryAnalytics
from core.mlops.analytics.dataset_analytics import DatasetAnalytics
from core.mlops.analytics.report_generator import ReportGenerator


@pytest.fixture
def temp_kb():
    """Provides a temporary FormalKnowledgeBase database for testing analytics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_analytics_knowledge.db"
        kb = FormalKnowledgeBase(db_path=db_file)
        yield kb


def test_trajectory_analytics(temp_kb):
    """Verify that TrajectoryAnalytics extracts difficulty, family, and proof origin stats correctly."""
    kb = temp_kb

    # Log trajectories under various curriculum difficulties, families, and proof origins
    kb.log_trajectory(
        run_id="run_1",
        state_context="state_a",
        tactic_applied="exact H_squared",
        status="VERIFIED",
        reward=1.0,
        metadata={
            "difficulty": 1,
            "family": "pauli_involution",
            "proof_origin": "constructive",
        },
    )
    kb.log_trajectory(
        run_id="run_1",
        state_context="state_a",
        tactic_applied="sorry",
        status="TIMEOUT",
        reward=-1.0,
        metadata={
            "difficulty": 1,
            "family": "pauli_involution",
            "proof_origin": "constructive",
        },
    )
    kb.log_trajectory(
        run_id="run_2",
        state_context="state_b",
        tactic_applied="rfl",
        status="UNSOLVED_GOALS",
        reward=0.2,
        metadata={
            "difficulty": 2,
            "family": "hadamard_conjugation",
            "proof_origin": "axiomatic",
        },
    )
    kb.log_trajectory(
        run_id="run_2",
        state_context="state_b",
        tactic_applied="exact H_X_H_eq_Z",
        status="VERIFIED",
        reward=1.0,
        metadata={
            "difficulty": 2,
            "family": "hadamard_conjugation",
            "proof_origin": "axiomatic",
        },
    )

    analytics = TrajectoryAnalytics(kb)

    # 1. Test difficulty aggregation
    diff_metrics = analytics.get_success_rate_by_difficulty()
    assert len(diff_metrics) == 2
    assert diff_metrics[1]["total_attempts"] == 2
    assert diff_metrics[1]["success_rate"] == 0.5
    assert diff_metrics[2]["total_attempts"] == 2
    assert diff_metrics[2]["success_rate"] == 0.5

    # 2. Test family metrics
    fam_metrics = analytics.get_metrics_by_family()
    assert len(fam_metrics) == 2
    assert fam_metrics["pauli_involution"]["total_attempts"] == 2
    assert fam_metrics["pauli_involution"]["success_rate"] == 0.5
    assert fam_metrics["pauli_involution"]["avg_reward"] == 0.0  # (1.0 + -1.0)/2

    assert fam_metrics["hadamard_conjugation"]["total_attempts"] == 2
    assert fam_metrics["hadamard_conjugation"]["success_rate"] == 0.5
    assert fam_metrics["hadamard_conjugation"]["avg_reward"] == 0.6  # (0.2 + 1.0)/2

    # 3. Test proof origin metrics
    origin_metrics = analytics.get_metrics_by_proof_origin()
    assert len(origin_metrics) == 2
    assert origin_metrics["constructive"]["total_attempts"] == 2
    assert origin_metrics["constructive"]["success_rate"] == 0.5
    assert origin_metrics["constructive"]["avg_reward"] == 0.0

    assert origin_metrics["axiomatic"]["total_attempts"] == 2
    assert origin_metrics["axiomatic"]["success_rate"] == 0.5
    assert origin_metrics["axiomatic"]["avg_reward"] == 0.6


def test_dataset_analytics_valid():
    """Verify that DatasetAnalytics profiles a valid JSONL dataset correctly."""
    analytics = DatasetAnalytics()

    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl_file = Path(tmpdir) / "test_dataset.jsonl"
        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "prompt": "state_1",
                        "chosen": "exact H_squared",
                        "rejected": "sorry",
                    }
                )
                + "\n"
            )
            f.write(
                json.dumps({"prompt": "state_1", "chosen": "rfl", "rejected": "sorry"})
                + "\n"
            )
            f.write(
                json.dumps({"prompt": "state_2", "chosen": "rfl", "rejected": "sorry"})
                + "\n"
            )

        metrics = analytics.analyze_dpo_jsonl(str(jsonl_file))
        assert metrics["total_pairs"] == 3
        assert metrics["unique_prompts"] == 2
        assert metrics["avg_pairs_per_prompt"] == 1.5


def test_dataset_analytics_invalid_or_missing():
    """Verify that DatasetAnalytics returns zero counters for empty or missing files."""
    analytics = DatasetAnalytics()

    # Test non-existent file
    metrics = analytics.analyze_dpo_jsonl("non_existent_file.jsonl")
    assert metrics["total_pairs"] == 0
    assert metrics["unique_prompts"] == 0
    assert metrics["avg_pairs_per_prompt"] == 0.0

    # Test empty file
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_file = Path(tmpdir) / "empty.jsonl"
        empty_file.touch()

        metrics = analytics.analyze_dpo_jsonl(str(empty_file))
        assert metrics["total_pairs"] == 0
        assert metrics["unique_prompts"] == 0
        assert metrics["avg_pairs_per_prompt"] == 0.0


def test_report_generator(temp_kb):
    """Verify that ReportGenerator produces correct report structure and persists it."""
    kb = temp_kb

    # Log some dummy trajectories to KB
    kb.log_trajectory(
        run_id="run_test",
        state_context="state_a",
        tactic_applied="exact H_squared",
        status="VERIFIED",
        reward=1.0,
        metadata={
            "difficulty": 1,
            "family": "pauli_involution",
            "proof_origin": "constructive",
        },
    )

    traj_analytics = TrajectoryAnalytics(kb)
    dataset_analytics = DatasetAnalytics()

    # Mock dataset analytics
    dataset_analytics.analyze_dpo_jsonl = MagicMock(
        return_value={
            "total_pairs": 5,
            "unique_prompts": 2,
            "avg_pairs_per_prompt": 2.5,
        }
    )

    generator = ReportGenerator(traj_analytics, dataset_analytics)

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path_str = generator.generate_and_print_report(
            dataset_path="mock_dataset.jsonl", output_dir=tmpdir
        )
        report_path = Path(report_path_str)

        assert report_path.exists()
        assert report_path.name == "system_health_report.json"

        # Load and verify contents
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        assert "timestamp" in report_data
        assert "success_rate_by_difficulty" in report_data
        assert "metrics_by_family" in report_data
        assert "metrics_by_proof_origin" in report_data
        assert "dataset_metrics" in report_data

        assert report_data["dataset_metrics"]["total_pairs"] == 5
        # Cast key 1 back to int for assertions as JSON keys are always string
        assert report_data["success_rate_by_difficulty"]["1"]["total_attempts"] == 1
        assert report_data["success_rate_by_difficulty"]["1"]["success_rate"] == 1.0
        assert (
            report_data["metrics_by_proof_origin"]["constructive"]["total_attempts"]
            == 1
        )
        assert (
            report_data["metrics_by_proof_origin"]["constructive"]["success_rate"]
            == 1.0
        )
