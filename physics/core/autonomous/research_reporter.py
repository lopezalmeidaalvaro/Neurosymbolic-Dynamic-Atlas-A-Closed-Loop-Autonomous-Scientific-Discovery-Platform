import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from pathlib import Path
from typing import Dict, Any, List
from core.io import ARTIFACTS_DIR


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _history_filename(timestamp: str) -> str:
    safe_timestamp = timestamp.replace(":", "-")
    return f"massive_sweep_{safe_timestamp}.json"


def _build_history_index(history_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    reports: List[Dict[str, Any]] = []

    for report_path in sorted(history_dir.glob("massive_sweep_*.json")):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        metadata = report.get("metadata", {})
        reports.append(
            {
                "timestamp": metadata.get("timestamp", ""),
                "file": report_path.name,
                "systems": metadata.get("systems", []),
                "seeds": metadata.get("seeds", []),
                "noise_levels": metadata.get("noise_levels", []),
                "certification_schema_version": metadata.get(
                    "certification_schema_version", ""
                ),
                "confidence_method": metadata.get("confidence_method", ""),
            }
        )

    reports.sort(key=lambda item: item.get("timestamp", ""))
    return {"reports": reports}


def save_research_report(
    analysis_results: Dict[str, Any], hypotheses_results: Dict[str, Any]
) -> Path:
    """
    Aggregates findings and exports them to discoveries/noise_robustness_report.json
    """
    discoveries_dir = ARTIFACTS_DIR / "discoveries"
    discoveries_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "metadata": {
            "title": "Autonomous Noise Robustness & Topological Collapse Report",
            "timestamp": None,
            "pipeline_model": "Gemini 3.5 Flash",
        },
        "analysis_results": analysis_results,
        "hypotheses_evaluation": hypotheses_results,
    }

    # Populate timestamp
    from datetime import datetime, timezone

    report["metadata"]["timestamp"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    output_path = discoveries_dir / "noise_robustness_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[REPORTER] Research report successfully saved to {output_path}")
    return output_path


def save_massive_sweep_report(analysis_results: Dict[str, Any]) -> Path:
    """
    Aggregates findings and exports them to discoveries/massive_sweep_report.json.

    Phase 3.3A: Single source of truth — only ``"certified_results"`` (list)
    is exported.  Each element contains the per-system math vectors PLUS an
    inline ``"certification"`` block.  There is no separate top-level
    ``"certification"`` dict.
    """
    discoveries_dir = ARTIFACTS_DIR / "discoveries"
    discoveries_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime, timezone

    report = {
        "metadata": {
            "title": "Massive Topological Sweep & Attractor Stability Report",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pipeline_model": "Gemini 3.5 Flash",
            "certification_schema_version": "1.2.0",
            "confidence_method": "confidence_v2",
            "systems": analysis_results.get("metadata", {}).get("systems", []),
            "seeds": analysis_results.get("metadata", {}).get("seeds", []),
            "noise_levels": analysis_results.get("metadata", {}).get(
                "noise_levels", []
            ),
        },
        # Raw mathematical results dict (unchanged vectors, for tooling that reads "results" key)
        "results": analysis_results.get("results", {}),
        # Phase 3.3A — Single source of truth for certified data
        "certified_results": analysis_results.get("certified_results", []),
    }

    output_path = discoveries_dir / "massive_sweep_report.json"
    _write_json(output_path, report)

    history_dir = ARTIFACTS_DIR / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = history_dir / _history_filename(report["metadata"]["timestamp"])
    if snapshot_path.exists():
        snapshot_path = (
            history_dir / f"{snapshot_path.stem}_duplicate{snapshot_path.suffix}"
        )

    _write_json(snapshot_path, report)
    _write_json(history_dir / "history_index.json", _build_history_index(history_dir))

    print(f"[REPORTER] Massive sweep report successfully saved to {output_path}")
    print(f"[REPORTER] Historical massive sweep snapshot saved to {snapshot_path}")
    return output_path
