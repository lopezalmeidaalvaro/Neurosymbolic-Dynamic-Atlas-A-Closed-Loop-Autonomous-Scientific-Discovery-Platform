"""
PLUGIN: galois_group
Calcula irreducibilidad, discriminante y grupo de Galois.
Contrato: lee la expresion matematica de sys.argv[1].
Emite: galois_group_result.json
"""
import json, sys, time, math, tracemalloc
import sympy as sp
from sympy import Poly, Symbol, discriminant, factor, ZZ

OUTPUT = "galois_group_result.json"

def run(expr_str):
    tracemalloc.start()
    t0 = time.time()
    errors = []
    output = {}

    try:
        x = Symbol('x')
        # Parse expression: replace ^ with ** for SymPy
        p = sp.sympify(expr_str.replace('^', '**'))
        poly = Poly(p, x, domain=ZZ)

        is_irreducible = poly.is_irreducible
        factor_q = str(factor(p))
        disc_val = int(discriminant(p, x))
        disc_sign = "negative" if disc_val < 0 else "positive"

        frobenius_patterns = {}
        cycle_patterns = []
        for prime in [2, 3, 5, 7, 11, 13, 17, 19]:
            try:
                poly_mod = Poly(p, x, modulus=prime)
                factors_mod = sp.factor_list(poly_mod.as_expr(), modulus=prime)
                degrees = sorted([f.as_poly(x).degree() for f, _ in factors_mod[1]])
                pattern = tuple(degrees)
                frobenius_patterns[str(prime)] = list(pattern)
                cycle_patterns.append(pattern)
            except Exception:
                frobenius_patterns[str(prime)] = "error"

        has_5_cycle = any(pat == (5,) for pat in cycle_patterns)
        sqrt_disc = math.isqrt(abs(disc_val))
        disc_is_square = (sqrt_disc * sqrt_disc == abs(disc_val))

        if is_irreducible and has_5_cycle and not disc_is_square:
            galois_group, solvable, confidence = "S5", False, "high"
        elif is_irreducible and has_5_cycle and disc_is_square:
            galois_group, solvable, confidence = "A5", False, "high"
        elif is_irreducible:
            galois_group, solvable, confidence = "S5 (probable)", False, "medium"
        else:
            galois_group, solvable, confidence = "reducible", "unknown", "low"

        output = {
            "is_irreducible_over_Q": bool(is_irreducible),
            "factorization_over_Q": factor_q,
            "discriminant": disc_val,
            "discriminant_sign": disc_sign,
            "discriminant_is_perfect_square": disc_is_square,
            "frobenius_patterns_mod_p": frobenius_patterns,
            "has_5_cycle_in_frobenius": bool(has_5_cycle),
            "galois_group": galois_group,
            "galois_group_confidence": confidence,
            "solvable_by_radicals": solvable
        }
        status = "success"

    except Exception as e:
        errors.append(str(e))
        status = "error"

    elapsed = time.time() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "plugin": "galois_group",
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
        json.dump(cert, f, indent=2)


if __name__ == "__main__":
    expr = sys.argv[1] if len(sys.argv) > 1 else "x^5 - x + 1"
    run(expr)
