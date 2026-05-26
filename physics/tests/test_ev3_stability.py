import os
import sys
import numpy as np

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure we can import neurosymbolic
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from neurosymbolic.metrics.ev3 import compute_stable_ev3

def main():
    print("=" * 60)
    print("🧪 RUNNING STABLE EV3 NUMERICAL STABILITY VERIFICATION")
    print("=" * 60)

    np.random.seed(42)
    dimensions = [10, 50, 100, 200]
    n_samples = 150

    log_lines = []
    log_lines.append("=" * 60)
    log_lines.append("🧪 EV3 STABILITY VERIFICATION REPORT")
    log_lines.append("=" * 60)

    for d in dimensions:
        # Generate random embeddings from normal distribution
        # Covariance will be identity, so the singular values should be close to sqrt(N)
        embeddings = np.random.normal(0, 1.0, (n_samples, d))
        
        # Calculate stable EV3
        ev3_val = compute_stable_ev3(embeddings)
        
        line = f"Dimension D = {d:3d} | Matrix Shape: {n_samples}x{d} | Stable EV3 = {ev3_val:.6f}"
        print(line)
        log_lines.append(line)

    # Test near-collapsed representations (nearly redundant features)
    print("\nTesting near-collapsed representations...")
    log_lines.append("\nTesting near-collapsed representations...")
    embeddings_collapsed = np.random.normal(0, 1.0, (n_samples, 50))
    # Map all dimensions past 5 to be redundant
    for i in range(5, 50):
        embeddings_collapsed[:, i] = embeddings_collapsed[:, 0] * 0.1 + np.random.normal(0, 1e-12, n_samples)
        
    ev3_collapsed = compute_stable_ev3(embeddings_collapsed)
    line_coll = f"Redundant/Collapsed (50D, effective 5D) | Stable EV3 = {ev3_collapsed:.6f}"
    print(line_coll)
    log_lines.append(line_coll)

    # Save to experiments/ev3_stability.txt
    os.makedirs("experiments", exist_ok=True)
    report_path = "experiments/ev3_stability.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
        
    print(f"\n✅ EV3 stability report saved successfully to {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
