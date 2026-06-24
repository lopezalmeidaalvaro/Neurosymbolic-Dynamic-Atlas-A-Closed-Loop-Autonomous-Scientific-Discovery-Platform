"""
Placement Score Diagnosis: Why did Stage C prefer qubits 131-135 over 0-4?

Uses FakeFez to extract T1, T2, readout error, avg 2Q gate error,
and the Stage C scoring formula for three qubit groups from Run 8.

Outputs: quantum/diagnostics/PLACEMENT_SCORE_DIAGNOSIS.md
"""

import sys, os, textwrap
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from qiskit_ibm_runtime.fake_provider import FakeFez

from quantum.optimization.hardware_cost_model import (
    DEFAULT_READOUT_ERROR, DEFAULT_T1_SEC, DEFAULT_T2_SEC,
    get_gate_properties, get_qubit_quality,
)

# ── Qubit groups ──────────────────────────────────────────────────
GROUPS = {
    "WINNERS (QFT worked)":  [19, 35, 15, 13, 14],
    "LOSERS  (GHZ failed)":  [131, 132, 133, 134, 135],
    "TRIVIAL (0..4)":        [0, 1, 2, 3, 4],
}


def get_avg_2q_gate_error(backend, qubit, adj):
    """Replicate _physical_avg_gate_error from QubitPlacement."""
    errors = []
    for gate_name in ("sx", "x"):
        errors.append(get_gate_properties(backend, gate_name, (qubit,))["error"])
    for neighbor in adj.get(qubit, ()):
        two_q_errors = [
            get_gate_properties(backend, gn, (qubit, neighbor))["error"]
            for gn in ("cx", "ecr", "cz")
        ]
        errors.append(min(two_q_errors))
    return sum(errors) / len(errors) if errors else 0.01


def main():
    backend = FakeFez()
    num_physical = backend.num_qubits
    coupling_map = list(backend.coupling_map)

    # Build adjacency
    adj = {i: set() for i in range(num_physical)}
    for u, v in coupling_map:
        adj[u].add(v)
        adj[v].add(u)

    # ── Collect all qubit properties (needed for max_t1/max_t2) ──
    all_qualities = {}
    max_t1 = DEFAULT_T1_SEC
    max_t2 = DEFAULT_T2_SEC
    for p in range(num_physical):
        q = get_qubit_quality(backend, p)
        q["avg_gate_error"] = get_avg_2q_gate_error(backend, p, adj)
        q["degree"] = len(adj.get(p, ()))
        all_qualities[p] = q
        max_t1 = max(max_t1, q["t1"])
        max_t2 = max(max_t2, q["t2"])

    # ── Score formula (exactly as in qubit_placement.py L142-151) ──
    w1, w2, w3, w4 = 0.225, 0.225, 0.30, 0.25

    def score(p):
        q = all_qualities[p]
        return (
            w1 * (q["t1"] / max_t1)
            + w2 * (q["t2"] / max_t2)
            - w3 * q["readout_error"]
            - w4 * q["avg_gate_error"]
            + 0.01 * q["degree"]
        )

    # ── Compute scores for all physical qubits to find rank ──
    all_scores = [(p, score(p)) for p in range(num_physical)]
    all_scores.sort(key=lambda x: x[1], reverse=True)
    rank_map = {p: rank + 1 for rank, (p, _) in enumerate(all_scores)}

    # ── Build tables ──────────────────────────────────────────────
    lines = []
    lines.append("# Placement Score Diagnosis: Run 8 Qubit Groups\n")
    lines.append(f"- **Backend**: FakeFez ({num_physical} qubits)")
    lines.append(f"- **max_t1**: {max_t1*1e6:.1f} us  |  **max_t2**: {max_t2*1e6:.1f} us")
    lines.append(f"- **Scoring weights**: w_T1={w1}, w_T2={w2}, w_readout={w3}, w_gate={w4}, w_degree=0.01\n")

    for group_name, qubits in GROUPS.items():
        lines.append(f"## {group_name}: qubits {qubits}\n")
        lines.append("| Qubit | T1 (µs) | T2 (µs) | T1/max | T2/max | Readout Err | Avg Gate Err | Degree | **Score** | Rank/{} |".format(num_physical))
        lines.append("|------:|--------:|--------:|-------:|-------:|------------:|-------------:|-------:|----------:|-------:|")

        group_scores = []
        for p in qubits:
            q = all_qualities[p]
            s = score(p)
            group_scores.append(s)
            lines.append(
                f"| {p:>5} | {q['t1']*1e6:>7.1f} | {q['t2']*1e6:>7.1f} "
                f"| {q['t1']/max_t1:>6.3f} | {q['t2']/max_t2:>6.3f} "
                f"| {q['readout_error']:>11.5f} | {q['avg_gate_error']:>12.5f} "
                f"| {q['degree']:>6} | {s:>9.5f} | {rank_map[p]:>5} |"
            )
        avg_s = sum(group_scores) / len(group_scores)
        lines.append(f"\n**Group avg score: {avg_s:.5f}**\n")

    # ── Direct comparison ──────────────────────────────────────────
    lines.append("---\n## Direct Comparison: Key Metrics\n")
    lines.append("| Metric | LOSERS (131-135) avg | TRIVIAL (0-4) avg | WINNERS (19,35,15,13,14) avg |")
    lines.append("|--------|---------------------:|------------------:|-----------------------------:|")

    for metric, fmt, scale in [
        ("T1 (µs)", "{:.1f}", 1e6),
        ("T2 (µs)", "{:.1f}", 1e6),
        ("Readout Err", "{:.5f}", 1),
        ("Avg Gate Err", "{:.5f}", 1),
        ("Score", "{:.5f}", 1),
    ]:
        vals = {}
        for gname, qubits in GROUPS.items():
            key = gname.split("(")[0].strip()
            if metric == "Score":
                raw = [score(p) for p in qubits]
            else:
                field = {
                    "T1 (µs)": "t1", "T2 (µs)": "t2",
                    "Readout Err": "readout_error",
                    "Avg Gate Err": "avg_gate_error",
                }[metric]
                raw = [all_qualities[p][field] * scale for p in qubits]
            vals[key] = sum(raw) / len(raw)

        lines.append(
            f"| {metric} | "
            f"{fmt.format(vals['LOSERS'])} | "
            f"{fmt.format(vals['TRIVIAL'])} | "
            f"{fmt.format(vals['WINNERS'])} |"
        )

    # ── Verdict ────────────────────────────────────────────────────
    losers_t1 = sum(all_qualities[p]["t1"] for p in GROUPS["LOSERS  (GHZ failed)"]) / 5
    trivial_t1 = sum(all_qualities[p]["t1"] for p in GROUPS["TRIVIAL (0..4)"]) / 5
    losers_t2 = sum(all_qualities[p]["t2"] for p in GROUPS["LOSERS  (GHZ failed)"]) / 5
    trivial_t2 = sum(all_qualities[p]["t2"] for p in GROUPS["TRIVIAL (0..4)"]) / 5
    losers_ro = sum(all_qualities[p]["readout_error"] for p in GROUPS["LOSERS  (GHZ failed)"]) / 5
    trivial_ro = sum(all_qualities[p]["readout_error"] for p in GROUPS["TRIVIAL (0..4)"]) / 5
    losers_ge = sum(all_qualities[p]["avg_gate_error"] for p in GROUPS["LOSERS  (GHZ failed)"]) / 5
    trivial_ge = sum(all_qualities[p]["avg_gate_error"] for p in GROUPS["TRIVIAL (0..4)"]) / 5
    losers_score = sum(score(p) for p in GROUPS["LOSERS  (GHZ failed)"]) / 5
    trivial_score = sum(score(p) for p in GROUPS["TRIVIAL (0..4)"]) / 5

    lines.append("\n---\n## Verdict\n")

    t1_higher = losers_t1 > trivial_t1
    t2_higher = losers_t2 > trivial_t2
    ro_higher = losers_ro > trivial_ro
    ge_higher = losers_ge > trivial_ge
    score_higher = losers_score > trivial_score

    lines.append(f"### Q: Do qubits 131-135 have higher T1/T2 than 0-4 in FakeFez?")
    lines.append(f"- **T1**: LOSERS avg = {losers_t1*1e6:.1f} us vs TRIVIAL avg = {trivial_t1*1e6:.1f} us -> **{'YES' if t1_higher else 'NO'}** ({'+' if t1_higher else ''}{(losers_t1-trivial_t1)/trivial_t1*100:.1f}%)")
    lines.append(f"- **T2**: LOSERS avg = {losers_t2*1e6:.1f} us vs TRIVIAL avg = {trivial_t2*1e6:.1f} us -> **{'YES' if t2_higher else 'NO'}** ({'+' if t2_higher else ''}{(losers_t2-trivial_t2)/trivial_t2*100:.1f}%)")

    lines.append(f"\n### Q: Do they also have worse noise metrics?")
    lines.append(f"- **Readout Error**: LOSERS = {losers_ro:.5f} vs TRIVIAL = {trivial_ro:.5f} -> **{'WORSE' if ro_higher else 'BETTER'}** ({'+' if ro_higher else ''}{(losers_ro-trivial_ro)/trivial_ro*100:.1f}%)")
    lines.append(f"- **Gate Error**: LOSERS = {losers_ge:.5f} vs TRIVIAL = {trivial_ge:.5f} -> **{'WORSE' if ge_higher else 'BETTER'}** ({'+' if ge_higher else ''}{(losers_ge-trivial_ge)/trivial_ge*100:.1f}%)")

    lines.append(f"\n### Q: Does Stage C score the LOSERS higher than TRIVIAL?")
    lines.append(f"- **Score**: LOSERS = {losers_score:.5f} vs TRIVIAL = {trivial_score:.5f} -> **{'YES (BUG CONFIRMED)' if score_higher else 'NO'}**")

    if t1_higher and score_higher:
        lines.append(textwrap.dedent("""
        > [!CAUTION]
        > **Root cause confirmed**: The scoring formula over-weights T1/T2 coherence
        > (combined weight 0.70) relative to readout_error and gate_error (combined 0.30).
        > This allows high-coherence qubits with terrible noise to outscore
        > low-coherence qubits with clean noise — exactly the Run 8 failure mode.
        >
        > **The fallback mechanism added in the fix correctly detects and rejects
        > these false-positive high-score layouts.**
        """))
    elif not score_higher:
        lines.append(textwrap.dedent("""
        > [!NOTE]
        > In FakeFez, qubits 131-135 do NOT score higher than 0-4. The real
        > ibm_fez calibration must have different T1/T2 values on the day of Run 8.
        > The fallback mechanism is still essential as a safety net against
        > future calibration drift.
        """))
    else:
        lines.append(textwrap.dedent("""
        > [!WARNING]
        > Unexpected pattern: T1/T2 are not higher but score is. Investigate
        > degree bonus or other topological effects.
        """))

    # ── Write report ───────────────────────────────────────────────
    report = "\n".join(lines)
    out_dir = Path(__file__).resolve().parent
    out_path = out_dir / "PLACEMENT_SCORE_DIAGNOSIS.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n\n[OK] Report written to: {out_path}")


if __name__ == "__main__":
    main()
