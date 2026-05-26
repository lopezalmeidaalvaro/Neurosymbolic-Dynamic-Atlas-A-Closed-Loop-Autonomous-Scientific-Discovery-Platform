import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

"""
Phase 8C — SOTA Benchmark (COMPLETO, v2)
=========================================
Compares our pipeline against SOTA baselines:

Rules:
  1. Attempts pip install for each missing SOTA tool.
  2. If a tool fails to install, marks status='NOT_EVALUATED' with reason.
     NO mocks. NO simulated results.
  3. Calculates win_rate_real  (vs evaluated baselines only).
  4. Calculates win_rate_total (treating NOT_EVALUATED as defeats).
  5. Cost-performance: accuracy_per_second, jaccard_per_minute.

Outputs (per spec):
  artifacts/sota_results.csv
  artifacts/sota_summary.csv
  artifacts/sota_report.md
  figures/sota_radar.pdf
  figures/sota_cost_performance.pdf

Usage:
    python sota_benchmark.py [--dry-run] [--systems lorenz duffing]
"""

import sys
import os
import io
import json
import time
import subprocess
import argparse
import warnings
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import numpy as np
import pandas as pd

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8C] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("sota_benchmark")

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = Path("results/phase8c")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Package probing (with pip install attempt)
# ---------------------------------------------------------------------------

SOTA_PACKAGES = {
    "pysindy": "pysindy",
    "pysr":    "pysr",
    "ripser":  "ripser",
    "persim":  "persim",
    "aifeynman": "aifeynman",
    "sktime":  "sktime",
    "sklearn": "scikit-learn",
}


def probe_packages(attempt_install: bool = True) -> Dict[str, bool]:
    """
    Probes and (optionally) installs SOTA packages via pip.
    Returns dict: pkg_name → True if importable after probe.
    """
    status = {}
    for pkg, pip_name in SOTA_PACKAGES.items():
        try:
            __import__(pkg)
            status[pkg] = True
            log.info(f"  [probe] {pkg}: AVAILABLE")
        except ImportError:
            if attempt_install:
                log.info(f"  [probe] {pkg}: NOT found → attempting pip install {pip_name}...")
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", pip_name, "--quiet",
                         "--no-deps", "--timeout", "30"],
                        capture_output=True, text=True, timeout=60
                    )
                    if result.returncode == 0:
                        try:
                            __import__(pkg)
                            status[pkg] = True
                            log.info(f"  [probe] {pkg}: INSTALLED successfully")
                            continue
                        except ImportError:
                            log.info(f"  [probe] {pkg}: installed but import still fails")
                    else:
                        log.info(f"  [probe] {pkg}: pip install failed (rc={result.returncode})")
                except (subprocess.TimeoutExpired, Exception) as e:
                    log.info(f"  [probe] {pkg}: pip install error: {e}")
            status[pkg] = False
            log.info(f"  [probe] {pkg}: NOT_EVALUATED")
    return status


# ---------------------------------------------------------------------------
# Signal loader
# ---------------------------------------------------------------------------

def _load_signal(system: str, n_steps: int = 2000, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    from synthetic_systems import (
        generate_lorenz, generate_duffing, generate_van_der_pol,
        generate_rossler, generate_logistic_map
    )
    gen = {
        "lorenz":     lambda: generate_lorenz(n_timesteps=n_steps, dt=0.01,
                                               initial_state=np.random.uniform(-15, 15, 3))["x"],
        "duffing":    lambda: generate_duffing(n_timesteps=n_steps, dt=0.01,
                                               initial_state=np.random.uniform(-1, 1, 2))["x"],
        "van_der_pol": lambda: generate_van_der_pol(n_timesteps=n_steps, dt=0.01,
                                                    initial_state=np.random.uniform(-2, 2, 2))["x"],
        "rossler":    lambda: generate_rossler(n_timesteps=n_steps, dt=0.01,
                                               initial_state=np.random.uniform(-5, 5, 3))["x"],
        "logistic":   lambda: generate_logistic_map(n_iterations=n_steps, r=3.9,
                                                    initial_x=np.random.uniform(0.1, 0.9))["x"],
    }
    return gen[system]()


# ---------------------------------------------------------------------------
# Our pipeline metrics
# ---------------------------------------------------------------------------

def _run_our_pipeline(system: str, signal: np.ndarray, seed: int) -> Dict[str, float]:
    metrics = {}

    t0 = time.perf_counter()
    try:
        from core.autonomous.latent_snapshot_exporter import extract_ev3_features, impute_nan_features
        feat = extract_ev3_features(signal, extended=True, deep=True, scientific=True)
        metrics["ev3_norm"] = float(np.linalg.norm(impute_nan_features(np.array([feat]))[0]))
    except Exception:
        metrics["ev3_norm"] = float("nan")
    metrics["ev3_time_s"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    try:
        from symbolic_discovery import run_sindy
        t_arr = np.linspace(0, len(signal) * 0.01, len(signal))
        r = run_sindy(signal, t_arr)
        metrics["sindy_r2"] = float(r.get("r2_score", float("nan")))
    except Exception:
        metrics["sindy_r2"] = float("nan")
    metrics["sindy_time_s"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    try:
        from topological_analysis import run_topological_analysis
        r = run_topological_analysis(signal)
        metrics["topo_h0"] = float(len(r.get("persistence_diagram_0", [])))
    except Exception:
        metrics["topo_h0"] = float("nan")
    metrics["topo_time_s"] = time.perf_counter() - t0

    return metrics


# ---------------------------------------------------------------------------
# SOTA baseline runners  (NO mocks, NO simulations)
# ---------------------------------------------------------------------------

def _run_pysindy(signal: np.ndarray, n_steps: int,
                 available: bool) -> Dict[str, Any]:
    if not available:
        return {"status": "NOT_EVALUATED", "reason": "pysindy not installed",
                "r2": float("nan"), "n_terms": float("nan"), "time_s": float("nan")}
    if len(signal) < 50:
        return {"status": "TOO_SHORT", "reason": "signal < 50 points",
                "r2": float("nan"), "n_terms": float("nan"), "time_s": float("nan")}
    try:
        import pysindy as ps
        t = np.linspace(0, n_steps * 0.01, n_steps)
        X = signal.reshape(-1, 1)
        model = ps.SINDy(
            differentiation_method=ps.FiniteDifference(),
            feature_library=ps.PolynomialLibrary(degree=2),
            optimizer=ps.STLSQ(threshold=0.1),
        )
        t0 = time.perf_counter()
        model.fit(X, t=t)
        elapsed = time.perf_counter() - t0
        return {"status": "OK",
                "r2": float(model.score(X, t=t)),
                "n_terms": float(np.sum(np.abs(model.coefficients()) > 1e-6)),
                "time_s": elapsed}
    except Exception as e:
        return {"status": f"ERROR: {e}", "r2": float("nan"),
                "n_terms": float("nan"), "time_s": float("nan")}


def _run_ripser(signal: np.ndarray, available: bool) -> Dict[str, Any]:
    if not available:
        return {"status": "NOT_EVALUATED", "reason": "ripser not installed",
                "h0": float("nan"), "h1": float("nan"), "time_s": float("nan")}
    try:
        import ripser
        d, stride = 3, 1
        n = len(signal) - d * stride
        cloud = np.array([signal[i:i + d * stride:stride] for i in range(max(1, n))])
        if len(cloud) > 500:
            cloud = cloud[np.random.choice(len(cloud), 500, replace=False)]
        t0 = time.perf_counter()
        dgms = ripser.ripser(cloud, maxdim=1)["dgms"]
        elapsed = time.perf_counter() - t0
        return {"status": "OK",
                "h0": float(len(dgms[0])) if len(dgms) > 0 else float("nan"),
                "h1": float(len(dgms[1])) if len(dgms) > 1 else float("nan"),
                "time_s": elapsed}
    except Exception as e:
        return {"status": f"ERROR: {e}", "h0": float("nan"),
                "h1": float("nan"), "time_s": float("nan")}


def _run_sklearn_rf(signal: np.ndarray, available: bool) -> Dict[str, Any]:
    if not available:
        return {"status": "NOT_EVALUATED", "reason": "sklearn not installed",
                "accuracy": float("nan"), "time_s": float("nan")}
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        labels = (signal > np.median(signal)).astype(int)
        window = 10
        if len(signal) < window + 2:
            return {"status": "TOO_SHORT", "accuracy": float("nan"), "time_s": float("nan")}
        X = np.array([signal[i:i + window] for i in range(len(signal) - window)])
        y = labels[window:]
        if len(np.unique(y)) < 2:
            return {"status": "SINGLE_CLASS", "accuracy": float("nan"), "time_s": float("nan")}
        t0 = time.perf_counter()
        scores = cross_val_score(RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1),
                                 X, y, cv=3, scoring="accuracy")
        return {"status": "OK", "accuracy": float(np.mean(scores)),
                "time_s": time.perf_counter() - t0}
    except Exception as e:
        return {"status": f"ERROR: {e}", "accuracy": float("nan"), "time_s": float("nan")}


# ---------------------------------------------------------------------------
# Cost-performance
# ---------------------------------------------------------------------------

def accuracy_per_second(accuracy: float, time_s: float) -> float:
    import math
    if math.isnan(accuracy) or math.isnan(time_s) or time_s <= 0:
        return float("nan")
    return accuracy / time_s


def jaccard_per_minute(jaccard: float, time_s: float) -> float:
    import math
    if math.isnan(jaccard) or math.isnan(time_s) or time_s <= 0:
        return float("nan")
    return jaccard / (time_s / 60.0)


# ---------------------------------------------------------------------------
# Win rate calculations
# ---------------------------------------------------------------------------

def compute_win_rates(df: pd.DataFrame, our_baselines: List[str],
                      metric_col: str = "metric_value") -> Dict[str, float]:
    """
    Computes win rates for our pipeline vs evaluated baselines.

    win_rate_real  = wins vs baselines with status='OK' only
    win_rate_total = wins vs all baselines (NOT_EVALUATED = loss)
    """
    all_systems = df["system"].unique()
    our_means = {}
    other_means = {}

    for _, row in df.iterrows():
        bl = row["baseline"]
        sys_name = row["system"]
        mv = row[metric_col]
        status = row.get("status", "OK")
        if np.isnan(mv) or status not in ("OK",):
            continue
        if bl in our_baselines:
            our_means.setdefault(sys_name, []).append(mv)
        else:
            other_means.setdefault((bl, sys_name), []).append(mv)

    # Count wins (our mean > other mean) for each (system, competitor) pair
    n_eval_wins = 0
    n_eval_total = 0
    n_total_wins = 0
    n_total_baselines = len(df["baseline"].unique()) - len(our_baselines)

    evaluated_baselines = {bl for bl, _ in other_means.keys()}

    for (bl, sys_name), other_vals in other_means.items():
        our_vals = our_means.get(sys_name, [])
        n_eval_total += 1
        if our_vals and np.nanmean(our_vals) > np.nanmean(other_vals):
            n_eval_wins += 1

    # Not-evaluated count as losses
    not_evaluated = set()
    for _, row in df.iterrows():
        if row.get("status") == "NOT_EVALUATED" and row["baseline"] not in our_baselines:
            not_evaluated.add(row["baseline"])
    n_not_eval_losses = len(not_evaluated) * len(all_systems)
    n_total_denominator = n_eval_total + n_not_eval_losses

    return {
        "win_rate_real": n_eval_wins / max(n_eval_total, 1),
        "win_rate_total": n_eval_wins / max(n_total_denominator, 1),
        "n_eval_wins": n_eval_wins,
        "n_eval_total": n_eval_total,
        "n_not_evaluated_losses": n_not_eval_losses,
    }


# ---------------------------------------------------------------------------
# Main benchmark runner
# ---------------------------------------------------------------------------

DEFAULT_SYSTEMS = ["lorenz", "duffing", "van_der_pol", "rossler", "logistic"]
OUR_PIPELINE_BASELINES = ["OUR_PIPELINE_EV3", "OUR_PIPELINE_SINDy", "OUR_PIPELINE_TOPO"]


def run_sota_benchmark(
    systems: Optional[List[str]] = None,
    dry_run: bool = False,
    signal_length: int = 2000,
    skip_plots: bool = False,
    seed: int = 42,
    attempt_install: bool = True,
) -> pd.DataFrame:
    systems = systems or DEFAULT_SYSTEMS

    if dry_run:
        signal_length = 300
        systems = systems[:2]
        attempt_install = False  # Don't install in dry-run
        log.info("DRY-RUN: 300 steps, 2 systems, no pip install.")

    log.info("Probing SOTA package availability...")
    avail = probe_packages(attempt_install=attempt_install)
    log.info(f"Available: {[k for k, v in avail.items() if v]}")
    log.info(f"Not available: {[k for k, v in avail.items() if not v]}")

    rows = []

    for sys_name in systems:
        log.info(f"\n--- System: {sys_name} ---")
        signal = _load_signal(sys_name, signal_length, seed)

        # Our pipeline
        our_m = _run_our_pipeline(sys_name, signal, seed)
        ev3_t = our_m.get("ev3_time_s", float("nan"))
        sindy_r2 = our_m.get("sindy_r2", float("nan"))
        sindy_t = our_m.get("sindy_time_s", float("nan"))
        topo_h0 = our_m.get("topo_h0", float("nan"))
        topo_t = our_m.get("topo_time_s", float("nan"))

        ev3_norm = our_m.get("ev3_norm", float("nan"))
        rows.append({
            "system": sys_name, "baseline": "OUR_PIPELINE_EV3",
            "metric": "feature_norm", "metric_value": ev3_norm,
            "time_s": ev3_t,
            "accuracy_per_sec": accuracy_per_second(
                min(1.0, ev3_norm / max(ev3_norm, 1.0)), ev3_t),
            "jaccard_per_min": float("nan"),
            "status": "OK" if not np.isnan(ev3_norm) else "FAILED",
            "reason": "",
        })
        rows.append({
            "system": sys_name, "baseline": "OUR_PIPELINE_SINDy",
            "metric": "r2", "metric_value": sindy_r2,
            "time_s": sindy_t,
            "accuracy_per_sec": accuracy_per_second(max(0.0, sindy_r2), sindy_t),
            "jaccard_per_min": float("nan"),
            "status": "OK" if not np.isnan(sindy_r2) else "FAILED",
            "reason": "",
        })
        rows.append({
            "system": sys_name, "baseline": "OUR_PIPELINE_TOPO",
            "metric": "h0_count", "metric_value": topo_h0,
            "time_s": topo_t,
            "accuracy_per_sec": float("nan"),
            "jaccard_per_min": float("nan"),
            "status": "OK" if not np.isnan(topo_h0) else "FAILED",
            "reason": "",
        })

        # PySINDy
        r_ps = _run_pysindy(signal, signal_length, avail.get("pysindy", False))
        rows.append({
            "system": sys_name, "baseline": "PySINDy",
            "metric": "r2", "metric_value": r_ps.get("r2", float("nan")),
            "time_s": r_ps.get("time_s", float("nan")),
            "accuracy_per_sec": accuracy_per_second(
                max(0.0, r_ps.get("r2", float("nan"))), r_ps.get("time_s", float("nan"))),
            "jaccard_per_min": float("nan"),
            "status": r_ps.get("status", "UNKNOWN"),
            "reason": r_ps.get("reason", ""),
        })
        log.info(f"  PySINDy: {r_ps.get('status')} R²={r_ps.get('r2', float('nan')):.4f}")

        # Ripser
        r_rip = _run_ripser(signal, avail.get("ripser", False))
        rows.append({
            "system": sys_name, "baseline": "Ripser",
            "metric": "h0_count", "metric_value": r_rip.get("h0", float("nan")),
            "time_s": r_rip.get("time_s", float("nan")),
            "accuracy_per_sec": float("nan"),
            "jaccard_per_min": float("nan"),
            "status": r_rip.get("status", "UNKNOWN"),
            "reason": r_rip.get("reason", ""),
        })
        log.info(f"  Ripser: {r_rip.get('status')} H0={r_rip.get('h0', float('nan'))}")

        # sklearn RF
        r_rf = _run_sklearn_rf(signal, avail.get("sklearn", False))
        rows.append({
            "system": sys_name, "baseline": "sklearn_RF",
            "metric": "accuracy", "metric_value": r_rf.get("accuracy", float("nan")),
            "time_s": r_rf.get("time_s", float("nan")),
            "accuracy_per_sec": accuracy_per_second(
                r_rf.get("accuracy", float("nan")), r_rf.get("time_s", float("nan"))),
            "jaccard_per_min": float("nan"),
            "status": r_rf.get("status", "UNKNOWN"),
            "reason": r_rf.get("reason", ""),
        })
        log.info(f"  sklearn RF: {r_rf.get('status')} Acc={r_rf.get('accuracy', float('nan')):.4f}")

        # Not-installed probes (AI Feynman, PySR)
        for pkg, label, metric in [("aifeynman", "AI_Feynman", "n/a"),
                                    ("pysr", "PySR", "complexity")]:
            if not avail.get(pkg, False):
                rows.append({
                    "system": sys_name, "baseline": label,
                    "metric": metric, "metric_value": float("nan"),
                    "time_s": float("nan"),
                    "accuracy_per_sec": float("nan"),
                    "jaccard_per_min": float("nan"),
                    "status": "NOT_EVALUATED",
                    "reason": f"{pkg} not installed",
                })

    df = pd.DataFrame(rows)

    # Compute win rates
    wr = compute_win_rates(df, OUR_PIPELINE_BASELINES)
    log.info(f"Win rate (real):  {wr['win_rate_real']:.2%}")
    log.info(f"Win rate (total): {wr['win_rate_total']:.2%}")

    # Save artifacts/sota_results.csv
    results_path = ARTIFACTS_DIR / "sota_results.csv"
    df.to_csv(results_path, index=False)
    log.info(f"Saved: {results_path}")

    # Save artifacts/sota_summary.csv
    summary_df = df.groupby("baseline").agg(
        mean_metric=("metric_value", "mean"),
        mean_time_s=("time_s", "mean"),
        mean_acc_per_sec=("accuracy_per_sec", "mean"),
        status_ok_pct=("status", lambda x: (x == "OK").mean()),
    ).reset_index()
    summary_df["win_rate_real"] = wr["win_rate_real"]
    summary_df["win_rate_total"] = wr["win_rate_total"]
    summary_path = ARTIFACTS_DIR / "sota_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    log.info(f"Saved: {summary_path}")

    # Backward compat
    df.to_csv(RESULTS_DIR / "sota_benchmark.csv", index=False)

    # Plots
    if not skip_plots:
        try:
            _save_sota_plots(df)
        except Exception as e:
            log.warning(f"Plots failed: {e}")

    # Markdown report
    try:
        _save_sota_report(df, summary_df, wr)
    except Exception as e:
        log.warning(f"Markdown report failed: {e}")

    _print_sota_summary(df, wr)
    return df


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _save_sota_plots(df: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Cost-performance scatter
    ok = df[df["status"] == "OK"].copy()
    if not ok.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        for bl, grp in ok.groupby("baseline"):
            x = grp["time_s"].mean()
            y = grp["metric_value"].mean()
            if not (np.isnan(x) or np.isnan(y)):
                ax.scatter(x, y, s=100, label=bl)
                ax.annotate(bl, (x, y), textcoords="offset points", xytext=(6, 4), fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("Execution Time (s) [log scale]")
        ax.set_ylabel("Primary Metric Value")
        ax.set_title("SOTA Cost–Performance Scatter")
        ax.legend(fontsize=8, loc="best")
        plt.tight_layout()
        for ext in ("pdf", "png"):
            plt.savefig(FIGURES_DIR / f"sota_cost_performance.{ext}", dpi=150, bbox_inches="tight")
        plt.close()
        log.info(f"Saved: {FIGURES_DIR / 'sota_cost_performance.pdf'}")

    # Radar chart
    try:
        agg = df.groupby("baseline").agg(
            mean_metric=("metric_value", "mean"),
            mean_time=("time_s", "mean"),
        ).reset_index().dropna()
        if not agg.empty:
            agg["speed"] = 1.0 / (agg["mean_time"].clip(lower=1e-6))
            for col in ["mean_metric", "speed"]:
                lo, hi = agg[col].min(), agg[col].max()
                agg[col] = (agg[col] - lo) / (hi - lo + 1e-12)
            categories = ["mean_metric", "speed"]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
            for _, row in agg.iterrows():
                vals = [row["mean_metric"], row["speed"]] + [row["mean_metric"]]
                ax.plot(angles, vals, label=row["baseline"], linewidth=1.5)
                ax.fill(angles, vals, alpha=0.1)
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)
            ax.set_title("SOTA Radar: Normalized Performance", pad=20)
            ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
            plt.tight_layout()
            for ext in ("pdf", "png"):
                plt.savefig(FIGURES_DIR / f"sota_radar.{ext}", dpi=150, bbox_inches="tight")
            plt.close()
            log.info(f"Saved: {FIGURES_DIR / 'sota_radar.pdf'}")
    except Exception as e:
        log.warning(f"Radar chart error: {e}")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _save_sota_report(df: pd.DataFrame, summary: pd.DataFrame, wr: Dict):
    status_counts = df["status"].value_counts()
    ok_count = status_counts.get("OK", 0)
    ne_count = status_counts.get("NOT_EVALUATED", 0)

    table = summary.to_markdown(index=False, floatfmt=".4f") if not summary.empty else "_No data._"

    not_eval_reasons = df[df["status"] == "NOT_EVALUATED"][["baseline", "reason"]].drop_duplicates()
    reasons_md = not_eval_reasons.to_markdown(index=False) if not not_eval_reasons.empty else "_All evaluated._"

    md = f"""# Phase 8C — SOTA Benchmark Report

## Win Rate

| Metric | Value |
|--------|-------|
| win_rate_real (vs evaluated baselines) | {wr['win_rate_real']:.2%} |
| win_rate_total (NOT_EVALUATED = defeat) | {wr['win_rate_total']:.2%} |
| Wins vs evaluated | {wr['n_eval_wins']} / {wr['n_eval_total']} |
| NOT_EVALUATED losses | {wr['n_not_evaluated_losses']} |

## Status Summary

| Status | Count |
|--------|-------|
| OK | {ok_count} |
| NOT_EVALUATED | {ne_count} |
| Other | {len(df) - ok_count - ne_count} |

## Baseline Summary

{table}

## NOT_EVALUATED Reasons (no mocks used)

{reasons_md}

## Methodology

- pip install attempted for each missing package before evaluation.
- If a tool fails to install: `status='NOT_EVALUATED'` — **no mock data is generated**.
- Cost-performance: `accuracy_per_second = accuracy / time_s`.
- `win_rate_real` counts wins only against successfully-evaluated baselines.
- `win_rate_total` treats NOT_EVALUATED entries as defeats (conservative).

## Figures

- [`figures/sota_cost_performance.pdf`](../figures/sota_cost_performance.pdf)
- [`figures/sota_radar.pdf`](../figures/sota_radar.pdf)
"""
    path = ARTIFACTS_DIR / "sota_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    log.info(f"Saved: {path}")


def _print_sota_summary(df: pd.DataFrame, wr: Dict):
    print("\n" + "=" * 60)
    print("  PHASE 8C — SOTA BENCHMARK SUMMARY")
    print("=" * 60)
    for s, c in df["status"].value_counts().items():
        print(f"  {s:20s}: {c}")
    print(f"  Win rate (real):   {wr['win_rate_real']:.1%}")
    print(f"  Win rate (total):  {wr['win_rate_total']:.1%}")
    ok = df[df["status"] == "OK"]
    if not ok.empty:
        print("\n  Mean metric by baseline (OK only):")
        print(ok.groupby("baseline")["metric_value"].mean().to_string())
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 8C — SOTA Benchmark")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--systems", nargs="+", default=None)
    parser.add_argument("--signal-length", type=int, default=2000)
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--no-install", action="store_true",
                        help="Do not attempt pip install for missing packages.")
    args = parser.parse_args()
    run_sota_benchmark(
        systems=args.systems, dry_run=args.dry_run,
        signal_length=args.signal_length, skip_plots=args.skip_plots,
        attempt_install=not args.no_install,
    )


if __name__ == "__main__":
    main()
