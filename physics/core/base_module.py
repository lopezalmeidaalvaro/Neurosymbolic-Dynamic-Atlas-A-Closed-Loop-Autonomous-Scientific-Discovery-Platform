from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

try:
    from physics.core.artifact_manager import ArtifactManager
    from physics.core.config_manager import ConfigManager
    from physics.core.experiment_registry import ExperimentRegistry
    from physics.core.report_manager import ReportManager
except ModuleNotFoundError:
    from core.artifact_manager import ArtifactManager
    from core.config_manager import ConfigManager
    from core.experiment_registry import ExperimentRegistry
    from core.report_manager import ReportManager


class ScientificModule(ABC):
    """Common contract for phase modules."""

    def __init__(
        self,
        config_manager: ConfigManager | None = None,
        artifact_manager: ArtifactManager | None = None,
        experiment_registry: ExperimentRegistry | None = None,
    ):
        self.config_manager = config_manager or ConfigManager()
        self.artifact_manager = artifact_manager or ArtifactManager()
        self.experiment_registry = experiment_registry or ExperimentRegistry()
        self.report_manager = ReportManager()
        self.module_name = self.__class__.__name__
        self.experiment_id: str | None = None
        self.status = "initialized"

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Execute the module workflow."""

    def log_result(self, metrics_dict: dict[str, Any], output_name: str | None = None) -> str:
        output_name = output_name or f"{self.module_name.lower()}_report.md"
        report_path = self.report_manager.generate_phase_report(self.module_name, metrics_dict, output_name)
        self.experiment_id = self.experiment_registry.register(
            module=self.module_name,
            params={"system": "physics", "seed": self.config_manager.get("physics.random_seed", 42)},
            results={**metrics_dict, "report_path": str(report_path)},
            status="completed",
        )
        self.status = "completed"
        return str(report_path)

    def get_status(self) -> dict[str, Any]:
        return {
            "module": self.module_name,
            "status": self.status,
            "experiment_id": self.experiment_id,
            "registry": self.experiment_registry.get_statistics(),
        }
