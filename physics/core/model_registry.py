from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PHYSICS_ROOT = Path(__file__).resolve().parents[1]


class ModelRegistry:
    """Indexes existing checkpoints without moving or copying them."""

    DEFAULT_PATTERNS = [
        "models/*.pth",
        "models/ptbxl/*.pth",
        "artifacts/*.pth",
        "checkpoints/*.pth",
        "checkpoints/**/*.pth",
    ]

    def __init__(self, registry_path: str | Path | None = None):
        self.registry_path = Path(registry_path) if registry_path else PHYSICS_ROOT / "models" / "model_registry.json"
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry: dict[str, dict[str, Any]] = self._load()

    def scan_existing(self) -> dict[str, dict[str, Any]]:
        for pattern in self.DEFAULT_PATTERNS:
            for path in PHYSICS_ROOT.glob(pattern):
                if path.is_file():
                    self.register(path.stem, path, metadata={"source": "scan"}, persist=False)
        self._persist()
        return self.registry

    def register(
        self,
        name: str,
        path: str | Path,
        metadata: dict[str, Any] | None = None,
        persist: bool = True,
    ) -> str:
        model_path = Path(path)
        if not model_path.is_absolute():
            model_path = (PHYSICS_ROOT / model_path).resolve()
        key = self._unique_key(name, model_path)
        self.registry[key] = {
            "name": name,
            "path": str(model_path),
            "exists": model_path.exists(),
            "size_bytes": model_path.stat().st_size if model_path.exists() else None,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "metadata": metadata or {},
        }
        if persist:
            self._persist()
        return key

    def get_model_path(self, name: str) -> str | None:
        record = self.registry.get(name)
        if record is None:
            matches = [item for item in self.registry.values() if item.get("name") == name]
            record = matches[0] if matches else None
        return None if record is None else record.get("path")

    def list_models(self) -> list[dict[str, Any]]:
        return [dict(key=key, **value) for key, value in sorted(self.registry.items())]

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.registry_path.exists():
            return {}
        try:
            return json.loads(self.registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _persist(self) -> None:
        self.registry_path.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

    def _unique_key(self, name: str, path: Path) -> str:
        if name not in self.registry or self.registry.get(name, {}).get("path") == str(path):
            return name
        try:
            rel = path.relative_to(PHYSICS_ROOT)
        except ValueError:
            rel = path
        return str(rel).replace("\\", "/").replace("/", "__")
