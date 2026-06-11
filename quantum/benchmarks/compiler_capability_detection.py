import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

logger = logging.getLogger(__name__)

def detect_compiler_capabilities() -> Dict[str, Any]:
    capabilities = {}

    # 1. Qiskit
    try:
        import qiskit
        capabilities["Qiskit"] = {
            "available": True,
            "version": qiskit.__version__,
            "max_qubits": 127,  # Qiskit has no practical local limit
            "max_acceptable_time_seconds": 10.0,
            "supports_routing": True,
            "supports_layout": True,
            "supports_optimization": True
        }
    except ImportError:
        capabilities["Qiskit"] = {"available": False}

    # 2. TKET
    try:
        import pytket
        capabilities["TKET"] = {
            "available": True,
            "version": pytket.__version__,
            "max_qubits": 100,  # TKET scales well
            "max_acceptable_time_seconds": 10.0,
            "supports_routing": True,
            "supports_layout": True,
            "supports_optimization": True
        }
    except ImportError:
        capabilities["TKET"] = {"available": False}

    # 3. BQSKit
    try:
        import bqskit
        # BQSKit is synthesis-based and slow for large circuits, limit is 20 qubits
        capabilities["BQSKit"] = {
            "available": True,
            "version": bqskit.__version__,
            "max_qubits": 20,
            "max_acceptable_time_seconds": 30.0,
            "supports_routing": False,  # BQSKit doesn't do physical routing by default
            "supports_layout": False,
            "supports_optimization": True
        }
    except ImportError:
        capabilities["BQSKit"] = {"available": False}

    # 4. Cirq
    try:
        import cirq
        capabilities["Cirq"] = {
            "available": True,
            "version": cirq.__version__,
            "max_qubits": 50,
            "max_acceptable_time_seconds": 10.0,
            "supports_routing": False,  # Adapter uses QADE routing for coupling
            "supports_layout": False,
            "supports_optimization": True
        }
    except ImportError:
        capabilities["Cirq"] = {"available": False}

    # 5. PyZX
    try:
        import pyzx
        capabilities["PyZX"] = {
            "available": True,
            "version": pyzx.__version__,
            "max_qubits": 100,
            "max_acceptable_time_seconds": 10.0,
            "supports_routing": False,  # PyZX is purely algebraic/logical
            "supports_layout": False,
            "supports_optimization": True
        }
    except ImportError:
        capabilities["PyZX"] = {"available": False}

    # Save to file
    output_dir = Path("benchmarks/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "COMPILER_CAPABILITIES.json", "w") as f:
        json.dump(capabilities, f, indent=2)
    
    print(f"Dynamic compiler capability detection complete. Saved to benchmarks/results/COMPILER_CAPABILITIES.json")
    return capabilities

if __name__ == "__main__":
    detect_compiler_capabilities()
