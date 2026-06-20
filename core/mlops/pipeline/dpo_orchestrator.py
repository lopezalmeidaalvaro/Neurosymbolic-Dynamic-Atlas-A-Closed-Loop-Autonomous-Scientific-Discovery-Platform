import json
from datetime import datetime, timezone
from pathlib import Path
from mathematics import DPODatasetGenerator


class DPOPipelineOrchestrator:
    """Orchestrates the export, versioning, and metadata profiling of generated DPO datasets."""

    def __init__(self, dataset_generator: DPODatasetGenerator) -> None:
        self.dataset_generator = dataset_generator

    def export_versioned_dataset(
        self, output_dir: str = "mlops/artifacts/datasets"
    ) -> str:
        """Generates a versioned JSONL dataset along with a metadata .meta.json file."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # Format output filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dataset_filename = f"dpo_dataset_v1_{timestamp}.jsonl"
        output_file = out_path / dataset_filename

        # Write dataset and obtain pair count
        pair_count = self.dataset_generator.generate_dpo_jsonl(output_file)

        # Write matching metadata file
        meta_file = output_file.with_suffix(".meta.json")
        metadata = {
            "dataset_file": dataset_filename,
            "pair_count": pair_count,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
        }

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return str(output_file)
