import math
import copy
import statistics
from typing import Dict, Any, List, Set, Tuple

class RepresentationAnalyzer:
    """
    Analyzes historical quantum runs across multiple representation levels
    (Raw Patterns, Motifs, Extended Motifs, Scaffolds, Context-Aware)
    to compute predictive power, survival, transfer rate, and information gain.
    """

    def __init__(self):
        pass

    @staticmethod
    def is_subsequence(sub: List[str], main: List[str]) -> bool:
        n, m = len(sub), len(main)
        for i in range(m - n + 1):
            if main[i:i+n] == sub:
                return True
        return False

    @staticmethod
    def get_gate_repr(gate: Dict[str, Any]) -> str:
        gate_type = gate.get("type", "")
        qubits = gate.get("qubits", [])
        return f"{gate_type}({','.join(f'q{q}' for q in qubits)})"

    def get_circuit_canonical_repr(self, circuit: Dict[str, Any]) -> str:
        gates = circuit.get("gates", [])
        gate_reprs = [self.get_gate_repr(g) for g in gates]
        return "->".join(gate_reprs)

    def circuit_contains(self, circuit: Dict[str, Any], level: str, representation: str) -> bool:
        if "circuit" in circuit and isinstance(circuit["circuit"], dict):
            actual_circuit = circuit["circuit"]
            eval_dict = circuit
        else:
            actual_circuit = circuit
            eval_dict = circuit

        gates = actual_circuit.get("gates", [])
        gate_reprs = [self.get_gate_repr(g) for g in gates]
        gate_types = [g.get("type", "") for g in gates]

        if level == "LEVEL_1_RAW_PATTERN":
            return representation in gate_reprs

        elif level == "LEVEL_2_MOTIF" or level == "LEVEL_3_EXTENDED_MOTIF":
            motif_parts = representation.split("->")
            return self.is_subsequence(motif_parts, gate_types)

        elif level == "LEVEL_4_SCAFFOLD":
            canon = self.get_circuit_canonical_repr(actual_circuit)
            qubits_val = eval_dict.get("qubits", 2)
            qubit_count = len(qubits_val) if isinstance(qubits_val, list) else qubits_val
            if representation == "Bell Scaffold":
                return qubit_count == 2 and "H" in gate_types and "CNOT" in gate_types
            elif representation == "GHZ Scaffold":
                return qubit_count == 3 and "H" in gate_types and gate_types.count("CNOT") >= 2
            return canon == representation

        elif level == "LEVEL_5_CONTEXT_AWARE":
            # Form: Pattern: {base_pat} | Context: {task} | {qubits} qubits | {status}
            parts = [p.strip() for p in representation.split("|")]
            base_pat = parts[0].replace("Pattern:", "").strip()
            task = parts[1].replace("Context:", "").strip()
            qubits_str = parts[2].split()[0]
            status = parts[3].strip()

            circuit_task = eval_dict.get("task", "")
            qubits_val = eval_dict.get("qubits", 0)
            circuit_qubits = len(qubits_val) if isinstance(qubits_val, list) else qubits_val
            circuit_converged = eval_dict.get("converged", False)
            expected_status = "Converged" if circuit_converged else "Failed"

            if str(circuit_qubits) != qubits_str or circuit_task != task or expected_status != status:
                return False

            # Check pattern containment
            if "->" in base_pat:
                motif_parts = base_pat.split("->")
                return self.is_subsequence(motif_parts, gate_types)
            else:
                return base_pat in gate_reprs

        return False

    def does_record_match(self, record: Dict[str, Any], level: str, representation: str) -> bool:
        rec_pat = record.get("pattern") or record.get("pattern_repr")
        if not rec_pat:
            return False

        if level == "LEVEL_1_RAW_PATTERN":
            parts = rec_pat.split("->")
            return representation in parts

        elif level == "LEVEL_2_MOTIF" or level == "LEVEL_3_EXTENDED_MOTIF":
            # Strip qubits from rec_pat to check gate sequence
            rec_clean = "->".join(p.split("(")[0].strip() for p in rec_pat.split("->"))
            motif_parts = representation.split("->")
            rec_parts = rec_clean.split("->")
            return self.is_subsequence(motif_parts, rec_parts)

        elif level == "LEVEL_4_SCAFFOLD":
            if representation == "Bell Scaffold":
                return "H" in rec_pat and "CNOT" in rec_pat
            elif representation == "GHZ Scaffold":
                return "H" in rec_pat and rec_pat.count("CNOT") >= 2
            return rec_pat == representation

        elif level == "LEVEL_5_CONTEXT_AWARE":
            # Context-aware representation form: Pattern: {base_pat} | Context: {task} | {qubits} qubits | {status}
            parts = [p.strip() for p in representation.split("|")]
            base_pat = parts[0].replace("Pattern:", "").strip()
            task = parts[1].replace("Context:", "").strip()
            qubits_str = parts[2].split()[0]
            status = parts[3].strip()

            # Causal records are logged during GHZ (3 qubits) target, transferred from Bell
            record_task = "ghz_state"
            record_qubits = "3"
            
            # Since causal records don't directly save final convergence of the circuit,
            # we assume it matches the target status of the record if it survives.
            record_survived = record.get("survival_status", False)
            record_status = "Converged" if record_survived else "Failed"

            if record_task != task or record_qubits != qubits_str or record_status != status:
                return False

            # Check if base pattern matches
            if "->" in base_pat:
                rec_clean = "->".join(p.split("(")[0].strip() for p in rec_pat.split("->"))
                motif_parts = base_pat.split("->")
                rec_parts = rec_clean.split("->")
                return self.is_subsequence(motif_parts, rec_parts)
            else:
                parts = rec_pat.split("->")
                return base_pat in parts

        return False

    def compute_entropy(self, p: float) -> float:
        if p <= 0.0 or p >= 1.0:
            return 0.0
        return - (p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))

    def compute_information_gain(self, representation: str, level: str, evals: List[Dict[str, Any]]) -> float:
        if not evals:
            return 0.0

        total = len(evals)
        converged = sum(1 for e in evals if e.get("converged", False))
        p_baseline = converged / total
        H_baseline = self.compute_entropy(p_baseline)

        # Count containment
        contains_list = [self.circuit_contains(e, level, representation) for e in evals]
        count_x1 = sum(1 for c in contains_list if c)
        count_x0 = total - count_x1

        if count_x1 == 0 or count_x0 == 0:
            return 0.0

        p_x1 = count_x1 / total
        p_x0 = count_x0 / total

        converged_x1 = sum(1 for e, c in zip(evals, contains_list) if c and e.get("converged", False))
        converged_x0 = converged - converged_x1

        p_y_given_x1 = converged_x1 / count_x1
        p_y_given_x0 = converged_x0 / count_x0

        H_cond = p_x1 * self.compute_entropy(p_y_given_x1) + p_x0 * self.compute_entropy(p_y_given_x0)
        return H_baseline - H_cond

    def analyze(
        self,
        historical_evaluations: List[Dict[str, Any]],
        causal_records: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Runs the representation quality analysis across all 5 levels.
        """
        levels = [
            "LEVEL_1_RAW_PATTERN",
            "LEVEL_2_MOTIF",
            "LEVEL_3_EXTENDED_MOTIF",
            "LEVEL_4_SCAFFOLD",
            "LEVEL_5_CONTEXT_AWARE"
        ]

        # Extract unique representations for each level
        unique_reps: Dict[str, Set[str]] = {lvl: set() for lvl in levels}

        for ev in historical_evaluations:
            gates = ev.get("circuit", {}).get("gates", [])
            gate_reprs = [self.get_gate_repr(g) for g in gates]
            gate_types = [g.get("type", "") for g in gates]

            # Level 1
            for gr in gate_reprs:
                unique_reps["LEVEL_1_RAW_PATTERN"].add(gr)

            # Level 2 & 3
            n = len(gate_types)
            for length in range(1, 6):
                for i in range(n - length + 1):
                    sub = "->".join(gate_types[i:i+length])
                    if length <= 2:
                        unique_reps["LEVEL_2_MOTIF"].add(sub)
                    else:
                        unique_reps["LEVEL_3_EXTENDED_MOTIF"].add(sub)

        # Level 4 Scaffolds
        unique_reps["LEVEL_4_SCAFFOLD"].add("Bell Scaffold")
        unique_reps["LEVEL_4_SCAFFOLD"].add("GHZ Scaffold")

        # Level 5 Context-Aware (Pattern + Context)
        for ev in historical_evaluations:
            task = ev.get("task", "")
            qubits = ev.get("qubits", 0)
            status = "Converged" if ev.get("converged", False) else "Failed"

            gates = ev.get("circuit", {}).get("gates", [])
            gate_reprs = [self.get_gate_repr(g) for g in gates]
            gate_types = [g.get("type", "") for g in gates]

            # Extract Level 1 gates and Level 2/3 motifs
            for gr in gate_reprs:
                unique_reps["LEVEL_5_CONTEXT_AWARE"].add(f"Pattern: {gr} | Context: {task} | {qubits} qubits | {status}")
            n = len(gate_types)
            for length in range(1, 6):
                for i in range(n - length + 1):
                    sub = "->".join(gate_types[i:i+length])
                    unique_reps["LEVEL_5_CONTEXT_AWARE"].add(f"Pattern: {sub} | Context: {task} | {qubits} qubits | {status}")

        # Compute metrics for each unique representation at each level
        analysis_results = {}
        for lvl in levels:
            lvl_results = []
            for rep in unique_reps[lvl]:
                # 1. Frequency in evaluations
                matching_evals = [e for e in historical_evaluations if self.circuit_contains(e, lvl, rep)]
                freq = len(matching_evals)

                if freq == 0:
                    continue

                # 2. Mean Fidelity
                mean_fid = statistics.mean(e.get("fidelity", 0.0) for e in matching_evals)

                # 3. P(convergence | representation)
                converged_count = sum(1 for e in matching_evals if e.get("converged", False))
                p_conv = converged_count / freq

                # 4. Survival Probability, Mean Delta, and Transfer Success from causal records
                matching_records = [r for r in causal_records if self.does_record_match(r, lvl, rep)]
                if matching_records:
                    survived_count = sum(1 for r in matching_records if r.get("survival_status", False))
                    survival_prob = survived_count / len(matching_records)
                    
                    deltas = [r.get("delta_score") for r in matching_records if r.get("delta_score") is not None]
                    mean_delta = statistics.mean(deltas) if deltas else 0.0
                    
                    transfer_success = survived_count / len(matching_records)
                else:
                    survival_prob = 0.0
                    mean_delta = 0.0
                    transfer_success = 0.0

                # 5. Predictive Information Gain
                ig = self.compute_information_gain(rep, lvl, historical_evaluations)

                lvl_results.append({
                    "representation": rep,
                    "frequency": freq,
                    "mean_fidelity": round(mean_fid, 4),
                    "P_convergence": round(p_conv, 4),
                    "survival_probability": round(survival_prob, 4),
                    "mean_delta_score": round(mean_delta, 4),
                    "transfer_success_rate": round(transfer_success, 4),
                    "information_gain": round(ig, 4)
                })

            # Sort results by information_gain desc
            lvl_results.sort(key=lambda x: x["information_gain"], reverse=True)
            analysis_results[lvl] = lvl_results

        return analysis_results
