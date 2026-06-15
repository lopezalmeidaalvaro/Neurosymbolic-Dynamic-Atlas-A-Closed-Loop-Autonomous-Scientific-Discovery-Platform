from datetime import datetime, timezone
from typing import Any
from pydantic import ValidationError

# Strict imports from public API boundary
from mathematics import GateType, GateNode, QuantumEquivalenceIR


class FormalVerificationAdapter:
    """Adapter to map QADE motifs to the formal verification MathEngine contract.

    Includes defensive checks, validation safety, caching, and audit metadata.
    """

    SUPPORTED_GATES = {
        "I": GateType.I,
        "H": GateType.H,
        "X": GateType.X,
        "Y": GateType.Y,
        "Z": GateType.Z,
        "CNOT": GateType.CNOT,
        "SWAP": GateType.SWAP,
    }

    def __init__(self, math_engine: Any) -> None:
        self.math_engine = math_engine
        self._cache: dict[str, dict] = {}

    def certify_motif(
        self, motif_id: str, lhs_gates: list[dict], rhs_gates: list[dict]
    ) -> dict:
        """Translates gates to FormalizableIR, calls verification, caches and adds audit data."""
        # 1. Cache hit check
        if motif_id in self._cache:
            return self._cache[motif_id]

        # 2. Filter gates defensively
        for gate in lhs_gates + rhs_gates:
            gate_name = gate.get("type", gate.get("gate_type"))
            if gate_name not in self.SUPPORTED_GATES:
                err_res = {
                    "success": False,
                    "status": "UNSUPPORTED_GATES",
                    "error": f"Contiene puertas no soportadas por la API matemática: {gate_name}",
                }
                self._cache[motif_id] = err_res
                return err_res

        # 3. Build IR nodes with Pydantic validations wrapped defensively
        try:
            lhs_nodes = []
            for gate in lhs_gates:
                gate_name = gate.get("type", gate.get("gate_type"))
                # Default qubits to empty list if missing or invalid type
                qubits = gate.get("qubits", [])
                params = gate.get("parameters", None)
                lhs_nodes.append(
                    GateNode(
                        gate_type=self.SUPPORTED_GATES[gate_name],
                        qubits=qubits,
                        parameters=params,
                    )
                )

            rhs_nodes = []
            for gate in rhs_gates:
                gate_name = gate.get("type", gate.get("gate_type"))
                qubits = gate.get("qubits", [])
                params = gate.get("parameters", None)
                rhs_nodes.append(
                    GateNode(
                        gate_type=self.SUPPORTED_GATES[gate_name],
                        qubits=qubits,
                        parameters=params,
                    )
                )

            ir = QuantumEquivalenceIR(
                motif_id=motif_id,
                source_system="qade_optimizer",
                created_at=datetime.now(timezone.utc),
                lhs=lhs_nodes,
                rhs=rhs_nodes,
                assumptions=[],
            )

        except (ValidationError, TypeError, KeyError, ValueError) as e:
            # Wrap validation failure into a clean error certificate
            err_res = {
                "success": False,
                "status": "VALIDATION_ERROR",
                "error": f"Validation failed during IR conversion: {str(e)}",
            }
            self._cache[motif_id] = err_res
            return err_res

        # 4. Call MathEngine verify_discovery
        try:
            verification_dict = self.math_engine.verify_discovery(ir)
            cert = dict(verification_dict)
        except Exception as e:
            # Fallback wrapper if MathEngine.verify_discovery raises unexpected exception
            cert = {
                "success": False,
                "status": "INTERNAL_ERROR",
                "error": f"MathEngine raised unexpected error: {str(e)}",
            }

        # 5. Append IP audit metadata
        cert["certified_at"] = datetime.now(timezone.utc).isoformat()
        cert["certificate_version"] = "v1.0"

        # 6. Cache and return
        self._cache[motif_id] = cert
        return cert
