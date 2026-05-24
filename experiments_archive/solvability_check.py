import sympy as sp


def check_solvability():
    x = sp.Symbol("x")
    p = x**5 + 3 * x**4 - 2 * x**3 + 7 * x**2 - x + 1
    print(f"Polinomio: {p}")

    roots = sp.solve(p, x)
    print("Representación de las raíces:")
    for r in roots:
        print(f" - {r}")

    has_crootof = any(isinstance(r, sp.CRootOf) for r in roots)
    if has_crootof:
        print(
            "\nRESULTADO: El polinomio NO es resoluble por radicales (Sympy usa CRootOf)."
        )
    else:
        print(
            "\nRESULTADO: El polinomio ES resoluble por radicales (raíces explícitas encontradas)."
        )


if __name__ == "__main__":
    check_solvability()
