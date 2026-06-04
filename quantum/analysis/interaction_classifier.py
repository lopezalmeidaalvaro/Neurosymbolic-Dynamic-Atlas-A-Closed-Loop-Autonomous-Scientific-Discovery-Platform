import re
from typing import List, Dict, Any

class InteractionClassifier:
    """
    Classifies quantum gate sequences into specific interaction categories.
    """

    def classify_sequence(self, sequence: List[str]) -> str:
        """
        Analiza una secuencia de compuertas representadas como cadenas y determina su tipo de interacción.
        """
        if not sequence:
            return "UNKNOWN"

        # Parse gates into structured info: {"type": gate_name, "qubits": list of qubits}
        gates = []
        for g_str in sequence:
            if '(' in g_str and ')' in g_str:
                parts = g_str.split('(')
                gate_name = parts[0].strip()
                qubits_part = parts[1].rstrip(')').strip()
                qubits = [q.strip() for q in qubits_part.split(',') if q.strip()]
            else:
                gate_name = g_str.strip()
                qubits = []
            gates.append({"type": gate_name, "qubits": qubits})

        # 1. MEASUREMENT_STRUCTURE
        if any(g["type"] in ("MEASURE", "M") for g in gates):
            return "MEASUREMENT_STRUCTURE"

        # 2. SYMMETRY_EXTENSION (symmetric gate sequences, e.g. H->CNOT->H)
        types = [g["type"] for g in gates]
        if len(types) >= 3 and types == list(reversed(types)):
            return "SYMMETRY_EXTENSION"

        # 3. STATE_PREPARATION_EXTENSION (H followed by CNOT)
        h_indices = [i for i, g in enumerate(gates) if g["type"] == "H"]
        cnot_indices = [i for i, g in enumerate(gates) if g["type"] == "CNOT"]
        if h_indices and cnot_indices:
            if any(c_idx > h_idx for h_idx in h_indices for c_idx in cnot_indices):
                return "STATE_PREPARATION_EXTENSION"

        # 4. PARAMETER_PREPARATION (RX/RY/RZ/U followed by CNOT)
        rot_types = {"RX", "RY", "RZ", "U", "U1", "U2", "U3"}
        rot_indices = [i for i, g in enumerate(gates) if g["type"] in rot_types]
        if rot_indices and cnot_indices:
            if any(c_idx > r_idx for r_idx in rot_indices for c_idx in cnot_indices):
                return "PARAMETER_PREPARATION"

        # 5. PARAMETER_REFINEMENT (successive rotations on same qubit)
        for i in range(len(gates) - 1):
            g1, g2 = gates[i], gates[i+1]
            if g1["type"] in rot_types and g2["type"] in rot_types:
                if g1["qubits"] and g2["qubits"] and any(q in g2["qubits"] for q in g1["qubits"]):
                    return "PARAMETER_REFINEMENT"

        # 6. CONTROL_REUSE (target/control of CNOT reused in successive CNOTs)
        if len(cnot_indices) >= 2:
            for i in range(len(cnot_indices) - 1):
                idx1, idx2 = cnot_indices[i], cnot_indices[i+1]
                q1 = gates[idx1]["qubits"]
                q2 = gates[idx2]["qubits"]
                if q1 and q2 and any(q in q2 for q in q1):
                    return "CONTROL_REUSE"

        # 7. ENTANGLING_CHAIN (multiple entangling gates in series)
        if len(cnot_indices) >= 2:
            return "ENTANGLING_CHAIN"

        # 8. TOPOLOGY_EXPANSION (gates on different qubits)
        all_qubits = set()
        for g in gates:
            all_qubits.update(g["qubits"])
        if len(all_qubits) > 2:
            return "TOPOLOGY_EXPANSION"

        return "UNKNOWN"
