from datetime import datetime, timezone
from mathematics import QuantumEquivalenceIR, GateNode, GateType


class SyntheticQuantumMotifGenerator:
    """Generates synthetic quantum motifs with known identities and difficulty levels (Curriculum Learning)."""

    def generate_seed_motifs(self, count: int) -> list[QuantumEquivalenceIR]:
        """Generates a list of synthetically created known quantum equivalences under curriculum learning.

        Levels:
        - Level 1: Pauli Involution (difficulty=1)
          - X · X = I
          - Z · Z = I
        - Level 2: Hadamard Conjugation (difficulty=2)
          - H · X · H = Z
          - H · Z · H = X
        - Level 3: CNOT Involution (difficulty=3)
          - CNOT · CNOT = I
        """
        motifs = []
        for i in range(count):
            q = i % 10  # Cycle through 10 qubit indices to create variety
            eq_type = i % 5
            now = datetime.now(timezone.utc)

            if eq_type == 0:
                # Level 1: X · X = I
                lhs = [
                    GateNode(gate_type=GateType.X, qubits=[q]),
                    GateNode(gate_type=GateType.X, qubits=[q]),
                ]
                rhs = [GateNode(gate_type=GateType.I, qubits=[q])]
                motif_id = f"synth_X_X_I_q{q}_{i}"
                metadata = {
                    "difficulty": 1,
                    "family": "pauli_involution",
                    "proof_origin": "constructive",
                }
            elif eq_type == 1:
                # Level 1: Z · Z = I
                lhs = [
                    GateNode(gate_type=GateType.Z, qubits=[q]),
                    GateNode(gate_type=GateType.Z, qubits=[q]),
                ]
                rhs = [GateNode(gate_type=GateType.I, qubits=[q])]
                motif_id = f"synth_Z_Z_I_q{q}_{i}"
                metadata = {
                    "difficulty": 1,
                    "family": "pauli_involution",
                    "proof_origin": "constructive",
                }
            elif eq_type == 2:
                # Level 2: H · X · H = Z
                lhs = [
                    GateNode(gate_type=GateType.H, qubits=[q]),
                    GateNode(gate_type=GateType.X, qubits=[q]),
                    GateNode(gate_type=GateType.H, qubits=[q]),
                ]
                rhs = [GateNode(gate_type=GateType.Z, qubits=[q])]
                motif_id = f"synth_H_X_H_Z_q{q}_{i}"
                metadata = {
                    "difficulty": 2,
                    "family": "hadamard_conjugation",
                    "proof_origin": "axiomatic",
                }
            elif eq_type == 3:
                # Level 2: H · Z · H = X
                lhs = [
                    GateNode(gate_type=GateType.H, qubits=[q]),
                    GateNode(gate_type=GateType.Z, qubits=[q]),
                    GateNode(gate_type=GateType.H, qubits=[q]),
                ]
                rhs = [GateNode(gate_type=GateType.X, qubits=[q])]
                motif_id = f"synth_H_Z_H_X_q{q}_{i}"
                metadata = {
                    "difficulty": 2,
                    "family": "hadamard_conjugation",
                    "proof_origin": "axiomatic",
                }
            else:
                # Level 3: CNOT · CNOT = I
                q1 = q
                q2 = (q + 1) % 10
                # Ensure control and target are distinct
                if q1 == q2:
                    q2 = (q1 + 1) % 10
                lhs = [
                    GateNode(gate_type=GateType.CNOT, qubits=[q1, q2]),
                    GateNode(gate_type=GateType.CNOT, qubits=[q1, q2]),
                ]
                rhs = [
                    GateNode(gate_type=GateType.I, qubits=[q1]),
                    GateNode(gate_type=GateType.I, qubits=[q2]),
                ]
                motif_id = f"synth_CNOT_CNOT_I_q{q1}_q{q2}_{i}"
                metadata = {
                    "difficulty": 3,
                    "family": "cnot_involution",
                    "proof_origin": "axiomatic",
                }

            motif = QuantumEquivalenceIR(
                motif_id=motif_id,
                source_system="synthetic_generator",
                created_at=now,
                lhs=lhs,
                rhs=rhs,
                assumptions=[],
                metadata=metadata,
            )
            motifs.append(motif)

        return motifs
