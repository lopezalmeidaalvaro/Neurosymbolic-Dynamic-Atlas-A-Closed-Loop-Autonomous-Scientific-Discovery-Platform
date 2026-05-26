import numpy as np
from scipy.optimize import root


def get_bifurcation(f, df, period, x_guess, p_guess):
    def system(vars):
        x, p = vars
        curr_x = x
        curr_df = 1.0
        for _ in range(period):
            curr_df *= df(curr_x, p)
            curr_x = f(curr_x, p)
        return [curr_x - x, curr_df + 1.0]

    res = root(system, [x_guess, p_guess], method="lm")
    if res.success:
        return res.x[0], res.x[1]

    res = root(system, [x_guess, p_guess])
    if res.success:
        return res.x[0], res.x[1]

    return None, None


def find_all_bifurcations(f, df, name, p1_guess, x1_guess, p2_guess):
    print(f"--- Explorando {name} ---")
    bifs = []

    # Bifurcation 1 (period 1 -> 2)
    x1, p1 = get_bifurcation(f, df, 1, x1_guess, p1_guess)
    if p1 is None:
        print("Error p1")
        return []
    bifs.append(p1)
    print(f"Bifurcación de periodo 2: p1 = {p1:.6f}")

    def get_x_guess(p, x_start):
        x = x_start
        for _ in range(2000):
            x = f(x, p)
        return x

    # Bifurcation 2 (period 2 -> 4)
    x2_guess = get_x_guess(p2_guess - 0.01, 0.5)
    x2, p2 = get_bifurcation(f, df, 2, x2_guess, p2_guess)
    if p2 is None:
        print("Error p2")
        return []
    bifs.append(p2)
    print(f"Bifurcación de periodo 4: p2 = {p2:.6f}")

    ratios = []

    # Bifurcation 3 and 4
    for n in range(3, 5):
        period = 2 ** (n - 1)
        p_guess = bifs[-1] + (bifs[-1] - bifs[-2]) / 4.669
        x_guess = get_x_guess(p_guess - 1e-4, 0.5)

        x_n, p_n = get_bifurcation(f, df, period, x_guess, p_guess)
        if p_n is None:
            print(f"Error hallando bifurcación de periodo {period*2}")
            break
        bifs.append(p_n)
        print(f"Bifurcación de periodo {period*2}: p{n} = {p_n:.6f}")

    for i in range(len(bifs) - 2):
        delta = (bifs[i + 1] - bifs[i]) / (bifs[i + 2] - bifs[i + 1])
        ratios.append(delta)
        print(f"Ratio de convergencia delta_{i+1}: {delta:.5f}")

    return ratios


# Mapa Logístico (Polinómico)
f_log = lambda x, r: r * x * (1 - x)
df_log = lambda x, r: r * (1 - 2 * x)

# Mapa Senoidal (Trascendental)
f_sin = lambda x, c: c * np.sin(np.pi * x)
df_sin = lambda x, c: c * np.pi * np.cos(np.pi * x)

print("Iniciando Búsqueda de Invariantes de Escala (Feigenbaum)")

ratios_log = find_all_bifurcations(f_log, df_log, "Mapa Logístico", 3.0, 0.6, 3.45)
ratios_sin = find_all_bifurcations(f_sin, df_sin, "Mapa Senoidal", 0.72, 0.6, 0.83)

if len(ratios_log) >= 2 and len(ratios_sin) >= 2:
    if abs(ratios_log[-1] - ratios_sin[-1]) < 0.2:
        print("\n*** POSIBLE UNIVERSALIDAD DETECTADA ***")
        print(
            "Ambos sistemas convergen hacia el mismo ratio estructural geométrico (Constante de Feigenbaum)."
        )
