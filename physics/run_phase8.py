import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

"""
Phase 8 Orchestrator (COMPLETO, v2)
=====================================
Runs all Phase 8 stages in order: 8A → 8B → 8E → 8C → 8D.
Tracks progress via flag files in artifacts/phase8_flags/.

Flags:
  artifacts/phase8_flags/8a_done
  artifacts/phase8_flags/8b_done
  artifacts/phase8_flags/8e_done
  artifacts/phase8_flags/8c_done
  artifacts/phase8_flags/8d_done

Outputs:
  artifacts/phase8_completion_report.md
  (All per-phase outputs in artifacts/ and figures/)

Usage:
    python run_phase8.py                        # full run
    python run_phase8.py --dry-run              # show plan, skip ALL execution
    python run_phase8.py --stage 8A             # run one stage only
    python run_phase8.py --force-rerun          # ignore flags, re-run all
    python run_phase8.py --skip 8C              # skip specific stage
    python run_phase8.py --systems lorenz duffing --modules EV3 SINDy
    python run_phase8.py --max-seeds 10 --n-resamples 100

Flags behavior:
    If a flag exists and --force-rerun is NOT set, the stage is skipped.
    --dry-run prints the execution plan but runs NOTHING.
"""

import sys
import io
import os
import json
import time
import argparse
import warnings
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Phase8] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger("run_phase8")

# ---------------------------------------------------------------------------
# Directory structure
# ---------------------------------------------------------------------------

ARTIFACTS_DIR = Path("artifacts")
FLAGS_DIR = ARTIFACTS_DIR / "phase8_flags"
FIGURES_DIR = Path("figures")

for d in [ARTIFACTS_DIR, FLAGS_DIR, FIGURES_DIR, Path("results"),
          Path("papers"), Path("results/phase8a"),
          Path("results/phase8b"), Path("results/phase8c"), Path("results/phase8e")]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Flag management
# ---------------------------------------------------------------------------

STAGE_FLAGS = {
    "8A": FLAGS_DIR / "8a_done",
    "8B": FLAGS_DIR / "8b_done",
    "8E": FLAGS_DIR / "8e_done",
    "8C": FLAGS_DIR / "8c_done",
    "8D": FLAGS_DIR / "8d_done",
}

STAGE_ORDER = ["8A", "8B", "8E", "8C", "8D"]

STAGE_NAMES = {
    "8A": "Reproducibility Audit",
    "8B": "Ablation Study",
    "8E": "Robustness Stress Test",
    "8C": "SOTA Benchmark",
    "8D": "Auto Paper Generator",
}


def _is_done(stage: str) -> bool:
    return STAGE_FLAGS[stage].exists()


def _set_done(stage: str, metadata: Dict = None):
    flag_path = STAGE_FLAGS[stage]
    flag_path.write_text(json.dumps({
        "stage": stage,
        "name": STAGE_NAMES.get(stage, ""),
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    }, indent=2))
    log.info(f"  [FLAG SET] {flag_path}")


def _clear_done(stage: str):
    flag_path = STAGE_FLAGS[stage]
    if flag_path.exists():
        flag_path.unlink()
        log.info(f"  [FLAG CLEARED] {flag_path}")


def _read_flag(stage: str) -> Dict:
    try:
        return json.loads(STAGE_FLAGS[stage].read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Stage runners
# ---------------------------------------------------------------------------

def run_stage_8a(args: argparse.Namespace) -> Dict[str, Any]:
    """Phase 8A — Reproducibility Audit"""
    log.info("\n" + "=" * 60)
    log.info("  STAGE 8A — REPRODUCIBILITY AUDIT")
    log.info("=" * 60)
    from reproducibility_audit import run_reproducibility_audit
    df = run_reproducibility_audit(
        systems=args.systems,
        modules=args.modules,
        dry_run=False,
        initial_seeds=args.initial_seeds,
        increment=10,
        max_seeds=args.max_seeds,
        n_resamples=args.n_resamples,
        signal_length=args.signal_length,
    )
    n_stable = int(df["stable"].sum()) if "stable" in df.columns else 0
    n_total = len(df)
    return {
        "n_total": n_total,
        "n_stable": n_stable,
        "stable_pct": round(100 * n_stable / max(n_total, 1), 1),
        "csv_path": str(ARTIFACTS_DIR / "reproducibility_results.csv"),
    }


def run_stage_8b(args: argparse.Namespace) -> Dict[str, Any]:
    """Phase 8B — Ablation Study"""
    log.info("\n" + "=" * 60)
    log.info("  STAGE 8B — ABLATION STUDY")
    log.info("=" * 60)
    from ablation_study import run_ablation_study
    df = run_ablation_study(
        systems=args.systems,
        modules=args.modules,
        dry_run=False,
        n_resamples=min(1000, args.n_resamples),
        signal_length=args.signal_length,
    )
    n_large = int((df["impact"] == "Large").sum()) if "impact" in df.columns else 0
    return {
        "n_rows": len(df),
        "n_large_impact": n_large,
        "csv_path": str(ARTIFACTS_DIR / "ablation_results.csv"),
    }


def run_stage_8e(args: argparse.Namespace) -> Dict[str, Any]:
    """Phase 8E — Robustness Stress Test"""
    log.info("\n" + "=" * 60)
    log.info("  STAGE 8E — ROBUSTNESS STRESS TEST")
    log.info("=" * 60)
    from robustness_stress_test import run_robustness_stress_test
    dfs = run_robustness_stress_test(
        systems=args.systems,
        modules=args.modules,
        dry_run=False,
        signal_length=args.signal_length,
    )
    n_tests = sum(len(df) for df in dfs.values() if hasattr(df, "__len__"))
    return {
        "n_tests": n_tests,
        "tests": list(dfs.keys()),
        "csv_path": str(ARTIFACTS_DIR / "robustness_results.csv"),
    }


def run_stage_8c(args: argparse.Namespace) -> Dict[str, Any]:
    """Phase 8C — SOTA Benchmark"""
    log.info("\n" + "=" * 60)
    log.info("  STAGE 8C — SOTA BENCHMARK")
    log.info("=" * 60)
    from sota_benchmark import run_sota_benchmark
    df = run_sota_benchmark(
        systems=args.systems,
        dry_run=False,
        signal_length=args.signal_length,
    )
    ok_count = int((df["status"] == "OK").sum()) if "status" in df.columns else 0
    ne_count = int((df["status"] == "NOT_EVALUATED").sum()) if "status" in df.columns else 0
    return {
        "n_rows": len(df),
        "ok_count": ok_count,
        "not_evaluated": ne_count,
        "csv_path": str(ARTIFACTS_DIR / "sota_results.csv"),
    }


def run_stage_8d(args: argparse.Namespace) -> Dict[str, Any]:
    """Phase 8D — Auto Paper Generator"""
    log.info("\n" + "=" * 60)
    log.info("  STAGE 8D — AUTO PAPER GENERATOR")
    log.info("=" * 60)
    from auto_paper_generator import run_auto_paper_generator
    output = run_auto_paper_generator(
        dry_run=False,
        skip_pdf=args.skip_pdf,
    )
    return {
        "files_generated": [str(p) for p in output.values()],
        "pdf_compiled": "pdf" in output,
    }


STAGE_RUNNERS = {
    "8A": run_stage_8a,
    "8B": run_stage_8b,
    "8E": run_stage_8e,
    "8C": run_stage_8c,
    "8D": run_stage_8d,
}

# ---------------------------------------------------------------------------
# Progress + completion report
# ---------------------------------------------------------------------------

def _save_completion_report(results: Dict[str, Any], start_ts: datetime):
    elapsed = (datetime.now() - start_ts).total_seconds()

    rows = []
    for stage in STAGE_ORDER:
        flag = _read_flag(stage)
        rows.append({
            "Stage": stage,
            "Name": STAGE_NAMES.get(stage, ""),
            "Status": "DONE" if flag else "PENDING",
            "Timestamp": flag.get("timestamp", "—"),
            "Key Metric": _stage_summary_metric(stage, flag.get("metadata", {})),
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    table_md = df.to_markdown(index=False)

    done_count = sum(1 for s in STAGE_ORDER if _is_done(s))
    pct = 100 * done_count / len(STAGE_ORDER)

    md = f"""# Phase 8 — Completion Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total elapsed:** {elapsed:.1f}s ({elapsed/60:.1f} min)
**Progress:** {done_count}/{len(STAGE_ORDER)} stages complete ({pct:.0f}%)

## Stage Status

{table_md}

## Output Files

| Stage | Key Output |
|-------|------------|
| 8A | `artifacts/reproducibility_results.csv`, `artifacts/reproducibility_report.md` |
| 8B | `artifacts/ablation_results.csv`, `artifacts/ablation_summary.csv`, `artifacts/ablation_report.md` |
| 8E | `artifacts/robustness_results.csv`, `artifacts/robustness_report.md` |
| 8C | `artifacts/sota_results.csv`, `artifacts/sota_summary.csv`, `artifacts/sota_report.md` |
| 8D | `papers/system_paper.md`, `papers/system_paper.tex`, `papers/system_paper.pdf` |

## Flag Files

Flag files stored in `artifacts/phase8_flags/`.
Delete a flag file to force re-run of that stage.

## Errors (if any)

{"None reported." if not any(r.get("error") for r in results.values()) else
 chr(10).join(f"- **{k}**: {v['error']}" for k, v in results.items() if v.get("error"))}
"""
    path = ARTIFACTS_DIR / "phase8_completion_report.md"
    path.write_text(md, encoding="utf-8")
    log.info(f"Completion report: {path}")


def _stage_summary_metric(stage: str, meta: Dict) -> str:
    if not meta:
        return "—"
    if stage == "8A":
        return f"{meta.get('stable_pct', '?')}% stable"
    if stage == "8B":
        return f"{meta.get('n_large_impact', '?')} large-impact"
    if stage == "8E":
        return f"{meta.get('n_tests', '?')} test rows"
    if stage == "8C":
        return f"{meta.get('ok_count', '?')} OK, {meta.get('not_evaluated', '?')} N/E"
    if stage == "8D":
        return "PDF: " + ("yes" if meta.get("pdf_compiled") else "no")
    return "—"


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 8 Orchestrator — runs all evaluation stages in order (8A→8B→8E→8C→8D).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_phase8.py                          # full run (skip already-done stages)
  python run_phase8.py --dry-run               # show plan, run NOTHING
  python run_phase8.py --stage 8A              # run Phase 8A only
  python run_phase8.py --force-rerun           # ignore flags, re-run all stages
  python run_phase8.py --skip 8C 8D           # run 8A, 8B, 8E only
  python run_phase8.py --systems lorenz duffing --modules EV3 SINDy
  python run_phase8.py --max-seeds 10 --n-resamples 100
        """,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print execution plan but do NOT run any stage."
    )
    parser.add_argument(
        "--stage", choices=STAGE_ORDER,
        help="Run only one specific stage (ignores flags)."
    )
    parser.add_argument(
        "--skip", nargs="+", choices=STAGE_ORDER, default=[],
        help="Stages to skip."
    )
    parser.add_argument(
        "--force-rerun", action="store_true",
        help="Ignore done-flags and re-run all (or selected) stages."
    )
    parser.add_argument("--systems", nargs="+", default=None,
                        help="Dynamical systems (default: all 7).")
    parser.add_argument("--modules", nargs="+", default=None,
                        help="Pipeline modules (default: all).")
    parser.add_argument("--max-seeds", type=int, default=50,
                        help="Max seeds per (module, system) in 8A.")
    parser.add_argument("--initial-seeds", type=int, default=20,
                        help="Initial seeds before adaptive stopping.")
    parser.add_argument("--n-resamples", type=int, default=2000,
                        help="BCa bootstrap resamples in 8A (1000 for 8B).")
    parser.add_argument("--signal-length", type=int, default=2000,
                        help="Signal length for all stages.")
    parser.add_argument("--skip-pdf", action="store_true",
                        help="Skip pdflatex compilation in 8D.")
    return parser


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()
    start_ts = datetime.now()

    # Determine which stages to run
    if args.stage:
        stages_to_run = [args.stage]
    else:
        stages_to_run = [s for s in STAGE_ORDER if s not in args.skip]

    # Dry-run: just show the plan
    if args.dry_run:
        print("\n" + "=" * 60)
        print("  PHASE 8 — DRY-RUN PLAN (no stages will execute)")
        print("=" * 60)
        for stage in stages_to_run:
            flag_exists = _is_done(stage)
            will_run = args.force_rerun or not flag_exists
            flag_info = _read_flag(stage)
            ts_info = f" (done: {flag_info.get('timestamp','?')})" if flag_exists else ""
            action = "[WILL RUN]" if will_run else f"[SKIP — already done{ts_info}]"
            print(f"  {stage} — {STAGE_NAMES[stage]:30s} {action}")
        print()
        print("Config:")
        print(f"  Systems       : {args.systems or 'DEFAULT (all 7)'}")
        print(f"  Modules       : {args.modules or 'DEFAULT (all)'}")
        print(f"  Max seeds     : {args.max_seeds}")
        print(f"  n_resamples   : {args.n_resamples}")
        print(f"  Signal length : {args.signal_length}")
        print(f"  Flags dir     : {FLAGS_DIR}")
        print("=" * 60)
        print("\nAdd --force-rerun to re-run already-completed stages.")
        print("Remove --dry-run to execute.\n")
        return

    log.info(f"Phase 8 Orchestrator started: {start_ts.isoformat()}")
    log.info(f"Stages: {stages_to_run} | Force-rerun: {args.force_rerun}")
    log.info(f"Flags dir: {FLAGS_DIR}")

    results: Dict[str, Any] = {}
    stage_times: Dict[str, float] = {}

    for stage in stages_to_run:
        if _is_done(stage) and not args.force_rerun:
            flag_info = _read_flag(stage)
            log.info(f"\n  [SKIP] Stage {stage} already done "
                     f"({flag_info.get('timestamp', '?')}). Use --force-rerun to re-run.")
            results[stage] = {"status": "skipped", **flag_info.get("metadata", {})}
            continue

        if args.force_rerun:
            _clear_done(stage)

        t0 = time.perf_counter()
        try:
            runner = STAGE_RUNNERS[stage]
            meta = runner(args)
            elapsed = time.perf_counter() - t0
            stage_times[stage] = elapsed
            _set_done(stage, {**meta, "elapsed_s": round(elapsed, 2)})
            results[stage] = {"status": "success", **meta}
            log.info(f"\n  [✓] Stage {stage} completed in {elapsed:.1f}s")
        except KeyboardInterrupt:
            log.warning(f"\n  [!] Interrupted at stage {stage}.")
            break
        except Exception as e:
            elapsed = time.perf_counter() - t0
            stage_times[stage] = elapsed
            err_msg = str(e)
            tb = traceback.format_exc()
            log.error(f"\n  [✗] Stage {stage} FAILED after {elapsed:.1f}s: {err_msg}")
            log.debug(tb)
            results[stage] = {"status": "error", "error": err_msg, "traceback": tb}
            # Continue with next stage (don't abort all)
            continue

    # Final summary
    _save_completion_report(results, start_ts)

    total_elapsed = (datetime.now() - start_ts).total_seconds()
    done_count = sum(1 for s in STAGE_ORDER if _is_done(s))

    print("\n" + "=" * 60)
    print("  PHASE 8 — ORCHESTRATOR SUMMARY")
    print("=" * 60)
    for stage in STAGE_ORDER:
        flag = _read_flag(stage)
        st = results.get(stage, {}).get("status", "not_run")
        ts = flag.get("timestamp", "—") if flag else "—"
        t_s = stage_times.get(stage, None)
        t_str = f" ({t_s:.1f}s)" if t_s else ""
        icon = "✓" if _is_done(stage) else "✗"
        print(f"  [{icon}] {stage} — {STAGE_NAMES[stage]:30s} [{st}]{t_str}")
    print(f"\n  Total: {done_count}/{len(STAGE_ORDER)} stages done | {total_elapsed:.1f}s elapsed")
    print(f"  Completion report: {ARTIFACTS_DIR / 'phase8_completion_report.md'}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
