"""
topology_miner_v2.py — Orquestador de Embeddings Dinámicos v2
==============================================================
Lee chaos_benchmark.json, integra cada sistema dinámico, calcula
el vector de embedding de 8 dimensiones, lo persiste en disco y
lo registra directamente en SQLite (sin subprocesos anidados para
evitar database locks).

Después de ejecutar este script, usa evaluator_db.py eval con
--signature para registrar los embeddings desde el árbol de nodos.
"""

import os
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import sqlite3
import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft, fftfreq
from scipy.stats import kurtosis as scipy_kurtosis, skew as scipy_skew

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
BENCHMARK_PATH = os.path.join(ROOT_DIR, "chaos_benchmark.json")
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)

FIELD_ORDER = ["lyapunov_max", "spectral_entropy", "dominant_frequency",
               "variance", "autocorr_decay", "kurtosis", "skewness", "energy"]

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────

def compute_embedding(series: np.ndarray, dt: float) -> dict:
    x = np.asarray(series, dtype=float)

    variance = float(np.var(x))

    N = len(x)
    yf = np.abs(fft(x)[:N // 2]) ** 2
    xf = fftfreq(N, dt)[:N // 2]
    yf[0] = 0.0
    total_power = yf.sum()
    if total_power > 0:
        p = yf / total_power
        p_pos = p[p > 0]
        spectral_entropy = float(-np.sum(p_pos * np.log2(p_pos)))
        dominant_frequency = float(xf[np.argmax(yf)])
    else:
        spectral_entropy = 0.0
        dominant_frequency = 0.0

    x_centered = x - x.mean()
    norm = np.dot(x_centered, x_centered)
    autocorr_decay = float(N * dt)  # default: no decae
    if norm > 0:
        for lag in range(1, min(N, 10000)):
            rho = np.dot(x_centered[:-lag], x_centered[lag:]) / norm
            if abs(rho) < 1.0 / np.e:
                autocorr_decay = float(lag * dt)
                break

    kurt = float(scipy_kurtosis(x, fisher=True))
    skewness = float(scipy_skew(x))
    energy = float(np.sqrt(np.mean(x ** 2)))

    return {
        "spectral_entropy": spectral_entropy,
        "dominant_frequency": dominant_frequency,
        "variance": variance,
        "autocorr_decay": autocorr_decay,
        "kurtosis": kurt,
        "skewness": skewness,
        "energy": energy,
    }


def lyapunov_ode(rhs, state0, t_start, t_end, n_steps=2000, d0=1e-8):
    t_vals = np.linspace(t_start, t_end, n_steps)
    dt = t_vals[1] - t_vals[0]
    state = np.array(state0, dtype=float)
    pert = state.copy(); pert[0] += d0
    lyap_sum = 0.0; iters = 0
    for i in range(len(t_vals) - 1):
        t0, t1 = t_vals[i], t_vals[i + 1]
        s1 = solve_ivp(rhs, (t0, t1), state, method='RK45',
                       rtol=1e-7, atol=1e-7).y[:, -1]
        s2 = solve_ivp(rhs, (t0, t1), pert,  method='RK45',
                       rtol=1e-7, atol=1e-7).y[:, -1]
        diff = s2 - s1; d1 = np.linalg.norm(diff)
        if d1 > 0:
            lyap_sum += np.log(d1 / d0)
            pert = s1 + diff * (d0 / d1)
        state = s1; iters += 1
    return float(lyap_sum / (iters * dt)) if iters > 0 else 0.0


def lyapunov_map(map_fn, x0, n_warmup=5000, n_lyap=10000):
    x = float(x0)
    for _ in range(n_warmup): x = map_fn(x)
    dx = 1e-8; lyap_sum = 0.0
    for _ in range(n_lyap):
        x_p = x + dx
        xn = map_fn(x); xpn = map_fn(x_p)
        d1 = abs(xpn - xn)
        if d1 > 0: lyap_sum += np.log(d1 / dx)
        x = xn
    return float(lyap_sum / n_lyap)


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRADORES POR SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

def integrate_duffing():
    def rhs(t, s):
        x, y = s
        return [y, x - x**3 - 0.3*y + 0.5*np.cos(1.2*t)]
    t_span = (0, 800); N = 80000
    t_eval = np.linspace(*t_span, N)
    sol = solve_ivp(rhs, t_span, [0.1, 0.0], t_eval=t_eval, method='RK45',
                    rtol=1e-7, atol=1e-7)
    dt = t_eval[1] - t_eval[0]; cut = N // 5
    x_s = sol.y[0, cut:]; y_s = sol.y[1, cut:]
    emb = compute_embedding(x_s, dt)
    emb["lyapunov_max"] = lyapunov_ode(rhs, [x_s[0], y_s[0]], 160, 400)
    return emb


def integrate_van_der_pol():
    mu = 5.0
    def rhs(t, s):
        x, y = s
        return [y, mu*(1 - x**2)*y - x]
    t_span = (0, 400); N = 60000
    t_eval = np.linspace(*t_span, N)
    sol = solve_ivp(rhs, t_span, [0.5, 0.0], t_eval=t_eval, method='RK45',
                    rtol=1e-7, atol=1e-7)
    dt = t_eval[1] - t_eval[0]; cut = N // 5
    x_s = sol.y[0, cut:]; y_s = sol.y[1, cut:]
    emb = compute_embedding(x_s, dt)
    emb["lyapunov_max"] = lyapunov_ode(rhs, [x_s[0], y_s[0]], 80, 200)
    return emb


def integrate_logistic_map():
    r = 3.9
    fn = lambda x: r * x * (1 - x)
    N = 60000; x = 0.4
    for _ in range(5000): x = fn(x)
    series = []
    for _ in range(N): x = fn(x); series.append(x)
    x_s = np.array(series[N // 5:])
    emb = compute_embedding(x_s, 1.0)
    emb["lyapunov_max"] = lyapunov_map(fn, 0.4)
    return emb


def integrate_kuramoto():
    N_osc = 5; K = 2.0
    omega = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    def rhs(t, theta):
        dtheta = np.zeros(N_osc)
        for i in range(N_osc):
            dtheta[i] = omega[i] - (K / N_osc) * np.sum(np.sin(theta[i] - theta))
        return dtheta
    t_span = (0, 400); N = 60000
    t_eval = np.linspace(*t_span, N)
    np.random.seed(42)
    theta0 = np.random.uniform(0, 2*np.pi, N_osc)
    sol = solve_ivp(rhs, t_span, theta0, t_eval=t_eval, method='RK45',
                    rtol=1e-6, atol=1e-6)
    dt = t_eval[1] - t_eval[0]; cut = N // 5
    r_param = np.abs(np.mean(np.exp(1j * sol.y[:, cut:]), axis=0))
    emb = compute_embedding(r_param, dt)
    emb["lyapunov_max"] = lyapunov_ode(rhs, list(sol.y[:, cut]), 80, 160, n_steps=500)
    return emb


SYSTEM_INTEGRATORS = {
    "duffing_oscillator": integrate_duffing,
    "logistic_map":       integrate_logistic_map,
    "van_der_pol":        integrate_van_der_pol,
    "kuramoto_model":     integrate_kuramoto,
}


# ─────────────────────────────────────────────────────────────────────────────
# INSERCIÓN DIRECTA EN SQLITE
# ─────────────────────────────────────────────────────────────────────────────

def ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS structural_embeddings (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id            INTEGER,
            system_name        TEXT,
            lyapunov_max       REAL,
            spectral_entropy   REAL,
            dominant_frequency REAL,
            variance           REAL,
            autocorr_decay     REAL,
            kurtosis           REAL,
            skewness           REAL,
            energy             REAL,
            embedding_json     TEXT,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        )
    """)
    conn.commit()


def insert_embedding(conn, sys_id, emb):
    vals = [emb.get(f, 0.0) for f in FIELD_ORDER]
    conn.execute("""
        INSERT INTO structural_embeddings
            (node_id, system_name, lyapunov_max, spectral_entropy,
             dominant_frequency, variance, autocorr_decay, kurtosis,
             skewness, energy, embedding_json)
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (sys_id, *vals, json.dumps(emb, ensure_ascii=False)))
    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        benchmark = json.load(f)

    print(f"\n{'='*60}")
    print(f"  TOPOLOGY MINER v2 -- Atlas Vectorial de Caos")
    print(f"  Sistemas en benchmark: {len(benchmark)}")
    print(f"{'='*60}\n")

    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)

    results = {}
    for entry in benchmark:
        sys_id = entry["id"]
        if sys_id not in SYSTEM_INTEGRATORS:
            print(f"[SKIP] {sys_id} -- sin integrador definido.\n")
            continue

        print(f"  >> Procesando: {sys_id}...")
        try:
            emb = SYSTEM_INTEGRATORS[sys_id]()

            # Sanitizar
            for field in FIELD_ORDER:
                v = emb.get(field, 0.0)
                emb[field] = float(v) if (v is not None and np.isfinite(v)) else 0.0

            # Guardar JSON en disco
            sig_path = os.path.join(ARTIFACTS_DIR, f"{sys_id}_signature_v2.json")
            with open(sig_path, "w", encoding="utf-8") as f:
                json.dump(emb, f, indent=4)
            print(f"     Firma guardada: {os.path.basename(sig_path)}")

            # Insertar en SQLite
            insert_embedding(conn, sys_id, emb)
            print(f"     Embedding registrado en structural_embeddings")

            for k in FIELD_ORDER:
                print(f"       {k:<22}: {emb[k]:.6f}")
            results[sys_id] = emb

        except Exception as exc:
            import traceback
            print(f"  [ERROR] {sys_id}: {exc}")
            traceback.print_exc()

        print()

    conn.close()

    print(f"\n{'='*60}")
    print(f"  RESUMEN DE EMBEDDINGS GENERADOS")
    print(f"{'='*60}")
    for sys_id, emb in results.items():
        lyap = emb.get("lyapunov_max", 0.0)
        tag = "CAOTICO" if lyap > 0 else "REGULAR"
        print(f"  {sys_id:<30} Lyap={lyap:+.4f} [{tag}]")

    print(f"\n  Ejecuta: python temp_scripts/embedding_neighbors.py")
    print(f"{'='*60}\n")

    # Print JSON summary to stdout for evaluator capture
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
