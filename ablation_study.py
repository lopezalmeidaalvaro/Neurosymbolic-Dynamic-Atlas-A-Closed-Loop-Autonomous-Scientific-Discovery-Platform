"""
Phase 8B — Ablation Study
==========================
Systematically disables pipeline components and measures degradation:

  - Dependency resolver (DAG-aware cascade disabling)
  - 9 ablation configurations (NO_TDA, NO_KOOPMAN, etc.)
  - Cohen's d effect size
  - Δ% change from baseline + BCa bootstrap CI95
  - Heatmap: systems × modules impact matrix
  - Impact classification: Negligible / Small / Medium / Large

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

# Force UTF-8 for Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8B] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("ablation_study")

OUT_DIR = Path("results/phase8b")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Module dependency DAG
# ---------------------------------------------------------------------------
# Format: { module: [downstream_dependents] }
MODULE_DAG = {
    "EV3":       ["EV3_EXT", "EV3_DEEP", "EV3_SCI", "SINDy", "Topology", "Koopman"],
    "EV3_EXT":   ["EV3_DEEP", "EV3_SCI"],
    "EV3_DEEP":  ["EV3_SCI"],
    "EV3_SCI":   [],
    "SINDy":     [],
    "Topology":  ["Koopman"],
    "Koopman":   [],
    "NeuralODE": [],
    "PINN":      [],
}

# Ablation configurations: name → set of DISABLED modules
ABLATION_CONFIGS = {
    "BASELINE_FULL":      set(),                                              # all enabled
    "NO_TDA":             {"Topology"},
    "NO_KOOPMAN":         {"Koopman"},
    "NO_GEOMETRY":        {"Topology", "Koopman"},
    "NO_SINDY":           {"SINDy"},
    "NO_PYSR":            set(),                                              # PySR is optional; disable SINDy proxy
    "NO_PINN":            {"PINN"},
    "NO_NEURAL_ODE":      {"NeuralODE"},
    "NO_TOPOLOGY_GEOMETRY": {"Topology", "Koopman"},
}


def resolve_disabled_modules(disabled: set) -> set:
    """
    Cascade-disable all downstream dependents of a disabled module.

    E.g. disabling EV3 also disables EV3_EXT, EV3_DEEP, EV3_SCI, and their
    downstream dependents.
    """
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
# Metric extractor (a single call per module-system pair)
# ---------------------------------------------------------------------------

def _evaluate_module_on_signal(module: str, signal: np.ndarray, seed: int) -> float:
    """Returns scalar metric for one module-signal evaluation."""
    np.random.seed(seed)
    try:
        if module in ("EV3", "EV3_EXT", "EV3_DEEP", "EV3_SCI"):
            from core.autonomous.latent_snapshot_exporter import extract_ev3_features, impute_nan_features
            kwargs = {
                "extended": module in ("EV3_EXT", "EV3_DEEP", "EV3_SCI"),
                "deep": module in ("EV3_DEEP", "EV3_SCI"),
                "scientific": module == "EV3_SCI",
            }
            feat = extract_ev3_features(signal, **kwargs)
            feat_clean = impute_nan_features(np.array([feat]))[0]
            return float(np.linalg.norm(feat_clean))

        elif module == "SINDy":
            from symbolic_discovery import run_sindy
            t = np.linspace(0, len(signal) * 0.01, len(signal))
            r = run_sindy(signal, t)
            return float(r.get("n_active_terms", 0))

        elif module == "Topology":
            from topological_analysis import run_topological_analysis
            r = run_topological_analysis(signal)
            return float(len(r.get("persistence_diagram_0", [])))

        elif module == "Koopman":
            from koopman_analysis import run_koopman_analysis
            r = run_koopman_analysis(signal)
            eigs = r.get("eigenvalues", [1.0])
            return float(np.abs(np.array(eigs)).max()) if eigs else float("nan")

        elif module == "NeuralODE":
            from neural_ode_module import run_neural_ode
            r = run_neural_ode(signal, n_epochs=20, seed=seed)
            return float(r.get("final_loss", float("nan")))

        elif module == "PINN":
            from pinn_module import run_pinn_forward
            r = run_pinn_forward(signal, n_epochs=20, seed=seed)
            return float(r.get("final_loss", float("nan")))

    except Exception as e:
        log.debug(f"Module {module} error: {e}")
    return float("nan")


def _load_signal(system: str, n_steps: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    from synthetic_systems import (
        generate_lorenz, generate_duffing, generate_van_der_pol,
        generate_rossler, generate_logistic_map
    )
    if system == "lorenz":
        return generate_lorenz(n_timesteps=n_steps, dt=0.01,
                                initial_state=np.random.uniform(-15, 15, 3))["x"]
    elif system == "duffing":
        return generate_duffing(n_timesteps=n_steps, dt=0.01,
                                 initial_state=np.random.uniform(-1, 1, 2))["x"]
    elif system == "van_der_pol":
        return generate_van_der_pol(n_timesteps=n_steps, dt=0.01,
                                    initial_state=np.random.uniform(-2, 2, 2))["x"]
    elif system == "rossler":
        return generate_rossler(n_timesteps=n_steps, dt=0.01,
                                 initial_state=np.random.uniform(-5, 5, 3))["x"]
    elif system == "logistic":
        return generate_logistic_map(n_iterations=n_steps, r=3.9,
                                     initial_x=np.random.uniform(0.1, 0.9))["x"]
    elif system in ("ECG200", "ECG5000"):
        from ucr_loader import load_ucr_dataset
        data = load_ucr_dataset(system)
        rng = np.random.RandomState(seed)
        idx = rng.randint(0, len(data["X_train"]))
        return data["X_train"][idx]
    else:
        raise ValueError(f"Unknown system: {system}")


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def cohens_d(base_samples: np.ndarray, ablated_samples: np.ndarray) -> float:
    """
    Pooled Cohen's d:
        d = (mu_base - mu_ablated) / sigma_pooled
    where sigma_pooled = sqrt(((n_b-1)*s_b^2 + (n_a-1)*s_a^2) / (n_b+n_a-2))
    """
    base = base_samples[~np.isnan(base_samples)]
    ablated = ablated_samples[~np.isnan(ablated_samples)]
    if len(base) < 2 or len(ablated) < 2:
        return float("nan")
    n_b, n_a = len(base), len(ablated)
    s_b, s_a = float(np.std(base, ddof=1)), float(np.std(ablated, ddof=1))
    sigma_pooled = np.sqrt(((n_b - 1) * s_b**2 + (n_a - 1) * s_a**2) / (n_b + n_a - 2))
    if sigma_pooled < 1e-12:
        return 0.0
    return float((np.mean(base) - np.mean(ablated)) / sigma_pooled)


def delta_percent(base_mean: float, ablated_mean: float) -> float:
    """Δ% = (base - ablated) / |base| × 100"""
    if abs(base_mean) < 1e-12 or np.isnan(base_mean):
        return float("nan")
    return float((base_mean - ablated_mean) / abs(base_mean) * 100)


def bca_delta_ci(base_samples: np.ndarray, ablated_samples: np.ndarray,
                 n_resamples: int = 1000) -> Tuple[float, float]:
    """BCa CI95 of Δ% via paired bootstrap."""
    base = base_samples[~np.isnan(base_samples)]
    ablated = ablated_samples[~np.isnan(ablated_samples)]
    if len(base) < 2 or len(ablated) < 2:
        return float("nan"), float("nan")

    def delta_stat(b, a):
        mu_b = np.mean(b)
        mu_a = np.mean(a)
        return np.where(np.abs(mu_b) > 1e-12, (mu_b - mu_a) / np.abs(mu_b) * 100, np.nan)

    try:
        result = scipy_bootstrap(
            (base, ablated),
            statistic=delta_stat,
            n_resamples=n_resamples,
            confidence_level=0.95,
            method="BCa",
            random_state=42,
        )
        return float(result.confidence_interval.low), float(result.confidence_interval.high)
    except Exception:
        return float("nan"), float("nan")


def classify_impact(d: float) -> str:
    """Classifies Cohen's d into Negligible/Small/Medium/Large."""
    if np.isnan(d):
        return "N/A"
    ad = abs(d)
    if ad < 0.2:
        return "Negligible"
    elif ad < 0.5:
        return "Small"
    elif ad < 0.8:
        return "Medium"
    else:
        return "Large"


# ---------------------------------------------------------------------------
# Main ablation runner
# ---------------------------------------------------------------------------

DEFAULT_SYSTEMS = ["lorenz", "duffing", "van_der_pol", "rossler", "logistic", "ECG200", "ECG5000"]
DEFAULT_MODULES = ["EV3", "EV3_EXT", "EV3_DEEP", "EV3_SCI", "SINDy", "Topology", "Koopman", "NeuralODE", "PINN"]
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
    Runs ablation study across all systems, modules, and configurations.

    For each (ablation_config, system):
      1. Runs enabled modules with multiple seeds.
      2. Computes Δ% and Cohen's d vs BASELINE_FULL.
      3. Exports results to CSV and JSON.
      4. Generates heatmap of impact.
    """
    systems = systems or DEFAULT_SYSTEMS
    modules = modules or DEFAULT_MODULES
    ablation_configs = ablation_configs or ABLATION_CONFIGS
    seeds = seeds or DEFAULT_SEEDS

    if dry_run:
        seeds = [0, 1]
        n_resamples = 50
        signal_length = 200
        log.info("DRY-RUN mode: 2 seeds, 50 resamples, 200 steps.")

    log.info(f"Ablation study: {len(ablation_configs)} configs x {len(systems)} systems x {len(modules)} modules")

    # Step 1: Collect raw metrics for every (config, module, system, seed)
    raw: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
    # raw[config][system][module] = [metric_seed0, metric_seed1, ...]

    total = len(ablation_configs) * len(systems) * len(modules) * len(seeds)
    done = 0

    for config_name, disabled_raw in ablation_configs.items():
        disabled = resolve_disabled_modules(set(disabled_raw))
        raw[config_name] = {}
        for sys_name in systems:
            raw[config_name][sys_name] = {}
            for mod in modules:
                raw[config_name][sys_name][mod] = []
                if mod in disabled:
                    # Module is ablated — fill with NaN
                    raw[config_name][sys_name][mod] = [float("nan")] * len(seeds)
                    done += len(seeds)
                    continue
                for seed in seeds:
                    done += 1
                    if done % max(1, total // 20) == 0:
                        log.info(f"  Progress: {done}/{total} ({100*done//total}%)")
                    try:
                        sig = _load_signal(sys_name, signal_length, seed)
                        val = _evaluate_module_on_signal(mod, sig, seed)
                        raw[config_name][sys_name][mod].append(val)
                    except Exception as e:
                        log.debug(f"  Error [{config_name}/{sys_name}/{mod}/seed={seed}]: {e}")
                        raw[config_name][sys_name][mod].append(float("nan"))

    # Step 2: Compute statistics against BASELINE_FULL
    rows = []
    for config_name in ablation_configs:
        if config_name == "BASELINE_FULL":
            continue
        for sys_name in systems:
            for mod in modules:
                base_arr = np.array(raw["BASELINE_FULL"][sys_name][mod])
                abl_arr = np.array(raw[config_name][sys_name][mod])

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
                    "ci_lo": round(ci_lo, 3) if not np.isnan(ci_lo) else float("nan"),
                    "ci_hi": round(ci_hi, 3) if not np.isnan(ci_hi) else float("nan"),
                    "impact": impact,
                })

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / "ablation_report.csv"
    df.to_csv(csv_path, index=False)
    log.info(f"Ablation report saved to {csv_path}")

    # JSON with raw metrics
    json_path = OUT_DIR / "ablation_raw.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, default=str)
    log.info(f"Raw ablation data saved to {json_path}")

    # Step 3: Heatmap
    if not skip_heatmap:
        try:
            _save_ablation_heatmap(df)
        except Exception as e:
            log.warning(f"Could not generate heatmap: {e}")

    _print_ablation_summary(df)
    return df


def _save_ablation_heatmap(df: pd.DataFrame):
    """Saves systems × modules heatmap of mean |Cohen's d| per ablation config."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    figures_dir = Path("figures")
    figures_dir.mkdir(exist_ok=True)

    configs = [c for c in df["ablation"].unique() if c != "BASELINE_FULL"]
    systems = sorted(df["system"].unique())
    modules = sorted(df["module"].unique())

    # Aggregate: mean |d| per (system, module) across all non-baseline ablations
    pivot = df.groupby(["system", "module"])["cohens_d"].apply(
        lambda x: float(np.nanmean(np.abs(x.dropna())))
    ).reset_index()
    pivot.columns = ["system", "module", "mean_abs_d"]
    matrix = pivot.pivot(index="system", columns="module", values="mean_abs_d").fillna(0)

    fig, ax = plt.subplots(figsize=(max(8, len(modules) * 1.2), max(5, len(systems) * 0.8)))
    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(matrix.values, cmap=cmap, aspect="auto", vmin=0, vmax=2.0)
    plt.colorbar(im, ax=ax, label="|Cohen's d| (mean across ablations)")

    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=9)
    ax.set_title("Ablation Impact Heatmap — Mean |Cohen's d| per System × Module", fontsize=11)

    # Annotate cells
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.values[i, j]
            text_color = "white" if val > 1.0 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color=text_color, fontsize=7)

    plt.tight_layout()
    out_path = figures_dir / "ablation_heatmap.pdf"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Heatmap saved to {out_path}")

    # Also save PNG for quick viewing
    out_png = figures_dir / "ablation_heatmap.png"
    fig2, ax2 = plt.subplots(figsize=(max(8, len(modules) * 1.2), max(5, len(systems) * 0.8)))
    im2 = ax2.imshow(matrix.values, cmap=cmap, aspect="auto", vmin=0, vmax=2.0)
    plt.colorbar(im2, ax=ax2, label="|Cohen's d|")
    ax2.set_xticks(range(len(matrix.columns)))
    ax2.set_xticklabels(matrix.columns, rotation=45, ha="right", fontsize=9)
    ax2.set_yticks(range(len(matrix.index)))
    ax2.set_yticklabels(matrix.index, fontsize=9)
    ax2.set_title("Ablation Heatmap", fontsize=11)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.values[i, j]
            ax2.text(j, i, f"{val:.2f}", ha="center", va="center",
                     color="white" if val > 1.0 else "black", fontsize=7)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Heatmap PNG saved to {out_png}")


def _print_ablation_summary(df: pd.DataFrame):
    print("\n" + "=" * 60)
    print("  PHASE 8B — ABLATION STUDY SUMMARY")
    print("=" * 60)
    if df.empty:
        print("  No data.")
    else:
        top = df.nlargest(5, "cohens_d")[["ablation", "system", "module", "delta_pct", "cohens_d", "impact"]]
        print("  Top 5 highest-impact ablations (by Cohen's d):")
        print(top.to_string(index=False))
        print()
        impact_counts = df["impact"].value_counts()
        print("  Impact distribution:")
        for label, count in impact_counts.items():
            print(f"    {label:12s}: {count}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
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
        systems=args.systems,
        modules=args.modules,
        dry_run=args.dry_run,
        n_resamples=args.n_resamples,
        signal_length=args.signal_length,
        skip_heatmap=args.skip_heatmap,
    )


if __name__ == "__main__":
    main()
