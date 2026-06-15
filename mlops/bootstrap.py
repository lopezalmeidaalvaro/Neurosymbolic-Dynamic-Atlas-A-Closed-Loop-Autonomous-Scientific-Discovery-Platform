from mathematics import MathEngine, DPODatasetGenerator
from mlops.self_play.generators import SyntheticQuantumMotifGenerator
from mlops.self_play.worker import SelfPlayWorker
from mlops.pipeline.dpo_orchestrator import DPOPipelineOrchestrator
from mlops.analytics.trajectory_analytics import TrajectoryAnalytics
from mlops.analytics.dataset_analytics import DatasetAnalytics
from mlops.analytics.report_generator import ReportGenerator


def bootstrap_mlops(math_engine: MathEngine) -> dict:
    """Wires and instantiates the MLOps self-play and dataset pipelines."""
    # 1. Synthetic motif generator
    generator = SyntheticQuantumMotifGenerator()

    # 2. Self Play Worker
    worker = SelfPlayWorker(math_engine)

    # 3. DPO Pipeline Orchestrator (extracts kb from MathEngine)
    kb = math_engine.get_rlcf_interface()
    dataset_generator = DPODatasetGenerator(kb)
    orchestrator = DPOPipelineOrchestrator(dataset_generator)

    # 4. Analytics & Report Generator
    trajectory_analytics = TrajectoryAnalytics(kb)
    dataset_analytics = DatasetAnalytics()
    report_generator = ReportGenerator(trajectory_analytics, dataset_analytics)

    return {
        "generator": generator,
        "worker": worker,
        "orchestrator": orchestrator,
        "report_generator": report_generator,
    }


def run_training_cycle(
    math_engine: MathEngine,
    count: int = 10,
    output_dir: str = "mlops/artifacts/datasets",
) -> dict:
    """Executes a full self-play training loop:

    1. Generate synthetic quantum motifs.
    2. Run verification self-play session against the engine (generating database logs).
    3. Package and export preference-aligned DPO dataset.
    4. Compile and log the health analytics report.
    """
    components = bootstrap_mlops(math_engine)

    # Generate synthetic motifs
    motifs = components["generator"].generate_seed_motifs(count)

    # Execute self-play against the formal verification engine
    session_stats = components["worker"].run_self_play_session(motifs)

    # Export versioned DPO preference dataset
    dataset_path = components["orchestrator"].export_versioned_dataset(output_dir)

    # Generate the curriculum observability metrics report
    report_path = components["report_generator"].generate_and_print_report(dataset_path)

    return {
        "session_stats": session_stats,
        "dataset_path": dataset_path,
        "report_path": report_path,
    }
