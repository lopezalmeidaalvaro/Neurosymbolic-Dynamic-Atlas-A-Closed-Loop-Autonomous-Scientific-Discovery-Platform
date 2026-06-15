import json
from datetime import datetime, timezone
from pathlib import Path
from mlops.analytics.trajectory_analytics import TrajectoryAnalytics
from mlops.analytics.dataset_analytics import DatasetAnalytics


class ReportGenerator:
    """Combines metrics from trajectories and datasets to produce health and readiness reports."""

    def __init__(
        self,
        trajectory_analytics: TrajectoryAnalytics,
        dataset_analytics: DatasetAnalytics,
    ) -> None:
        self.trajectory_analytics = trajectory_analytics
        self.dataset_analytics = dataset_analytics

    def generate_and_print_report(
        self, dataset_path: str = None, output_dir: str = "mlops/artifacts/reports"
    ) -> str:
        """Collects metrics, saves them as a JSON health report, and prints a summary to stdout."""
        # 1. Extract Metrics
        difficulty_metrics = self.trajectory_analytics.get_success_rate_by_difficulty()
        family_metrics = self.trajectory_analytics.get_metrics_by_family()
        origin_metrics = self.trajectory_analytics.get_metrics_by_proof_origin()
        dataset_metrics = self.dataset_analytics.analyze_dpo_jsonl(dataset_path)

        # 2. Compile Unified Report
        system_health_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success_rate_by_difficulty": difficulty_metrics,
            "metrics_by_family": family_metrics,
            "metrics_by_proof_origin": origin_metrics,
            "dataset_metrics": dataset_metrics,
        }

        # 3. Persist JSON Report
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        report_file = out_path / "system_health_report.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(system_health_report, f, indent=2)

        # 4. Print Formatted Console Summary (stdout)
        print("\n" + "=" * 60)
        print("                 SYSTEM HEALTH & CURRICULUM REPORT")
        print("=" * 60)
        print(f"Timestamp: {system_health_report['timestamp']}")
        print("-" * 60)
        print("Success Rates by Difficulty Level:")
        if difficulty_metrics:
            for diff, data in sorted(difficulty_metrics.items()):
                print(
                    f"  Level {diff}: success_rate = {data['success_rate']:.2%}, total_attempts = {data['total_attempts']}"
                )
        else:
            print("  No metrics recorded.")

        print("-" * 60)
        print("Metrics by Motif Family:")
        if family_metrics:
            for family, data in sorted(family_metrics.items()):
                print(
                    f"  Family '{family}': success_rate = {data['success_rate']:.2%}, avg_reward = {data['avg_reward']:.4f}, total_attempts = {data['total_attempts']}"
                )
        else:
            print("  No metrics recorded.")

        print("-" * 60)
        print("Metrics by Proof Origin (Epistemological Purity):")
        if origin_metrics:
            for origin, data in sorted(origin_metrics.items()):
                print(
                    f"  Origin '{origin}': success_rate = {data['success_rate']:.2%}, avg_reward = {data['avg_reward']:.4f}, total_attempts = {data['total_attempts']}"
                )
        else:
            print("  No metrics recorded.")

        print("-" * 60)
        print("Dataset Telemetry:")
        print(f"  Target File: {dataset_path or 'N/A'}")
        print(f"  Total DPO Pairs: {dataset_metrics['total_pairs']}")
        print(f"  Unique Prompts (States): {dataset_metrics['unique_prompts']}")
        print(
            f"  Avg Pairs per Prompt Density: {dataset_metrics['avg_pairs_per_prompt']:.2f}"
        )
        print("=" * 60 + "\n")

        return str(report_file)
