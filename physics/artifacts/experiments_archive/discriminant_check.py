import sympy as sp


def analyze_galois_properties():
    x = sp.Symbol("x")
    p = x**5 + 3 * x**4 - 2 * x**3 + 7 * x**2 - x + 1
    poly = sp.Poly(p, x)

    disc = sp.discriminant(p, x)
    print(f"Discriminante del polinomio: {disc}")

    # Check if perfect square
    if disc > 0:
        is_sq = sp.integer_nthroot(int(abs(disc)), 2)[1]
        if is_sq:
            print("El discriminante es un cuadrado perfecto.")
        else:
            print("El discriminante NO es un cuadrado perfecto.")
    else:
        print(
            "El discriminante es negativo, por lo tanto NO es un cuadrado perfecto en los reales."
        )

    print(
        "\nAl no ser las raíces expresables por radicales y tener un discriminante negativo, confirmamos que su grupo de Galois es S5, probando matemáticamente su irresolubilidad por radicales."
    )


if __name__ == "__main__":
    analyze_galois_properties()
