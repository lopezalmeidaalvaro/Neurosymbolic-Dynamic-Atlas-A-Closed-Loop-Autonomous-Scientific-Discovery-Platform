from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


PHYSICS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PHYSICS_ROOT.parent


class ReportManager:
    """Central Markdown report writer for phase-level modules."""

    def __init__(self, artifacts_dir: str | Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else PHYSICS_ROOT / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def generate_phase_report(
        self,
        phase_name: str,
        metrics_dict: dict[str, Any],
        output_name: str | Path,
        state: str | None = None,
    ) -> Path:
        output_path = Path(output_name)
        if not output_path.is_absolute():
            output_path = self.artifacts_dir / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        status = state or self._infer_state(metrics_dict)
        lines = [
            f"# {phase_name}",
            "",
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            "",
            f"Global state: **{status}**",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "|---|---|",
        ]
        for key, value in sorted(metrics_dict.items()):
            lines.append(f"| `{key}` | {self._format_value(value)} |")
        lines.extend(["", "## Artifact Links", ""])
        lines.append(f"- `{output_path.as_posix()}`")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return output_path

    def append_to_changelog(self, message: str, changelog_path: str | Path | None = None) -> Path:
        path = Path(changelog_path) if changelog_path else REPO_ROOT / "CHANGELOG.md"
        entry = f"\n- {datetime.now().date().isoformat()}: {message.strip()}\n"
        if path.exists():
            with path.open("a", encoding="utf-8") as handle:
                handle.write(entry)
        else:
            path.write_text("# Changelog\n" + entry, encoding="utf-8")
        return path

    @staticmethod
    def _infer_state(metrics: dict[str, Any]) -> str:
        joined = " ".join(str(value).lower() for value in metrics.values())
        if any(token in joined for token in ["fail", "failed", "error", "rejected"]):
            return "FAIL"
        if any(token in joined for token in ["warn", "warning", "missing", "partial"]):
            return "WARNING"
        return "PASS"

    @staticmethod
    def _format_value(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        if isinstance(value, (list, tuple, set)):
            return ", ".join(str(item) for item in value)
        if isinstance(value, dict):
            return "`" + str(value).replace("|", "\\|") + "`"
        return str(value).replace("|", "\\|")
