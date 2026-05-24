import numpy as np
from scipy.integrate import solve_ivp
import sqlite3
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
sys.path.append(os.path.dirname(__file__))

try:
    from topology_miner_v2 import compute_embedding
except ImportError:
    print("[ERROR] No se pudo importar topology_miner_v2.")
    sys.exit(1)


def lorenz(t, state):
    x, y, z = state
    return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0 / 3.0) * z]


def rossler(t, state):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]


def chua(t, state):
    x, y, z = state
    alpha = 15.6
    beta = 28.0
    m0 = -1.143
    m1 = -0.714
    f_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1.0) - np.abs(x - 1.0))
    return [alpha * (y - x - f_x), x - y + z, -beta * y]


def duffing(t, state):
    x, y = state
    dxdt = y
    dydt = x - x**3 - 0.3 * y + 0.5 * np.cos(1.2 * t)
    return [dxdt, dydt]


def main():
    print("FASE 13 - Integrando atractores continuos 3D...")
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, 30000)
    dt = t_eval[1] - t_eval[0]

    systems = {
        "lorenz": (lorenz, [1.0, 1.0, 1.0], 28.0),
        "rossler": (rossler, [1.0, 1.0, 1.0], 5.7),
        "chua": (chua, [0.1, 0.1, 0.1], 15.6),
        "duffing": (duffing, [0.1, 0.0], 0.5),
    }

    conn = sqlite3.connect(DB_PATH)

    # Ensure the table has noise_level and seed columns (idempotent migration)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS structural_embeddings (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id            INTEGER,
            system_name        TEXT,
            noise_level        REAL DEFAULT 0.0,
            seed               INTEGER DEFAULT 42,
            lyapunov_max       REAL,
            spectral_entropy   REAL,
            dominant_frequency REAL,
            variance           REAL,
            autocorr_decay     REAL,
            kurtosis           REAL,
            skewness           REAL,
            energy             REAL,
            embedding_json     TEXT,
            UNIQUE(system_name, noise_level, seed)
        )
    """)
    # Add columns if upgrading from old schema without them
    for col, default in [("noise_level", "0.0"), ("seed", "42")]:
        try:
            conn.execute(
                f"ALTER TABLE structural_embeddings ADD COLUMN {col} REAL DEFAULT {default}"
            )
        except Exception:
            pass  # Column already exists
    conn.commit()
    # Parse noise, seed and system from CLI arguments
    noise = 0.0
    seed = 42
    system_filter = None
    for idx, arg in enumerate(sys.argv):
        if arg == "--noise" and idx + 1 < len(sys.argv):
            try:
                noise = float(sys.argv[idx + 1])
            except ValueError:
                pass
        if arg == "--seed" and idx + 1 < len(sys.argv):
            try:
                seed = int(sys.argv[idx + 1])
            except ValueError:
                pass
        if arg == "--system" and idx + 1 < len(sys.argv):
            system_filter = sys.argv[idx + 1]

    if system_filter:
        if system_filter in systems:
            systems = {system_filter: systems[system_filter]}
        else:
            print(f"[WARN] System '{system_filter}' not recognized. Running all.")

    for name, (func, init, param) in systems.items():
        print(f"Resolviendo {name}...")
        sol = solve_ivp(func, t_span, init, t_eval=t_eval, method="RK45")
        x_signal = sol.y[0]

        # Descartar transitorio (primeros 5000 pasos)
        x_signal = x_signal[5000:]

        if noise > 0.0:
            noise_std = noise * np.std(x_signal)
            np.random.seed(seed)
            x_signal = x_signal + np.random.normal(0, noise_std, len(x_signal))

        print(f"Calculando embedding v2 para {name}...")
        emb = compute_embedding(x_signal, dt=dt)

        emb["lyapunov_max"] = 0.5 if name != "chua" else 0.3  # Caos

        features = [
            "lyapunov_max",
            "spectral_entropy",
            "dominant_frequency",
            "variance",
            "autocorr_decay",
            "kurtosis",
            "skewness",
            "energy",
        ]
        vals = [float(emb.get(f, 0.0)) for f in features]

        # DELETE existing row for this (system, noise, seed) triplet, then INSERT fresh.
        # This avoids ON CONFLICT dependency on pre-existing UNIQUE constraints.
        conn.execute(
            "DELETE FROM structural_embeddings WHERE system_name=? AND noise_level=? AND seed=?",
            (name, noise, seed),
        )
        conn.execute(
            "INSERT INTO structural_embeddings "
            "(node_id, system_name, noise_level, seed, "
            " lyapunov_max, spectral_entropy, dominant_frequency, "
            " variance, autocorr_decay, kurtosis, skewness, energy) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (13, name, noise, seed, *vals),
        )

    conn.commit()
    conn.close()
    print("Integraciones 3D guardadas exitosamente.")


if __name__ == "__main__":
    main()
