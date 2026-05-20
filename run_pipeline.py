import os
import subprocess
import sys
import argparse
import time
import sqlite3
import json
import io
from datetime import datetime

# Force stdout to UTF-8 in Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from core.io import export_session, ARTIFACTS_DIR, resolve_path


def print_step(step_name):
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")
    print(f"{'='*60}")

def run_cmd(command):
    print(f"Ejecutando: {' '.join(command)}")
    t0 = time.time()
    env = os.environ.copy()
    env["EVAL_CALLED"] = "1"
    result = subprocess.run(command, env=env)
    duration = time.time() - t0
    status = "SUCCESS" if result.returncode == 0 else "ERROR"
    if result.returncode != 0:
        print(f"\n❌ ERROR: El comando ha fallado. Deteniendo pipeline.")
        sys.exit(1)
    print("✅ Paso completado con éxito.\n")
    return duration, status

def main():
    parser = argparse.ArgumentParser(description="Neurosymbolic Pipeline Runner (Dynamic Atlas)")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment identifier")
    parser.add_argument("--noise", type=float, default=0.0, help="Noise level injection (default: 0.0)")
    parser.add_argument("--seed", type=int, default=42, help="Seed value (default: 42)")
    parser.add_argument("--system", type=str, default=None, help="Dynamical system to run (default: None for all)")
    
    args = parser.parse_args()

    print_step(f"INICIANDO NEUROSYMBOLIC PIPELINE: {args.experiment} (Noise: {args.noise}, Seed: {args.seed}, System: {args.system})")
    
    # Ensure artifacts directories exist
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    
    telemetry_list = []

    # PASO 1: Generación de series temporales y extracción de features (Embeddings)
    print_step("PASO 1: Integración de Atractores (Lorenz, Rössler) y Extracción")
    cmd = ["python", "experiments_archive/continuous_attractors.py", "--noise", str(args.noise), "--seed", str(args.seed)]
    if args.system:
        cmd += ["--system", args.system]
    duration, status = run_cmd(cmd)
    telemetry_list.append({
        "framework_family": "NUMERICAL",
        "framework": "scipy",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Integración de atractores continuos en 3D"
    })
    
    # PASO 2: Proyección Latente y Cálculo de Curvatura
    print_step("PASO 2: Geometría Diferencial y Clustering")
    duration, status = run_cmd(["python", "experiments_archive/continuous_geometry.py"])
    telemetry_list.append({
        "framework_family": "NUMERICAL",
        "framework": "scikit-learn",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "PCA, cálculo de curvatura geodésica local y clustering DBSCAN"
    })
    
    # PASO 3: Generación de Gráficos PCA y Geodésicas
    print_step("PASO 3: Generación de Artefactos Visuales")
    duration, status = run_cmd(["python", "experiments_archive/universal_atlas_visualization.py"])
    telemetry_list.append({
        "framework_family": "VISUALIZATION",
        "framework": "matplotlib",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Generación de gráficos del atlas universal"
    })
    
    # PASO 4: Benchmark formal vs Estado del Arte (ROCKET / DTW)
    print_step("PASO 4: Benchmark vs Estado del Arte (ROCKET/DTW)")
    duration, status = run_cmd(["python", "experiments_archive/baseline_benchmark.py", "--noise", str(args.noise), "--seed", str(args.seed), "--fast"])
    telemetry_list.append({
        "framework_family": "BENCHMARK",
        "framework": "sktime",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Evaluación comparativa contra modelos de referencia"
    })
    
    # PASO 5: Congelar el conocimiento en el JSON maestro
    print_step("PASO 5: Exportando Memoria Semántica (ATLAS_INSIGHTS)")
    duration, status = run_cmd(["python", "export_knowledge.py"])
    telemetry_list.append({
        "framework_family": "KNOWLEDGE_EXPORT",
        "framework": "sqlite3",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Exportación de meta_insights guardados en base de datos"
    })
    
    # PASO 6: Recopilar datos y exportar la sesión validada por contrato
    print_step("PASO 6: Validando y Exportando Sesión Científica")
    
    # Recuperar embeddings desde SQLite
    embeddings_dict = {}
    db_path = os.path.join("runs", "math_search.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, "
                "variance, autocorr_decay, kurtosis, skewness, energy "
                "FROM structural_embeddings "
                "WHERE noise_level=? AND seed=?",
                (args.noise, args.seed)
            )
            rows = cursor.fetchall()
            if not rows:
                # Fallback: read any row for this system (old schema without noise/seed cols)
                cursor.execute(
                    "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, "
                    "variance, autocorr_decay, kurtosis, skewness, energy FROM structural_embeddings"
                )
                rows = cursor.fetchall()
            for r in rows:
                name = r[0]
                embeddings_dict[name] = {
                    "lyapunov_max": float(r[1] if r[1] is not None else 0.0),
                    "spectral_entropy": float(r[2] if r[2] is not None else 0.0),
                    "dominant_frequency": float(r[3] if r[3] is not None else 0.0),
                    "variance": float(r[4] if r[4] is not None else 0.0),
                    "autocorr_decay": float(r[5] if r[5] is not None else 0.0),
                    "kurtosis": float(r[6] if r[6] is not None else 0.0),
                    "skewness": float(r[7] if r[7] is not None else 0.0),
                    "energy": float(r[8] if r[8] is not None else 0.0)
                }
            conn.close()
        except Exception as e:
            print(f"[WARN] Error recuperando embeddings de SQLite: {e}")


    # Recuperar resultados del benchmark
    comparisons_dict = {}
    benchmark_path = resolve_path("benchmark_results.json")
    if benchmark_path.exists():
        try:
            with open(benchmark_path, "r", encoding="utf-8") as f:
                results = json.load(f)
            for model_name, metrics in results.items():
                comparisons_dict[model_name] = {
                    "accuracy": float(metrics.get("accuracy", 0.0)),
                    "time_seconds": float(metrics.get("time_seconds", 0.0))
                }
        except Exception as e:
            print(f"[WARN] Error leyendo benchmark_results.json: {e}")

    # Estructurar sesión para validación contra ExperimentSession
    from datetime import timezone
    session_data = {
        "metadata": {
            "id": args.experiment,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "modelo": "Gemini 3.5 Flash",
            "versión": "1.0.0",
            "noiseLevel": args.noise,
            "seed": args.seed
        },
        "telemetry": telemetry_list,
        "embeddings": embeddings_dict,
        "benchmarks": {
            "comparisons": comparisons_dict
        }
    }

    try:
        exported_file = export_session(session_data, args.experiment)
        print_step(f"PIPELINE COMPLETADO EXITOSAMENTE. Sesión guardada en:\n{exported_file}")
    except Exception as e:
        print(f"\n❌ ERROR DE VALIDACIÓN DE CONTRATO DE DATOS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
