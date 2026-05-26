import json
import time
import sys
import os
import tracemalloc
import multiprocessing
import sympy as sp
from sympy import symbols, expand, Poly, resultant

OUTPUT = "cert_B2_bring.json"


def apply_limits():
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    except ImportError:
        pass  # Windows fallback


def _bring_worker(result_queue):
    apply_limits()
    tracemalloc.start()
    t0 = time.time()
    errors = []
    status = "SUCCESS"
    invariants = {}

    try:
        x, y = symbols("x y")
        p = x**5 + 3 * x**4 - 2 * x**3 + 7 * x**2 - x + 1

        # Eliminating x^4: Substitute x = y - 3/5
        p_depressed = p.subs(x, y - sp.Rational(3, 5))
        p_depressed = expand(p_depressed)

        # General Tschirnhaus transformation to trigger expression swell
        # z = y^4 + a*y^3 + b*y^2 + c*y + d
        z, a, b, c, d = symbols("z a b c d")
        tschirnhaus = z - (y**4 + a * y**3 + b * y**2 + c * y + d)

        # Taking the resultant will explode combinatorially
        res = resultant(p_depressed, tschirnhaus, y)
        res_expanded = expand(res)

        invariants = {
            "polynomial": "x^5 + 3x^4 - 2x^3 + 7x^2 - x + 1",
            "depressed_form": str(p_depressed),
            "resultant_length": len(str(res_expanded)),
        }
    except MemoryError:
        status = "RESOURCE_EXHAUSTED"
        errors.append("MemoryError: Límite de RAM excedido durante la expansión.")
    except Exception as e:
        status = "ERROR"
        errors.append(str(e))

    elapsed = time.time() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "branch": "B2_bring_jerrard",
        "status": status,
        "invariants": invariants,
        "metrics": {
            "execution_time_sec": round(elapsed, 4),
            "peak_ram_mb": round(peak / (1024 * 1024), 2),
        },
        "errors": errors,
    }
    result_queue.put(cert)


def run():
    result_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_bring_worker, args=(result_queue,))
    t0_main = time.time()
    proc.start()
    proc.join(timeout=15)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        cert = {
            "branch": "B2_bring_jerrard",
            "status": "TIMEOUT",
            "invariants": {},
            "metrics": {
                "execution_time_sec": round(time.time() - t0_main, 4),
                "peak_ram_mb": 0.0,  # Unknown since it was killed
            },
            "errors": ["Timeout de 15 segundos excedido debido a Expression Swell."],
        }
    else:
        if not result_queue.empty():
            cert = result_queue.get()
        else:
            cert = {
                "branch": "B2_bring_jerrard",
                "status": "RESOURCE_EXHAUSTED",
                "invariants": {},
                "metrics": {
                    "execution_time_sec": round(time.time() - t0_main, 4),
                    "peak_ram_mb": 0.0,
                },
                "errors": [
                    f"Proceso abortado anormalmente (Exit Code: {proc.exitcode}). Posible agotamiento de RAM o límite del SO."
                ],
            }

    with open(OUTPUT, "w") as f:
        json.dump(cert, f, indent=2)


if __name__ == "__main__":
    run()
