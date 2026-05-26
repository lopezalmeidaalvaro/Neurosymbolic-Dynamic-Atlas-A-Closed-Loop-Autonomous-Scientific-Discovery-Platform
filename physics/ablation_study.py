import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

"""
Phase 8B — Ablation Study (COMPLETO, v2)
=========================================
Systematically disables pipeline components and measures degradation:

  - Dependency DAG (interno): cascade-disable downstream dependents
  - Fallback AR(p) para módulos dependientes ausentes (status='DEPENDENCY_BYPASS')
  - Δ% = (base - ablated) / base × 100
  - Cohen's d con pooled std
  - Bootstrap CI95 para Δ% (1000 remuestreos, BCa)
  - Outputs:
      artifacts/ablation_results.csv   (todas las filas)
      artifacts/ablation_summary.csv   (columnas: module_removed, delta_pct,
                                         cohens_d, ci95_lower, ci95_upper, interpretation)
      artifacts/ablation_report.md
      figures/ablation_heatmap.pdf

Usage:
    python ablation_study.py [--dry-run] [--systems lorenz] [--skip-heatmap]
"""

import sys
import os
import io
import json
import time
import argparse
import warnings
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from scipy.stats import bootstrap as scipy_bootstrap

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8B] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("ablation_study")

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = Path("results/phase8b")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Module dependency DAG
# { module: [downstream_dependents] }
# ---------------------------------------------------------------------------
MODULE_DAG: Dict[str, List[str]] = {
    "EV3":       ["EV3_EXT", "EV3_DEEP", "EV3_SCI", "SINDy", "Topology", "Koopman"],
    "EV3_EXT":   ["EV3_DEEP", "EV3_SCI"],
    "EV3_DEEP":  ["EV3_SCI"],
    "EV3_SCI":   [],
    "SINDy":     [],
    "PySR":      [],
    "Topology":  ["Koopman"],
    "Koopman":   [],
    "NeuralODE": [],
    "PINN":      [],
}

# Ablation configurations: name → set of DISABLED modules (before cascade)
ABLATION_CONFIGS: Dict[str, set] = {
    "BASELINE_FULL":        set(),
    "NO_TDA":               {"Topology"},
    "NO_KOOPMAN":           {"Koopman"},
    "NO_GEOMETRY":          {"Topology", "Koopman"},
    "NO_SINDY":             {"SINDy"},
    "NO_PYSR":              {"PySR"},
    "NO_PINN":              {"PINN"},
    "NO_NEURAL_ODE":        {"NeuralODE"},
    "NO_TOPOLOGY_GEOMETRY": {"Topology", "Koopman"},
}


def resolve_disabled_modules(disabled: set) -> set:
    """Cascade-disable all downstream dependents via BFS on MODULE_DAG."""
    expanded = set(disabled)
    changed = True
    while changed:
        changed = False
        for mod in list(expanded):
            for dep in MODULE_DAG.get(mod, []):
                if dep not in expanded:
                    expanded.add(dep)
                    changed = True
    return expanded


# ---------------------------------------------------------------------------
# AR(p) fallback metric
# ---------------------------------------------------------------------------

def _ar_fallback_metric(signal: np.ndarray, p: int = 3) -> float:
    """
    Fallback metric: AR(p) model AIC. Used when a module dependency is bypassed.
    Marks the evaluation as DEPENDENCY_BYPASS.
    """
    n = len(signal)
    if n < p + 2:
        return float("nan")
    try:
        # Build Yule-Walker system
        r = np.array([np.correlate(signal - signal.mean(),
                                   np.roll(signal - signal.mean(), k))[0] / n
                      for k in range(p + 1)])
        R = np.array([[r[abs(i - j)] for j in range(p)] for i in range(p)])
        rhs = r[1:p + 1]
        coeffs = np.linalg.solve(R, rhs)
        pred = np.array([np.dot(coeffs, signal[i:i+p][::-1]) for i in range(p, n)])
        residual_var = float(np.var(signal[p:] - pred))
        aic = n * np.log(residual_var + 1e-12) + 2 * p
        return float(aic)
    except Exception:
        return float("nan")


# ---------------------------------------------------------------------------
# Module evaluator
# ---------------------------------------------------------------------------

def _evaluate_module(module: str, signal: np.ndarray, seed: int,
                     disabled: set) -> Tuple[float, str]:
    """
    Returns (metric_value, status).
    status = 'OK' | 'DISABLED' | 'DEPENDENCY_BYPASS' | 'ERROR'
    """
    if module in disabled:
        return float("nan"), "DISABLED"

    np.random.seed(seed)
    try:
        if module in ("EV3", "EV3_EXT", "EV3_DEEP", "EV3_SCI"):
            from core.autonomous.latent_snapshot_exporter import extract_ev3_features, impute_nan_features
            feat = extract_ev3_features(
                signal,
                extended=module in ("EV3_EXT", "EV3_DEEP", "EV3_SCI"),
                deep=module in ("EV3_DEEP", "EV3_SCI"),
                scientific=(module == "EV3_SCI"),
            )
            return float(np.linalg.norm(impute_nan_features(np.array([feat]))[0])), "OK"

        elif module == "SINDy":
            from symbolic_discovery import run_sindy
            t = np.linspace(0, len(signal) * 0.01, len(signal))
            return float(run_sindy(signal, t).get("n_active_terms", 0)), "OK"

        elif module == "PySR":
            try:
                from symbolic_discovery import run_pysr
                t = np.linspace(0, len(signal) * 0.01, len(signal))
                result = run_pysr(signal, t)
                return float(result.get("best_complexity", float("nan"))), "OK"
            except Exception:
                # PySR not available → AR fallback
                return _ar_fallback_metric(signal), "DEPENDENCY_BYPASS"

        elif module == "Topology":
            from topological_analysis import run_topological_analysis
            return float(len(run_topological_analysis(signal).get("persistence_diagram_0", []))), "OK"

        elif module == "Koopman":
            # Check if Topology (dependency) was disabled
            if "Topology" in disabled:
                return _ar_fallback_metric(signal), "DEPENDENCY_BYPASS"
            from koopman_analysis import run_koopman_analysis
            eigs = run_koopman_analysis(signal).get("eigenvalues", [1.0])
            return float(np.abs(np.array(eigs)).max()) if eigs else float("nan"), "OK"

        elif module == "NeuralODE":
            from neural_ode_module import run_neural_ode
            r = run_neural_ode(signal, n_epochs=20, seed=seed)
            return float(r.get("final_loss", float("nan"))), "OK"

        elif module == "PINN":
            from pinn_module import run_pinn_forward
            r = run_pinn_forward(signal, n_epochs=20, seed=seed)
            return float(r.get("final_loss", float("nan"))), "OK"

    except Exception as e:
        log.debug(f"Module {module} error: {e}")
    return float("nan"), "ERROR"


def _load_signal(system: str, n_steps: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    from synthetic_systems import (
        generate_lorenz, generate_duffing, generate_van_der_pol,
        generate_rossler, generate_logistic_map
    )
    gen = {
        "lorenz":      lambda: generate_lorenz(n_timesteps=n_steps, dt=0.01,
                                                initial_state=np.random.uniform(-15, 15, 3))["x"],
        "duffing":     lambda: generate_duffing(n_timesteps=n_steps, dt=0.01,
                                                 initial_state=np.random.uniform(-1, 1, 2))["x"],
        "van_der_pol": lambda: generate_van_der_pol(n_timesteps=n_steps, dt=0.01,
                                                     initial_state=np.random.uniform(-2, 2, 2))["x"],
        "rossler":     lambda: generate_rossler(n_timesteps=n_steps, dt=0.01,
                                                initial_state=np.random.uniform(-5, 5, 3))["x"],
        "logistic":    lambda: generate_logistic_map(n_iterations=n_steps, r=3.9,
                                                     initial_x=np.random.uniform(0.1, 0.9))["x"],
        "ECG200":      lambda: _load_ecg("ECG200", n_steps, seed),
        "ECG5000":     lambda: _load_ecg("ECG5000", n_steps, seed),
    }
    return gen[system]()


def _load_ecg(name: str, n_steps: int, seed: int) -> np.ndarray:
    from ucr_loader import load_ucr_dataset
    data = load_ucr_dataset(name)
    rng = np.random.RandomState(seed)
    return data["X_train"][rng.randint(0, len(data["X_train"]))]


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def cohens_d(base: np.ndarray, ablated: np.ndarray) -> float:
    """Pooled Cohen's d = (mu_base - mu_ablated) / sigma_pooled."""
    b = base[~np.isnan(base)]
    a = ablated[~np.isnan(ablated)]
    if len(b) < 2 or len(a) < 2:
        return float("nan")
    n_b, n_a = len(b), len(a)
    s_b = float(np.std(b, ddof=1))
    s_a = float(np.std(a, ddof=1))
    sp = np.sqrt(((n_b - 1) * s_b**2 + (n_a - 1) * s_a**2) / (n_b + n_a - 2))
    return 0.0 if sp < 1e-12 else float((np.mean(b) - np.mean(a)) / sp)


def delta_percent(base_mean: float, ablated_mean: float) -> float:
    """Δ% = (base - ablated) / base × 100."""
    if abs(base_mean) < 1e-12 or np.isnan(base_mean):
        return float("nan")
    return float((base_mean - ablated_mean) / abs(base_mean) * 100)


def bca_delta_ci(base: np.ndarray, ablated: np.ndarray,
                 n_resamples: int = 1000) -> Tuple[float, float]:
    """BCa CI95 of Δ% via paired bootstrap."""
    b = base[~np.isnan(base)]
    a = ablated[~np.isnan(ablated)]
    if len(b) < 2 or len(a) < 2:
        return float("nan"), float("nan")

    def delta_stat(x, y):
        mu_x, mu_y = np.mean(x), np.mean(y)
        return (mu_x - mu_y) / abs(mu_x) * 100 if abs(mu_x) > 1e-12 else np.nan

    try:
        res = scipy_bootstrap((b, a), statistic=delta_stat,
                              n_resamples=n_resamples, confidence_level=0.95,
                              method="BCa", random_state=42)
        return float(res.confidence_interval.low), float(res.confidence_interval.high)
    except Exception:
        return float("nan"), float("nan")


def classify_impact(d: float) -> str:
    if np.isnan(d):
        return "N/A"
    ad = abs(d)
    return "Negligible" if ad < 0.2 else "Small" if ad < 0.5 else "Medium" if ad < 0.8 else "Large"


# ---------------------------------------------------------------------------
# Main ablation runner
# ---------------------------------------------------------------------------

DEFAULT_SYSTEMS = ["lorenz", "duffing", "van_der_pol", "rossler", "logistic", "ECG200", "ECG5000"]
DEFAULT_MODULES = ["EV3", "EV3_EXT", "EV3_DEEP", "EV3_SCI", "SINDy", "PySR",
                   "Topology", "Koopman", "NeuralODE", "PINN"]
DEFAULT_SEEDS = [0, 1, 2, 3, 4]


def run_ablation_study(
    systems: Optional[List[str]] = None,
    modules: Optional[List[str]] = None,
    ablation_configs: Optional[Dict[str, set]] = None,
    seeds: Optional[List[int]] = None,
    dry_run: bool = False,
    n_resamples: int = 1000,
    signal_length: int = 1000,
    skip_heatmap: bool = False,
) -> pd.DataFrame:
    """
    Full ablation study. Saves:
      artifacts/ablation_results.csv
      artifacts/ablation_summary.csv
      artifacts/ablation_report.md
      figures/ablation_heatmap.pdf
    """
    systems = systems or DEFAULT_SYSTEMS
    modules = modules or DEFAULT_MODULES
    ablation_configs = ablation_configs or ABLATION_CONFIGS
    seeds = seeds or DEFAULT_SEEDS

    if dry_run:
        seeds = [0, 1]
        n_resamples = 50
        signal_length = 200
        log.info("DRY-RUN: 2 seeds, 50 resamples, 200 steps.")

    log.info(f"Ablation: {len(ablation_configs)} configs × {len(systems)} systems × {len(modules)} modules")

    # --- Collect raw metrics ---
    # raw[config_name][system][module] = [(metric, status), ...]
    raw: Dict[str, Dict[str, Dict[str, List[Tuple[float, str]]]]] = {}
    total = len(ablation_configs) * len(systems) * len(modules) * len(seeds)
    done = 0

    for config_name, disabled_raw in ablation_configs.items():
        disabled = resolve_disabled_modules(set(disabled_raw))
        raw[config_name] = {}
        for sys_name in systems:
            raw[config_name][sys_name] = {}
            for mod in modules:
                raw[config_name][sys_name][mod] = []
                for seed in seeds:
                    done += 1
                    if done % max(1, total // 10) == 0:
                        log.info(f"  Progress: {done}/{total} ({100*done//total}%)")
                    try:
                        sig = _load_signal(sys_name, signal_length, seed)
                        val, status = _evaluate_module(mod, sig, seed, disabled)
                        raw[config_name][sys_name][mod].append((val, status))
                    except Exception as e:
                        log.debug(f"  [{config_name}/{sys_name}/{mod}/s={seed}]: {e}")
                        raw[config_name][sys_name][mod].append((float("nan"), "ERROR"))

    # --- Compute statistics vs BASELINE_FULL ---
    rows = []
    for config_name in ablation_configs:
        if config_name == "BASELINE_FULL":
            continue
        for sys_name in systems:
            for mod in modules:
                base_pairs = raw["BASELINE_FULL"][sys_name][mod]
                abl_pairs = raw[config_name][sys_name][mod]
                base_arr = np.array([v for v, _ in base_pairs])
                abl_arr = np.array([v for v, _ in abl_pairs])

                # Status: collect unique non-OK, non-DISABLED statuses
                abl_statuses = list({s for _, s in abl_pairs if s not in ("OK", "DISABLED")})
                row_status = abl_statuses[0] if abl_statuses else "OK"
                if all(s == "DISABLED" for _, s in abl_pairs):
                    row_status = "DISABLED"

                base_mean = float(np.nanmean(base_arr))
                abl_mean = float(np.nanmean(abl_arr))
                dp = delta_percent(base_mean, abl_mean)
                d = cohens_d(base_arr, abl_arr)
                ci_lo, ci_hi = bca_delta_ci(base_arr, abl_arr, n_resamples)
                impact = classify_impact(d)

                rows.append({
                    "ablation": config_name,
                    "system": sys_name,
                    "module": mod,
                    "baseline_mean": round(base_mean, 6),
                    "ablated_mean": round(abl_mean, 6),
                    "delta_pct": round(dp, 3) if not np.isnan(dp) else float("nan"),
                    "cohens_d": round(d, 4) if not np.isnan(d) else float("nan"),
                    "ci95_lower": round(ci_lo, 3) if not np.isnan(ci_lo) else float("nan"),
                    "ci95_upper": round(ci_hi, 3) if not np.isnan(ci_hi) else float("nan"),
                    "impact": impact,
                    "status": row_status,
                })

    df = pd.DataFrame(rows)

    # --- Save artifacts/ablation_results.csv ---
    results_path = ARTIFACTS_DIR / "ablation_results.csv"
    df.to_csv(results_path, index=False)
    log.info(f"Saved: {results_path}")

    # --- Save artifacts/ablation_summary.csv (spec columns) ---
    # Aggregate per module_removed: mean delta_pct and cohens_d across all systems/modules
    if not df.empty:
        summary = df.groupby("ablation").agg(
            delta_pct=("delta_pct", "mean"),
            cohens_d=("cohens_d", "mean"),
            ci95_lower=("ci95_lower", "mean"),
            ci95_upper=("ci95_upper", "mean"),
        ).reset_index()
        summary.columns = ["module_removed", "delta_pct", "cohens_d", "ci95_lower", "ci95_upper"]
        summary["interpretation"] = summary["cohens_d"].apply(classify_impact)
        summary_path = ARTIFACTS_DIR / "ablation_summary.csv"
        summary.to_csv(summary_path, index=False)
        log.info(f"Saved: {summary_path}")
    else:
        summary = pd.DataFrame()

    # Backward compat
    df.to_csv(RESULTS_DIR / "ablation_report.csv", index=False)

    # --- Heatmap ---
    if not skip_heatmap:
        try:
            _save_ablation_heatmap(df)
        except Exception as e:
            log.warning(f"Heatmap failed: {e}")

    # --- Markdown report ---
    try:
        _save_ablation_report(df, summary)
    except Exception as e:
        log.warning(f"Markdown report failed: {e}")

    _print_ablation_summary(df)
    return df


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------

def _save_ablation_heatmap(df: pd.DataFrame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pivot = df.groupby(["system", "module"])["cohens_d"].apply(
        lambda x: float(np.nanmean(np.abs(x.dropna())))
    ).reset_index()
    pivot.columns = ["system", "module", "mean_abs_d"]
    matrix = pivot.pivot(index="system", columns="module", values="mean_abs_d").fillna(0)

    fig, ax = plt.subplots(figsize=(max(8, len(matrix.columns) * 1.2),
                                    max(5, len(matrix.index) * 0.8)))
    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(matrix.values, cmap=cmap, aspect="auto", vmin=0, vmax=2.0)
    plt.colorbar(im, ax=ax, label="|Cohen's d| (mean across ablations)")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=9)
    ax.set_title("Ablation Impact Heatmap — Mean |Cohen's d| per System × Module", fontsize=11)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if val > 1.0 else "black", fontsize=7)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        path = FIGURES_DIR / f"ablation_heatmap.{ext}"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        log.info(f"Heatmap saved: {path}")
    plt.close()


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _save_ablation_report(df: pd.DataFrame, summary: pd.DataFrame):
    n_large = (df["impact"] == "Large").sum() if not df.empty else 0
    n_bypass = (df["status"] == "DEPENDENCY_BYPASS").sum() if not df.empty else 0

    summary_md = summary.to_markdown(index=False, floatfmt=".3f") if not summary.empty else "_No data._"

    top5 = df.nlargest(5, "cohens_d") if not df.empty and "cohens_d" in df.columns else pd.DataFrame()
    top5_md = top5[["ablation", "system", "module", "delta_pct", "cohens_d",
                     "ci95_lower", "ci95_upper", "impact"]].to_markdown(
        index=False, floatfmt=".3f") if not top5.empty else "_No data._"

    md = f"""# Phase 8B — Ablation Study Report

## Summary

- Total ablation rows: {len(df)}
- Large-impact removals (|d| ≥ 0.8): **{n_large}**
- Dependency-bypass events (AR(p) fallback): {n_bypass}

## Per-Config Summary

{summary_md}

## Top 5 Highest-Impact Ablations (by Cohen's d)

{top5_md}

## Methodology

- Dependency DAG: cascade disabling of downstream modules.
- Fallback: when a dependent module is missing, AR(p) AIC metric is used
  and row is marked `status=DEPENDENCY_BYPASS`.
- Δ% = (baseline_mean − ablated_mean) / |baseline_mean| × 100
- Cohen's d: pooled standard deviation formula.
- CI95: BCa bootstrap, 1000 resamples (`scipy.stats.bootstrap, method='BCa'`).
- Impact: Negligible (|d|<0.2), Small, Medium, Large (|d|≥0.8).

## Heatmap

See [`figures/ablation_heatmap.pdf`](../figures/ablation_heatmap.pdf).
"""
    path = ARTIFACTS_DIR / "ablation_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    log.info(f"Ablation report saved: {path}")


def _print_ablation_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("  PHASE 8B — ABLATION STUDY SUMMARY")
    print("=" * 60)
    if not df.empty and "cohens_d" in df.columns:
        top = df.nlargest(5, "cohens_d")[
            ["ablation", "system", "module", "delta_pct", "cohens_d", "impact"]]
        print("  Top 5 (Cohen's d):")
        print(top.to_string(index=False))
        print()
        for lbl, cnt in df["impact"].value_counts().items():
            print(f"    {lbl:12s}: {cnt}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 8B — Ablation Study")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--systems", nargs="+", default=None)
    parser.add_argument("--modules", nargs="+", default=None)
    parser.add_argument("--n-resamples", type=int, default=1000)
    parser.add_argument("--signal-length", type=int, default=1000)
    parser.add_argument("--skip-heatmap", action="store_true")
    args = parser.parse_args()
    run_ablation_study(
        systems=args.systems, modules=args.modules, dry_run=args.dry_run,
        n_resamples=args.n_resamples, signal_length=args.signal_length,
        skip_heatmap=args.skip_heatmap,
    )


if __name__ == "__main__":
    main()
