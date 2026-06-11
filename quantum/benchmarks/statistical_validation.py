import os
import sys
import math
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def cliffs_delta(x: List[float], y: List[float]) -> float:
    """
    Computes Cliff's delta effect size between two groups using fast binary search.
    """
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    n1 = len(x_arr)
    n2 = len(y_arr)
    if n1 == 0 or n2 == 0:
        return 0.0
    
    y_sorted = np.sort(y_arr)
    # searchsorted returns insertion index to maintain order.
    # index of first element >= val
    left = np.searchsorted(y_sorted, x_arr, side='left')
    # index of first element > val
    right = np.searchsorted(y_sorted, x_arr, side='right')
    
    greater = np.sum(left)
    less = np.sum(n2 - right)
    
    return float(greater - less) / (n1 * n2)

def bootstrap_ci(data: List[float], confidence: float = 0.95, num_resamples: int = 1000) -> Tuple[float, float]:
    """
    Computes bootstrap confidence intervals for the mean.
    """
    if len(data) == 0:
        return (0.0, 0.0)
    resamples = []
    # Seed for reproducibility
    rng = np.random.default_rng(42)
    for _ in range(num_resamples):
        sample = rng.choice(data, size=len(data), replace=True)
        resamples.append(np.mean(sample))
    
    alpha = 1.0 - confidence
    lower = np.percentile(resamples, (alpha / 2.0) * 100)
    upper = np.percentile(resamples, (1.0 - alpha / 2.0) * 100)
    return (float(lower), float(upper))

def perform_mwu_test(x: List[float], y: List[float]) -> float:
    """
    Performs Mann-Whitney U test between two groups.
    """
    if len(x) == 0 or len(y) == 0:
        return 1.0
    try:
        stat, p_val = mannwhitneyu(x, y, alternative='two-sided')
        return float(p_val)
    except Exception:
        return 1.0

def win_rate_ci(wins: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Computes Wilson score interval for binomial proportion (win rate).
    """
    if total == 0:
        return (0.0, 0.0)
    p = wins / total
    # 95% confidence corresponds to z = 1.96
    z = 1.96 if confidence == 0.95 else 2.58
    denom = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    spread = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))
    lower = max(0.0, (center - spread) / denom)
    upper = min(1.0, (center + spread) / denom)
    return (lower, upper)

def run_statistical_validation(csv_path: str) -> Dict[str, Any]:
    """
    Reads the benchmark CSV results and runs statistical significance tests.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV path {csv_path} does not exist.")
        return {}

    df = pd.read_csv(csv_path)
    # Filter out NOT_AVAILABLE rows
    df = df[df["depth"] != "NOT_AVAILABLE"]
    df["depth"] = pd.to_numeric(df["depth"])
    df["gate_count"] = pd.to_numeric(df["gate_count"])
    df["fidelity"] = pd.to_numeric(df["fidelity"])
    df["compile_time"] = pd.to_numeric(df["compile_time"])

    workflows = df["workflow"].unique()
    qiskit_runs = df[df["workflow"] == "Qiskit"]

    validation_report = {}

    for w in workflows:
        if w == "Qiskit":
            continue

        w_runs = df[df["workflow"] == w]
        n_runs = len(w_runs)
        
        # Compare fidelity
        q_fid = qiskit_runs["fidelity"].tolist()
        w_fid = w_runs["fidelity"].tolist()

        p_val_fid = perform_mwu_test(w_fid, q_fid)
        delta_fid = cliffs_delta(w_fid, q_fid)
        ci_fid = bootstrap_ci(w_fid)

        # Compare gate count
        q_gates = qiskit_runs["gate_count"].tolist()
        w_gates = w_runs["gate_count"].tolist()
        
        p_val_gates = perform_mwu_test(w_gates, q_gates)
        delta_gates = cliffs_delta(w_gates, q_gates)
        ci_gates = bootstrap_ci(w_gates)

        validation_report[w] = {
            "n_samples": n_runs,
            "fidelity": {
                "mean": float(np.mean(w_fid)) if w_fid else 0.0,
                "median": float(np.median(w_fid)) if w_fid else 0.0,
                "std": float(np.std(w_fid)) if w_fid else 0.0,
                "ci_95": ci_fid,
                "p_value_vs_qiskit": p_val_fid,
                "effect_size_cliffs_delta": delta_fid
            },
            "gates": {
                "mean": float(np.mean(w_gates)) if w_gates else 0.0,
                "median": float(np.median(w_gates)) if w_gates else 0.0,
                "std": float(np.std(w_gates)) if w_gates else 0.0,
                "ci_95": ci_gates,
                "p_value_vs_qiskit": p_val_gates,
                "effect_size_cliffs_delta": delta_gates
            }
        }

    # Generate report
    generate_validation_markdown(validation_report)
    return validation_report

def generate_validation_markdown(report: Dict[str, Any]):
    lines = [
        "# Statistical Validation Report",
        "",
        "This report evaluates the statistical significance of QADE compiling performance compared to Qiskit L3.",
        "",
        "## 1. Statistical Significance Table (Fidelity)",
        "",
        "| Compiler Workflow | N | Mean Fidelity | Median Fidelity | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |"
    ]

    insufficient_power_lines = []

    for w, metrics in report.items():
        fid = metrics["fidelity"]
        p_val = fid["p_value_vs_qiskit"]
        n = metrics["n_samples"]
        
        sig = "Significativo (p < 0.05)" if p_val < 0.05 else "No Significativo"
        ci_str = f"[{fid['ci_95'][0]:.4f}, {fid['ci_95'][1]:.4f}]"

        lines.append(
            f"| **{w}** | {n} | {fid['mean']:.4f} | {fid['median']:.4f} | {ci_str} | {p_val:.4e} | {fid['effect_size_cliffs_delta']:.4f} | {sig} |"
        )

        if n < 30:
            insufficient_power_lines.append(
                f"- **{w}**: n={n} (Below the minimum threshold of 30 runs per configuration)"
            )

    lines.extend([
        "",
        "## 2. Statistical Significance Table (Gate Count)",
        "",
        "| Compiler Workflow | N | Mean Gates | Median Gates | 95% Confidence Interval | p-value vs Qiskit L3 | Cliff's Delta | Significance |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |"
    ])

    for w, metrics in report.items():
        gates = metrics["gates"]
        p_val = gates["p_value_vs_qiskit"]
        n = metrics["n_samples"]
        
        sig = "Significativo (p < 0.05)" if p_val < 0.05 else "No Significativo"
        ci_str = f"[{gates['ci_95'][0]:.1f}, {gates['ci_95'][1]:.1f}]"

        lines.append(
            f"| **{w}** | {n} | {gates['mean']:.1f} | {gates['median']:.1f} | {ci_str} | {p_val:.4e} | {gates['effect_size_cliffs_delta']:.4f} | {sig} |"
        )

    lines.extend([
        "",
        "## 3. Results with Insufficient Statistical Power",
        ""
    ])

    if insufficient_power_lines:
        lines.extend(insufficient_power_lines)
    else:
        lines.append("No workflows have insufficient statistical power in this test (all n >= 30).")

    report_path = Path("benchmarks/reports/STATISTICAL_VALIDATION_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Statistical validation report saved to benchmarks/reports/STATISTICAL_VALIDATION_REPORT.md")

if __name__ == "__main__":
    run_statistical_validation("docs/ALL_COMPILERS_BENCHMARK_RESULTS.csv")
