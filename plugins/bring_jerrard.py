"""
PLUGIN: bring_jerrard
Intenta transformar el polinomio a forma Bring-Jerrard via Tschirnhaus.
Ejecutado por el orquestador dentro de un subproceso con timeout de 15s.
Contrato: lee la expresion matematica de sys.argv[1].
Emite: bring_jerrard_result.json
"""
import json, sys, time, tracemalloc
import sympy as sp
from sympy import symbols, expand, Poly, resultant, ZZ

OUTPUT = "bring_jerrard_result.json"


def run(expr_str):
    tracemalloc.start()
    t0 = time.time()
    errors = []
    output = {}
    status = "success"

    try:
        x, y = symbols('x y')
        p = sp.sympify(expr_str.replace('^', '**'))

        # Step 1: depress x^4 via x -> y - a4/(5*a5)
        poly = Poly(p, x, domain=ZZ)
        coeffs = poly.all_coeffs()  # [a5, a4, a3, a2, a1, a0]
        a5 = coeffs[0] if len(coeffs) > 0 else 0
        a4 = coeffs[1] if len(coeffs) > 1 else 0
        shift = sp.Rational(-a4, 5 * a5) if a5 != 0 else 0
        p_dep = expand(p.subs(x, y + shift))

        # Detect if already in Bring-Jerrard form (only x^5, x^1, x^0 terms)
        poly_dep = Poly(p_dep, y, domain='QQ')
        dep_coeffs = poly_dep.all_coeffs()

        coeff_labels = {5: 'x^5', 4: 'x^4', 3: 'x^3', 2: 'x^2', 1: 'x^1', 0: 'x^0'}
        degree = poly_dep.degree()
        coeff_map = {}
        for i, c in enumerate(dep_coeffs):
            power = degree - i
            coeff_map[f"coeff_{coeff_labels.get(power, f'x^{power}')}"] = str(c)

        # Check if already depressed (x^4, x^3, x^2 all zero)
        is_bring_jerrard = all(
            dep_coeffs[i] == 0
            for i in range(len(dep_coeffs))
            if (degree - i) in (4, 3, 2)
        )

        if is_bring_jerrard:
            bring_note = "Polynomial is already in Bring-Jerrard form (no x^4, x^3, x^2 terms). No further Tschirnhaus substitutions required."
        else:
            # Attempt a Tschirnhaus resultant to eliminate x^3 - this is the heavy step
            z, a = symbols('z a')
            tschirnhaus = z - (y**2 + a * y)
            # NOTE: this resultant can cause Expression Swell for dense polynomials
            res = resultant(p_dep, tschirnhaus, y)
            bring_note = f"Tschirnhaus resultant computed. Length of expression: {len(str(res))} chars."

        output = {
            "depressed_polynomial": str(p_dep),
            "coefficient_map": coeff_map,
            "is_already_bring_jerrard": is_bring_jerrard,
            "note": bring_note
        }

    except MemoryError:
        errors.append("MemoryError: RAM limit exceeded during Tschirnhaus expansion.")
        status = "failure"
    except Exception as e:
        errors.append(str(e))
        status = "error"

    elapsed = time.time() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    cert = {
        "plugin": "bring_jerrard",
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
