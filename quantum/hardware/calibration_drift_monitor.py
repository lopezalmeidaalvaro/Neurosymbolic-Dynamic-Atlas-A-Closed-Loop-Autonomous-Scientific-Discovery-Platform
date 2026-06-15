import os
import json
import math
from datetime import datetime
from typing import Any, Dict, Optional

from qiskit_ibm_runtime import QiskitRuntimeService
from quantum.optimization.hardware_cost_model_v2 import get_qubit_quality, get_gate_properties


def get_calibration_snapshot(backend: Any) -> Dict[str, Any]:
    """Captura un snapshot completo del estado de calibración del backend."""
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend.name,
        "qubits": {},
        "gates": {}
    }
    
    num_qubits = backend.num_qubits
    for q in range(num_qubits):
        quality = get_qubit_quality(backend, q)
        snapshot["qubits"][str(q)] = {
            "t1": quality["t1"],
            "t2": quality["t2"],
            "readout_error": quality["readout_error"]
        }
        
    target = getattr(backend, "target", None)
    if target is not None:
        for op_name in target.operation_names:
            if op_name in ("cx", "ecr", "cz"):
                for qargs in target[op_name].keys():
                    if len(qargs) == 2:
                        props = target[op_name].get(qargs)
                        if props is not None:
                            error = getattr(props, "error", 0.01)
                            duration = getattr(props, "duration", 300e-9)
                            key = f"{op_name}_{qargs[0]}_{qargs[1]}"
                            snapshot["gates"][key] = {
                                "gate_error": float(error) if error is not None else 0.01,
                                "gate_length_ns": (float(duration) * 1e9) if duration is not None else 300.0
                            }
    return snapshot


def compare_snapshots(compile_snapshot: Dict[str, Any], execute_snapshot: Dict[str, Any], threshold_pct: float = 10.0) -> Dict[str, Any]:
    """Compara dos snapshots y calcula la deriva porcentual máxima de calibración."""
    t_compile = datetime.fromisoformat(compile_snapshot["timestamp"])
    t_execute = datetime.fromisoformat(execute_snapshot["timestamp"])
    hours_elapsed = (t_execute - t_compile).total_seconds() / 3600.0
    
    max_t1_drift = 0.0
    max_t2_drift = 0.0
    max_gate_drift = 0.0
    
    # Compare qubits properties
    for q, props_c in compile_snapshot["qubits"].items():
        props_e = execute_snapshot["qubits"].get(q)
        if props_e:
            t1_c = props_c["t1"]
            t1_e = props_e["t1"]
            if t1_c > 0:
                max_t1_drift = max(max_t1_drift, abs(t1_e - t1_c) / t1_c * 100.0)
                
            t2_c = props_c["t2"]
            t2_e = props_e["t2"]
            if t2_c > 0:
                max_t2_drift = max(max_t2_drift, abs(t2_e - t2_c) / t2_c * 100.0)
                
    # Compare CNOT gate errors
    for gate, props_c in compile_snapshot["gates"].items():
        props_e = execute_snapshot["gates"].get(gate)
        if props_e:
            err_c = props_c["gate_error"]
            err_e = props_e["gate_error"]
            if err_c > 0:
                max_gate_drift = max(max_gate_drift, abs(err_e - err_c) / err_c * 100.0)
                
    drift_exceeds = (
        max_t1_drift > threshold_pct or 
        max_t2_drift > threshold_pct or 
        max_gate_drift > threshold_pct
    )
    
    return {
        "hours_elapsed": hours_elapsed,
        "max_t1_drift_pct": max_t1_drift,
        "max_t2_drift_pct": max_t2_drift,
        "max_gate_error_drift_pct": max_gate_drift,
        "drift_exceeds_threshold": drift_exceeds,
        "threshold_pct": threshold_pct
    }
