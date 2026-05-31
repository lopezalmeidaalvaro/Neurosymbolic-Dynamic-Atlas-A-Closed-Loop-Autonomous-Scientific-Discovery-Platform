from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

try:
    import pandas as pd
except Exception:  # pragma: no cover - optional convenience dependency
    pd = None

try:
    from physics.core.io.artifact_manager import LEGACY_ARTIFACTS_DIR, resolve_path
except ModuleNotFoundError:
    from core.io.artifact_manager import LEGACY_ARTIFACTS_DIR, resolve_path


class ArtifactManager:
    """Small IO facade over the existing artifact path resolver."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir).resolve() if base_dir else LEGACY_ARTIFACTS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name_or_path: str | Path) -> Path:
        path = Path(name_or_path)
        if path.is_absolute():
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        if len(path.parts) > 1:
            candidate = self.base_dir / path
            candidate.parent.mkdir(parents=True, exist_ok=True)
            return candidate
        resolved = resolve_path(path)
        if resolved.exists():
            return resolved
        candidate = self.base_dir / path
        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    def save_json(self, name_or_path: str | Path, data: Any) -> Path:
        path = self._path(name_or_path)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, default=str)
        return path

    def load_json(self, name_or_path: str | Path) -> Any:
        with self._path(name_or_path).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_csv(self, name_or_path: str | Path, data: Any) -> Path:
        path = self._path(name_or_path)
        if pd is not None and hasattr(data, "to_csv"):
            data.to_csv(path, index=False)
            return path
        if pd is not None:
            pd.DataFrame(data).to_csv(path, index=False)
            return path
        rows = list(data if isinstance(data, Iterable) and not isinstance(data, (str, bytes, dict)) else [data])
        headers = sorted({key for row in rows if isinstance(row, dict) for key in row})
        with path.open("w", encoding="utf-8") as handle:
            if headers:
                handle.write(",".join(headers) + "\n")
                for row in rows:
                    handle.write(",".join(str(row.get(key, "")) for key in headers) + "\n")
            else:
                handle.write("\n".join(str(row) for row in rows))
        return path

    def load_csv(self, name_or_path: str | Path) -> Any:
        path = self._path(name_or_path)
        if pd is None:
            return path.read_text(encoding="utf-8")
        return pd.read_csv(path)

    def save_markdown(self, name_or_path: str | Path, content: str) -> Path:
        path = self._path(name_or_path)
        path.write_text(content, encoding="utf-8")
        return path

    def list_artifacts(self, pattern: str = "*") -> list[Path]:
        if not self.base_dir.exists():
            return []
        return sorted(path for path in self.base_dir.rglob(pattern) if path.is_file())

    def get_experiment_dir(self, experiment_name: str) -> Path:
        safe_name = str(experiment_name).replace("/", "_").replace("\\", "_")
        path = self.base_dir / "experiments" / safe_name
        path.mkdir(parents=True, exist_ok=True)
        return path
