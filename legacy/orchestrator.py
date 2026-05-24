import json
import subprocess
import sys
import time
import os

BRANCHES = [
    ("B1_galois", "subrama_B1_galois.py", "cert_B1_galois.json"),
    ("B2_bring_jerrard", "subrama_B2_bring.py", "cert_B2_bring.json"),
    ("B3_sturm", "subrama_B3_sturm.py", "cert_B3_sturm.json"),
]

FINAL_REPORT = "reporte_final.json"


def run_branch(name, script, cert_file):
    print(f"\n{'='*60}")
    print(f"[ORQUESTADOR] Ejecutando rama: {name} -> {script}")
    print(f"{'='*60}")
    t0 = time.time()
    try:
        subprocess.run([sys.executable, script], timeout=30)
        elapsed = round(time.time() - t0, 4)
        if os.path.exists(cert_file):
            with open(cert_file) as f:
                return json.load(f)
        else:
            return _fail_cert(name, "ERROR", ["No se genero cert JSON"], elapsed)
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - t0, 4)
        return _fail_cert(
            name, "TIMEOUT", ["Timeout global (30s) en orquestador"], elapsed
        )
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        return _fail_cert(name, "ERROR", [str(e)], elapsed)


def _fail_cert(branch, status, errors, elapsed):
    return {
        "branch": branch,
        "status": status,
        "invariants": {},
        "metrics": {"execution_time_sec": elapsed, "peak_ram_mb": 0.0},
        "errors": errors,
    }


def merge_invariants(certs):
    merged = {}
    for cert in certs:
        if cert.get("status") == "SUCCESS":
            merged[cert["branch"]] = cert.get("invariants", {})
    return merged


def infer_conclusions(merged):
    conclusions = {}

    b1 = merged.get("B1_galois")
    if b1:
        conclusions["galois_group"] = b1.get("galois_group")
        conclusions["solvable_by_radicals"] = b1.get("solvable_by_radicals")

    b3 = merged.get("B3_sturm")
    if b3:
        conclusions["n_real_roots"] = b3.get("n_real_roots_sturm")
        if b3.get("bisection_results"):
            conclusions["real_root_approx"] = b3["bisection_results"][0][
                "midpoint_float64"
            ]

    b2 = merged.get("B2_bring_jerrard")
    if b2:
        conclusions["bring_jerrard"] = "SUCCESS"
    else:
        conclusions["bring_jerrard"] = (
            "FAILED/TIMEOUT - Inferencia basada solo en B1 y B3"
        )

    return conclusions


def main():
    print("\n" + "=" * 60)
    print(
        "  ORQUESTADOR MATEMATICO (STRESS TEST) -- x^5 + 3x^4 - 2x^3 + 7x^2 - x + 1 = 0"
    )
    print("=" * 60)

    certs = []
    for name, script, cert_file in BRANCHES:
        if os.path.exists(cert_file):
            os.remove(cert_file)
        cert = run_branch(name, script, cert_file)
        certs.append(cert)

    print("\n" + "=" * 60)
    print("[ORQUESTADOR] RESUMEN DE RAMAS")
    print("=" * 60)
    for cert in certs:
        status = cert.get("status", "UNKNOWN")
        errors = " | ".join(cert.get("errors", []))
        err_msg = f" -> Errors: {errors}" if errors else ""
        print(f"  [{status:18s}] {cert['branch']:20s}{err_msg}")

    merged = merge_invariants(certs)
    conclusions = infer_conclusions(merged)

    report = {
        "system": "Orquestador Matemático Neurosimbólico (Stress Test)",
        "polynomial": "x^5 + 3x^4 - 2x^3 + 7x^2 - x + 1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "branch_certificates": certs,
        "merged_invariants": merged,
        "conclusions": conclusions,
    }

    with open(FINAL_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print("\n" + "=" * 60)
    print(f"  REPORTE FINAL GENERADO: {FINAL_REPORT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
