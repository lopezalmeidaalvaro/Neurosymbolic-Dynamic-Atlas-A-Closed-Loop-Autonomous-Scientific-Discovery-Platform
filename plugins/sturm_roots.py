"""
PLUGIN: sturm_roots
Construye la secuencia de Sturm y aisla raices reales.
Contrato: lee la expresion matematica de sys.argv[1].
Emite: sturm_roots_result.json
"""
import json, sys, time, tracemalloc
from sympy import Symbol, Poly, ZZ, sturm, count_roots, Rational, CRootOf

OUTPUT = "sturm_roots_result.json"

def sign_changes(seq):
    filtered = [s for s in seq if s != 0]
    return sum(1 for i in range(len(filtered) - 1) if filtered[i] * filtered[i+1] < 0)

def eval_sturm_at(sturm_seq, point):
    return [int(p.eval(point)) for p in sturm_seq]

def count_in(sturm_seq, a, b):
    va = sign_changes(eval_sturm_at(sturm_seq, a))
    vb = sign_changes(eval_sturm_at(sturm_seq, b))
    return va - vb

def bisect_root(sturm_seq, a, b, tol=Rational(1, 10**10)):
    a, b = Rational(a), Rational(b)
    for _ in range(100):
        if b - a <= tol:
            break
        mid = (a + b) / 2
        if count_in(sturm_seq, a, mid) == 1:
            b = mid
        else:
            a = mid
    return a, b

def run(expr_str):
    import sympy as sp
    tracemalloc.start()
    t0 = time.time()
    errors = []
    output = {}
    status = "success"

    try:
        x = Symbol('x')
        p = sp.sympify(expr_str.replace('^', '**'))
        poly = Poly(p, x, domain=ZZ)

        sturm_seq = sturm(poly)
        M = 1000
        n_real = count_in(sturm_seq, -M, M)

        isolation_intervals = []
        for i in range(-M, M):
            if count_in(sturm_seq, i, i+1) == 1:
                isolation_intervals.append((i, i+1))

        bisection_results = []
        for (a_i, b_i) in isolation_intervals:
            lo, hi = bisect_root(sturm_seq, a_i, b_i)
            bisection_results.append({
                "interval_initial": [a_i, b_i],
                "interval_refined": [str(lo), str(hi)],
                "midpoint_float64": float((lo + hi) / 2)
            })

        # Exact value via CRootOf for the first real root
        real_root_exact = None
        try:
            real_root_exact = str(CRootOf(p, 0).evalf(30))
        except Exception:
            real_root_exact = "unavailable"

        output = {
            "sturm_sequence_length": len(sturm_seq),
            "sturm_sequence": [str(s) for s in sturm_seq],
            "n_real_roots": n_real,
            "isolation_intervals": isolation_intervals,
            "bisection_results": bisection_results,
            "first_real_root_30dec": real_root_exact
        }

    except Exception as e:
        errors.append(str(e))
        status = "error"

    elapsed = time.time() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "plugin": "sturm_roots",
        "status": status,
        "input": {"target_expression": expr_str},
        "output": output,
        "metrics": {
            "runtime_sec": round(elapsed, 4),
            "peak_ram_mb": round(peak / (1024 * 1024), 2)
        },
        "errors": errors
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2, default=str)


if __name__ == "__main__":
    expr = sys.argv[1] if len(sys.argv) > 1 else "x^5 - x + 1"
    run(expr)
