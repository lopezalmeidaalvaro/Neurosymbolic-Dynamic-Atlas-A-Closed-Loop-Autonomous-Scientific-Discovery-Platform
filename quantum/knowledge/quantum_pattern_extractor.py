import hashlib
from typing import Dict, Any, List

class QuantumPatternExtractor:
    """
    Extractor de patrones y motivos de diseño cuánticos a partir de circuitos evaluados.
    Detecta secuencias de compuertas recurrentes y motivos de entrelazamiento.
    """

    def __init__(self, min_length: int = 2, max_length: int = 3, score_threshold: float = 0.5):
        self.min_length = min_length
        self.max_length = max_length
        self.score_threshold = score_threshold

    def extract_patterns(self, evaluated_population: List[Any]) -> List[Dict[str, Any]]:
        """
        Extrae patrones a partir de los mejores circuitos de la población evaluada.
        """
        # Filtrar circuitos con desempeño alto
        high_performers = [
            e for e in evaluated_population
            if getattr(e, "valid", False) and getattr(e, "score", 0.0) >= self.score_threshold
        ]

        # Si no hay candidatos con score alto, tomar el top 30% de la población
        if not high_performers:
            sorted_pop = sorted(evaluated_population, key=lambda x: getattr(x, "score", 0.0), reverse=True)
            cutoff = max(1, int(len(sorted_pop) * 0.3))
            high_performers = sorted_pop[:cutoff]

        patterns_dict = {}  # representation -> { "pattern_id", "sequence", "scores", "type" }

        for eval_obj in high_performers:
            circuit = getattr(eval_obj, "circuit", eval_obj.get("circuit") if isinstance(eval_obj, dict) else None)
            if not circuit:
                continue

            gates = circuit.get("gates", [])
            score = getattr(eval_obj, "score", eval_obj.get("score", 0.0) if isinstance(eval_obj, dict) else 0.0)

            # 1. Secuencias de tipos de compuertas simples (sin qubits)
            gate_types = [g.get("type") for g in gates if g.get("type")]

            # 2. Motivos con qubits canonicalizados relativos para entrelazamientos
            rel_gates = []
            qubit_map = {}
            for g in gates:
                g_type = g.get("type")
                g_qubits = g.get("qubits", [])
                
                mapped_qubits = []
                for q in g_qubits:
                    if q not in qubit_map:
                        qubit_map[q] = f"q{len(qubit_map)}"
                    mapped_qubits.append(qubit_map[q])
                
                if mapped_qubits:
                    rel_gates.append(f"{g_type}({','.join(mapped_qubits)})")
                else:
                    rel_gates.append(g_type)

            # Extraer subsecuencias de longitud min_length a max_length
            for length in range(self.min_length, self.max_length + 1):
                # Patrones basados solo en tipos de compuertas
                for i in range(len(gate_types) - length + 1):
                    subseq = tuple(gate_types[i:i+length])
                    seq_str = "->".join(subseq)
                    
                    if seq_str not in patterns_dict:
                        pat_id = f"type_seq_{self._hash_string(seq_str)[:8]}"
                        patterns_dict[seq_str] = {
                            "pattern_id": pat_id,
                            "sequence": list(subseq),
                            "scores": [],
                            "type": "repeated_subsequence"
                        }
                    patterns_dict[seq_str]["scores"].append(score)

                # Patrones basados en compuertas relativas (motivos estructurales/entrelazamiento)
                for i in range(len(rel_gates) - length + 1):
                    subseq = tuple(rel_gates[i:i+length])
                    seq_str = "->".join(subseq)
                    
                    # Detectar si es motivo de entrelazamiento
                    is_entanglement = any("CNOT" in g or "CX" in g for g in subseq) and any("H" in g for g in subseq)
                    p_type = "entanglement_motif" if is_entanglement else "structural_motif"

                    if seq_str not in patterns_dict:
                        pat_id = f"struct_seq_{self._hash_string(seq_str)[:8]}"
                        patterns_dict[seq_str] = {
                            "pattern_id": pat_id,
                            "sequence": list(subseq),
                            "scores": [],
                            "type": p_type
                        }
                    patterns_dict[seq_str]["scores"].append(score)

        # Construir objetos finales
        results = []
        for seq_str, pdata in patterns_dict.items():
            scores = pdata["scores"]
            frequency = len(scores)
            avg_score = sum(scores) / frequency if frequency > 0 else 0.0
            
            results.append({
                "pattern_id": pdata["pattern_id"],
                "sequence": pdata["sequence"],
                "frequency": frequency,
                "avg_score": round(avg_score, 4),
                "type": pdata["type"],
                "representation": seq_str
            })

        # Ordenar por frecuencia (descendente) y luego por avg_score (descendente)
        results.sort(key=lambda x: (x["frequency"], x["avg_score"]), reverse=True)
        return results

    def _hash_string(self, s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()
