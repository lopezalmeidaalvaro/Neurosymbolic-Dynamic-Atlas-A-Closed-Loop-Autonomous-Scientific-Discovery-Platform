from pathlib import Path
from typing import Union

# Base directories relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PHYSICS_ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "dashboard" / "public" / "artifacts"
LEGACY_ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"


def resolve_path(filename_or_path: Union[str, Path]) -> Path:
    """
    Resolves a filename or subpath relative to ARTIFACTS_DIR.
    If the file does not exist in the new directory (ARTIFACTS_DIR),
    it falls back to checking the legacy directory (LEGACY_ARTIFACTS_DIR).
    """
    path_obj = Path(filename_or_path)

    # Try resolving in the new artifacts directory
    new_path = ARTIFACTS_DIR / path_obj
    if new_path.exists():
        return new_path

    # Check if the path exists in the legacy directory
    legacy_path = LEGACY_ARTIFACTS_DIR / path_obj
    if legacy_path.exists():
        return legacy_path

    # Return the path in the new directory as default (for writes or if missing in both)
    return new_path
