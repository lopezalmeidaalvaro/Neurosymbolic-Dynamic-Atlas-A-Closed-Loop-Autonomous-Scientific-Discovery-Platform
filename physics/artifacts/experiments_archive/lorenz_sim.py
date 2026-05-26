import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os


def lorenz(t, state, sigma, beta, rho):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]


sigma = 10.0
beta = 8.0 / 3.0
rhos = [15.0, 28.0]
initial_state = [1.0, 1.0, 1.0]
t_span = (0, 50)
t_eval = np.linspace(t_span[0], t_span[1], 10000)

fig = plt.figure(figsize=(12, 6))

for i, rho in enumerate(rhos):
    sol = solve_ivp(
        lorenz,
        t_span,
        initial_state,
        args=(sigma, beta, rho),
        t_eval=t_eval,
        method="RK45",
    )

    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    ax.plot(sol.y[0], sol.y[1], sol.y[2], lw=0.5)
    ax.set_title(f"Lorenz System ($\\rho$={rho})")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

plt.tight_layout()
output_path = os.path.abspath("artifacts/lorenz_rho_comparison.png")
plt.savefig(output_path)
print(f"Grafico guardado exitosamente en: {output_path}")
