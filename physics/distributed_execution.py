from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from physics.core.base_module import ScientificModule
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule


PHYSICS_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"


class ExperimentCache:
    """SQLite cache with invalidation by params, experiment version, and code version."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else ARTIFACTS_DIR / "experiment_cache.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def make_key(self, experiment: dict[str, Any]) -> str:
        payload = {
            "params": _jsonable(experiment.get("params", experiment)),
            "version": experiment.get("version", "v1"),
            "code_version": experiment.get("code_version") or _code_version(experiment.get("module_path")),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            row = conn.execute("SELECT result_json FROM cache WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, key: str, experiment: dict[str, Any], result: Any) -> None:
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache
                (key, version, code_version, params_json, result_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    experiment.get("version", "v1"),
                    experiment.get("code_version") or _code_version(experiment.get("module_path")),
                    json.dumps(_jsonable(experiment.get("params", experiment)), sort_keys=True, default=str),
                    json.dumps(_jsonable(result), default=str),
                    time.time(),
                ),
            )
            conn.commit()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    version TEXT,
                    code_version TEXT,
                    params_json TEXT,
                    result_json TEXT,
                    timestamp REAL
                )
                """
            )
            conn.commit()


class DistributedExecution(ScientificModule):
    """Distributed/parallel experiment executor using Ray, multiprocessing, then Dask."""

    def setup_ray_cluster(self, n_workers: int | None = None, use_gpu: bool = False) -> dict[str, Any]:
        try:
            import ray

            if not ray.is_initialized():
                ray.init(num_cpus=n_workers, num_gpus=1 if use_gpu else 0, ignore_reinit_error=True, include_dashboard=False)
            return {"available": True, "backend": "ray", "n_workers": n_workers, "use_gpu": use_gpu}
        except Exception as exc:
            return {"available": False, "backend": "ray", "error": str(exc)}

    def parallel_experiment_executor(self, experiment_list: list[dict[str, Any]], max_concurrent: int | None = None) -> list[dict[str, Any]]:
        max_concurrent = max_concurrent or min(os.cpu_count() or 1, max(1, len(experiment_list)))
        cache_path = str(ARTIFACTS_DIR / "experiment_cache.db")
        ray_status = self.setup_ray_cluster(max_concurrent, use_gpu=False)
        if ray_status.get("available"):
            import ray

            remote_fn = ray.remote(_execute_one_experiment)
            refs = [remote_fn.remote({"experiment": exp, "cache_path": cache_path}) for exp in experiment_list]
            return ray.get(refs)
        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_concurrent) as executor:
                payloads = [{"experiment": exp, "cache_path": cache_path} for exp in experiment_list]
                return list(executor.map(_execute_one_experiment, payloads))
        except Exception:
            try:
                from dask import delayed, compute

                tasks = [delayed(_execute_one_experiment)({"experiment": exp, "cache_path": cache_path}) for exp in experiment_list]
                return list(compute(*tasks, scheduler="threads", num_workers=max_concurrent))
            except Exception:
                return [_execute_one_experiment({"experiment": exp, "cache_path": cache_path}) for exp in experiment_list]

    def benchmark_scalability(self, sizes: list[int]) -> pd.DataFrame:
        rows = []
        serial_baseline_per_task = _time_serial_baseline()
        for size in sizes:
            experiments = [_benchmark_experiment(i, size) for i in range(size)]
            max_concurrent = min(os.cpu_count() or 1, size)
            start = time.perf_counter()
            results = self.parallel_experiment_executor(experiments, max_concurrent=max_concurrent)
            elapsed = max(time.perf_counter() - start, 1e-9)
            ideal_serial = serial_baseline_per_task * size
            speedup = ideal_serial / elapsed
            rows.append(
                {
                    "n_experiments": size,
                    "elapsed_seconds": elapsed,
                    "throughput_exp_per_sec": size / elapsed,
                    "speedup_vs_serial_estimate": speedup,
                    "efficiency": speedup / max(1, max_concurrent),
                    "cache_hits": sum(1 for item in results if item.get("cache_hit")),
                    "workers": max_concurrent,
                }
            )
        return pd.DataFrame(rows)

    def run(self, sizes: list[int] | None = None, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        sizes = sizes or [10, 50, 100, 500]
        frame = self.benchmark_scalability(sizes)
        self.artifact_manager.save_csv("hpc_benchmark.csv", frame)
        metrics = {
            "sizes": sizes,
            "max_throughput": float(frame["throughput_exp_per_sec"].max()),
            "max_speedup": float(frame["speedup_vs_serial_estimate"].max()),
            "mean_efficiency": float(frame["efficiency"].mean()),
            "cache_db": str(ARTIFACTS_DIR / "experiment_cache.db"),
        }
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": "distributed_execution", "sizes": sizes},
            results=metrics,
            status="completed",
        )
        report_path = self.log_result(metrics, "hpc_benchmark.md")
        return {"metrics": metrics, "report_path": report_path, "table": frame.to_dict(orient="records")}


class AsyncExperimentEngine:
    """Small async facade over the same cached experiment executor."""

    def __init__(self, max_workers: int | None = None, cache_path: str | Path | None = None):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers or (os.cpu_count() or 2))
        self.cache_path = str(cache_path or ARTIFACTS_DIR / "experiment_cache.db")
        self.futures: dict[str, concurrent.futures.Future] = {}

    def submit(self, experiment: dict[str, Any]) -> str:
        job_id = experiment.get("id") or hashlib.sha256(json.dumps(_jsonable(experiment), sort_keys=True).encode("utf-8")).hexdigest()[:16]
        self.futures[job_id] = self.executor.submit(_execute_one_experiment, {"experiment": experiment, "cache_path": self.cache_path})
        return job_id

    def get_results(self, job_id: str | None = None) -> Any:
        if job_id:
            return self.futures[job_id].result()
        return {key: future.result() for key, future in self.futures.items() if future.done()}

    def cancel(self, job_id: str) -> bool:
        return self.futures[job_id].cancel() if job_id in self.futures else False

    def status(self, job_id: str | None = None) -> Any:
        if job_id:
            future = self.futures.get(job_id)
            if future is None:
                return "missing"
            if future.cancelled():
                return "cancelled"
            if future.done():
                return "done"
            return "running"
        return {key: self.status(key) for key in self.futures}


def _execute_one_experiment(payload: dict[str, Any]) -> dict[str, Any]:
    experiment = payload["experiment"]
    cache = ExperimentCache(payload["cache_path"])
    key = cache.make_key(experiment)
    cached = cache.get(key)
    if cached is not None:
        cached["cache_hit"] = True
        return cached
    start = time.perf_counter()
    params = experiment.get("params", {})
    result = _default_experiment(params)
    result.update({"id": experiment.get("id"), "elapsed_seconds": time.perf_counter() - start, "cache_hit": False})
    cache.set(key, experiment, result)
    return result


def _default_experiment(params: dict[str, Any]) -> dict[str, Any]:
    x = float(params.get("x", 1.0))
    n = int(params.get("n", 1000))
    values = np.sin(np.linspace(0.0, x, n)) ** 2 + np.cos(np.linspace(0.0, x, n)) ** 2
    return {"metric": float(values.mean()), "n": n, "x": x}


def _benchmark_experiment(index: int, batch_size: int) -> dict[str, Any]:
    return {
        "id": f"hpc_{batch_size}_{index}",
        "version": "benchmark_v1",
        "module_path": str(Path(__file__).resolve()),
        "params": {"x": 1.0 + index / max(1, batch_size), "n": 1500, "batch_size": batch_size, "index": index},
    }


def _time_serial_baseline() -> float:
    start = time.perf_counter()
    _default_experiment({"x": 1.5, "n": 1500})
    return max(time.perf_counter() - start, 1e-9)


def _code_version(module_path: str | None = None) -> str:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=PHYSICS_ROOT.parent, text=True).strip()
        if commit:
            return f"git:{commit}"
    except Exception:
        pass
    path = Path(module_path) if module_path else Path(__file__).resolve()
    if path.exists():
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return "unknown"


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


if __name__ == "__main__":
    print(json.dumps(DistributedExecution().run(), indent=2, default=str))
