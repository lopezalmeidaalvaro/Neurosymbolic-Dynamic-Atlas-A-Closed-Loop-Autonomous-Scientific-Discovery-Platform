from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2

from quantum.integration.qiskit_adapter import qiskit_to_qade_json
from quantum.optimization.hardware_cost_model import estimate_physical_cost
from quantum.optimization.qubit_placement import QubitPlacement
from quantum.optimization.routing_engine import AdvancedRouter


def test_physical_cost_model_reports_required_metrics():
    backend = GenericBackendV2(num_qubits=3, coupling_map=[[0, 1], [1, 2]])
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)

    metrics = estimate_physical_cost(qc, backend)

    assert metrics["gate_fidelity"] > 0
    assert metrics["readout_fidelity"] > 0
    assert metrics["coherence_fidelity"] > 0
    assert metrics["total_estimated_fidelity"] > 0
    assert metrics["critical_duration_us"] >= 0
    assert "score" in metrics


def test_fidelity_aware_placement_returns_bijection_for_logical_qubits():
    backend = GenericBackendV2(num_qubits=4, coupling_map=[[0, 1], [1, 2], [2, 3]])
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qade_json = qiskit_to_qade_json(qc)

    layout = QubitPlacement(3, list(backend.coupling_map), backend=backend).place(
        qade_json, method="fidelity_aware"
    )

    assert set(layout.keys()) == {0, 1, 2}
    assert len(set(layout.values())) == 3


def test_coherence_aware_sabre_routes_non_adjacent_gate():
    backend = GenericBackendV2(num_qubits=3, coupling_map=[[0, 1], [1, 2]])
    qc = QuantumCircuit(3)
    qc.cx(0, 2)
    qade_json = qiskit_to_qade_json(qc)

    router = AdvancedRouter(list(backend.coupling_map), backend=backend)
    routed_json, _ = router.route(qade_json, method="coherence_aware_sabre")

    assert any(g["type"].upper() == "SWAP" for g in routed_json["gates"])
    assert routed_json["gates"][-1]["qubits"] in ([1, 2], [2, 1], [0, 1], [1, 0])
