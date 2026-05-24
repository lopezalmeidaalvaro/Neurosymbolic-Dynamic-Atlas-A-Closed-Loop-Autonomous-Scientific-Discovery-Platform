import json
import argparse
import sys
import io
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Reproducibility status ranks
REPRO_RANKS = {"validated": 4, "replicated": 3, "preliminary": 2, "uncertain": 1}


def get_repro_rank(status_str):
    return REPRO_RANKS.get(status_str.lower(), 0)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate scientific regressions against baseline snapshots"
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        help="Name of baseline to compare against. If omitted, uses the latest baseline in the index.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    artifacts_dir = project_root / "dashboard" / "public" / "artifacts"
    baselines_dir = artifacts_dir / "baselines"
    discoveries_dir = artifacts_dir / "discoveries"

    # 1. Load baseline index
    index_path = baselines_dir / "baseline_index.json"
    if not index_path.exists():
        print("❌ Error: baseline_index.json not found. Run create_baseline.py first.")
        sys.exit(1)

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing baseline_index.json: {e}")
        sys.exit(1)

    baselines = index_data.get("baselines", [])
    if not baselines:
        print("❌ Error: No baselines defined in baseline_index.json.")
        sys.exit(1)

    # 2. Select baseline
    selected_baseline = None
    if args.baseline:
        for b in baselines:
            if b.get("name") == args.baseline:
                selected_baseline = b
                break
        if not selected_baseline:
            print(f"❌ Error: Baseline '{args.baseline}' not found in index.")
            sys.exit(1)
    else:
        # Default to the latest baseline (last one in the list)
        selected_baseline = baselines[-1]

    print(
        f"🔍 Comparing against baseline: '{selected_baseline['name']}' (timestamp: {selected_baseline['timestamp']})"
    )

    # 3. Load baseline sweep file
    baseline_file_path = baselines_dir / selected_baseline["source"]
    if not baseline_file_path.exists():
        print(f"❌ Error: Baseline file not found at {baseline_file_path}")
        sys.exit(1)

    try:
        with open(baseline_file_path, "r", encoding="utf-8") as f:
            baseline_sweep = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing baseline sweep file: {e}")
        sys.exit(1)

    # 4. Load current sweep file
    current_sweep_path = discoveries_dir / "massive_sweep_report.json"
    if not current_sweep_path.exists():
        print(
            f"❌ Error: Current massive sweep report not found at {current_sweep_path}"
        )
        sys.exit(1)

    try:
        with open(current_sweep_path, "r", encoding="utf-8") as f:
            current_sweep = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing current sweep report: {e}")
        sys.exit(1)

    # Group results by system
    baseline_systems = {
        r["system"]: r for r in baseline_sweep.get("certified_results", [])
    }
    current_systems = {
        r["system"]: r for r in current_sweep.get("certified_results", [])
    }

    systems_report = []
    global_status = "pass"

    all_systems = sorted(
        list(set(list(baseline_systems.keys()) + list(current_systems.keys())))
    )

    for system in all_systems:
        b_res = baseline_systems.get(system)
        c_res = current_systems.get(system)

        system_status = "pass"
        system_metrics = {}

        # If missing in baseline or current
        if not b_res:
            print(
                f"ℹ️ System '{system}' is new in current sweep (not present in baseline)."
            )
            systems_report.append(
                {
                    "system": system,
                    "status": "pass",
                    "message": "New system introduced",
                    "metrics": {},
                }
            )
            continue

        if not c_res:
            print(f"❌ Failure: System '{system}' is missing in current sweep.")
            systems_report.append(
                {
                    "system": system,
                    "status": "failure",
                    "message": "System missing in current sweep",
                    "metrics": {},
                }
            )
            global_status = "failure"
            continue

        # Extract certification structures
        b_cert = b_res.get("certification", {})
        c_cert = c_res.get("certification", {})

        # Metrics comparison details helper
        # Thresholds:
        # critical_score: warning > 10%, failure > 25%
        # confidence_score: warning > 15%, failure > 30%
        # acceleration: warning > 20%, failure > 35%
        # reproducibility: downgrade = failure

        # 1) critical_score
        b_cs = b_cert.get("critical_score", 0.0)
        c_cs = c_cert.get("critical_score", 0.0)
        cs_delta = c_cs - b_cs
        cs_pct = (abs(cs_delta) / b_cs * 100.0) if b_cs != 0 else 0.0

        cs_status = "pass"
        if cs_pct > 25.0:
            cs_status = "failure"
        elif cs_pct > 10.0:
            cs_status = "warning"

        # 2) confidence_score
        b_conf = b_cert.get("confidence_score", 0.0)
        c_conf = c_cert.get("confidence_score", 0.0)
        conf_delta = c_conf - b_conf
        conf_pct = (abs(conf_delta) / b_conf * 100.0) if b_conf != 0 else 0.0

        conf_status = "pass"
        if conf_pct > 30.0:
            conf_status = "failure"
        elif conf_pct > 15.0:
            conf_status = "warning"

        # 3) acceleration
        b_acc = b_cert.get("evidence", {}).get("acceleration", 0.0)
        c_acc = c_cert.get("evidence", {}).get("acceleration", 0.0)
        acc_delta = c_acc - b_acc
        acc_pct = (abs(acc_delta) / b_acc * 100.0) if b_acc != 0 else 0.0

        acc_status = "pass"
        if acc_pct > 35.0:
            acc_status = "failure"
        elif acc_pct > 20.0:
            acc_status = "warning"

        # 4) acceleration_std
        b_acc_std = b_cert.get("evidence", {}).get("acceleration_std", 0.0)
        c_acc_std = c_cert.get("evidence", {}).get("acceleration_std", 0.0)
        acc_std_delta = c_acc_std - b_acc_std
        acc_std_pct = (
            (abs(acc_std_delta) / b_acc_std * 100.0) if b_acc_std != 0 else 0.0
        )
        acc_std_status = "pass"  # no threshold defined in step 4

        # 5) reproducibility_status
        b_repro = b_cert.get("reproducibility_status", "uncertain")
        c_repro = c_cert.get("reproducibility_status", "uncertain")
        repro_status = "pass"

        b_rank = get_repro_rank(b_repro)
        c_rank = get_repro_rank(c_repro)
        if c_rank < b_rank:
            repro_status = "failure"

        # Determine system overall status
        status_list = [cs_status, conf_status, acc_status, acc_std_status, repro_status]
        if "failure" in status_list:
            system_status = "failure"
        elif "warning" in status_list:
            system_status = "warning"

        if system_status == "failure":
            global_status = "failure"
        elif system_status == "warning" and global_status != "failure":
            global_status = "warning"

        system_metrics = {
            "critical_score": {
                "baseline": b_cs,
                "current": c_cs,
                "delta": cs_delta,
                "pct_change": cs_pct,
                "status": cs_status,
            },
            "confidence_score": {
                "baseline": b_conf,
                "current": c_conf,
                "delta": conf_delta,
                "pct_change": conf_pct,
                "status": conf_status,
            },
            "acceleration": {
                "baseline": b_acc,
                "current": c_acc,
                "delta": acc_delta,
                "pct_change": acc_pct,
                "status": acc_status,
            },
            "acceleration_std": {
                "baseline": b_acc_std,
                "current": c_acc_std,
                "delta": acc_std_delta,
                "pct_change": acc_std_pct,
                "status": acc_std_status,
            },
            "reproducibility_status": {
                "baseline": b_repro,
                "current": c_repro,
                "status": repro_status,
            },
        }

        systems_report.append(
            {"system": system, "status": system_status, "metrics": system_metrics}
        )

    # Construct final report
    report = {
        "summary": {
            "status": global_status,
            "baseline_name": selected_baseline["name"],
            "baseline_timestamp": selected_baseline["timestamp"],
            "current_timestamp": current_sweep.get("metadata", {}).get("timestamp", ""),
        },
        "systems": systems_report,
    }

    # Ensure discoveries directory exists
    discoveries_dir.mkdir(parents=True, exist_ok=True)
    report_output_path = discoveries_dir / "scientific_regression_report.json"

    try:
        with open(report_output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(
            f"✅ Scientific regression report successfully written to {report_output_path}"
        )
    except Exception as e:
        print(f"❌ Failed to write scientific regression report: {e}")
        sys.exit(1)

    # Console Output Log
    print("\n" + "=" * 60)
    print("⚖️  SCIENTIFIC REGRESSION CHECK RESULTS")
    print("=" * 60)
    status_emoji = {"pass": "🟢 PASS", "warning": "🟡 WARNING", "failure": "🔴 FAILURE"}
    print(f"GLOBAL STATUS: {status_emoji[global_status]}")
    print("-" * 60)

    for sys_data in systems_report:
        sys_name = sys_data["system"]
        sys_stat = sys_data["status"]
        print(f"\nSystem: {sys_name.upper()} ({status_emoji[sys_stat]})")

        metrics = sys_data.get("metrics", {})
        if not metrics:
            print(f"  {sys_data.get('message', 'No metrics available')}")
            continue

        for m_name, m_data in metrics.items():
            stat_marker = (
                "✓"
                if m_data["status"] == "pass"
                else ("⚠️" if m_data["status"] == "warning" else "❌")
            )
            if m_name == "reproducibility_status":
                print(
                    f"  {stat_marker} {m_name:<22}: {m_data['baseline']} -> {m_data['current']} (status: {m_data['status']})"
                )
            else:
                pct_str = (
                    f"({m_data['pct_change']:.2f}%)" if "pct_change" in m_data else ""
                )
                print(
                    f"  {stat_marker} {m_name:<22}: baseline={m_data['baseline']:.6f} | current={m_data['current']:.6f} | delta={m_data['delta']:+.6f} {pct_str} (status: {m_data['status']})"
                )

    print("\n" + "=" * 60)

    if global_status == "failure":
        print(
            "❌ Scientific regression check failed. Code modifications caused unacceptable performance drop."
        )
        sys.exit(1)
    elif global_status == "warning":
        print(
            "⚠️  Scientific regression check passed with warnings. Noticeable drift detected."
        )
        sys.exit(0)
    else:
        print("✅ Scientific regression check passed. No deviations detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
