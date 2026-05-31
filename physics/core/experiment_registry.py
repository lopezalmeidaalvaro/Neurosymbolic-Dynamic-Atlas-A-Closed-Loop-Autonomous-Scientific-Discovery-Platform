from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

try:
    from physics.experiment_versioning import ExperimentTracker
except ModuleNotFoundError:
    from experiment_versioning import ExperimentTracker


class ExperimentRegistry:
    """Adapter that preserves ExperimentTracker storage and adds phase APIs."""

    def __init__(self, storage_path: str | Path | None = None):
        self.tracker = ExperimentTracker(str(storage_path)) if storage_path else ExperimentTracker()
        self.storage_path = self.tracker.storage_path

    def register(
        self,
        module: str,
        params: dict[str, Any] | None = None,
        results: dict[str, Any] | None = None,
        status: str = "registered",
        experiment_id: str | None = None,
    ) -> str:
        params = dict(params or {})
        if experiment_id:
            params["requested_experiment_id"] = experiment_id
        system = str(params.pop("system", "physics"))
        seed = int(params.pop("seed", params.get("random_seed", 42)))
        return self.tracker.log_experiment(
            system=system,
            module=module,
            seed=seed,
            hyperparameters=params,
            results=results or {},
            status=status,
        )

    def update_status(
        self,
        experiment_id: str,
        status: str,
        results: dict[str, Any] | None = None,
    ) -> bool:
        row = self.get_experiment(experiment_id)
        if row is None:
            return False
        merged = json.loads(row.get("results_json") or "{}")
        if results:
            merged.update(results)
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE experiments SET status = ?, results_json = ? WHERE id = ?",
                (status, json.dumps(merged, indent=2, default=str), row["id"]),
            )
            conn.commit()
        return True

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        direct = self.tracker.get_experiment(experiment_id)
        if direct is not None:
            return direct
        with sqlite3.connect(self.storage_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments")
            for row in cursor.fetchall():
                data = dict(row)
                try:
                    params = json.loads(data.get("hyperparameters_json") or "{}")
                except json.JSONDecodeError:
                    params = {}
                if params.get("requested_experiment_id") == experiment_id:
                    return data
        return None

    def list_by_module(self, module: str, limit: int = 100) -> list[dict[str, Any]]:
        return self.tracker.query_experiments(module=module, limit=limit)

    def list_by_status(self, status: str, limit: int = 100) -> list[dict[str, Any]]:
        return self.tracker.query_experiments(status=status, limit=limit)

    def get_statistics(self) -> dict[str, Any]:
        with sqlite3.connect(self.storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM experiments")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT status, COUNT(*) FROM experiments GROUP BY status")
            by_status = dict(cursor.fetchall())
            cursor.execute("SELECT module, COUNT(*) FROM experiments GROUP BY module")
            by_module = dict(cursor.fetchall())
        return {"total": total, "by_status": by_status, "by_module": by_module}
