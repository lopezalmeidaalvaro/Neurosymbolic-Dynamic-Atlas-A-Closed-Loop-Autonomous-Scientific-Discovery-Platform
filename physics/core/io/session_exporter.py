from pathlib import Path
from typing import Union, Dict, Any
import json
from core.schemas import ExperimentSession
from core.io.artifact_manager import ARTIFACTS_DIR


def export_session(
    session_data: Union[Dict[str, Any], ExperimentSession], experiment_id: str
) -> Path:
    """
    Validate session data against ExperimentSession schema and export to JSON in ARTIFACTS_DIR/sessions/
    """
    if isinstance(session_data, dict):
        # Validate raw dictionary against ExperimentSession schema
        session = ExperimentSession.model_validate(session_data)
    elif isinstance(session_data, ExperimentSession):
        session = session_data
    else:
        raise TypeError("session_data must be a dict or an ExperimentSession instance")

    # Ensure sessions directory exists
    sessions_dir = ARTIFACTS_DIR / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Resolve output path: if experiment_id doesn't end with .json, append it
    output_filename = (
        experiment_id if experiment_id.endswith(".json") else f"{experiment_id}.json"
    )
    output_path = sessions_dir / output_filename

    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        # Use by_alias=True to serialize 'version' as 'versión'
        f.write(session.model_dump_json(by_alias=True, indent=2))

    print(f"Session successfully exported to {output_path}")
    return output_path
