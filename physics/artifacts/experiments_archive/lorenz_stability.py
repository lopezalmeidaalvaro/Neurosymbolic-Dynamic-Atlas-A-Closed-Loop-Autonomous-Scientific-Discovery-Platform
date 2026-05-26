import sympy as sp

# Definir variables y parametros
x, y, z = sp.symbols("x y z", real=True)
sigma, beta, rho = sp.symbols("sigma beta rho", real=True, positive=True)

# Ecuaciones del sistema de Lorenz
dxdt = sigma * (y - x)
dydt = x * (rho - z) - y
dzdt = x * y - beta * z

# Encontrar puntos de equilibrio
equilibria = sp.solve([dxdt, dydt, dzdt], (x, y, z))

print("Puntos de equilibrio encontrados:")
for eq in equilibria:
    print(f" - {eq}")

# Calcular matriz Jacobiana
J = sp.Matrix([dxdt, dydt, dzdt]).jacobian([x, y, z])
print("\nMatriz Jacobiana:")
sp.pprint(J)

# Analizar la estabilidad de los puntos de equilibrio para valores especificos
sigma_val = 10
beta_val = 8 / 3
rho_vals = [15, 28]

for r_val in rho_vals:
    print(f"\n--- Analisis para rho = {r_val} ---")

    # Sustituir valores de sigma, beta y rho
    eqs_sub = [
        (
            eq[0].subs({beta: beta_val, rho: r_val}),
            eq[1].subs({beta: beta_val, rho: r_val}),
            eq[2].subs({beta: beta_val, rho: r_val}),
        )
        for eq in equilibria
    ]

    for i, eq in enumerate(eqs_sub):
        try:
            # Evaluar numéricamente si es posible
            eq_num = (float(eq[0].evalf()), float(eq[1].evalf()), float(eq[2].evalf()))
            print(f"\nEquilibrio {i+1}: {eq_num}")

            # Evaluar el Jacobiano en este punto de equilibrio
            J_eq = J.subs(
                {
                    x: eq[0],
                    y: eq[1],
                    z: eq[2],
                    sigma: sigma_val,
                    beta: beta_val,
                    rho: r_val,
                }
            )

            # Calcular autovalores
            eigenvals = J_eq.eigenvals()
            print("Autovalores:")
            for ev in eigenvals:
                ev_num = complex(ev.evalf())
                print(f"  {ev_num:.4f}")

            # Determinar estabilidad
            max_real_part = max([sp.re(ev).evalf() for ev in eigenvals])
            if max_real_part < 0:
                print("-> ESTABLE (Todas las partes reales son negativas)")
            elif max_real_part > 0:
                print("-> INESTABLE (Al menos una parte real es positiva)")
            else:
                print("-> INDETERMINADO (Parte real maxima es cero)")
        except Exception as e:
            print(f"Error evaluando el equilibrio: {e}")
