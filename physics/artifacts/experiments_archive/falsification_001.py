import numpy as np
from scipy.stats import pearsonr
import sqlite3
import json
import os
import sys
import subprocess

# Removed stdout wrapper

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

# Ensure topology_miner_v2 is importable
sys.path.append(os.path.dirname(__file__))
try:
    from topology_miner_v2 import compute_embedding
except ImportError:
    print("[ERROR] No se pudo importar compute_embedding de topology_miner_v2")
    sys.exit(1)


def main():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    print("=====================================================")
    print("  EXPERIMENTO DE FALSACIÓN 001 - RUIDO ESTOCÁSTICO")
    print("=====================================================")

    r_vals = np.linspace(2.8, 4.0, 150)
    variances = []
    energies = []

    print(f"Ejecutando barrido paramétrico con ruido estocástico (N={len(r_vals)})...")
    np.random.seed(42)  # For reproducibility

    # 1. Simulación con ruido estocástico
    for r in r_vals:
        N_warmup = 500
        N_steps = 1500
        N_total = N_warmup + N_steps

        # Generar ruido Gaussiano
        xi = np.random.normal(0, 0.1, N_total)

        x = 0.4  # initial condition
        series = np.zeros(N_steps)

        for i in range(N_total):
            x = r * x * (1 - x) + xi[i]
            x = np.clip(x, -2.0, 2.0)
            if i >= N_warmup:
                series[i - N_warmup] = x

        # Compute embedding v2
        emb = compute_embedding(series, dt=1.0)

        variances.append(emb["variance"])
        energies.append(emb["energy"])

    variances = np.array(variances)
    energies = np.array(energies)

    # Manejar posibles NaNs
    variances = np.nan_to_num(variances)
    energies = np.nan_to_num(energies)

    # 2. Cálculo de Refutación
    r_pearson, p_value = pearsonr(variances, energies)
    print("\n  Correlación original (sin ruido): r ≈ 0.916")
    print(
        f"  Nueva correlación (con ruido) : r = {r_pearson:.4f} (p-value={p_value:.4e})"
    )

    if r_pearson >= 0.80:
        verdict = "survived"
        print(
            "  [VEREDICTO] La conjetura SOBREVIVE. Es un invariante topológico robusto."
        )
        new_status = "validated_under_noise"
        new_confidence = 0.99
    else:
        verdict = "falsified"
        print(
            "  [VEREDICTO] La conjetura es FALSADA. Era un artefacto estadístico frágil."
        )
        new_status = "falsified"
        new_confidence = 0.10

    print("=====================================================\n")

    # 3. Actualización Epistemológica (SQLite)
    conn = sqlite3.connect(DB_PATH)

    # Update all matching conjectures
    query = """
        UPDATE generated_conjectures 
        SET status = ?, confidence_score = ? 
        WHERE hypothesis_text LIKE '%variance%' AND hypothesis_text LIKE '%energy%'
    """
    conn.execute(query, (new_status, new_confidence))
    conn.commit()
    conn.close()

    # 4. Persistencia y Evaluación
    results = {
        "original_r": 0.9164745317797641,
        "noisy_r": r_pearson,
        "p_value": p_value,
        "verdict": verdict,
    }

    results_path = os.path.join(ARTIFACTS_DIR, "falsification_001_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    # Invocar a evaluator_db.py (con protección para evitar bucle infinito)
    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable,
            EVALUATOR_PATH,
            "eval",
            "none",
            "epistemological_engine",
            "scipy",
            os.path.join("temp_scripts", "falsification_001.py"),
            "--artifact",
            "falsification_report|artifacts/falsification_001_results.json",
            "--notes",
            "Fase 10: Ejecución de falsación estocástica. Inyección de ruido Gaussiano (sigma=0.1) en Mapa Logístico para testear robustez de la correlación Varianza-Energía.",
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)


if __name__ == "__main__":
    main()
