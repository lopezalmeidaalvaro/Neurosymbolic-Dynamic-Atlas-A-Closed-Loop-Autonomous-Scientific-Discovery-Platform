import argparse
import sys
from core.observability.documentation_manager import DocumentationManager
from core.observability.snapshot_generator import ArchitectureSnapshotGenerator

def main():
    parser = argparse.ArgumentParser(description="Discovery Platform Observability & DaC CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")
    
    # 1. record-phase
    record_parser = subparsers.add_parser("record-phase", help="Log the successful completion of a phase")
    record_parser.add_argument("--phase", required=True, help="Phase Identifier (e.g., 'Phase 1D')")
    record_parser.add_argument("--caps", required=True, help="Comma-separated list of enabled capabilities")
    record_parser.add_argument("--test-counts", type=int, default=0, help="Total number of passing tests")
    record_parser.add_argument("--val-results", default="All tests passed successfully.", help="Validation evidence snippet or summary")
    record_parser.add_argument("--bench-outcomes", default="Benchmark completed successfully.", help="Benchmark outcomes summary")
    
    # 2. snapshot
    snapshot_parser = subparsers.add_parser("snapshot", help="Generate the architecture snapshot docs/ARCHITECTURE.md")
    
    args = parser.parse_args()
    
    if args.command == "record-phase":
        capabilities = [c.strip() for c in args.caps.split(",") if c.strip()]
        DocumentationManager.record_phase_completion(
            phase_id=args.phase,
            capabilities_enabled=capabilities,
            validation_results=args.val_results,
            benchmark_outcomes=args.bench_outcomes,
            test_counts=args.test_counts
        )
        print(f"Phase {args.phase} logged successfully.")
    elif args.command == "snapshot":
        ArchitectureSnapshotGenerator.generate_snapshot()
        print("Architecture snapshot regenerated successfully.")

if __name__ == "__main__":
    main()
