"""
CORE ORCHESTRATOR — Plugin Architecture
Reglas estrictas:
  - PROHIBIDO import sympy o cualquier libreria matematica.
  - Solo: os, sys, json, subprocess, multiprocessing, time.
  - Es ciego al contenido matematico: solo lee job.json, lanza plugins,
    recoge sus JSON y ensambla final_report.json.
"""
import os
import sys
import json
import subprocess
import time

# ── Rutas ──────────────────────────────────────────────────────────────────
ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR  = os.path.join(ROOT_DIR, "plugins")
JOB_FILE     = os.path.join(ROOT_DIR, "job.json")
REPORT_FILE  = os.path.join(ROOT_DIR, "final_report.json")

PLUGIN_TIMEOUT_SEC = 15
# ── Result filenames emitted by each plugin ────────────────────────────────
PLUGIN_OUTPUT_MAP = {
    "galois_group":  "galois_group_result.json",
    "sturm_roots":   "sturm_roots_result.json",
    "bring_jerrard": "bring_jerrard_result.json",
}


def load_job():
    """Load and validate job.json."""
    with open(JOB_FILE, encoding="utf-8") as f:
        job = json.load(f)
    required = {"job_id", "target_expression", "active_plugins"}
    missing = required - job.keys()
    if missing:
        raise ValueError(f"job.json is missing fields: {missing}")
    return job


def _fail_result(plugin_name, expr, reason, elapsed):
    """Return a contract-compliant failure result."""
    return {
        "plugin": plugin_name,
        "status": "failure",
        "input": {"target_expression": expr},
        "output": {},
        "metrics": {"runtime_sec": round(elapsed, 4), "peak_ram_mb": 0.0},
        "errors": [reason]
    }


def run_plugin(plugin_name, expr):
    """
    Launch a plugin as a subprocess, wait up to PLUGIN_TIMEOUT_SEC seconds,
    then read and return its JSON result file.
    No math logic here — fully blind to what the plugin computes.
    """
    script = os.path.join(PLUGINS_DIR, f"{plugin_name}.py")
    result_file = os.path.join(ROOT_DIR, PLUGIN_OUTPUT_MAP.get(plugin_name, f"{plugin_name}_result.json"))

    # Remove stale result from a previous run
    if os.path.exists(result_file):
        os.remove(result_file)

    if not os.path.exists(script):
        return _fail_result(plugin_name, expr, f"Plugin script not found: {script}", 0.0)

    print(f"  [LAUNCH] {plugin_name} <- \"{expr}\"")
    t0 = time.time()

    try:
        proc = subprocess.Popen(
            [sys.executable, script, expr],
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = proc.communicate(timeout=PLUGIN_TIMEOUT_SEC)
            elapsed = time.time() - t0
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            elapsed = time.time() - t0
            return _fail_result(
                plugin_name, expr,
                f"TIMEOUT after {PLUGIN_TIMEOUT_SEC}s (Expression Swell or resource exhaustion)",
                elapsed
            )

        if proc.returncode != 0:
            elapsed = time.time() - t0
            return _fail_result(
                plugin_name, expr,
                f"Plugin exited with code {proc.returncode}. stderr: {stderr.strip()[:400]}",
                elapsed
            )

        # Read the emitted JSON certificate
        if os.path.exists(result_file):
            with open(result_file, encoding="utf-8") as f:
                result = json.load(f)
            print(f"  [OK]     {plugin_name} -> status={result.get('status')} "
                  f"runtime={result.get('metrics', {}).get('runtime_sec')}s")
            return result
        else:
            return _fail_result(plugin_name, expr, "Plugin completed but emitted no result file.", elapsed)

    except Exception as exc:
        elapsed = time.time() - t0
        return _fail_result(plugin_name, expr, str(exc), elapsed)


def assemble_report(job, results):
    """
    Assemble final_report.json.
    Blind: no math inference. Only bookkeeping.
    """
    n_success = sum(1 for r in results if r.get("status") == "success")
    n_failure = sum(1 for r in results if r.get("status") != "success")
    return {
        "job_id":     job["job_id"],
        "polynomial": job["target_expression"],
        "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "orchestrator": "core/orchestrator.py",
        "summary": {
            "plugins_requested": len(job["active_plugins"]),
            "plugins_succeeded": n_success,
            "plugins_failed":    n_failure
        },
        "plugin_results": results
    }


def main():
    print("=" * 64)
    print("  CORE ORCHESTRATOR  --  Plugin Architecture")
    print("=" * 64)

    # Step 1: Load job
    try:
        job = load_job()
    except Exception as e:
        print(f"[FATAL] Cannot load job.json: {e}")
        sys.exit(1)

    print(f"\n  Job ID  : {job['job_id']}")
    print(f"  Target  : {job['target_expression']}")
    print(f"  Plugins : {job['active_plugins']}")
    print()

    # Step 2: Execute each plugin
    results = []
    for plugin_name in job["active_plugins"]:
        result = run_plugin(plugin_name, job["target_expression"])
        results.append(result)

    # Step 3: Assemble and write report
    report = assemble_report(job, results)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    # Step 4: Print summary
    print()
    print("=" * 64)
    print("  SUMMARY")
    print("=" * 64)
    for r in results:
        tag = "[OK]  " if r.get("status") == "success" else "[FAIL]"
        errs = " | ".join(r.get("errors", []))[:80]
        err_str = f"  -> {errs}" if errs else ""
        print(f"  {tag} {r['plugin']:20s}{err_str}")
    print()
    print(f"  Final report -> {REPORT_FILE}")
    print("=" * 64)


if __name__ == "__main__":
    main()
