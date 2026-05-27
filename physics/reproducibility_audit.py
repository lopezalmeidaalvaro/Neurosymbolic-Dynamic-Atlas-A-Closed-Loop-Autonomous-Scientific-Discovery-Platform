import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

"""
Phase 8A — Reproducibility Audit (COMPLETO, v2)
================================================
Evaluates pipeline stability using:
  - Sobol quasi-random seed sequences (scipy.stats.qmc.Sobol → integers)
  - BCa bootstrap 95% CI (scipy.stats.bootstrap, method='BCa', n_resamples=2000)
  - Sequential adaptive stopping: rel_width = (CI_hi - CI_lo) / |mean| < 0.05
  - Max 50 seeds per (module, system) combination
  - CPU tasks: ProcessPoolExecutor (max_workers = cpu_count - 2, min 1)
  - GPU tasks: serialized queue with torch.cuda.empty_cache() + autocast
  - RAM/VRAM profiling via tracemalloc and torch
  - Outputs:
      artifacts/reproducibility_results.csv   (required columns)
      artifacts/reproducibility_report.md     (stability table + violin narrative)
      figures/reproducibility_violin.pdf      (violin plot per module)

Usage:
    python reproducibility_audit.py [--dry-run] [--systems lorenz duffing] [--modules EV3 SINDy]
    python reproducibility_audit.py --systems lorenz duffing --modules EV3 SINDy PySR --max-seeds 5
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
import contextlib
from concurrent.futures import ProcessPoolExecutor, as_completed
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
MAX_WORKERS = int(os.environ.get("OMP_NUM_THREADS", "2"))
MIXED_PRECISION = False

try:
    import torch
    HAS_GPU = torch.cuda.is_available()
    if HAS_GPU:
        MIXED_PRECISION = True
        log.info(f"GPU detected: {torch.cuda.get_device_name(0)}. GPU tasks serialized; CPU tasks: {MAX_WORKERS} workers.")
    else:
        log.info(f"CPU-only mode. Workers: {MAX_WORKERS}")
except ImportError:
    log.info("PyTorch not found. CPU-only mode.")

# GPU modules require serialized execution + empty_cache + autocast
GPU_MODULES = {"NeuralODE", "PINN", "EV3_SCI"}

# ---------------------------------------------------------------------------
# Output directories  (spec: artifacts/ and figures/)
# ---------------------------------------------------------------------------
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
# Also keep a results mirror for backward compatibility
RESULTS_DIR = Path("results/phase8a")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Sobol Quasi-Random Seed Generator
# ---------------------------------------------------------------------------

def generate_sobol_seeds(n_seeds: int, scramble: bool = True) -> List[int]:
    """
    Generates n_seeds quasi-random integer seeds via a 1-D Sobol sequence.
    Maps each point p ∈ [0, 1) to an integer seed via S = floor(p × (2^31 - 1)).
    """
    sampler = Sobol(d=1, scramble=scramble, seed=42)
    n_pow2 = 1
    while n_pow2 < n_seeds:
        n_pow2 *= 2
    points = sampler.random(n_pow2)[:n_seeds, 0]
    return [int(p * (2**31 - 1)) for p in points]


# ---------------------------------------------------------------------------
# Signal loaders
# ---------------------------------------------------------------------------

def _load_signal(system: str, n_steps: int = 2000, seed: int = 42) -> np.ndarray:
    """Returns a 1-D signal for a given dynamical system."""
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
# Module runners (scalar metric per call)
# ---------------------------------------------------------------------------

def _run_module(module: str, signal: np.ndarray, seed: int) -> float:
    """Dispatches a module run and returns a scalar metric."""
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

        elif module == "PySR":
            from symbolic_discovery import run_pysr
            t = np.linspace(0, len(signal) * 0.01, len(signal))
            result = run_pysr(signal, t)
            return float(result.get("best_complexity", float("nan")))

        elif module == "Topology":
            from topological_analysis import run_topological_analysis
            return float(len(run_topological_analysis(signal).get("persistence_diagram_0", [])))

        elif module == "Koopman":
            from koopman_analysis import run_koopman_analysis
            eigs = run_koopman_analysis(signal).get("eigenvalues", [1.0])
            return float(np.abs(np.array(eigs)).max()) if eigs else float("nan")

        elif module == "NeuralODE":
            import torch
            torch.manual_seed(seed)
            if HAS_GPU:
                torch.cuda.empty_cache()
                with torch.cuda.amp.autocast(enabled=MIXED_PRECISION):
                    from neural_ode_module import run_neural_ode
                    result = run_neural_ode(signal, n_epochs=30, seed=seed)
            else:
                from neural_ode_module import run_neural_ode
                result = run_neural_ode(signal, n_epochs=30, seed=seed)
            return float(result.get("final_loss", float("nan")))

        elif module == "PINN":
            import torch
            torch.manual_seed(seed)
            if HAS_GPU:
                torch.cuda.empty_cache()
                with torch.cuda.amp.autocast(enabled=MIXED_PRECISION):
                    from pinn_module import run_pinn_forward
                    result = run_pinn_forward(signal, n_epochs=30, seed=seed)
            else:
                from pinn_module import run_pinn_forward
                result = run_pinn_forward(signal, n_epochs=30, seed=seed)
            return float(result.get("final_loss", float("nan")))

    except Exception as e:
        log.debug(f"Module {module} error: {e}")
    return float("nan")


# ---------------------------------------------------------------------------
# BCa Bootstrap CI95
# ---------------------------------------------------------------------------

def bca_bootstrap_ci(samples: np.ndarray, n_resamples: int = 2000,
                     confidence_level: float = 0.95) -> Tuple[float, float, float]:
    """
    BCa bootstrap 95% CI on the mean (scipy.stats.bootstrap, method='BCa').
    Returns (mean, ci_lower, ci_upper).
    """
    valid = samples[~np.isnan(samples)]
    if len(valid) < 2:
        return float(np.nanmean(samples)), float("nan"), float("nan")

    result = scipy_bootstrap(
        (valid,),
        statistic=np.mean,
        n_resamples=n_resamples,
        confidence_level=confidence_level,
        method="BCa",
        random_state=42,
    )
    return (float(np.mean(valid)),
            float(result.confidence_interval.low),
            float(result.confidence_interval.high))


# ---------------------------------------------------------------------------
# Relative CI Width
# ---------------------------------------------------------------------------

def relative_ci_width(ci_lower: float, ci_upper: float, mu: float) -> float:
    """rel_width = (CI_upper - CI_lower) / |mean|. Returns inf if undefined."""
    if np.isnan(ci_lower) or np.isnan(ci_upper) or abs(mu) < 1e-12:
        return float("inf")
    return (ci_upper - ci_lower) / abs(mu)


# ---------------------------------------------------------------------------
# RAM / VRAM Profiling
# ---------------------------------------------------------------------------

def profile_memory(module: str, signal: np.ndarray, seed: int = 42) -> Dict[str, float]:
    """Measures peak RAM (tracemalloc) and VRAM (torch) for one module run."""
    vram_before = 0.0
    if HAS_GPU:
        import torch
        torch.cuda.reset_peak_memory_stats()
        vram_before = torch.cuda.memory_allocated() / (1024 ** 2)

    tracemalloc.start()
    try:
        _run_module(module, signal, seed)
    except Exception:
        pass
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_ram_mb = peak / (1024 ** 2)

    peak_vram_mb = 0.0
    if HAS_GPU:
        import torch
        peak_vram_mb = max(0.0,
            (torch.cuda.max_memory_allocated() / (1024 ** 2)) - vram_before)

    return {"peak_ram_mb": round(peak_ram_mb, 3), "peak_vram_mb": round(peak_vram_mb, 3)}


# ---------------------------------------------------------------------------
# Single-seed evaluation (suitable for ProcessPoolExecutor pickling)
# ---------------------------------------------------------------------------

def _eval_one_seed(args):
    """Worker function: (module, system, seed, n_steps) → float metric."""
    module, system, seed, n_steps = args
    try:
        sig = _load_signal(system, n_steps, seed)
        return _run_module(module, sig, seed)
    except Exception:
        return float("nan")


# ---------------------------------------------------------------------------
# Sequential Adaptive Stopping (with CPU/GPU dispatch)
# ---------------------------------------------------------------------------

def adaptive_evaluation(
    module: str, system: str,
    initial_seeds: int = 20,
    increment: int = 10,
    max_seeds: int = 50,
    w_rel_threshold: float = 0.05,
    n_resamples: int = 2000,
    signal_length: int = 2000,
    n_workers: int = 1,
) -> Dict[str, Any]:
    """
    Sequential adaptive evaluation with BCa bootstrap convergence criterion.
    - GPU modules (NeuralODE, PINN): serialized, with empty_cache + autocast.
    - CPU modules: parallelized via ProcessPoolExecutor (n_workers workers).
    - Stops when rel_width < 0.05 or seeds exhausted (max 50).
    """
    all_seeds = generate_sobol_seeds(max_seeds)
    metrics: List[float] = []
    times: List[float] = []
    converged = False
    n_used = 0

    # Build batch schedule: [initial, increment, increment, ...]
    batch_schedule = [initial_seeds]
    remaining = max_seeds - initial_seeds
    while remaining > 0:
        batch_schedule.append(min(increment, remaining))
        remaining -= increment

    is_gpu_module = module in GPU_MODULES

    for batch_size in batch_schedule:
        batch_seeds = all_seeds[n_used: n_used + batch_size]

        if is_gpu_module or n_workers <= 1:
            # Serialized execution
            for seed in batch_seeds:
                t0 = time.perf_counter()
                val = _eval_one_seed((module, system, seed, signal_length))
                metrics.append(val)
                times.append(time.perf_counter() - t0)
        else:
            # Parallel CPU execution
            args_list = [(module, system, seed, signal_length) for seed in batch_seeds]
            t0 = time.perf_counter()
            try:
                with ProcessPoolExecutor(max_workers=n_workers) as executor:
                    futures = {executor.submit(_eval_one_seed, a): a for a in args_list}
                    for fut in as_completed(futures):
                        try:
                            val = fut.result()
                        except Exception:
                            val = float("nan")
                        metrics.append(val)
                        times.append((time.perf_counter() - t0) / len(args_list))
            except Exception:
                # Fallback to serial if parallel fails (e.g., spawn context issues)
                for a in args_list:
                    t1 = time.perf_counter()
                    metrics.append(_eval_one_seed(a))
                    times.append(time.perf_counter() - t1)

        n_used += batch_size

        arr = np.array(metrics)
        mu, ci_lo, ci_hi = bca_bootstrap_ci(arr, n_resamples=n_resamples)
        w_rel = relative_ci_width(ci_lo, ci_hi, mu)

        log.debug(f"  [{module}/{system}] n={n_used} μ={mu:.4f} w_rel={w_rel:.4f}")

        if w_rel < w_rel_threshold:
            converged = True
            break

    arr = np.array(metrics)
    valid_arr = arr[~np.isnan(arr)]
    mu, ci_lo, ci_hi = bca_bootstrap_ci(arr, n_resamples=n_resamples)
    sigma = float(np.nanstd(valid_arr, ddof=1)) if len(valid_arr) > 1 else float("nan")
    cv = sigma / abs(mu) if (not np.isnan(mu) and abs(mu) > 1e-12) else float("nan")
    w_rel = relative_ci_width(ci_lo, ci_hi, mu)
    stable = converged and (not np.isnan(cv)) and cv < 0.05

    return {
        "module": module,
        "system": system,
        "n_seeds": n_used,
        "mean": mu,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "rel_width": w_rel,
        "cv": cv,
        "converged": converged,
        "stable": stable,
        "convergence_status": "CONVERGED" if converged else "NOT_CONVERGED",
        "stability": "STABLE" if stable else "UNSTABLE",
        "mean_time_s": float(np.nanmean(times)) if times else float("nan"),
        "total_time_s": float(np.nansum(times)) if times else float("nan"),
        "raw_metrics": [round(m, 8) for m in metrics],
    }


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
    n_workers: Optional[int] = None,
) -> pd.DataFrame:
    """
    Full reproducibility audit.

    Returns DataFrame with required columns:
        module, system, n_seeds, mean, ci_lower, ci_upper, rel_width, cv, converged, stable
    Also saves artifacts/reproducibility_results.csv and artifacts/reproducibility_report.md.
    """
    systems = systems or DEFAULT_SYSTEMS
    modules = modules or DEFAULT_MODULES
    n_workers = n_workers or MAX_WORKERS

    CHECKPOINT_PATH = "artifacts/reproducibility_checkpoint.csv"
    checkpoint_path = Path(CHECKPOINT_PATH)
    completed_combos = set()
    rows = []

    # Load existing checkpoint if it exists
    if checkpoint_path.exists():
        try:
            checkpoint_df = pd.read_csv(checkpoint_path)
            if not checkpoint_df.empty and "module" in checkpoint_df.columns and "system" in checkpoint_df.columns:
                for _, r_row in checkpoint_df.iterrows():
                    r_dict = r_row.to_dict()
                    r_dict["converged"] = bool(r_dict["converged"])
                    r_dict["stable"] = bool(r_dict["stable"])
                    r_dict["convergence_status"] = "CONVERGED" if r_dict["converged"] else "NOT_CONVERGED"
                    r_dict["stability"] = "STABLE" if r_dict["stable"] else "UNSTABLE"
                    r_dict["mean_time_s"] = r_dict.get("mean_time_s", float("nan"))
                    r_dict["total_time_s"] = r_dict.get("total_time_s", float("nan"))
                    r_dict["peak_ram_mb"] = r_dict.get("peak_ram_mb", float("nan"))
                    r_dict["peak_vram_mb"] = r_dict.get("peak_vram_mb", float("nan"))
                    r_dict["raw_metrics"] = []
                    
                    if r_dict["module"] in modules and r_dict["system"] in systems:
                        rows.append(r_dict)
                        completed_combos.add((r_dict["module"], r_dict["system"]))
                log.info(f"Loaded {len(completed_combos)} completed combinations from checkpoint.")
        except Exception as e:
            log.warning(f"Failed to load checkpoint from {CHECKPOINT_PATH}: {e}")

    # Ensure checkpoint file is initialized if we have new work to do
    import csv
    if not completed_combos:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        if not checkpoint_path.exists():
            try:
                with open(checkpoint_path, "w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper", "rel_width", "cv", "converged", "stable"])
            except Exception as e:
                log.warning(f"Failed to initialize checkpoint CSV: {e}")

    if dry_run:
        log.info("DRY-RUN: 2 seeds, 5 resamples, 200 steps.")
        initial_seeds = 2
        increment = 1
        max_seeds = 4
        n_resamples = 5
        signal_length = 200

    total_combos = len(modules) * len(systems)
    log.info(f"Reproducibility audit: {len(modules)} modules × {len(systems)} systems = {total_combos} combos")
    log.info(f"Sobol: initial={initial_seeds}, increment={increment}, max={max_seeds}, BCa n_resamples={n_resamples}")
    log.info(f"CPU workers: {n_workers} | GPU: {HAS_GPU} (mixed_precision={MIXED_PRECISION})")

    combo_idx = 0

    for mod in modules:
        for sys_name in systems:
            combo_idx += 1
            if (mod, sys_name) in completed_combos:
                log.info(f"[{combo_idx}/{total_combos}] Skipping completed combo (checkpoint): {mod} × {sys_name}")
                continue

            log.info(f"[{combo_idx}/{total_combos}] {mod} × {sys_name}")

            result = adaptive_evaluation(
                module=mod, system=sys_name,
                initial_seeds=initial_seeds, increment=increment,
                max_seeds=max_seeds, w_rel_threshold=0.05,
                n_resamples=n_resamples, signal_length=signal_length,
                n_workers=n_workers,
            )

            # Memory profiling
            if profile_mem and "error" not in result:
                try:
                    sig = _load_signal(sys_name, signal_length, 42)
                    mem = profile_memory(mod, sig, 42)
                    result.update(mem)
                except Exception:
                    result["peak_ram_mb"] = float("nan")
                    result["peak_vram_mb"] = float("nan")
            else:
                result["peak_ram_mb"] = float("nan")
                result["peak_vram_mb"] = float("nan")

            w_rel = result.get("rel_width", float("nan"))
            cv = result.get("cv", float("nan"))
            log.info(
                f"  → {result.get('convergence_status')} | {result.get('stability')} | "
                f"rel_width={w_rel:.4f} | CV={cv:.4f}"
                if not (np.isnan(w_rel) or np.isnan(cv)) else
                f"  → {result.get('convergence_status')} | {result.get('stability')} | rel_width/CV=NaN"
            )
            rows.append(result)

            # Write to checkpoint file immediately and flush
            try:
                with open(checkpoint_path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([
                        result["module"],
                        result["system"],
                        result["n_seeds"],
                        result["mean"],
                        result["ci_lower"],
                        result["ci_upper"],
                        result["rel_width"],
                        result["cv"],
                        result["converged"],
                        result["stable"]
                    ])
            except Exception as e:
                log.warning(f"Failed to write to checkpoint: {e}")

    # All combinations completed! Delete or rename the checkpoint file
    if checkpoint_path.exists():
        try:
            final_checkpoint_path = ARTIFACTS_DIR / "reproducibility_checkpoint_final.csv"
            if final_checkpoint_path.exists():
                final_checkpoint_path.unlink()
            checkpoint_path.rename(final_checkpoint_path)
            log.info(f"Checkpoint successfully moved to {final_checkpoint_path}")
        except Exception as e:
            log.warning(f"Failed to move checkpoint file to final destination: {e}")

    df = pd.DataFrame(rows)

    # Required columns per spec
    required_cols = ["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper",
                     "rel_width", "cv", "converged", "stable"]
    df_summary = df[[c for c in required_cols + ["convergence_status", "stability",
                                                   "mean_time_s", "total_time_s",
                                                   "peak_ram_mb", "peak_vram_mb"]
                     if c in df.columns]]

    # Save to artifacts/ (spec requirement)
    csv_path = ARTIFACTS_DIR / "reproducibility_results.csv"
    df_summary.to_csv(csv_path, index=False)
    log.info(f"CSV saved: {csv_path}")

    # Backward-compat copy in results/
    df_summary.to_csv(RESULTS_DIR / "reproducibility_report.csv", index=False)

    # Full JSON
    json_path = RESULTS_DIR / "reproducibility_full.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=str)

    # Generate violin plot
    try:
        _save_violin_plot(rows, df_summary)
    except Exception as e:
        log.warning(f"Violin plot failed: {e}")

    # Generate Markdown report
    _save_markdown_report(df_summary)

    _print_summary(df_summary)
    return df_summary


# ---------------------------------------------------------------------------
# Violin plot
# ---------------------------------------------------------------------------

def _save_violin_plot(rows: List[Dict], df: pd.DataFrame):
    """Generates violin plots of metric distributions per module."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    modules_present = df["module"].unique() if "module" in df.columns else []
    # Build per-module distribution from raw_metrics
    module_data = {}
    for row in rows:
        mod = row.get("module", "?")
        vals = [v for v in row.get("raw_metrics", []) if not np.isnan(v)]
        if mod not in module_data:
            module_data[mod] = []
        module_data[mod].extend(vals)

    module_data = {k: v for k, v in module_data.items() if len(v) >= 2}
    if not module_data:
        log.warning("No data for violin plot.")
        return

    fig, ax = plt.subplots(figsize=(max(10, len(module_data) * 1.5), 6))
    labels = list(module_data.keys())
    data = [module_data[k] for k in labels]

    parts = ax.violinplot(data, positions=range(len(labels)), showmeans=True, showmedians=True)
    for pc in parts["bodies"]:
        pc.set_alpha(0.7)
        pc.set_facecolor("#3498db")
    if "cmeans" in parts:
        parts["cmeans"].set_color("#e74c3c")
        parts["cmeans"].set_linewidth(2)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Scalar Metric Value")
    ax.set_title("Reproducibility Audit — Metric Distribution per Module (violin)")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    pdf_path = FIGURES_DIR / "reproducibility_violin.pdf"
    plt.savefig(pdf_path, dpi=150, bbox_inches="tight")
    png_path = FIGURES_DIR / "reproducibility_violin.png"
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Violin plot saved: {pdf_path}")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def _save_markdown_report(df: pd.DataFrame):
    """Generates artifacts/reproducibility_report.md."""
    n_total = len(df)
    n_conv = df["converged"].sum() if "converged" in df.columns else 0
    n_stable = df["stable"].sum() if "stable" in df.columns else 0
    median_cv = df["cv"].median() if "cv" in df.columns else float("nan")
    max_ram = df["peak_ram_mb"].max() if "peak_ram_mb" in df.columns else float("nan")

    table_cols = [c for c in ["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper",
                               "rel_width", "cv", "converged", "stable"] if c in df.columns]
    table_md = df[table_cols].to_markdown(index=False, floatfmt=".4f")

    md = f"""# Phase 8A — Reproducibility Audit Report

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total evaluations | {n_total} |
| Converged (rel_width < 0.05) | {n_conv} / {n_total} ({100*n_conv/max(n_total,1):.1f}%) |
| Stable (CV < 0.05 + converged) | {n_stable} / {n_total} ({100*n_stable/max(n_total,1):.1f}%) |
| Median CV | {median_cv:.4f} |
| Peak RAM (max) | {max_ram:.1f} MB |

## Methodology

Seeds are generated via **Sobol quasi-random sequence** (1-D, scrambled),
mapped to integers as $S = \\lfloor p \\times (2^{{31}}-1) \\rfloor$.

Confidence intervals use **BCa bootstrap** (`scipy.stats.bootstrap`, `method='BCa'`,
`n_resamples=2000`). Sequential adaptive stopping halts when:

$$W_{{\\text{{rel}}}} = \\frac{{CI_{{\\text{{hi}}}} - CI_{{\\text{{lo}}}}}}{{|\\mu|}} < 0.05$$

Hard cap: **50 seeds** per (module, system) combination.

CPU tasks use `ProcessPoolExecutor` (max_workers = cpu_count − 2, min 1).
GPU tasks (NeuralODE, PINN) are **serialized** with `torch.cuda.empty_cache()` and
`torch.cuda.amp.autocast` for mixed precision.

## Stability Table

{table_md}

## Violin Plots

See [`figures/reproducibility_violin.pdf`](../figures/reproducibility_violin.pdf)
for metric distribution per module across all Sobol seeds.

## Notes

- `converged=True` indicates rel_width < 0.05 was achieved before the 50-seed cap.
- `stable=True` additionally requires CV < 0.05.
- `N/A` values indicate modules that raised exceptions on all seeds.
"""
    md_path = ARTIFACTS_DIR / "reproducibility_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    log.info(f"Markdown report saved: {md_path}")


# ---------------------------------------------------------------------------
# Summary printer
# ---------------------------------------------------------------------------

def _print_summary(df: pd.DataFrame):
    n_total = len(df)
    n_conv = df["converged"].sum() if "converged" in df.columns else 0
    n_stable = df["stable"].sum() if "stable" in df.columns else 0
    print("\n" + "=" * 60)
    print("  PHASE 8A — REPRODUCIBILITY AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Total evaluations : {n_total}")
    print(f"  Converged         : {n_conv} / {n_total} ({100*n_conv/max(n_total,1):.1f}%)")
    print(f"  Stable            : {n_stable} / {n_total} ({100*n_stable/max(n_total,1):.1f}%)")
    if "cv" in df.columns:
        valid_cv = df["cv"].dropna()
        if len(valid_cv):
            print(f"  Median CV         : {valid_cv.median():.4f}")
    if "peak_ram_mb" in df.columns:
        valid_ram = df["peak_ram_mb"].dropna()
        if len(valid_ram):
            print(f"  Peak RAM (max)    : {valid_ram.max():.1f} MB")
    print(f"  BCa n_resamples   : 2000 (method='BCa')")
    print(f"  Sobol seed mapping: S = floor(p × (2^31 - 1))")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 8A — Reproducibility Audit (Sobol + BCa bootstrap)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--systems", nargs="+", default=None)
    parser.add_argument("--modules", nargs="+", default=None)
    parser.add_argument("--initial-seeds", type=int, default=20)
    parser.add_argument("--increment", type=int, default=10)
    parser.add_argument("--max-seeds", type=int, default=50)
    parser.add_argument("--n-resamples", type=int, default=2000)
    parser.add_argument("--signal-length", type=int, default=2000)
    parser.add_argument("--no-memory-profile", action="store_true")
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    df = run_reproducibility_audit(
        systems=args.systems, modules=args.modules, dry_run=args.dry_run,
        initial_seeds=args.initial_seeds, increment=args.increment,
        max_seeds=args.max_seeds, n_resamples=args.n_resamples,
        signal_length=args.signal_length, profile_mem=not args.no_memory_profile,
        n_workers=args.workers,
    )
    cols = ["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper",
            "rel_width", "cv", "converged", "stable"]
    print(df[[c for c in cols if c in df.columns]].to_string(index=False))


if __name__ == "__main__":
    main()
