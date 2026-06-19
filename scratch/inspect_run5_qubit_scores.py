import json
from pathlib import Path

def inspect_scores():
    checkpoint_path = Path("benchmarks/checkpoints/RUN5_CHECKPOINT.json")
    if not checkpoint_path.exists():
        print("ERROR: Checkpoint not found.")
        return
        
    with open(checkpoint_path, "r") as f:
        checkpoint = json.load(f)
        
    snapshot = checkpoint.get("calibration_snapshot", {})
    qubits_data = snapshot.get("qubits", {})
    
    # Let's extract T1, T2, readout error
    qualities = {}
    max_t1 = 1e-15
    max_t2 = 1e-15
    
    for q_str, data in qubits_data.items():
        q = int(q_str)
        t1 = data.get("t1", 50e-6)
        t2 = data.get("t2", 70e-6)
        readout = data.get("readout_error", 0.01)
        
        qualities[q] = {
            "t1": t1,
            "t2": t2,
            "readout_error": readout,
            # We don't have gate errors in checkpoint (only qubit properties), so mock avg_gate_error
            "avg_gate_error": 0.01,
            "degree": 3 # Mock degree
        }
        max_t1 = max(max_t1, t1)
        max_t2 = max(max_t2, t2)
        
    w1, w2, w3, w4 = 0.35, 0.35, 0.15, 0.15
    physical_scores = []
    for p, quality in qualities.items():
        score = (
            w1 * (quality["t1"] / max_t1)
            + w2 * (quality["t2"] / max_t2)
            - w3 * quality["readout_error"]
            - w4 * quality["avg_gate_error"]
            + 0.01 * quality["degree"]
        )
        physical_scores.append((p, score))
    physical_scores.sort(key=lambda item: item[1], reverse=True)
    
    print("Top 15 physical qubits from Run 5 calibration snapshot:")
    for rank, (p, score) in enumerate(physical_scores[:15]):
        print(f"  Rank {rank+1}: Qubit {p} (Score: {score:.4f}, T1: {qualities[p]['t1']*1e6:.1f}us, T2: {qualities[p]['t2']*1e6:.1f}us, Readout: {qualities[p]['readout_error']*100:.2f}%)")

if __name__ == "__main__":
    inspect_scores()
