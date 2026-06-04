import math
from typing import Dict, Any, List

class TransferabilityFeatureEngine:
    """
    Computes structural similarity and complexity features to explain and predict 
    the transferability of quantum knowledge units across different domains.
    """

    def compute_features(
        self, 
        scaffold_rep: str, 
        sequence: List[str], 
        source_context: Dict[str, Any], 
        target_context: Dict[str, Any],
        memory: Any = None
    ) -> Dict[str, float]:
        
        # 1. Extract qubit counts
        q_src = source_context.get("qubit_count", 2)
        q_tgt = target_context.get("qubit_count", 2)
        
        # 2. Topology Similarity (based on qubit count difference)
        topology_similarity = 1.0 - (abs(q_src - q_tgt) / max(q_src, q_tgt)) if max(q_src, q_tgt) > 0 else 1.0
        
        # 3. Entanglement Overlap (whether both domains aim to generate entangled states)
        entangled_tasks = {
            "bell_state", "ghz_state", "w_state", "error_correction",
            "qaoa", "vqe", "qft", "grover", "amplitude_encoding",
            "hardware_efficient", "quantum_walk"
        }
        src_task = source_context.get("task_name", "")
        tgt_task = target_context.get("task_name", "")
        
        entanglement_overlap = 1.0 if (src_task in entangled_tasks and tgt_task in entangled_tasks) else 0.5
        
        # 4. State Preparation Overlap
        state_prep_tasks = {
            "bell_state", "ghz_state", "w_state", "error_correction",
            "qaoa", "vqe", "qft", "grover", "amplitude_encoding",
            "hardware_efficient", "quantum_walk"
        }
        state_preparation_overlap = 1.0 if (src_task in state_prep_tasks and tgt_task in state_prep_tasks) else 0.5
        
        # 5. Circuit Depth Difference (Proxy estimation based on qubits and tasks)
        depth_src = 2 if src_task == "bell_state" else (4 if src_task == "ghz_state" else 6)
        depth_tgt = 2 if tgt_task == "bell_state" else (4 if tgt_task == "ghz_state" else 6)
        circuit_depth_difference = float(abs(depth_src - depth_tgt))
        
        # 6. Gate Distribution Distance (RX/RY vs standard Clifford/CNOT)
        # Variational and W-state tasks rely on rotations RX/RY, whereas Bell/GHZ use H/CNOT
        rotation_tasks = {
            "variational_ansatz", "w_state", "qaoa", "vqe", "qft", 
            "amplitude_encoding", "hardware_efficient", "quantum_walk"
        }
        uses_rotation_src = src_task in rotation_tasks
        uses_rotation_tgt = tgt_task in rotation_tasks
        gate_distribution_distance = 0.8 if (uses_rotation_src != uses_rotation_tgt) else 0.1
        
        # 7. Context Distance
        context_distance = 1.0 - topology_similarity
        if src_task != tgt_task:
            context_distance += 0.5
            
        # 8. Scaffold Complexity (length of the sequence)
        scaffold_complexity = float(len(sequence))
        
        # 9. Interaction Frequency
        # Retrieves historical frequency of constituent patterns from memory if available
        interaction_frequency = 5.0
        if memory is not None:
            patterns = memory.retrieve("quantum:distillation:patterns") or []
            
            # Sum constituent frequencies using substring match
            freq_sum = 0
            for p in patterns:
                p_rep = p.get("representation", "")
                if p_rep and p_rep in scaffold_rep:
                    freq_sum += p.get("frequency", 1)
            if freq_sum > 0:
                interaction_frequency = float(freq_sum)
                
        return {
            "topology_similarity": round(topology_similarity, 4),
            "qubit_count_difference": float(abs(q_src - q_tgt)),
            "entanglement_overlap": entanglement_overlap,
            "state_preparation_overlap": state_preparation_overlap,
            "circuit_depth_difference": circuit_depth_difference,
            "gate_distribution_distance": gate_distribution_distance,
            "context_distance": round(context_distance, 4),
            "scaffold_complexity": scaffold_complexity,
            "interaction_frequency": interaction_frequency
        }
