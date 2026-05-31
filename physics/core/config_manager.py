from __future__ import annotations

from pathlib import Path
from typing import Any

import importlib.util
import yaml


PHYSICS_ROOT = Path(__file__).resolve().parents[1]
_CONFIG_MODULE_PATH = PHYSICS_ROOT / "neurosymbolic" / "config.py"
_SPEC = importlib.util.spec_from_file_location("_physics_neurosymbolic_config", _CONFIG_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Could not load config module from {_CONFIG_MODULE_PATH}")
_CONFIG_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CONFIG_MODULE)
load_config = _CONFIG_MODULE.load_config


class ConfigManager:
    """Mutable facade over the existing YAML loader."""

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path) if config_path else PHYSICS_ROOT / "config.yaml"
        self.config = load_config(self.config_path)

    def get(self, key: str, default: Any = None) -> Any:
        cursor: Any = self.config
        for part in key.split("."):
            if not isinstance(cursor, dict) or part not in cursor:
                return default
            cursor = cursor[part]
        return cursor

    def set(self, key: str, value: Any) -> None:
        cursor = self.config
        parts = key.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = value
        self._persist()

    def get_all(self) -> dict[str, Any]:
        return dict(self.config)

    def _persist(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.config, handle, sort_keys=False)
