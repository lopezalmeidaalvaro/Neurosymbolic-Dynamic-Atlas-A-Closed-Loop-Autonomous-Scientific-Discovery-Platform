import numpy as np


def generate_lorenz(
    n_timesteps=5000, dt=0.01, sigma=10, rho=28, beta=8 / 3, initial_state=None
):
    """
    Integrates the 3D Lorenz chaotic system using Runge-Kutta 4th Order (RK4).
    """
    if initial_state is None:
        np.random.seed(42)
        initial_state = np.random.uniform(-15.0, 15.0, 3)

    t = np.arange(n_timesteps) * dt
    x = np.zeros(n_timesteps)
    y = np.zeros(n_timesteps)
    z = np.zeros(n_timesteps)

    x[0], y[0], z[0] = initial_state

    def lorenz_rhs(curr_x, curr_y, curr_z):
        return (
            sigma * (curr_y - curr_x),
            curr_x * (rho - curr_z) - curr_y,
            curr_x * curr_y - beta * curr_z,
        )

    # RK4 Integration Loop
    for i in range(n_timesteps - 1):
        cx, cy, cz = x[i], y[i], z[i]

        k1_x, k1_y, k1_z = lorenz_rhs(cx, cy, cz)
        k2_x, k2_y, k2_z = lorenz_rhs(
            cx + 0.5 * dt * k1_x, cy + 0.5 * dt * k1_y, cz + 0.5 * dt * k1_z
        )
        k3_x, k3_y, k3_z = lorenz_rhs(
            cx + 0.5 * dt * k2_x, cy + 0.5 * dt * k2_y, cz + 0.5 * dt * k2_z
        )
        k4_x, k4_y, k4_z = lorenz_rhs(cx + dt * k3_x, cy + dt * k3_y, cz + dt * k3_z)

        x[i + 1] = cx + (dt / 6.0) * (k1_x + 2 * k2_x + 2 * k3_x + k4_x)
        y[i + 1] = cy + (dt / 6.0) * (k1_y + 2 * k2_y + 2 * k3_y + k4_y)
        z[i + 1] = cz + (dt / 6.0) * (k1_z + 2 * k2_z + 2 * k3_z + k4_z)

    # Derivatives using 2nd-order finite differences
    dx = np.gradient(x, dt)
    dy = np.gradient(y, dt)
    dz = np.gradient(z, dt)

    return {
        "t": t,
        "x": x,
        "y": y,
        "z": z,
        "derivatives": {"dx": dx, "dy": dy, "dz": dz},
        "params": {"sigma": sigma, "rho": rho, "beta": beta},
    }


def generate_rossler(
    n_timesteps=5000, dt=0.01, a=0.2, b=0.2, c=5.7, initial_state=None
):
    """
    Integrates the 3D Rössler chaotic attractor using Runge-Kutta 4th Order (RK4).
    """
    if initial_state is None:
        np.random.seed(42)
        initial_state = np.random.uniform(-5.0, 5.0, 3)

    t = np.arange(n_timesteps) * dt
    x = np.zeros(n_timesteps)
    y = np.zeros(n_timesteps)
    z = np.zeros(n_timesteps)

    x[0], y[0], z[0] = initial_state

    def rossler_rhs(curr_x, curr_y, curr_z):
        return (-curr_y - curr_z, curr_x + a * curr_y, b + curr_z * (curr_x - c))

    # RK4 Integration Loop
    for i in range(n_timesteps - 1):
        cx, cy, cz = x[i], y[i], z[i]

        k1_x, k1_y, k1_z = rossler_rhs(cx, cy, cz)
        k2_x, k2_y, k2_z = rossler_rhs(
            cx + 0.5 * dt * k1_x, cy + 0.5 * dt * k1_y, cz + 0.5 * dt * k1_z
        )
        k3_x, k3_y, k3_z = rossler_rhs(
            cx + 0.5 * dt * k2_x, cy + 0.5 * dt * k2_y, cz + 0.5 * dt * k2_z
        )
        k4_x, k4_y, k4_z = rossler_rhs(cx + dt * k3_x, cy + dt * k3_y, cz + dt * k3_z)

        x[i + 1] = cx + (dt / 6.0) * (k1_x + 2 * k2_x + 2 * k3_x + k4_x)
        y[i + 1] = cy + (dt / 6.0) * (k1_y + 2 * k2_y + 2 * k3_y + k4_y)
        z[i + 1] = cz + (dt / 6.0) * (k1_z + 2 * k2_z + 2 * k3_z + k4_z)

    # Derivatives
    dx = np.gradient(x, dt)
    dy = np.gradient(y, dt)
    dz = np.gradient(z, dt)

    return {
        "t": t,
        "x": x,
        "y": y,
        "z": z,
        "derivatives": {"dx": dx, "dy": dy, "dz": dz},
        "params": {"a": a, "b": b, "c": c},
    }


def generate_duffing(
    n_timesteps=5000,
    dt=0.01,
    alpha=1.0,
    beta=-1.0,
    gamma=0.3,
    delta=0.2,
    omega=1.2,
    initial_state=None,
):
    """
    Integrates the forced Duffing non-linear oscillator equation using Runge-Kutta 4th Order (RK4).
    x'' = -delta*x' - alpha*x - beta*x^3 + gamma*cos(omega*t)
    """
    if initial_state is None:
        np.random.seed(42)
        initial_state = np.random.uniform(-1.0, 1.0, 2)

    t = np.arange(n_timesteps) * dt
    x = np.zeros(n_timesteps)
    v = np.zeros(n_timesteps)

    x[0], v[0] = initial_state

    def duffing_rhs(curr_t, curr_x, curr_v):
        return (
            curr_v,
            -delta * curr_v
            - alpha * curr_x
            - beta * (curr_x**3)
            + gamma * np.cos(omega * curr_t),
        )

    # RK4 Loop
    for i in range(n_timesteps - 1):
        cx, cv, ct = x[i], v[i], t[i]

        k1_x, k1_v = duffing_rhs(ct, cx, cv)
        k2_x, k2_v = duffing_rhs(
            ct + 0.5 * dt, cx + 0.5 * dt * k1_x, cv + 0.5 * dt * k1_v
        )
        k3_x, k3_v = duffing_rhs(
            ct + 0.5 * dt, cx + 0.5 * dt * k2_x, cv + 0.5 * dt * k2_v
        )
        k4_x, k4_v = duffing_rhs(ct + dt, cx + dt * k3_x, cv + dt * k3_v)

        x[i + 1] = np.clip(
            cx + (dt / 6.0) * (k1_x + 2 * k2_x + 2 * k3_x + k4_x), -50.0, 50.0
        )
        v[i + 1] = np.clip(
            cv + (dt / 6.0) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v), -50.0, 50.0
        )

    dx = np.gradient(x, dt)
    dv = np.gradient(v, dt)

    return {
        "t": t,
        "x": x,
        "v": v,
        "derivatives": {"dx": dx, "dv": dv},
        "params": {
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
            "delta": delta,
            "omega": omega,
        },
    }


def generate_van_der_pol(n_timesteps=5000, dt=0.01, mu=1.5, initial_state=None):
    """
    Integrates the Van der Pol oscillator equations using Runge-Kutta 4th Order (RK4).
    x'' - mu*(1-x^2)*x' + x = 0
    """
    if initial_state is None:
        np.random.seed(42)
        initial_state = np.random.uniform(-2.0, 2.0, 2)

    t = np.arange(n_timesteps) * dt
    x = np.zeros(n_timesteps)
    v = np.zeros(n_timesteps)

    x[0], v[0] = initial_state

    def vdp_rhs(curr_x, curr_v):
        return (curr_v, mu * (1.0 - curr_x**2) * curr_v - curr_x)

    # RK4 Loop
    for i in range(n_timesteps - 1):
        cx, cv = x[i], v[i]

        k1_x, k1_v = vdp_rhs(cx, cv)
        k2_x, k2_v = vdp_rhs(cx + 0.5 * dt * k1_x, cv + 0.5 * dt * k1_v)
        k3_x, k3_v = vdp_rhs(cx + 0.5 * dt * k2_x, cv + 0.5 * dt * k2_v)
        k4_x, k4_v = vdp_rhs(cx + dt * k3_x, cv + dt * k3_v)

        x[i + 1] = np.clip(
            cx + (dt / 6.0) * (k1_x + 2 * k2_x + 2 * k3_x + k4_x), -50.0, 50.0
        )
        v[i + 1] = np.clip(
            cv + (dt / 6.0) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v), -50.0, 50.0
        )

    dx = np.gradient(x, dt)
    dv = np.gradient(v, dt)

    return {
        "t": t,
        "x": x,
        "v": v,
        "derivatives": {"dx": dx, "dv": dv},
        "params": {"mu": mu},
    }


def generate_logistic_map(n_iterations=2000, r=3.9, initial_x=0.5):
    """
    Simulates the chaotic Logistic discrete-time map.
    """
    x = np.zeros(n_iterations)
    x[0] = initial_x
    for t in range(n_iterations - 1):
        x[t + 1] = r * x[t] * (1.0 - x[t])

    return {"x": x, "params": {"r": r}}


def get_ground_truth_equations(system_name):
    """
    Returns the ground truth symbolic representations and names for each system.
    """
    if system_name == "lorenz":
        return {
            "equations_latex": [
                "\\frac{dx}{dt} = \\sigma(y-x)",
                "\\frac{dy}{dt} = x(\\rho-z) - y",
                "\\frac{dz}{dt} = xy - \\beta z",
            ],
            "equations_sympy": {
                "dx": "sigma * (y - x)",
                "dy": "x * (rho - z) - y",
                "dz": "x * y - beta * z",
            },
            "variables": ["x", "y", "z"],
            "params_names": ["sigma", "rho", "beta"],
        }
    elif system_name == "rossler":
        return {
            "equations_latex": [
                "\\frac{dx}{dt} = -y - z",
                "\\frac{dy}{dt} = x + a y",
                "\\frac{dz}{dt} = b + z(x-c)",
            ],
            "equations_sympy": {
                "dx": "-y - z",
                "dy": "x + a * y",
                "dz": "b + z * (x - c)",
            },
            "variables": ["x", "y", "z"],
            "params_names": ["a", "b", "c"],
        }
    elif system_name == "duffing":
        return {
            "equations_latex": [
                "\\frac{dx}{dt} = v",
                "\\frac{dv}{dt} = -\\delta v - \\alpha x - \\beta x^3 + \\gamma \\cos(\\omega t)",
            ],
            "equations_sympy": {
                "dx": "v",
                "dv": "-delta * v - alpha * x - beta * (x**3) + gamma * cos(omega * t)",
            },
            "variables": ["x", "v"],
            "params_names": ["alpha", "beta", "gamma", "delta", "omega"],
        }
    elif system_name == "van_der_pol":
        return {
            "equations_latex": [
                "\\frac{dx}{dt} = v",
                "\\frac{dv}{dt} = \\mu(1-x^2)v - x",
            ],
            "equations_sympy": {"dx": "v", "dv": "mu * (1 - x**2) * v - x"},
            "variables": ["x", "v"],
            "params_names": ["mu"],
        }
    elif system_name == "logistic":
        return {
            "equations_latex": ["x_{t+1} = r x_t (1 - x_t)"],
            "equations_sympy": {"x_next": "r * x * (1 - x)"},
            "variables": ["x"],
            "params_names": ["r"],
        }
    else:
        raise ValueError(f"Unknown system name: {system_name}")
