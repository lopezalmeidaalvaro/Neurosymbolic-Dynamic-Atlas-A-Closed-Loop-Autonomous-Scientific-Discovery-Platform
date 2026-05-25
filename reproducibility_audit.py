"""
Phase 8A — Reproducibility Audit
=================================
Evaluates pipeline stability using:
  - Sobol quasi-random seed sequences (scipy.stats.qmc.Sobol)
  - BCa bootstrap 95% confidence intervals (scipy.stats.bootstrap)
  - Sequential adaptive stopping (W_rel < 0.05 or cap at 50 seeds)
  - Coefficient of Variation (CV) stability classification
  - Peak RAM / VRAM profiling via tracemalloc and torch

Usage:
    python reproducibility_audit.py [--dry-run] [--systems lorenz duffing] [--modules EV3 SINDy]
"""

import sys
import os
import io
import json
import time
import tracemalloc
import argparse
import warnings
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from scipy.stats.qmc import Sobol
from scipy.stats import bootstrap as scipy_bootstrap

# Force UTF-8 for Windows terminals
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8A] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("reproducibility_audit")

# ---------------------------------------------------------------------------
# Hardware Detection
# ---------------------------------------------------------------------------
HAS_GPU = False
MAX_WORKERS = max(1, (os.cpu_count() or 2) - 2)
GPU_BATCH_SIZE = 32
MIXED_PRECISION = False

try:
    import torch
    HAS_GPU = torch.cuda.is_available()
    if HAS_GPU:
        GPU_BATCH_SIZE = 32
        MIXED_PRECISION = True
        MAX_WORKERS = 1  # Avoid GPU contention
        log.info(f"GPU detected: {torch.cuda.get_device_name(0)}. Workers limited to 1.")
    else:
        log.info(f"CPU-only mode. Workers: {MAX_WORKERS}")
except ImportError:
    log.info("PyTorch not found. CPU-only mode.")

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
OUT_DIR = Path("results/phase8a")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Sobol Quasi-Random Seed Generator
# ---------------------------------------------------------------------------

def generate_sobol_seeds(n_seeds: int, scramble: bool = True) -> List[int]:
    """
    Generates n_seeds quasi-random integer seeds via a 1-D Sobol sequence.

    Maps each point p ∈ [0, 1) to an integer seed via:
        S = floor(p * (2^31 - 1))

    This ensures better space coverage than uniform random seeds,
    particularly valuable for GPU modules (PINN, NeuralODE) where
    initialization geometry strongly affects convergence.
    """
    sampler = Sobol(d=1, scramble=scramble, seed=42)
    # Sobol requires power-of-2 sample counts for full-sequence quality;
    # we generate the next power of 2 >= n_seeds and truncate.
    n_pow2 = 1
    while n_pow2 < n_seeds:
        n_pow2 *= 2
    points = sampler.random(n_pow2)[:n_seeds, 0]   # shape (n_seeds,)
    seeds = [int(p * (2**31 - 1)) for p in points]
    return seeds


# ---------------------------------------------------------------------------
# Module runners — thin wrappers that return a single scalar metric
# ---------------------------------------------------------------------------

def _load_signal(system: str, n_steps: int = 2000, seed: int = 42) -> np.ndarray:
    """Returns a 1-D signal for a given dynamical system."""
    np.random.seed(seed)
    from synthetic_systems import (
        generate_lorenz, generate_duffing, generate_van_der_pol,
        generate_rossler, generate_logistic_map
    )
    if system == "lorenz":
        d = generate_lorenz(n_timesteps=n_steps, dt=0.01,
                            initial_state=np.random.uniform(-15, 15, 3))
        return d["x"]
    elif system == "duffing":
        d = generate_duffing(n_timesteps=n_steps, dt=0.01,
                             initial_state=np.random.uniform(-1, 1, 2))
        return d["x"]
    elif system == "van_der_pol":
        d = generate_van_der_pol(n_timesteps=n_steps, dt=0.01,
                                 initial_state=np.random.uniform(-2, 2, 2))
        return d["x"]
    elif system == "rossler":
        d = generate_rossler(n_timesteps=n_steps, dt=0.01,
                              initial_state=np.random.uniform(-5, 5, 3))
        return d["x"]
    elif system == "logistic":
        d = generate_logistic_map(n_iterations=n_steps, r=3.9,
                                  initial_x=np.random.uniform(0.1, 0.9))
        return d["x"]
    elif system in ("ECG200", "ECG5000"):
        from ucr_loader import load_ucr_dataset
        data = load_ucr_dataset(system)
        rng = np.random.RandomState(seed)
        idx = rng.randint(0, len(data["X_train"]))
        return data["X_train"][idx]
    else:
        raise ValueError(f"Unknown system: {system}")


def _run_ev3(signal: np.ndarray, variant: str, seed: int) -> float:
    """Extract EV3 features and return L2 norm as reproducibility metric."""
    from core.autonomous.latent_snapshot_exporter import extract_ev3_features, impute_nan_features
    np.random.seed(seed)
    kwargs = {
        "extended": variant in ("EV3_EXT", "EV3_DEEP", "EV3_SCI"),
        "deep": variant in ("EV3_DEEP", "EV3_SCI"),
        "scientific": variant == "EV3_SCI",
    }
    feat = extract_ev3_features(signal, **kwargs)
    feat_clean = impute_nan_features(np.array([feat]))[0]
    return float(np.linalg.norm(feat_clean))


def _run_sindy(signal: np.ndarray, seed: int) -> float:
    """Run SINDy identification; return Jaccard similarity to trivial lib."""
    from symbolic_discovery import run_sindy
    np.random.seed(seed)
    try:
        t = np.linspace(0, len(signal) * 0.01, len(signal))
        result = run_sindy(signal, t)
        # Return number of non-zero coefficients as scalar metric
        return float(result.get("n_active_terms", 0))
    except Exception:
        return float("nan")


def _run_topology(signal: np.ndarray, seed: int) -> float:
    """Run persistent homology; return H0 birth-death interval count."""
    from topological_analysis import run_topological_analysis
    np.random.seed(seed)
    try:
        result = run_topological_analysis(signal)
        h0 = result.get("persistence_diagram_0", [])
        return float(len(h0))
    except Exception:
        return float("nan")


def _run_koopman(signal: np.ndarray, seed: int) -> float:
    """Run Koopman/DMD; return dominant eigenvalue magnitude."""
    from koopman_analysis import run_koopman_analysis
    np.random.seed(seed)
    try:
        result = run_koopman_analysis(signal)
        eigs = result.get("eigenvalues", [1.0])
        if len(eigs) == 0:
            return float("nan")
        return float(np.abs(np.array(eigs)).max())
    except Exception:
        return float("nan")


def _run_neural_ode(signal: np.ndarray, seed: int) -> float:
    """Run Neural ODE; return final training loss."""
    from neural_ode_module import run_neural_ode
    np.random.seed(seed)
    try:
        if HAS_GPU:
            import torch
            torch.manual_seed(seed)
            torch.cuda.empty_cache()
        result = run_neural_ode(signal, n_epochs=30, seed=seed)
        return float(result.get("final_loss", float("nan")))
    except Exception:
        return float("nan")


def _run_pinn(signal: np.ndarray, seed: int) -> float:
    """Run PINN forward pass; return final MSE loss."""
    from pinn_module import run_pinn_forward
    np.random.seed(seed)
    try:
        if HAS_GPU:
            import torch
            torch.manual_seed(seed)
            torch.cuda.empty_cache()
        result = run_pinn_forward(signal, n_epochs=30, seed=seed)
        return float(result.get("final_loss", float("nan")))
    except Exception:
        return float("nan")


# Module dispatch table
MODULE_RUNNERS = {
    "EV3":       lambda sig, seed: _run_ev3(sig, "EV3", seed),
    "EV3_EXT":   lambda sig, seed: _run_ev3(sig, "EV3_EXT", seed),
    "EV3_DEEP":  lambda sig, seed: _run_ev3(sig, "EV3_DEEP", seed),
    "EV3_SCI":   lambda sig, seed: _run_ev3(sig, "EV3_SCI", seed),
    "SINDy":     _run_sindy,
    "Topology":  _run_topology,
    "Koopman":   _run_koopman,
    "NeuralODE": _run_neural_ode,
    "PINN":      _run_pinn,
}

# ---------------------------------------------------------------------------
# BCa Bootstrap CI95
# ---------------------------------------------------------------------------

def bca_bootstrap_ci(samples: np.ndarray, n_resamples: int = 2000,
                     confidence_level: float = 0.95) -> Tuple[float, float, float]:
    """
    Computes BCa bootstrap 95% CI on the mean.

    Returns:
        (mean, ci_lower, ci_upper)
    """
    valid = samples[~np.isnan(samples)]
    if len(valid) < 2:
        mu = float(np.nanmean(samples))
        return mu, float("nan"), float("nan")

    result = scipy_bootstrap(
        (valid,),
        statistic=np.mean,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
        method="BCa",
        random_state=42,
    )
    mu = float(np.mean(valid))
    return mu, float(result.confidence_interval.low), float(result.confidence_interval.high)


# ---------------------------------------------------------------------------
# Relative CI Width (convergence criterion)
# ---------------------------------------------------------------------------

def relative_ci_width(ci_lower: float, ci_upper: float, mu: float) -> float:
    """
    W_rel = (CI_upper - CI_lower) / |mu|

    Returns inf if mu == 0 to force continuation.
    """
    if np.isnan(ci_lower) or np.isnan(ci_upper):
        return float("inf")
    width = ci_upper - ci_lower
    if abs(mu) < 1e-12:
        return float("inf")
    return width / abs(mu)


# ---------------------------------------------------------------------------
# Sequential Adaptive Stopping
# ---------------------------------------------------------------------------

def adaptive_evaluation(
    module: str, system: str,
    initial_seeds: int = 20,
    increment: int = 10,
    max_seeds: int = 50,
    w_rel_threshold: float = 0.05,
    n_resamples: int = 2000,
    signal_length: int = 2000,
) -> Dict[str, Any]:
    """
    Performs sequential adaptive evaluation:

    Step A: Run with initial_seeds Sobol seeds.
    Step B: Compute BCa CI95.
    Step C: Check W_rel < threshold → converged.
    Step D: If not converged, add increment more seeds (up to max_seeds).

    Returns a result dict with all metrics.
    """
    runner = MODULE_RUNNERS.get(module)
    if runner is None:
        return {"error": f"Module '{module}' not found"}

    all_seeds = generate_sobol_seeds(max_seeds)
    metrics: List[float] = []
    times: List[float] = []
    converged = False
    n_used = 0

    # Adaptive batching
    batch_schedule = [initial_seeds]
    remaining = max_seeds - initial_seeds
    while remaining > 0:
        batch_schedule.append(min(increment, remaining))
        remaining -= increment

    for batch_size in batch_schedule:
        batch_seeds = all_seeds[n_used: n_used + batch_size]
        for seed in batch_seeds:
            try:
                sig = _load_signal(system, n_steps=signal_length, seed=seed)
                t0 = time.perf_counter()
                val = runner(sig, seed)
                elapsed = time.perf_counter() - t0
                metrics.append(val)
                times.append(elapsed)
            except Exception as e:
                metrics.append(float("nan"))
                times.append(float("nan"))
                log.debug(f"  Error [{module}/{system}/seed={seed}]: {e}")
        n_used += batch_size

        arr = np.array(metrics)
        mu, ci_lo, ci_hi = bca_bootstrap_ci(arr, n_resamples=n_resamples)
        w_rel = relative_ci_width(ci_lo, ci_hi, mu)

        if w_rel < w_rel_threshold:
            converged = True
            break

    arr = np.array(metrics)
    valid_arr = arr[~np.isnan(arr)]
    mu, ci_lo, ci_hi = bca_bootstrap_ci(arr, n_resamples=n_resamples)
    sigma = float(np.nanstd(valid_arr)) if len(valid_arr) > 1 else float("nan")
    cv = sigma / abs(mu) if (not np.isnan(mu) and abs(mu) > 1e-12) else float("nan")

    stability = "STABLE" if (converged and not np.isnan(cv) and cv < 0.05) else "UNSTABLE"

    return {
        "module": module,
        "system": system,
        "n_seeds": n_used,
        "converged": converged,
        "convergence_status": "CONVERGED" if converged else "NOT_CONVERGED",
        "mean": mu,
        "std": sigma,
        "cv": cv,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "w_rel": relative_ci_width(ci_lo, ci_hi, mu),
        "stability": stability,
        "mean_time_s": float(np.nanmean(times)) if times else float("nan"),
        "total_time_s": float(np.nansum(times)) if times else float("nan"),
        "raw_metrics": [round(m, 8) for m in metrics],
    }


# ---------------------------------------------------------------------------
# RAM / VRAM Profiling
# ---------------------------------------------------------------------------

def profile_memory(module: str, system: str, seed: int = 42,
                   signal_length: int = 2000) -> Dict[str, float]:
    """Measures peak RAM (tracemalloc) and VRAM (torch) during one module run."""
    runner = MODULE_RUNNERS.get(module)
    if runner is None:
        return {"peak_ram_mb": float("nan"), "peak_vram_mb": float("nan")}

    sig = _load_signal(system, n_steps=signal_length, seed=seed)

    tracemalloc.start()
    vram_before = 0.0
    if HAS_GPU:
        import torch
        torch.cuda.reset_peak_memory_stats()
        vram_before = torch.cuda.memory_allocated() / (1024 ** 2)

    try:
        runner(sig, seed)
    except Exception:
        pass

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_ram_mb = peak / (1024 ** 2)

    peak_vram_mb = 0.0
    if HAS_GPU:
        import torch
        peak_vram_mb = (torch.cuda.max_memory_allocated() - vram_before * (1024 ** 2)) / (1024 ** 2)

    return {"peak_ram_mb": round(peak_ram_mb, 3), "peak_vram_mb": round(peak_vram_mb, 3)}


# ---------------------------------------------------------------------------
# Main audit runner
# ---------------------------------------------------------------------------

DEFAULT_SYSTEMS = ["lorenz", "duffing", "van_der_pol", "rossler", "logistic", "ECG200", "ECG5000"]
DEFAULT_MODULES = ["EV3", "EV3_EXT", "EV3_DEEP", "EV3_SCI", "SINDy", "Topology", "Koopman", "NeuralODE", "PINN"]


def run_reproducibility_audit(
    systems: Optional[List[str]] = None,
    modules: Optional[List[str]] = None,
    dry_run: bool = False,
    initial_seeds: int = 20,
    increment: int = 10,
    max_seeds: int = 50,
    n_resamples: int = 2000,
    signal_length: int = 2000,
    profile_mem: bool = True,
) -> pd.DataFrame:
    """
    Orchestrates the full reproducibility audit.

    Args:
        systems: List of system names (default: all 7).
        modules: List of module names (default: all 9).
        dry_run: If True, uses 2 seeds, 5 resamples, 200-step signals.
        initial_seeds: Starting number of Sobol seeds.
        increment: Additional seeds per convergence check.
        max_seeds: Hard cap on seed count.
        n_resamples: BCa bootstrap resamples.
        signal_length: Dynamical system integration steps.
        profile_mem: Whether to profile peak RAM/VRAM.

    Returns:
        DataFrame with one row per (module, system) pair.
    """
    systems = systems or DEFAULT_SYSTEMS
    modules = modules or DEFAULT_MODULES

    if dry_run:
        log.info("DRY-RUN mode: reduced seeds and resamples.")
        initial_seeds = 2
        increment = 1
        max_seeds = 4
        n_resamples = 5
        signal_length = 200

    total_combos = len(modules) * len(systems)
    log.info(f"Starting reproducibility audit: {len(modules)} modules x {len(systems)} systems = {total_combos} combos")
    log.info(f"Sobol: initial={initial_seeds}, increment={increment}, max={max_seeds}, BCa resamples={n_resamples}")

    rows = []
    combo_idx = 0

    for mod in modules:
        for sys_name in systems:
            combo_idx += 1
            log.info(f"[{combo_idx}/{total_combos}] {mod} x {sys_name}")

            result = adaptive_evaluation(
                module=mod, system=sys_name,
                initial_seeds=initial_seeds, increment=increment,
                max_seeds=max_seeds, w_rel_threshold=0.05,
                n_resamples=n_resamples, signal_length=signal_length,
            )

            if profile_mem and "error" not in result:
                mem = profile_memory(mod, sys_name, signal_length=signal_length)
                result.update(mem)
            else:
                result["peak_ram_mb"] = float("nan")
                result["peak_vram_mb"] = float("nan")

            # Log brief summary
            status = result.get("convergence_status", "ERROR")
            stab = result.get("stability", "N/A")
            cv = result.get("cv", float("nan"))
            log.info(f"  → {status} | {stab} | CV={cv:.4f}" if not np.isnan(cv) else f"  → {status} | {stab} | CV=NaN")

            rows.append(result)

    df = pd.DataFrame(rows)
    # Drop raw_metrics column for the summary CSV (keep it in full JSON)
    df_summary = df.drop(columns=["raw_metrics"], errors="ignore")

    csv_path = OUT_DIR / "reproducibility_report.csv"
    df_summary.to_csv(csv_path, index=False)
    log.info(f"Reproducibility report saved to {csv_path}")

    # Full JSON with raw metrics
    json_path = OUT_DIR / "reproducibility_full.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=str)
    log.info(f"Full JSON with raw metrics saved to {json_path}")

    # Summary statistics
    _print_summary(df_summary)

    return df_summary


def _print_summary(df: pd.DataFrame):
    """Prints a concise audit summary to stdout."""
    n_total = len(df)
    n_converged = (df["convergence_status"] == "CONVERGED").sum() if "convergence_status" in df.columns else 0
    n_stable = (df["stability"] == "STABLE").sum() if "stability" in df.columns else 0

    print("\n" + "=" * 60)
    print("  PHASE 8A — REPRODUCIBILITY AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Total evaluations   : {n_total}")
    print(f"  Converged           : {n_converged} / {n_total} ({100*n_converged/max(n_total,1):.1f}%)")
    print(f"  Stable (CV < 0.05)  : {n_stable} / {n_total} ({100*n_stable/max(n_total,1):.1f}%)")

    if "cv" in df.columns:
        valid_cv = df["cv"].dropna()
        if len(valid_cv) > 0:
            print(f"  Median CV           : {valid_cv.median():.4f}")
            print(f"  Max CV              : {valid_cv.max():.4f}")

    if "peak_ram_mb" in df.columns:
        valid_ram = df["peak_ram_mb"].dropna()
        if len(valid_ram) > 0:
            print(f"  Peak RAM (max)      : {valid_ram.max():.1f} MB")

    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 8A — Reproducibility Audit with Sobol seeds and BCa bootstrap CI95"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Quick validation run (2 seeds, 5 resamples, 200 steps)")
    parser.add_argument("--systems", nargs="+", default=None,
                        help=f"Systems to evaluate (default: {DEFAULT_SYSTEMS})")
    parser.add_argument("--modules", nargs="+", default=None,
                        help=f"Modules to evaluate (default: {DEFAULT_MODULES})")
    parser.add_argument("--initial-seeds", type=int, default=20)
    parser.add_argument("--increment", type=int, default=10)
    parser.add_argument("--max-seeds", type=int, default=50)
    parser.add_argument("--n-resamples", type=int, default=2000)
    parser.add_argument("--signal-length", type=int, default=2000)
    parser.add_argument("--no-memory-profile", action="store_true",
                        help="Skip RAM/VRAM profiling (faster)")
    args = parser.parse_args()

    df = run_reproducibility_audit(
        systems=args.systems,
        modules=args.modules,
        dry_run=args.dry_run,
        initial_seeds=args.initial_seeds,
        increment=args.increment,
        max_seeds=args.max_seeds,
        n_resamples=args.n_resamples,
        signal_length=args.signal_length,
        profile_mem=not args.no_memory_profile,
    )

    # Print top-level table
    cols = ["module", "system", "convergence_status", "stability", "mean", "cv", "w_rel", "mean_time_s"]
    available = [c for c in cols if c in df.columns]
    print(df[available].to_string(index=False))


if __name__ == "__main__":
    main()
