import json, time
import tracemalloc
from sympy import Symbol, Poly, ZZ, sturm, count_roots, Rational, CRootOf

OUTPUT = "cert_B3_sturm.json"

def sign_changes(seq):
    filtered = [s for s in seq if s != 0]
    return sum(1 for i in range(len(filtered)-1) if filtered[i] * filtered[i+1] < 0)

def eval_sturm_at(sturm_seq, point):
    return [int(p.eval(point)) for p in sturm_seq]

def count_real_roots_in(sturm_seq, a, b):
    va = sign_changes(eval_sturm_at(sturm_seq, a))
    vb = sign_changes(eval_sturm_at(sturm_seq, b))
    return va - vb

def bisect_root(sturm_seq, a, b, tol=Rational(1, 10**10)):
    a, b = Rational(a), Rational(b)
    iterations = 0
    while b - a > tol and iterations < 100:
        mid = (a + b) / 2
        left_count = count_real_roots_in(sturm_seq, a, mid)
        if left_count == 1:
            b = mid
        else:
            a = mid
        iterations += 1
    return a, b, iterations

def run():
    tracemalloc.start()
    t0 = time.time()
    errors = []
    status = "SUCCESS"
    invariants = {}

    try:
        x = Symbol('x')
        p = x**5 + 3*x**4 - 2*x**3 + 7*x**2 - x + 1
        poly = Poly(p, x, domain=ZZ)

        sturm_seq = sturm(poly)
        sturm_strs = [str(s) for s in sturm_seq]

        M = 1000
        n_real_global = count_real_roots_in(sturm_seq, -M, M)

        search_points = list(range(-M, M+1, 1))
        isolation_intervals = []
        for i in range(len(search_points)-1):
            a_i, b_i = search_points[i], search_points[i+1]
            if count_real_roots_in(sturm_seq, a_i, b_i) == 1:
                isolation_intervals.append((a_i, b_i))

        bisect_results = []
        for (a_i, b_i) in isolation_intervals:
            lo, hi, iters = bisect_root(sturm_seq, a_i, b_i)
            midpoint = float((lo + hi) / 2)
            bisect_results.append({
                "interval_initial": [a_i, b_i],
                "interval_refined": [str(lo), str(hi)],
                "midpoint_float64": midpoint
            })

        invariants = {
            "polynomial": "x^5 + 3x^4 - 2x^3 + 7x^2 - x + 1",
            "sturm_sequence_length": len(sturm_seq),
            "n_real_roots_sturm": n_real_global,
            "isolation_intervals_found": isolation_intervals,
            "bisection_results": bisect_results
        }
    except Exception as e:
        status = "ERROR"
        errors.append(str(e))

    elapsed = time.time() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "branch": "B3_sturm",
        "status": status,
        "invariants": invariants,
        "metrics": {
            "execution_time_sec": round(elapsed, 4),
            "peak_ram_mb": round(peak / (1024 * 1024), 2)
        },
        "errors": errors
    }

    with open(OUTPUT, "w") as f:
        json.dump(cert, f, indent=2, default=str)

if __name__ == "__main__":
    run()
