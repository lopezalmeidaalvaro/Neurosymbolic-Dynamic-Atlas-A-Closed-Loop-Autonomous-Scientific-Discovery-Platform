import json
from pathlib import Path
from typing import Dict, Any
from core.io import ARTIFACTS_DIR

def save_research_report(analysis_results: Dict[str, Any], hypotheses_results: Dict[str, Any]) -> Path:
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
        "hypotheses_evaluation": hypotheses_results
    }
    
    # Populate timestamp
    from datetime import datetime, timezone
    report["metadata"]["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
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
            "noise_levels": analysis_results.get("metadata", {}).get("noise_levels", [])
        },
        # Raw mathematical results dict (unchanged vectors, for tooling that reads "results" key)
        "results": analysis_results.get("results", {}),
        # Phase 3.3A — Single source of truth for certified data
        "certified_results": analysis_results.get("certified_results", []),
    }

    output_path = discoveries_dir / "massive_sweep_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[REPORTER] Massive sweep report successfully saved to {output_path}")
    return output_path


