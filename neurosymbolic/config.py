"""Configuration loading helpers for reproducible experiments."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")


def _expand_env(value: Any) -> Any:
    """Expand shell-style environment placeholders inside YAML values.

    Args:
        value: Arbitrary parsed YAML value.

    Returns:
        Value with string placeholders expanded recursively.

    Raises:
        None.
    """
    if isinstance(value, str):
        return _ENV_PATTERN.sub(
            lambda match: os.environ.get(match.group(1), match.group(2) or ""),
            value,
        )
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    return value


def resolve_config_path(path: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the experiment configuration path.

    Args:
        path: Optional explicit configuration path. If omitted, the
            ``NEUROSYMBOLIC_CONFIG`` environment variable is checked before
            falling back to ``config.yaml`` in the current working directory.

    Returns:
        Absolute path to the configuration file.

    Raises:
        FileNotFoundError: If the resolved configuration path does not exist.
    """
    raw_path = path or os.environ.get("NEUROSYMBOLIC_CONFIG", "config.yaml")
    config_path = Path(raw_path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    return config_path


def load_config(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load a YAML configuration file.

    Args:
        path: Optional explicit configuration path.

    Returns:
        Parsed YAML configuration as a dictionary.

    Raises:
        FileNotFoundError: If the resolved configuration path does not exist.
        ValueError: If the YAML root is not a mapping.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    config_path = resolve_config_path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration root must be a mapping: {config_path}")
    return _expand_env(data)
