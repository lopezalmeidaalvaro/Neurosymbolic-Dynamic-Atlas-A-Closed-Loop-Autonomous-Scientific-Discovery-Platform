import json
import time
import sys
import tracemalloc
import sympy as sp
from sympy import Poly, Symbol, discriminant, factor, ZZ

OUTPUT = "cert_B1_galois.json"


def run():
    tracemalloc.start()
    t0 = time.time()
    errors = []

    try:
        x = Symbol("x")
        p = x**5 + 3 * x**4 - 2 * x**3 + 7 * x**2 - x + 1
        poly = Poly(p, x, domain=ZZ)

        is_irreducible = poly.is_irreducible
        factor_q = str(factor(p))
        disc = discriminant(p, x)
        disc_val = int(disc)
        disc_sign = "negative" if disc_val < 0 else "positive"

        frobenius_patterns = {}
        primes_to_test = [2, 3, 5, 7, 11, 13, 17, 19]
        cycle_patterns = []

        for prime in primes_to_test:
            try:
                poly_mod = Poly(p, x, modulus=prime)
                factors_mod = sp.factor_list(poly_mod.as_expr(), modulus=prime)
                degrees = sorted([f.as_poly(x).degree() for f, _ in factors_mod[1]])
                pattern = tuple(degrees)
                frobenius_patterns[str(prime)] = list(pattern)
                cycle_patterns.append(pattern)
            except Exception:
                frobenius_patterns[str(prime)] = "error"

        has_5_cycle = any(p == (5,) for p in cycle_patterns)

        import math

        sqrt_disc = math.isqrt(abs(disc_val))
        disc_is_square = sqrt_disc * sqrt_disc == abs(disc_val)

        if is_irreducible and has_5_cycle and not disc_is_square:
            galois_group = "S5"
            solvable_by_radicals = False
            galois_confidence = "high"
        elif is_irreducible and has_5_cycle and disc_is_square:
            galois_group = "A5"
            solvable_by_radicals = False
            galois_confidence = "high"
        elif is_irreducible:
            galois_group = "S5 (probable)"
            solvable_by_radicals = False
            galois_confidence = "medium"
        else:
            galois_group = "reducible"
            solvable_by_radicals = "unknown"
            galois_confidence = "low"

        invariants = {
            "polynomial": "x^5 + 3x^4 - 2x^3 + 7x^2 - x + 1",
            "is_irreducible_over_Q": bool(is_irreducible),
            "factorization_over_Q": factor_q,
            "discriminant": disc_val,
            "discriminant_sign": disc_sign,
            "discriminant_is_perfect_square": disc_is_square,
            "frobenius_patterns_mod_p": frobenius_patterns,
            "has_5_cycle_in_frobenius": bool(has_5_cycle),
            "galois_group": galois_group,
            "galois_group_confidence": galois_confidence,
            "solvable_by_radicals": solvable_by_radicals,
        }
        status = "SUCCESS"
    except Exception as e:
        invariants = {}
        errors.append(str(e))
        status = "ERROR"

    elapsed = time.time() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "branch": "B1_galois",
        "status": status,
        "invariants": invariants,
        "metrics": {
            "execution_time_sec": round(elapsed, 4),
            "peak_ram_mb": round(peak / (1024 * 1024), 2),
        },
        "errors": errors,
    }

    with open(OUTPUT, "w") as f:
        json.dump(cert, f, indent=2)


if __name__ == "__main__":
    run()
