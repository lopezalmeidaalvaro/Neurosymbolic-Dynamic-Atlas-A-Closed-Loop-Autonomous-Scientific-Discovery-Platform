import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

"""
Phase 8D — Auto Paper Generator (COMPLETO, v2)
================================================
Generates a scientific manuscript reading REAL data from:
  - artifacts/reproducibility_results.csv  (8A)
  - artifacts/ablation_results.csv         (8B)
  - artifacts/robustness_results.csv       (8E)
  - artifacts/sota_results.csv             (8C)
  - artifacts/benchmark_report.md          (original benchmark)
  - artifacts/redundancy_results.csv       (feature redundancy)

Rules:
  - NO invented numbers. Missing data → "N/A" documented in Threats to Validity.
  - 6 Threats to Validity subsections (5.1–5.6).
  - Computational Cost table (module, time, RAM, VRAM).
  - All text sanitized via scientific_guard.sanitize_hypothesis().
  - Generates: papers/system_paper.tex, papers/system_paper.md,
               papers/references.bib, papers/system_paper.pdf (pdflatex, 3 passes).

Usage:
    python auto_paper_generator.py [--dry-run] [--skip-pdf]
"""

import sys
import io
import os
import json
import subprocess
import argparse
import warnings
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import numpy as np
import pandas as pd

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [8D] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("auto_paper_generator")

PAPERS_DIR = Path("papers")
PAPERS_DIR.mkdir(exist_ok=True)

ARTIFACTS_DIR = Path("artifacts")
RESULTS_DIR = Path("results")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_read_csv(path: Path) -> Optional[pd.DataFrame]:
    try:
        if path.exists():
            return pd.read_csv(path)
    except Exception as e:
        log.warning(f"Could not read {path}: {e}")
    return None


def _fmt(val: Any, decimals: int = 4, suffix: str = "") -> str:
    """Returns formatted float or 'N/A' for NaN/None."""
    if val is None or (isinstance(val, float) and (val != val)):  # isnan
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}{suffix}"
    except Exception:
        return str(val) if val is not None else "N/A"


# ---------------------------------------------------------------------------
# Data ingestion — reads ALL 6 sources
# ---------------------------------------------------------------------------

def _load_all_results() -> Dict[str, Any]:
    """Loads all Phase 8 results from artifacts/ and results/. Never invents data."""
    results = {}

    # 8A — Reproducibility (spec: artifacts/reproducibility_results.csv)
    results["reproducibility"] = (
        _safe_read_csv(ARTIFACTS_DIR / "reproducibility_results.csv") or
        _safe_read_csv(RESULTS_DIR / "phase8a" / "reproducibility_report.csv")
    )

    # 8B — Ablation (spec: artifacts/ablation_results.csv)
    results["ablation"] = (
        _safe_read_csv(ARTIFACTS_DIR / "ablation_results.csv") or
        _safe_read_csv(RESULTS_DIR / "phase8b" / "ablation_report.csv")
    )

    # 8B summary
    results["ablation_summary"] = _safe_read_csv(ARTIFACTS_DIR / "ablation_summary.csv")

    # 8C — SOTA (spec: artifacts/sota_results.csv)
    results["sota"] = (
        _safe_read_csv(ARTIFACTS_DIR / "sota_results.csv") or
        _safe_read_csv(RESULTS_DIR / "phase8c" / "sota_benchmark.csv")
    )

    # 8E — Robustness (spec: artifacts/robustness_results.csv)
    results["robustness"] = (
        _safe_read_csv(ARTIFACTS_DIR / "robustness_results.csv") or
        _safe_read_csv(RESULTS_DIR / "phase8e" / "robustness_noise.csv")
    )
    results["robustness_noise"] = _safe_read_csv(RESULTS_DIR / "phase8e" / "robustness_noise.csv")
    results["robustness_missing"] = _safe_read_csv(RESULTS_DIR / "phase8e" / "robustness_missing_data.csv")
    results["robustness_ood"] = _safe_read_csv(RESULTS_DIR / "phase8e" / "robustness_ood.csv")

    # Benchmark report (original phase: benchmark_report.md, benchmark_scientific_results.csv)
    results["benchmark_csv"] = (
        _safe_read_csv(ARTIFACTS_DIR / "benchmark_scientific_results.csv") or
        _safe_read_csv(ARTIFACTS_DIR / "benchmark_report.csv")
    )

    # Feature redundancy (feature_redundancy_analysis.py output)
    results["redundancy"] = (
        _safe_read_csv(ARTIFACTS_DIR / "feature_redundancy_report.csv") or
        _safe_read_csv(ARTIFACTS_DIR / "correlated_features.json".replace(".json", ".csv"))
    )

    # Log availability
    for k, v in results.items():
        status = "OK" if v is not None and not (hasattr(v, "empty") and v.empty) else "MISSING"
        log.info(f"  [{status}] {k}")

    return results


# ---------------------------------------------------------------------------
# Key statistics extractor
# ---------------------------------------------------------------------------

def _extract_key_stats(results: Dict[str, Any]) -> Dict[str, str]:
    """Extracts publication-ready statistics. Returns 'N/A' for all missing data."""
    stats = {}

    # 8A — Reproducibility
    df = results.get("reproducibility")
    if df is not None and not df.empty:
        n_total = len(df)
        n_conv = int((df["converged"] == True).sum()) if "converged" in df.columns else 0  # noqa
        n_stable = int((df["stable"] == True).sum()) if "stable" in df.columns else 0  # noqa
        median_cv = df["cv"].dropna().median() if "cv" in df.columns else float("nan")
        max_ram = df["peak_ram_mb"].dropna().max() if "peak_ram_mb" in df.columns else float("nan")
        max_vram = df["peak_vram_mb"].dropna().max() if "peak_vram_mb" in df.columns else float("nan")
        stats["repro_total"] = str(n_total)
        stats["repro_converged_pct"] = _fmt(100 * n_conv / max(n_total, 1), 1, "%")
        stats["repro_stable_pct"] = _fmt(100 * n_stable / max(n_total, 1), 1, "%")
        stats["repro_median_cv"] = _fmt(median_cv, 4)
        stats["repro_max_ram_mb"] = _fmt(max_ram, 1)
        stats["repro_max_vram_mb"] = _fmt(max_vram, 1)
        stats["repro_mean_time_s"] = _fmt(df["mean_time_s"].dropna().mean(), 2) if "mean_time_s" in df.columns else "N/A"
    else:
        for k in ["repro_total", "repro_converged_pct", "repro_stable_pct",
                  "repro_median_cv", "repro_max_ram_mb", "repro_max_vram_mb", "repro_mean_time_s"]:
            stats[k] = "N/A"

    # 8B — Ablation
    df = results.get("ablation")
    if df is not None and not df.empty and "cohens_d" in df.columns:
        top = df.nlargest(1, "cohens_d")
        stats["ablation_top_config"] = str(top["ablation"].iloc[0]) if len(top) > 0 else "N/A"
        stats["ablation_top_d"] = _fmt(top["cohens_d"].iloc[0]) if len(top) > 0 else "N/A"
        large_count = int((df["impact"] == "Large").sum()) if "impact" in df.columns else 0
        bypass_count = int((df["status"] == "DEPENDENCY_BYPASS").sum()) if "status" in df.columns else 0
        stats["ablation_large_count"] = str(large_count)
        stats["ablation_bypass_count"] = str(bypass_count)
    else:
        for k in ["ablation_top_config", "ablation_top_d",
                  "ablation_large_count", "ablation_bypass_count"]:
            stats[k] = "N/A"

    # 8C — SOTA
    df = results.get("sota")
    if df is not None and not df.empty:
        ok_count = int((df["status"] == "OK").sum()) if "status" in df.columns else 0
        ne_count = int((df["status"] == "NOT_EVALUATED").sum()) if "status" in df.columns else 0
        stats["sota_ok_count"] = str(ok_count)
        stats["sota_not_eval_count"] = str(ne_count)
        # Win rates from sota_summary if available
        df_sum = results.get("ablation_summary")  # reuse safe_read for sota_summary
        sota_sum = _safe_read_csv(ARTIFACTS_DIR / "sota_summary.csv")
        if sota_sum is not None and "win_rate_real" in sota_sum.columns:
            stats["sota_win_rate_real"] = _fmt(sota_sum["win_rate_real"].iloc[0], 2, "")
            stats["sota_win_rate_total"] = _fmt(sota_sum["win_rate_total"].iloc[0], 2, "")
        else:
            stats["sota_win_rate_real"] = "N/A"
            stats["sota_win_rate_total"] = "N/A"
    else:
        for k in ["sota_ok_count", "sota_not_eval_count",
                  "sota_win_rate_real", "sota_win_rate_total"]:
            stats[k] = "N/A"

    # 8E — Robustness
    df_noise = results.get("robustness_noise")
    if df_noise is not None and not df_noise.empty and "NRS" in df_noise.columns:
        best_nrs_mod = df_noise.groupby("module")["NRS"].mean().idxmax() if "module" in df_noise.columns else "N/A"
        stats["noise_best_module"] = str(best_nrs_mod)
        stats["noise_mean_nrs"] = _fmt(df_noise["NRS"].mean(), 4)
    else:
        stats["noise_best_module"] = "N/A"
        stats["noise_mean_nrs"] = "N/A"

    df_ood = results.get("robustness_ood")
    if df_ood is not None and not df_ood.empty and "generalization_gap" in df_ood.columns:
        stats["ood_mean_gap"] = _fmt(df_ood["generalization_gap"].mean(), 4)
    else:
        stats["ood_mean_gap"] = "N/A"

    df_miss = results.get("robustness_missing")
    if df_miss is not None and not df_miss.empty and "MDT" in df_miss.columns:
        stats["mean_mdt"] = _fmt(df_miss["MDT"].mean() * 100, 1, "%")
    else:
        stats["mean_mdt"] = "N/A"

    # Benchmark
    df_bench = results.get("benchmark_csv")
    if df_bench is not None and not df_bench.empty:
        n_ok = int((df_bench.get("status", pd.Series()) == "OK").sum()) if "status" in df_bench.columns else 0
        stats["benchmark_ok_count"] = str(n_ok)
    else:
        stats["benchmark_ok_count"] = "N/A"

    # Feature redundancy
    df_red = results.get("redundancy")
    if df_red is not None and not df_red.empty:
        stats["redundancy_n_redundant"] = str(len(df_red))
    else:
        stats["redundancy_n_redundant"] = "N/A"

    return stats


# ---------------------------------------------------------------------------
# Scientific Guard
# ---------------------------------------------------------------------------

def _sanitize(text: str) -> str:
    try:
        from scientific_guard import sanitize_hypothesis
        return sanitize_hypothesis(text)
    except ImportError:
        return text


# ---------------------------------------------------------------------------
# Computational cost table
# ---------------------------------------------------------------------------

def _build_cost_table(results: Dict[str, Any]) -> str:
    """Builds a Markdown table of computational costs from reproducibility data."""
    df = results.get("reproducibility")
    if df is None or df.empty:
        return "_No computational cost data available (Phase 8A not run)._"

    cost_cols = [c for c in ["module", "mean_time_s", "peak_ram_mb", "peak_vram_mb"]
                 if c in df.columns]
    if "module" not in cost_cols:
        return "_No module column in reproducibility data._"

    agg = df.groupby("module").agg({
        c: "mean" for c in cost_cols if c != "module"
    }).reset_index()

    # Rename for the table
    rename = {"mean_time_s": "Mean Time (s)", "peak_ram_mb": "Peak RAM (MB)",
               "peak_vram_mb": "Peak VRAM (MB)"}
    agg = agg.rename(columns=rename)

    # Format N/A
    for col in agg.columns:
        if col != "module":
            agg[col] = agg[col].apply(lambda x: _fmt(x, 2) if not isinstance(x, str) else x)

    return agg.to_markdown(index=False)


# ---------------------------------------------------------------------------
# Bibliography
# ---------------------------------------------------------------------------

BIB_CONTENT = r"""@article{chen2018neural,
  title={Neural ordinary differential equations},
  author={Chen, Ricky TQ and Rubanova, Yulia and Bettencourt, Jesse and Duvenaud, David},
  journal={Advances in neural information processing systems},
  volume={31},
  year={2018}
}

@article{brunton2016discovering,
  title={Discovering governing equations from data by sparse identification of nonlinear dynamical systems},
  author={Brunton, Steven L and Proctor, Joshua L and Kutz, J Nathan},
  journal={Proceedings of the national academy of sciences},
  volume={113},
  number={15},
  pages={3932--3937},
  year={2016}
}

@article{cranmer2020discovering,
  title={Discovering symbolic models from deep learning with inductive biases},
  author={Cranmer, Miles and Sanchez Gonzalez, Alvaro and others},
  journal={Advances in Neural Information Processing Systems},
  volume={33},
  pages={17429--17442},
  year={2020}
}

@article{edelsbrunner2008persistent,
  title={Persistent homology---a survey},
  author={Edelsbrunner, Herbert and Harer, John},
  journal={Contemporary mathematics},
  volume={453},
  pages={257--282},
  year={2008}
}

@article{schmid2010dynamic,
  title={Dynamic mode decomposition of numerical and experimental data},
  author={Schmid, Peter J},
  journal={Journal of fluid mechanics},
  volume={656},
  pages={5--28},
  year={2010}
}

@article{raissi2019physics,
  title={Physics-informed neural networks: A deep learning framework for solving forward and inverse problems},
  author={Raissi, Maziar and Perdikaris, Paris and Karniadakis, George Em},
  journal={Journal of Computational Physics},
  volume={378},
  pages={686--707},
  year={2019}
}

@article{lorenz1963deterministic,
  title={Deterministic nonperiodic flow},
  author={Lorenz, Edward N},
  journal={Journal of atmospheric sciences},
  volume={20},
  number={2},
  pages={130--141},
  year={1963}
}

@book{cohen1988statistical,
  title={Statistical power analysis for the behavioral sciences},
  author={Cohen, Jacob},
  year={1988},
  publisher={Lawrence Erlbaum Associates}
}

@book{efron1994introduction,
  title={An introduction to the bootstrap},
  author={Efron, Bradley and Tibshirani, Robert J},
  year={1994},
  publisher={CRC press}
}

@article{joe2003remark,
  title={Remark on algorithm 659: Implementing Sobol's quasirandom sequence generator},
  author={Joe, Stephen and Kuo, Frances Y},
  journal={ACM Transactions on Mathematical Software},
  volume={29},
  number={1},
  pages={49--57},
  year={2003}
}
"""


def save_bibliography():
    path = PAPERS_DIR / "references.bib"
    with open(path, "w", encoding="utf-8") as f:
        f.write(BIB_CONTENT)
    log.info(f"Bibliography saved: {path}")


# ---------------------------------------------------------------------------
# Markdown paper
# ---------------------------------------------------------------------------

def generate_markdown_paper(stats: Dict[str, str], results: Dict[str, Any]) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")

    # Tables
    df_repro = results.get("reproducibility")
    repro_table = "_No data — run Phase 8A first._"
    if df_repro is not None and not df_repro.empty:
        cols = [c for c in ["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper",
                             "rel_width", "cv", "converged", "stable"] if c in df_repro.columns]
        repro_table = df_repro[cols].head(20).to_markdown(index=False, floatfmt=".4f")

    df_abl = results.get("ablation")
    abl_table = "_No data — run Phase 8B first._"
    if df_abl is not None and not df_abl.empty and "cohens_d" in df_abl.columns:
        cols = [c for c in ["ablation", "system", "module", "delta_pct", "cohens_d",
                             "ci95_lower", "ci95_upper", "impact", "status"] if c in df_abl.columns]
        abl_table = df_abl.nlargest(15, "cohens_d")[cols].to_markdown(index=False, floatfmt=".3f")

    df_sota = results.get("sota")
    sota_table = "_No data — run Phase 8C first._"
    if df_sota is not None and not df_sota.empty:
        cols = [c for c in ["baseline", "system", "metric", "metric_value", "time_s",
                             "accuracy_per_sec", "status"] if c in df_sota.columns]
        sota_table = df_sota[cols].groupby(["baseline", "metric"]).agg(
            mean_value=("metric_value", "mean"), mean_time=("time_s", "mean")
        ).reset_index().to_markdown(index=False, floatfmt=".4f")

    cost_table = _build_cost_table(results)

    na_fields = [k for k, v in stats.items() if v == "N/A"]

    md = _sanitize(f"""# Neuro-Symbolic Dynamic Atlas: Comprehensive Evaluation Report

**Date:** {date_str}
**Version:** Phase 8 — Automated Evaluation Report

> **Disclaimer**: All results are model-specific observations derived from numerical simulations
> of chaotic dynamical systems (Lorenz, Duffing, Van der Pol, Rössler, Logistic Map).
> No claims are made about real physical systems, universal laws, or out-of-domain performance.

---

## Abstract

We present a systematic evaluation of the Neuro-Symbolic Dynamic Atlas pipeline across
{stats.get('repro_total', 'N/A')} module-system combinations (Phase 8A).
Reproducibility analysis using Sobol quasi-random seeds and BCa bootstrap confidence intervals
shows {stats.get('repro_converged_pct', 'N/A')} of evaluations converge within relative CI
width < 5%, with {stats.get('repro_stable_pct', 'N/A')} classified as stable
(CV < 0.05, median CV = {stats.get('repro_median_cv', 'N/A')}).
Ablation analysis (Phase 8B) identifies {stats.get('ablation_large_count', 'N/A')} large-impact
module removals (|d| ≥ 0.8), with the highest impact from `{stats.get('ablation_top_config', 'N/A')}`
(d = {stats.get('ablation_top_d', 'N/A')}).
Noise robustness (Phase 8E): mean NRS = {stats.get('noise_mean_nrs', 'N/A')}
(best module: {stats.get('noise_best_module', 'N/A')}).
Mean OOD generalization gap: {stats.get('ood_mean_gap', 'N/A')}.

---

## 1. Introduction

Scientific machine learning pipelines require rigorous validation beyond held-out accuracy.
This report evaluates the Neuro-Symbolic Dynamic Atlas along four orthogonal axes:
(1) statistical reproducibility across randomized initializations,
(2) modular ablation sensitivity with DAG-aware dependency resolution,
(3) comparison against SOTA reference implementations,
and (4) robustness under measurement degradation and distribution shift.

---

## 2. Reproducibility Audit (Phase 8A)

### 2.1 Methodology

Seeds are generated via Sobol quasi-random sequence mapped to integers as
$S = \\lfloor p \\times (2^{{31}} - 1) \\rfloor$.
Confidence intervals use BCa bootstrap (`scipy.stats.bootstrap`, method='BCa',
n_resamples=2000).
Sequential adaptive stopping: $W_{{\\text{{rel}}}} = (CI_{{hi}} - CI_{{lo}}) / |\\mu| < 0.05$
(max 50 seeds per combination).
Stability: CV = $\\sigma/\\mu < 0.05$ AND converged.

### 2.2 Results

| Metric | Value |
|--------|-------|
| Total evaluations | {stats.get('repro_total', 'N/A')} |
| Converged (W_rel < 0.05) | {stats.get('repro_converged_pct', 'N/A')} |
| Stable (CV < 0.05) | {stats.get('repro_stable_pct', 'N/A')} |
| Median CV | {stats.get('repro_median_cv', 'N/A')} |
| Peak RAM | {stats.get('repro_max_ram_mb', 'N/A')} MB |
| Peak VRAM | {stats.get('repro_max_vram_mb', 'N/A')} MB |

**Sample results** (first 20 rows):

{repro_table}

---

## 3. Ablation Study (Phase 8B)

### 3.1 Methodology

Nine ablation configurations systematically disable pipeline components.
A DAG-aware resolver cascades disabling to all downstream dependents.
When a dependency is missing, an AR(p) fallback metric is used
(`status=DEPENDENCY_BYPASS`).

For each (config, system, module):
- $\\Delta\\% = (\\mu_{{\\text{{base}}}} - \\mu_{{\\text{{abl}}}}) / |\\mu_{{\\text{{base}}}}| \\times 100$
- Cohen's $d = (\\mu_{{\\text{{base}}}} - \\mu_{{\\text{{abl}}}}) / \\sigma_{{\\text{{pooled}}}}$
- BCa CI₉₅ of $\\Delta\\%$ (1000 resamples)

Impact: Negligible ($|d| < 0.2$), Small, Medium, Large ($|d| \\geq 0.8$).

### 3.2 Results

**Large-impact removals: {stats.get('ablation_large_count', 'N/A')}**
(Dependency bypass events: {stats.get('ablation_bypass_count', 'N/A')})

{abl_table}

See `figures/ablation_heatmap.pdf` for the systems × modules impact matrix.

---

## 4. SOTA Benchmark (Phase 8C)

### 4.1 Methodology

pip install attempted for each missing SOTA package.
If install fails: `status='NOT_EVALUATED'` — **no mock results generated**.
`win_rate_real` = wins vs evaluated baselines only.
`win_rate_total` = wins vs all baselines (NOT_EVALUATED = defeat).

### 4.2 Results

| Metric | Value |
|--------|-------|
| Evaluated baselines (OK) | {stats.get('sota_ok_count', 'N/A')} |
| Not evaluated | {stats.get('sota_not_eval_count', 'N/A')} |
| Win rate (real) | {stats.get('sota_win_rate_real', 'N/A')} |
| Win rate (total) | {stats.get('sota_win_rate_total', 'N/A')} |

{sota_table}

See `figures/sota_radar.pdf` and `figures/sota_cost_performance.pdf`.

---

## 5. Robustness Stress Test (Phase 8E)

### 5.1 Noise Robustness

Gaussian white noise at SNR ∈ {{∞, 20, 10, 5, 0}} dB.
NRS = negative linear slope of normalized metric vs SNR index.
- **Mean NRS**: {stats.get('noise_mean_nrs', 'N/A')}
- **Best module**: {stats.get('noise_best_module', 'N/A')}

### 5.2 Missing Data Tolerance

Random dropout at [0%, 10%, 30%, 50%] with linear interpolation.
MDT = max drop rate at < 20% relative degradation.
- **Mean MDT**: {stats.get('mean_mdt', 'N/A')}

### 5.3 Parameter Drift

Physical parameters modulated: σ: 10→14 (Lorenz), γ: 0.3→0.5 (Duffing).
DDL = estimated timestep of first >2σ deviation.

### 5.4 OOD Generalization

Train: {{Lorenz, Duffing}} → Test: {{Rössler, Van der Pol}}.
GG = |μ_in − μ_OOD| / |μ_in|.
- **Mean OOD Gap**: {stats.get('ood_mean_gap', 'N/A')}

---

## 6. Computational Cost

Measured from Phase 8A reproducibility runs (mean across seeds and systems).
Missing values (N/A) indicate profiling was not enabled or module errored.

{cost_table}

> [!NOTE]
> CPU timing measured via `time.perf_counter()`.
> RAM via `tracemalloc`. VRAM via `torch.cuda.max_memory_allocated()` (GPU only).

---

## 7. Threats to Validity

### 7.1 Statistical Reproducibility

{f"The following metrics are reported as N/A due to missing data: {', '.join(na_fields[:10])}. " if na_fields else "All statistical metrics were successfully computed."}
BCa bootstrap CI validity requires n_resamples ≥ n_data and non-degenerate distributions.
Short dry-run signals (200 steps) may produce wider CIs than production runs.

### 7.2 Synthetic Dataset Bias

All dynamical systems are numerically integrated (RK4 solver).
Real-world sensor data involves non-Gaussian noise, missing channels, multi-scale coupling,
and hardware quantization effects not present in these benchmarks.
Results are **not** expected to generalize directly to empirical time series without re-validation.

### 7.3 Hardware Dependence

Execution times depend heavily on CPU model, GPU presence, RAM bandwidth,
and background process load. Comparisons across different hardware configurations
are not valid without normalization. VRAM measurements assume NVIDIA CUDA ≥ 11.0.

### 7.4 Hyperparameter Sensitivity

SINDy threshold (0.1), PINN architecture depth (default), NeuralODE step-size,
and EV3 embedding dimensionality have **not** been exhaustively tuned per system.
Performance may improve substantially with system-specific hyperparameter search.

### 7.5 Domain Transfer Limitations

The pipeline processes 1-D signal proxies (x-component) of inherently 3-D chaotic attractors.
Full phase-space reconstruction is not attempted. Performance on multi-dimensional,
multi-modal, or non-stationary empirical data may differ significantly from reported values.

### 7.6 Simulator-Reality Gap

All benchmark results derive from numerical integration of idealized ODEs.
The gap between these simulations and experimental measurements constitutes
a fundamental external validity threat. All conclusions in this report are
**model-specific observations** and should not be interpreted as physical laws
or universal properties of the corresponding dynamical phenomena.

---

## 8. Conclusions

This evaluation establishes baseline reproducibility, ablation sensitivity, robustness profiles,
and comparative positioning for the Neuro-Symbolic Dynamic Atlas pipeline.
All reported values are model-specific observations on numerical simulations.
**No claims are made about universal physical laws or real-world systems.**

---

## References

See `papers/references.bib`.

- Chen et al. (2018) — Neural ODEs
- Brunton et al. (2016) — SINDy
- Edelsbrunner & Harer (2008) — Persistent Homology
- Raissi et al. (2019) — PINNs
- Cohen (1988) — Effect sizes
- Efron & Tibshirani (1994) — Bootstrap
- Joe & Kuo (2003) — Sobol sequences
""")
    return md


# ---------------------------------------------------------------------------
# LaTeX paper
# ---------------------------------------------------------------------------

def generate_latex_paper(stats: Dict[str, str], results: Dict[str, Any]) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    s = lambda k: stats.get(k, "N/A")

    # Reproducibility table rows
    repro_rows = ""
    df_r = results.get("reproducibility")
    if df_r is not None and not df_r.empty:
        req_cols = ["module", "system", "n_seeds", "mean", "ci_lower", "ci_upper",
                    "rel_width", "cv", "converged", "stable"]
        available = [c for c in req_cols if c in df_r.columns]
        for _, row in df_r[available].head(10).iterrows():
            mod = str(row.get("module", "N/A")).replace("_", r"\_")
            sys_ = str(row.get("system", "N/A"))
            n = str(row.get("n_seeds", "N/A"))
            cv_ = _fmt(row.get("cv", float("nan")), 4)
            conv = str(row.get("converged", "N/A"))
            stable = str(row.get("stable", "N/A"))
            repro_rows += f"        {mod} & {sys_} & {n} & {cv_} & {conv} & {stable} \\\\\n"

    # Ablation table rows
    abl_rows = ""
    df_a = results.get("ablation")
    if df_a is not None and not df_a.empty and "cohens_d" in df_a.columns:
        for _, row in df_a.nlargest(8, "cohens_d").iterrows():
            abl = str(row.get("ablation", "N/A")).replace("_", r"\_")
            sys_ = str(row.get("system", "N/A"))
            mod = str(row.get("module", "N/A")).replace("_", r"\_")
            dp = _fmt(row.get("delta_pct", float("nan")), 1)
            d = _fmt(row.get("cohens_d", float("nan")), 3)
            impact = str(row.get("impact", "N/A"))
            abl_rows += f"        {abl} & {sys_} & {mod} & {dp} & {d} & {impact} \\\\\n"

    # Computational cost table
    cost_rows = ""
    df_r2 = results.get("reproducibility")
    if df_r2 is not None and not df_r2.empty:
        cost_cols = {c for c in ["module", "mean_time_s", "peak_ram_mb", "peak_vram_mb"] if c in df_r2.columns}
        if "module" in cost_cols:
            agg = df_r2.groupby("module")[list(cost_cols - {"module"})].mean().reset_index()
            for _, row in agg.head(8).iterrows():
                mod = str(row.get("module", "N/A")).replace("_", r"\_")
                t = _fmt(row.get("mean_time_s", float("nan")), 2)
                ram = _fmt(row.get("peak_ram_mb", float("nan")), 1)
                vram = _fmt(row.get("peak_vram_mb", float("nan")), 1)
                cost_rows += f"        {mod} & {t} & {ram} & {vram} \\\\\n"

    tex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{longtable}
\geometry{margin=2.5cm}

\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}

\title{Neuro-Symbolic Dynamic Atlas: \\
Reproducibility, Ablation, and Robustness Analysis}
\author{Automated Scientific Report --- Phase 8}
\date{""" + date_str + r"""}

\begin{document}
\maketitle
\tableofcontents
\clearpage

\begin{abstract}
We present a systematic evaluation of the Neuro-Symbolic Dynamic Atlas pipeline across
""" + s("repro_total") + r""" module-system combinations.
Reproducibility analysis (BCa bootstrap, Sobol seeds, adaptive stopping) shows
""" + s("repro_converged_pct") + r""" convergence and """ + s("repro_stable_pct") + r""" stability
(median CV = """ + s("repro_median_cv") + r""").
Ablation study identifies """ + s("ablation_large_count") + r""" large-impact removals ($|d|\geq 0.8$).
Mean OOD gap: """ + s("ood_mean_gap") + r""".
\textbf{All results are model-specific observations on numerical simulations.}
\end{abstract}

\section{Introduction}
Scientific machine learning pipelines require validation beyond held-out accuracy.
This report covers: (1) reproducibility, (2) ablation, (3) SOTA comparison, (4) robustness.

\section{Reproducibility Audit (Phase 8A)}
Seeds: $S = \lfloor p \times (2^{31}-1) \rfloor$ (Sobol)~\cite{joe2003remark}.
BCa bootstrap CI$_{95}$~\cite{efron1994introduction} with $n_{\text{resamples}}=2000$.
Convergence: $W_{\text{rel}} = (CI_{hi}-CI_{lo})/|\mu| < 0.05$ (max 50 seeds).

\begin{table}[h]
\centering
\caption{Reproducibility Audit Summary}
\begin{tabular}{lr}
\toprule
Metric & Value \\
\midrule
Total evaluations & """ + s("repro_total") + r""" \\
Converged ($W_{\text{rel}}<0.05$) & """ + s("repro_converged_pct") + r""" \\
Stable (CV $<$ 0.05) & """ + s("repro_stable_pct") + r""" \\
Median CV & """ + s("repro_median_cv") + r""" \\
Peak RAM & """ + s("repro_max_ram_mb") + r""" MB \\
Peak VRAM & """ + s("repro_max_vram_mb") + r""" MB \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[h]
\centering
\caption{Sample Reproducibility Results (first 10)}
\begin{tabular}{llrrrll}
\toprule
Module & System & Seeds & CV & Converged & Stable \\
\midrule
""" + repro_rows + r"""\bottomrule
\end{tabular}
\end{table}

\section{Ablation Study (Phase 8B)}
\begin{align}
\Delta\% &= \frac{\mu_{\text{base}} - \mu_{\text{abl}}}{|\mu_{\text{base}}|} \times 100 \\
d &= \frac{\mu_{\text{base}} - \mu_{\text{abl}}}{\sigma_{\text{pooled}}}
\end{align}
DAG-aware cascade disabling; AR(p) fallback (\texttt{DEPENDENCY\_BYPASS}).
Large-impact removals: """ + s("ablation_large_count") + r""".

\begin{table}[h]
\centering
\caption{Top 8 Ablations by Cohen's $d$}
\begin{tabular}{llllrrl}
\toprule
Config & System & Module & $\Delta\%$ & $d$ & Impact \\
\midrule
""" + abl_rows + r"""\bottomrule
\end{tabular}
\end{table}

\section{SOTA Benchmark (Phase 8C)}
pip install attempted for all missing packages.
Unavailable tools: \texttt{NOT\_EVALUATED} (no mocks).
OK evaluations: """ + s("sota_ok_count") + r""". Not evaluated: """ + s("sota_not_eval_count") + r""".
Win rate (real): """ + s("sota_win_rate_real") + r"""; Win rate (total): """ + s("sota_win_rate_total") + r""".

\section{Robustness Stress Test (Phase 8E)}
\subsection{Noise Robustness}
SNR $\in \{+\infty, 20, 10, 5, 0\}$ dB. NRS = $-\text{slope}(\text{norm. metric vs SNR})$.
Best: \textbf{""" + s("noise_best_module") + r"""}, Mean NRS: """ + s("noise_mean_nrs") + r""".

\subsection{Missing Data}
Dropout [0\%, 10\%, 30\%, 50\%] + linear interpolation. MDT = max drop at $<$20\% degradation.
Mean MDT: """ + s("mean_mdt") + r""".

\subsection{Parameter Drift}
$\sigma: 10 \to 14$ (Lorenz), $\gamma: 0.3 \to 0.5$ (Duffing).

\subsection{OOD Generalization}
Train: \{Lorenz, Duffing\}, Test: \{R\"ossler, Van der Pol\}.
GG = $|\mu_{\text{in}} - \mu_{\text{ood}}|/|\mu_{\text{in}}|$. Mean gap: """ + s("ood_mean_gap") + r""".

\section{Computational Cost}
\begin{table}[h]
\centering
\caption{Mean Computational Cost per Module (from Phase 8A)}
\begin{tabular}{lrrr}
\toprule
Module & Mean Time (s) & Peak RAM (MB) & Peak VRAM (MB) \\
\midrule
""" + cost_rows + r"""\bottomrule
\end{tabular}
\end{table}

\section{Threats to Validity}
\subsection{Statistical Reproducibility}
BCa bootstrap validity requires non-degenerate distributions and $n_{\text{seeds}} \geq 2$.
\subsection{Synthetic Dataset Bias}
All systems numerically integrated; real sensor noise unmodeled.
\subsection{Hardware Dependence}
Timings depend on CPU/GPU model; cross-platform comparisons invalid without normalization.
\subsection{Hyperparameter Sensitivity}
SINDy threshold, PINN depth, NeuralODE step-size not exhaustively tuned.
\subsection{Domain Transfer Limitations}
1-D signal proxies of 3-D systems; multi-dimensional performance may differ.
\subsection{Simulator-Reality Gap}
RK4 integration only; no empirical validation. Results are model-specific observations.

\section{Conclusions}
\textbf{Model-specific observations only.} All reported metrics derive from numerical simulations.
No claims about universal physical laws or out-of-domain performance are made.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
    return tex


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def run_auto_paper_generator(dry_run: bool = False, skip_pdf: bool = False) -> Dict[str, Path]:
    """
    Reads ALL Phase 8 result files and generates complete manuscript.
    Returns dict of generated file paths.
    """
    log.info("Loading all Phase 8 result files...")
    results = _load_all_results()
    stats = _extract_key_stats(results)

    na_count = sum(1 for v in stats.values() if v == "N/A")
    log.info(f"Stats: {len(stats)} fields, {na_count} N/A (missing data)")

    # Sanitize all stats values
    stats = {k: _sanitize(v) for k, v in stats.items()}

    # Markdown
    log.info("Generating Markdown paper...")
    md = generate_markdown_paper(stats, results)
    md_path = PAPERS_DIR / "system_paper.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    log.info(f"Markdown: {md_path}")

    # LaTeX
    log.info("Generating LaTeX paper...")
    tex = generate_latex_paper(stats, results)
    tex_path = PAPERS_DIR / "system_paper.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    log.info(f"LaTeX: {tex_path}")

    # Bibliography
    save_bibliography()

    output = {"markdown": md_path, "latex": tex_path, "bib": PAPERS_DIR / "references.bib"}

    # PDF
    if not skip_pdf:
        pdf = _compile_pdf(tex_path)
        if pdf:
            output["pdf"] = pdf

    _print_summary(stats, output)
    return output


def _compile_pdf(tex_path: Path) -> Optional[Path]:
    """pdflatex 3 passes, saves error log on failure."""
    try:
        result = subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=5)
        if result.returncode != 0:
            log.warning("pdflatex not found; saving .tex only.")
            return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        log.warning("pdflatex not available; saving .tex only.")
        return None

    cwd = tex_path.parent
    pdf_path = tex_path.with_suffix(".pdf")

    for pass_n in range(1, 4):
        log.info(f"  pdflatex pass {pass_n}/3...")
        try:
            r = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(cwd), str(tex_path)],
                capture_output=True, text=True, timeout=120, cwd=str(cwd)
            )
            if r.returncode != 0 and pass_n == 3:
                log.warning(f"  pdflatex error (rc={r.returncode}).")
                # Save error log
                log_path = PAPERS_DIR / "pdflatex_error.log"
                with open(log_path, "w", encoding="utf-8") as lf:
                    lf.write(r.stdout or "")
                    lf.write(r.stderr or "")
                log.warning(f"  Error log: {log_path}")
        except subprocess.TimeoutExpired:
            log.warning("  pdflatex timed out.")
            return None
        except Exception as e:
            log.warning(f"  pdflatex error: {e}")
            return None

    if pdf_path.exists():
        log.info(f"PDF compiled: {pdf_path}")
        return pdf_path
    log.warning("PDF not found after pdflatex.")
    return None


def _print_summary(stats: Dict[str, str], output: Dict[str, Path]):
    print("\n" + "=" * 60)
    print("  PHASE 8D — AUTO PAPER GENERATOR SUMMARY")
    print("=" * 60)
    print(f"  N/A fields : {sum(1 for v in stats.values() if v == 'N/A')} / {len(stats)}")
    for label, path in output.items():
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {label:10s}: {path}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 8D — Auto Paper Generator")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-pdf", action="store_true")
    args = parser.parse_args()
    run_auto_paper_generator(dry_run=args.dry_run, skip_pdf=args.skip_pdf)


if __name__ == "__main__":
    main()
