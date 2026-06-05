from typing import Dict, Any, List, Tuple, Union
from qiskit import QuantumCircuit
from qiskit.providers.backend import BackendV2
from quantum.optimization.hardware_cost_model import estimate_physical_cost

def get_fake_backend(backend_name: str) -> BackendV2:
    """
    Returns an instance of an IBM fake backend by name.
    """
    from qiskit_ibm_runtime.fake_provider import (
        FakeSherbrooke, FakeBrisbane, FakeKyoto, FakeTorino, FakeFez
    )
    
    backends = {
        "fakesherbrooke": FakeSherbrooke,
        "fakebrisbane": FakeBrisbane,
        "fakekyoto": FakeKyoto,
        "faketorino": FakeTorino,
        "fakefez": FakeFez,
        "sherbrooke": FakeSherbrooke,
        "brisbane": FakeBrisbane,
        "kyoto": FakeKyoto,
        "torino": FakeTorino,
        "fez": FakeFez,
    }
    
    name_clean = backend_name.lower().replace("_", "").replace("-", "")
    cls = backends.get(name_clean)
    if cls is None:
        # Fallback to FakeBrisbane if not found
        return FakeBrisbane()
    return cls()

def estimate_fidelity(circuit: QuantumCircuit, backend: BackendV2) -> Dict[str, Any]:
    """
    Estimates the execution fidelity of a compiled circuit on a given backend.
    
    F_est = F_gate * F_readout * F_coherence
    """
    metrics = estimate_physical_cost(circuit, backend)
    active_qubits = metrics.get("active_qubits", [])
    quality = metrics.get("qubit_quality", {})
    t1_values = [quality[q]["t1"] for q in active_qubits if q in quality]
    t2_values = [quality[q]["t2"] for q in active_qubits if q in quality]
    metrics["mean_t1_sec"] = sum(t1_values) / len(t1_values) if t1_values else 100e-6
    metrics["mean_t2_sec"] = sum(t2_values) / len(t2_values) if t2_values else 50e-6
    return metrics
