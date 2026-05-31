from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from physics.core.base_module import ScientificModule
    from physics.scientific_guard import assign_claim_level, sanitize_hypothesis
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from scientific_guard import assign_claim_level, sanitize_hypothesis

from satellite.thermal.fdir_engine import FDIREngine
from satellite.thermal.hardware_in_the_loop import HardwareInTheLoopSimulator
from satellite.thermal.hil_real_hardware import RealHILInterface


class ExperimentRunner:
    """Wrapper around the existing HIL simulation and real-hardware interfaces."""

    def __init__(self, simulated: bool = True):
        self.hil = HardwareInTheLoopSimulator(miscalibrated=True)
        self.real_interface = RealHILInterface(port=None)
        self.simulated = simulated or self.real_interface.emulated
        self.mode = "SIMULATED - No physical hardware connected" if self.simulated else "PHYSICAL HARDWARE CONNECTED"

    def run_experiment(self, duration: int = 120, interval: int = 10) -> pd.DataFrame:
        plant_state = np.full(6, 293.15)
        dt_state = np.full(6, 293.15)
        rows = []
        power = 25.0
        for step in range(int(duration / interval) + 1):
            t_curr = step * interval
            measured = self.hil.read_sensors(plant_state - 273.15, noise_std=0.5)
            predicted = self.hil.predict_next(dt_state - 273.15, horizon=interval, power=power, t_current=t_curr)
            self.hil.correct_model(measured, predicted, dt=interval)
            plant_state = plant_state + np.array([0.02 * power, 0.01, 0.01, 0.0, -0.01, 0.0])
            dt_state = dt_state + np.array([0.018 * power, 0.01, 0.01, 0.0, -0.005, 0.0])
            rows.append({"time": t_curr, "measured": measured, "predicted": predicted, "power_W": power, "mode": self.mode})
            power = 10.0 if predicted > 80.0 else 25.0
        return pd.DataFrame(rows)

    def compare_with_simulation(self, measured, predicted) -> dict[str, float]:
        measured = np.asarray(measured, dtype=float).ravel()
        predicted = np.asarray(predicted, dtype=float).ravel()
        n = min(len(measured), len(predicted))
        measured = measured[:n]
        predicted = predicted[:n]
        return {
            "rmse": float(np.sqrt(mean_squared_error(measured, predicted))),
            "mae": float(mean_absolute_error(measured, predicted)),
            "r2": float(r2_score(measured, predicted)) if n > 1 else 0.0,
        }


class AnomalyDetector:
    """Wrapper around satellite.thermal.fdir_engine.FDIREngine."""

    def __init__(self):
        self.fdir = FDIREngine()
        self.history: list[list[float]] = []

    def detect_anomaly(self, predicted, measured, threshold: float = 3.0) -> dict[str, Any]:
        predicted_arr = _six_node(predicted)
        measured_arr = _six_node(measured)
        self.history.append(measured_arr.tolist())
        residual = measured_arr - predicted_arr
        z_score = float(np.max(np.abs(residual)) / max(self.fdir.sigma, 1e-9))
        fault_id, confidence, action = self.fdir.detect_fault(
            measured_arr,
            predicted_arr,
            dt_params={"eps_rad": 0.85},
            history=self.history,
        )
        is_anomaly = bool(z_score >= threshold or fault_id not in {"F0"})
        hypothesis = None
        if is_anomaly:
            text = (
                f"NO VALIDADA - requiere verificacion experimental: anomaly {fault_id} "
                f"may indicate a candidate causal mechanism, but causality is not established."
            )
            hypothesis = {
                "hypothesis": sanitize_hypothesis(text),
                "confidence_prior": min(0.35, float(confidence) * 0.4),
                "validation_state": "NO VALIDADA - requiere verificacion experimental",
                "claim_level": assign_claim_level(text, "simulated anomaly detector output only; unvalidated"),
            }
        return {
            "is_anomaly": is_anomaly,
            "fault_id": fault_id,
            "confidence": float(confidence),
            "action": action,
            "z_score": z_score,
            "causal_hypothesis_candidate": hypothesis,
        }


class PhysicalLabInterface(ScientificModule):
    """Virtual-to-physical lab validation coordinator."""

    def run_physical_validation_cycle(self) -> dict[str, Any]:
        runner = ExperimentRunner(simulated=True)
        detector = AnomalyDetector()
        telemetry = runner.run_experiment()
        metrics = runner.compare_with_simulation(telemetry["measured"], telemetry["predicted"])
        detections = [
            detector.detect_anomaly(predicted=row["predicted"], measured=row["measured"])
            for _, row in telemetry.iterrows()
        ]
        hypotheses = [item["causal_hypothesis_candidate"] for item in detections if item.get("causal_hypothesis_candidate")]
        for idx, hypothesis in enumerate(hypotheses, start=1):
            self.experiment_registry.register(
                module=self.module_name,
                params={"system": "physical_lab", "hypothesis_index": idx},
                results=hypothesis,
                status="requires_validation",
            )
        self.artifact_manager.save_csv("physical_validation_telemetry.csv", telemetry)
        self.artifact_manager.save_json("physical_validation_anomalies.json", detections)
        return {"mode": runner.mode, "comparison": metrics, "detections": detections, "hypotheses": hypotheses}

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        cycle = self.run_physical_validation_cycle()
        metrics = {
            "mode": cycle["mode"],
            **cycle["comparison"],
            "anomalies_detected": sum(1 for item in cycle["detections"] if item["is_anomaly"]),
            "causal_hypotheses_created": len(cycle["hypotheses"]),
        }
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": "physical_lab"},
            results=metrics,
            status="completed",
        )
        report_path = self.log_result(metrics, "physical_validation_report.md")
        return {"metrics": metrics, "report_path": report_path}


def _six_node(value) -> np.ndarray:
    arr = np.asarray(value, dtype=float).ravel()
    if arr.size == 1:
        return np.array([arr[0], 20.0, 20.0, 20.0, 20.0, 20.0])
    if arr.size < 6:
        return np.pad(arr, (0, 6 - arr.size), constant_values=float(np.mean(arr)))
    return arr[:6]


if __name__ == "__main__":
    print(json.dumps(PhysicalLabInterface().run(), indent=2, default=str))
