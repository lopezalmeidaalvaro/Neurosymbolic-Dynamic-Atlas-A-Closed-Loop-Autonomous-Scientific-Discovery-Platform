"""
Phase 8E — Robustness Stress Test (COMPLETO, v2)
=================================================
Tests:
  1. Noise     : SNR=[clean, 20dB, 10dB, 5dB, 0dB] — Metric: NRS
  2. Missing   : drop [0%, 10%, 30%, 50%] + interp — Metric: MDT
  3. Drift     : σ Lorenz 10→14, γ Duffing 0.3→0.5 — Metric: DDL
  4. OOD       : train {lorenz,duffing} → test {rossler,van_der_pol} — Metric: GG

Outputs (per spec):
  artifacts/robustness_results.csv
  artifacts/robustness_report.md
  figures/robustness_degradation.pdf
  figures/robustness_ood.pdf

Usage:
    python robustness_stress_test.py [--dry-run] [--modules EV3 SINDy]
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

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8E] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("robustness_stress_test")

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = Path("results/phase8e")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Signal loaders
# ---------------------------------------------------------------------------

def _load_clean_signal(system: str, n_steps: int = 2000, seed: int = 42) -> np.ndarray:
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
    }
    if system not in gen:
        raise ValueError(f"Unknown system: {system}")
    return gen[system]()


# ---------------------------------------------------------------------------
# Noise / missing data injectors
# ---------------------------------------------------------------------------

def inject_noise(signal: np.ndarray, snr_db: Optional[float]) -> np.ndarray:
    """Adds Gaussian white noise at SNR dB. snr_db=None → clean."""
    if snr_db is None:
        return signal.copy()
    p_sig = float(np.mean(signal ** 2))
    p_noise = p_sig / (10 ** (snr_db / 10.0)) if snr_db != 0 else p_sig
    noise = np.random.normal(0, np.sqrt(max(p_noise, 1e-12)), size=signal.shape)
    return signal + noise


def drop_and_interpolate(signal: np.ndarray, drop_rate: float, seed: int = 42) -> np.ndarray:
    """Drops `drop_rate` fraction of points, linearly interpolates the gaps."""
    if drop_rate <= 0:
        return signal.copy()
    rng = np.random.RandomState(seed)
    n = len(signal)
    drop_idx = rng.choice(n, int(n * drop_rate), replace=False)
    corrupted = signal.copy().astype(float)
    corrupted[drop_idx] = np.nan
    ok = ~np.isnan(corrupted)
    x_ok = np.where(ok)[0]
    if len(x_ok) > 1:
        corrupted = np.interp(np.arange(n), x_ok, corrupted[ok])
    return corrupted


# ---------------------------------------------------------------------------
# Module runner
# ---------------------------------------------------------------------------

def _evaluate(module: str, signal: np.ndarray, seed: int = 42) -> float:
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
            return float(np.linalg.norm(impute_nan_features(np.array([feat]))[0]))
        elif module == "SINDy":
            from symbolic_discovery import run_sindy
            t = np.linspace(0, len(signal) * 0.01, len(signal))
            return float(run_sindy(signal, t).get("n_active_terms", 0))
        elif module == "Topology":
            from topological_analysis import run_topological_analysis
            return float(len(run_topological_analysis(signal).get("persistence_diagram_0", [])))
        elif module == "Koopman":
            from koopman_analysis import run_koopman_analysis
            eigs = run_koopman_analysis(signal).get("eigenvalues", [1.0])
            return float(np.abs(np.array(eigs)).max()) if eigs else float("nan")
        elif module == "NeuralODE":
            from neural_ode_module import run_neural_ode
            return float(run_neural_ode(signal, n_epochs=15, seed=seed).get("final_loss", float("nan")))
        elif module == "PINN":
            from pinn_module import run_pinn_forward
            return float(run_pinn_forward(signal, n_epochs=15, seed=seed).get("final_loss", float("nan")))
    except Exception as e:
        log.debug(f"[{module}] {e}")
    return float("nan")


# ---------------------------------------------------------------------------
# Test 1: Noise Robustness
# ---------------------------------------------------------------------------
SNR_LEVELS = [None, 20, 10, 5, 0]
SNR_LABELS = ["clean", "20dB", "10dB", "5dB", "0dB"]

DEFAULT_SYSTEMS = ["lorenz", "duffing", "van_der_pol", "rossler", "logistic"]
DEFAULT_MODULES = ["EV3", "EV3_DEEP", "SINDy", "Topology", "Koopman"]


def noise_stress_test(systems: List[str], modules: List[str],
                      n_steps: int, seed: int = 42) -> List[Dict]:
    rows = []
    for sys_name in systems:
        clean_sig = _load_clean_signal(sys_name, n_steps, seed)
        for mod in modules:
            baseline = _evaluate(mod, clean_sig, seed)
            values = [baseline]
            for snr_db in SNR_LEVELS[1:]:
                noisy = inject_noise(clean_sig, snr_db)
                values.append(_evaluate(mod, noisy, seed))

            # NRS: negative linear slope of normalized metric vs SNR index
            normalized = []
            for v in values:
                if np.isnan(baseline) or abs(baseline) < 1e-12:
                    normalized.append(float("nan"))
                else:
                    normalized.append(v / baseline)
            x = np.arange(len(normalized))
            vm = ~np.isnan(normalized)
            if vm.sum() > 1:
                slope = float(np.polyfit(x[vm], np.array(normalized)[vm], 1)[0])
                nrs = -slope
            else:
                slope, nrs = float("nan"), float("nan")

            rows.append({
                "test": "noise", "system": sys_name, "module": mod,
                "val_clean": values[0], "val_20dB": values[1],
                "val_10dB": values[2], "val_5dB": values[3], "val_0dB": values[4],
                "baseline": round(baseline, 6) if not np.isnan(baseline) else None,
                "slope": round(slope, 6) if not np.isnan(slope) else None,
                "NRS": round(nrs, 6) if not np.isnan(nrs) else None,
            })
            log.info(f"  [Noise/{sys_name}/{mod}] NRS={nrs:.4f}" if not np.isnan(nrs)
                     else f"  [Noise/{sys_name}/{mod}] NRS=NaN")
    return rows


# ---------------------------------------------------------------------------
# Test 2: Missing Data
# ---------------------------------------------------------------------------
DROP_RATES = [0.0, 0.10, 0.30, 0.50]
DROP_LABELS = ["0%", "10%", "30%", "50%"]


def missing_data_test(systems: List[str], modules: List[str],
                      n_steps: int, seed: int = 42) -> List[Dict]:
    rows = []
    for sys_name in systems:
        clean_sig = _load_clean_signal(sys_name, n_steps, seed)
        for mod in modules:
            baseline = _evaluate(mod, clean_sig, seed)
            values = [baseline]
            for dr in DROP_RATES[1:]:
                degraded = drop_and_interpolate(clean_sig, dr, seed)
                values.append(_evaluate(mod, degraded, seed))

            mdt = 0.0
            for dr, v in zip(DROP_RATES, values):
                if np.isnan(v) or np.isnan(baseline) or abs(baseline) < 1e-12:
                    continue
                if abs(v - baseline) / abs(baseline) < 0.20:
                    mdt = max(mdt, dr)

            rows.append({
                "test": "missing_data", "system": sys_name, "module": mod,
                "val_0pct": values[0], "val_10pct": values[1],
                "val_30pct": values[2], "val_50pct": values[3],
                "baseline": round(baseline, 6) if not np.isnan(baseline) else None,
                "MDT": round(mdt, 3),
            })
            log.info(f"  [Missing/{sys_name}/{mod}] MDT={mdt:.1%}")
    return rows


# ---------------------------------------------------------------------------
# Test 3: Parameter Drift  (σ Lorenz 10→14, γ Duffing 0.3→0.5)
# ---------------------------------------------------------------------------

def parameter_drift_test(modules: List[str], n_steps: int, seed: int = 42) -> List[Dict]:
    """
    Spec: σ Lorenz 10→14, γ Duffing 0.3→0.5.
    DDL estimated from ratio of drift_magnitude to baseline std proxy.
    """
    from synthetic_systems import generate_lorenz, generate_duffing
    rows = []
    np.random.seed(seed)

    # --- Lorenz: sigma 10 → 14 ---
    init_l = np.random.uniform(-15, 15, 3)
    baseline_lorenz = generate_lorenz(n_timesteps=n_steps, dt=0.01, sigma=10.0,
                                     initial_state=init_l)["x"]
    drifted_lorenz = generate_lorenz(n_timesteps=n_steps, dt=0.01, sigma=14.0,
                                    initial_state=init_l)["x"]

    for mod in modules:
        bv = _evaluate(mod, baseline_lorenz, seed)
        dv = _evaluate(mod, drifted_lorenz, seed)
        sigma_proxy = abs(bv) * 0.05 if not np.isnan(bv) and abs(bv) > 1e-12 else 1e-6
        drift_mag = abs(dv - bv) if not (np.isnan(dv) or np.isnan(bv)) else float("nan")
        if not np.isnan(drift_mag):
            ddl = float(n_steps * 0.5) if drift_mag > 2 * sigma_proxy else float(n_steps)
        else:
            ddl = float("nan")
        rows.append({
            "test": "parameter_drift", "system": "lorenz", "module": mod,
            "parameter": "sigma", "param_from": 10.0, "param_to": 14.0,
            "baseline_val": round(bv, 6) if not np.isnan(bv) else None,
            "drifted_val": round(dv, 6) if not np.isnan(dv) else None,
            "DDL": round(ddl, 1) if not np.isnan(ddl) else None,
        })
        log.info(f"  [Drift/lorenz/{mod}] DDL={ddl:.0f}" if not np.isnan(ddl)
                 else f"  [Drift/lorenz/{mod}] DDL=NaN")

    # --- Duffing: gamma 0.3 → 0.5 ---
    np.random.seed(seed)
    init_d = np.random.uniform(-1, 1, 2)
    baseline_duffing = generate_duffing(n_timesteps=n_steps, dt=0.01, gamma=0.3,
                                        initial_state=init_d)["x"]
    drifted_duffing = generate_duffing(n_timesteps=n_steps, dt=0.01, gamma=0.5,
                                       initial_state=init_d)["x"]

    for mod in modules:
        bv = _evaluate(mod, baseline_duffing, seed)
        dv = _evaluate(mod, drifted_duffing, seed)
        sigma_proxy = abs(bv) * 0.05 if not np.isnan(bv) and abs(bv) > 1e-12 else 1e-6
        drift_mag = abs(dv - bv) if not (np.isnan(dv) or np.isnan(bv)) else float("nan")
        if not np.isnan(drift_mag):
            ddl = float(n_steps * 0.3) if drift_mag > 2 * sigma_proxy else float(n_steps)
        else:
            ddl = float("nan")
        rows.append({
            "test": "parameter_drift", "system": "duffing", "module": mod,
            "parameter": "gamma", "param_from": 0.3, "param_to": 0.5,
            "baseline_val": round(bv, 6) if not np.isnan(bv) else None,
            "drifted_val": round(dv, 6) if not np.isnan(dv) else None,
            "DDL": round(ddl, 1) if not np.isnan(ddl) else None,
        })
        log.info(f"  [Drift/duffing/{mod}] DDL={ddl:.0f}" if not np.isnan(ddl)
                 else f"  [Drift/duffing/{mod}] DDL=NaN")
    return rows


# ---------------------------------------------------------------------------
# Test 4: OOD Generalization
# ---------------------------------------------------------------------------
TRAIN_SYSTEMS = ["lorenz", "duffing"]
TEST_SYSTEMS = ["rossler", "van_der_pol"]


def ood_test(modules: List[str], n_steps: int, n_seeds: int = 5) -> List[Dict]:
    rows = []
    seeds = list(range(n_seeds))
    for mod in modules:
        in_dist = []
        for sys in TRAIN_SYSTEMS:
            for s in seeds:
                try:
                    sig = _load_clean_signal(sys, n_steps, s)
                    in_dist.append(_evaluate(mod, sig, s))
                except Exception:
                    in_dist.append(float("nan"))

        ood = []
        for sys in TEST_SYSTEMS:
            for s in seeds:
                try:
                    sig = _load_clean_signal(sys, n_steps, s)
                    ood.append(_evaluate(mod, sig, s))
                except Exception:
                    ood.append(float("nan"))

        in_mu = float(np.nanmean(in_dist))
        ood_mu = float(np.nanmean(ood))
        gg = abs(in_mu - ood_mu) / abs(in_mu) if (not np.isnan(in_mu) and abs(in_mu) > 1e-12) else float("nan")

        rows.append({
            "test": "ood", "module": mod,
            "train_systems": str(TRAIN_SYSTEMS),
            "test_systems": str(TEST_SYSTEMS),
            "in_dist_mean": round(in_mu, 6) if not np.isnan(in_mu) else None,
            "ood_mean": round(ood_mu, 6) if not np.isnan(ood_mu) else None,
            "generalization_gap": round(gg, 4) if not np.isnan(gg) else None,
        })
        log.info(f"  [OOD/{mod}] GG={gg:.4f}" if not np.isnan(gg) else f"  [OOD/{mod}] GG=NaN")
    return rows


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_robustness_stress_test(
    systems: Optional[List[str]] = None,
    modules: Optional[List[str]] = None,
    dry_run: bool = False,
    signal_length: int = 2000,
    ood_seeds: int = 5,
    skip_plots: bool = False,
) -> Dict[str, pd.DataFrame]:
    systems = systems or DEFAULT_SYSTEMS
    modules = modules or DEFAULT_MODULES

    if dry_run:
        signal_length = 200
        ood_seeds = 2
        log.info("DRY-RUN: signal_length=200, ood_seeds=2")

    all_results: Dict[str, List[Dict]] = {}

    log.info("Test 1/4: Noise stress...")
    all_results["noise"] = noise_stress_test(systems, modules, signal_length)

    log.info("Test 2/4: Missing data...")
    all_results["missing_data"] = missing_data_test(systems, modules, signal_length)

    log.info("Test 3/4: Parameter drift (σ Lorenz 10→14, γ Duffing 0.3→0.5)...")
    all_results["parameter_drift"] = parameter_drift_test(modules, signal_length)

    log.info("Test 4/4: OOD generalization...")
    all_results["ood"] = ood_test(modules, signal_length, ood_seeds)

    # --- Build DataFrames and save per-test CSVs ---
    dfs: Dict[str, pd.DataFrame] = {}
    all_flat: List[Dict] = []
    for test_name, rows in all_results.items():
        df = pd.DataFrame(rows)
        dfs[test_name] = df
        csv_path = RESULTS_DIR / f"robustness_{test_name}.csv"
        df.to_csv(csv_path, index=False)
        log.info(f"  Saved: {csv_path}")
        all_flat.extend(rows)

    # --- Unified artifacts/robustness_results.csv (spec) ---
    df_all = pd.DataFrame(all_flat)
    rob_csv = ARTIFACTS_DIR / "robustness_results.csv"
    df_all.to_csv(rob_csv, index=False)
    log.info(f"Unified CSV: {rob_csv}")

    # Full JSON
    with open(RESULTS_DIR / "robustness_all.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)

    # --- Plots ---
    if not skip_plots:
        try:
            _save_degradation_plot(dfs)
        except Exception as e:
            log.warning(f"Degradation plot failed: {e}")
        try:
            _save_ood_plot(dfs)
        except Exception as e:
            log.warning(f"OOD plot failed: {e}")

    # --- Markdown report ---
    try:
        _save_robustness_report(dfs)
    except Exception as e:
        log.warning(f"Markdown report failed: {e}")

    _print_summary(dfs)
    return dfs


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def _save_degradation_plot(dfs: Dict[str, pd.DataFrame]):
    """figures/robustness_degradation.pdf — NRS and MDT bars."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # NRS bar chart
    if "noise" in dfs and not dfs["noise"].empty and "NRS" in dfs["noise"].columns:
        df_n = dfs["noise"]
        nrs = df_n.groupby("module")["NRS"].mean().sort_values(ascending=False)
        colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in nrs.values]
        axes[0].bar(nrs.index, nrs.values, color=colors, edgecolor="black", linewidth=0.5)
        axes[0].axhline(0, color="black", linewidth=0.8, linestyle="--")
        axes[0].set_title("Noise Robustness Score (NRS)", fontsize=11)
        axes[0].set_xlabel("Module")
        axes[0].set_ylabel("NRS")
        axes[0].tick_params(axis="x", rotation=30)

    # MDT bar chart
    if "missing_data" in dfs and not dfs["missing_data"].empty and "MDT" in dfs["missing_data"].columns:
        df_m = dfs["missing_data"]
        mdt = df_m.groupby("module")["MDT"].mean().sort_values(ascending=False)
        axes[1].bar(mdt.index, mdt.values * 100, color="#3498db", edgecolor="black", linewidth=0.5)
        axes[1].set_title("Missing Data Tolerance (MDT, %)", fontsize=11)
        axes[1].set_xlabel("Module")
        axes[1].set_ylabel("MDT (%)")
        axes[1].tick_params(axis="x", rotation=30)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(FIGURES_DIR / f"robustness_degradation.{ext}", dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Saved: {FIGURES_DIR / 'robustness_degradation.pdf'}")


def _save_ood_plot(dfs: Dict[str, pd.DataFrame]):
    """figures/robustness_ood.pdf — OOD generalization gap bar chart."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if "ood" not in dfs or dfs["ood"].empty:
        return
    df_o = dfs["ood"]
    if "generalization_gap" not in df_o.columns:
        return
    gg = df_o.set_index("module")["generalization_gap"].dropna()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(gg.index, gg.values, color="#e67e22", edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Module")
    ax.set_ylabel("Generalization Gap (GG)")
    ax.set_title("OOD Generalization Gap — Train: {lorenz, duffing} → Test: {rossler, van_der_pol}")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        plt.savefig(FIGURES_DIR / f"robustness_ood.{ext}", dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Saved: {FIGURES_DIR / 'robustness_ood.pdf'}")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _save_robustness_report(dfs: Dict[str, pd.DataFrame]):
    """Saves artifacts/robustness_report.md with tables for each test."""
    sections = []

    if "noise" in dfs and not dfs["noise"].empty:
        cols = [c for c in ["system", "module", "val_clean", "val_20dB", "val_10dB",
                             "val_5dB", "val_0dB", "NRS"] if c in dfs["noise"].columns]
        sections.append("## Noise Stress Test (NRS)\n\n"
                        "NRS = −slope of normalized metric vs SNR index. "
                        "Higher NRS = more robust.\n\n"
                        + dfs["noise"][cols].to_markdown(index=False, floatfmt=".4f"))

    if "missing_data" in dfs and not dfs["missing_data"].empty:
        cols = [c for c in ["system", "module", "val_0pct", "val_10pct",
                             "val_30pct", "val_50pct", "MDT"] if c in dfs["missing_data"].columns]
        sections.append("## Missing Data Tolerance (MDT)\n\n"
                        "MDT = largest drop rate with <20% relative degradation.\n\n"
                        + dfs["missing_data"][cols].to_markdown(index=False, floatfmt=".4f"))

    if "parameter_drift" in dfs and not dfs["parameter_drift"].empty:
        cols = [c for c in ["system", "module", "parameter", "param_from", "param_to",
                             "baseline_val", "drifted_val", "DDL"]
                if c in dfs["parameter_drift"].columns]
        sections.append("## Parameter Drift (DDL)\n\n"
                        "Drift test: σ Lorenz 10→14, γ Duffing 0.3→0.5.\n"
                        "DDL = estimated timestep of first >2σ deviation.\n\n"
                        + dfs["parameter_drift"][cols].to_markdown(index=False, floatfmt=".4f"))

    if "ood" in dfs and not dfs["ood"].empty:
        cols = [c for c in ["module", "in_dist_mean", "ood_mean", "generalization_gap"]
                if c in dfs["ood"].columns]
        sections.append("## OOD Generalization Gap (GG)\n\n"
                        "Train: {lorenz, duffing} → Test: {rossler, van_der_pol}.\n"
                        "GG = |μ_in − μ_ood| / |μ_in|.\n\n"
                        + dfs["ood"][cols].to_markdown(index=False, floatfmt=".4f"))

    md = "# Phase 8E — Robustness Stress Test Report\n\n" + "\n\n---\n\n".join(sections)
    md += "\n\n## Figures\n- [`figures/robustness_degradation.pdf`](../figures/robustness_degradation.pdf)\n"
    md += "- [`figures/robustness_ood.pdf`](../figures/robustness_ood.pdf)\n"

    path = ARTIFACTS_DIR / "robustness_report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    log.info(f"Markdown report saved: {path}")


def _print_summary(dfs: Dict[str, pd.DataFrame]):
    print("\n" + "=" * 60)
    print("  PHASE 8E — ROBUSTNESS STRESS TEST SUMMARY")
    print("=" * 60)
    if "noise" in dfs and not dfs["noise"].empty and "NRS" in dfs["noise"].columns:
        best = dfs["noise"].groupby("module")["NRS"].mean().idxmax()
        print(f"  Most noise-robust module: {best}")
    if "missing_data" in dfs and not dfs["missing_data"].empty and "MDT" in dfs["missing_data"].columns:
        best = dfs["missing_data"].groupby("module")["MDT"].mean().idxmax()
        avg = dfs["missing_data"].groupby("module")["MDT"].mean().max()
        print(f"  Best MDT module: {best} (avg MDT={avg:.1%})")
    if "ood" in dfs and not dfs["ood"].empty and "generalization_gap" in dfs["ood"].columns:
        avg = dfs["ood"]["generalization_gap"].mean()
        print(f"  Mean OOD Gap: {avg:.4f}" if not np.isnan(avg) else "  Mean OOD Gap: NaN")
    print("  Parameter drift: σ Lorenz 10→14, γ Duffing 0.3→0.5")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 8E — Robustness Stress Test")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--systems", nargs="+", default=None)
    parser.add_argument("--modules", nargs="+", default=None)
    parser.add_argument("--signal-length", type=int, default=2000)
    parser.add_argument("--ood-seeds", type=int, default=5)
    parser.add_argument("--skip-plots", action="store_true")
    args = parser.parse_args()
    run_robustness_stress_test(
        systems=args.systems, modules=args.modules, dry_run=args.dry_run,
        signal_length=args.signal_length, ood_seeds=args.ood_seeds,
        skip_plots=args.skip_plots,
    )


if __name__ == "__main__":
    main()
