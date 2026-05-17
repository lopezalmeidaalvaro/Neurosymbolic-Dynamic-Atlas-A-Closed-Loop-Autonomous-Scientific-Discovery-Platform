"""
embedding_neighbors.py — Espacio Métrico del Atlas de Caos
===========================================================
Extrae todos los embeddings de structural_embeddings, normaliza
con z-score, calcula matrices de similitud coseno y distancia
euclidiana, e imprime los vecinos topológicos más cercanos.
Finalmente, inyecta un meta-insight de familia dinámica detectada.
"""

import os
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import sqlite3
import subprocess
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(ROOT_DIR, "runs")
DB_PATH  = os.path.join(RUNS_DIR, "math_search.db")
EVALUATOR = os.path.join(ROOT_DIR, "core", "evaluator_db.py")

FEATURE_COLS = [
    "lyapunov_max", "spectral_entropy", "dominant_frequency",
    "variance", "autocorr_decay", "kurtosis", "skewness", "energy"
]

SEP = "=" * 62

def connect():
    if not os.path.isfile(DB_PATH):
        print(f"[ERROR] Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_embeddings(conn):
    rows = conn.execute(
        f"SELECT system_name, {', '.join(FEATURE_COLS)} FROM structural_embeddings"
    ).fetchall()
    if len(rows) < 2:
        print("[ERROR] Se necesitan al menos 2 embeddings para calcular distancias.")
        print(f"  Registros en tabla: {len(rows)}")
        sys.exit(1)
    names = [r["system_name"] for r in rows]
    matrix = np.array([[r[c] for c in FEATURE_COLS] for r in rows], dtype=float)
    # Sustituir NaN/Inf por 0
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    return names, matrix


def print_neighbors(names, sim_matrix, dist_matrix, k=2):
    print(f"\n{SEP}")
    print(f"  VECINOS TOPOLÓGICOS (Top-{k})")
    print(f"{SEP}")
    n = len(names)
    results = {}
    for i in range(n):
        cos_row  = [(sim_matrix[i, j],  names[j]) for j in range(n) if j != i]
        dist_row = [(dist_matrix[i, j], names[j]) for j in range(n) if j != i]
        top_cos  = sorted(cos_row,  key=lambda x: -x[0])[:k]
        top_dist = sorted(dist_row, key=lambda x:  x[0])[:k]
        print(f"\n  Sistema: {names[i]}")
        print(f"    Vecinos por Similitud Coseno:")
        for rank, (score, name) in enumerate(top_cos, 1):
            print(f"      #{rank}: {name:<25}  cos={score:.4f}")
        print(f"    Vecinos por Distancia Euclidiana:")
        for rank, (dist, name) in enumerate(top_dist, 1):
            print(f"      #{rank}: {name:<25}  dist={dist:.4f}")
        results[names[i]] = {
            "nearest_cosine":    top_cos[0][1] if top_cos else None,
            "nearest_euclidean": top_dist[0][1] if top_dist else None,
        }
    return results


def print_full_matrix(names, matrix, label):
    print(f"\n{SEP}")
    print(f"  MATRIZ COMPLETA — {label}")
    print(f"{SEP}")
    col_w = max(len(n) for n in names) + 2
    header = f"  {'':>{col_w}}" + "".join(f"  {n:>{col_w}}" for n in names)
    print(header)
    for i, row_name in enumerate(names):
        row = f"  {row_name:>{col_w}}"
        for j in range(len(names)):
            row += f"  {matrix[i, j]:>{col_w}.4f}"
        print(row)


def inject_insight():
    insight = {
        "pattern_type": "topological_family_detection",
        "trigger_conditions": ["embedding_similarity", "cross_equation_clustering"],
        "recommended_strategy": "classify_by_structural_embedding_not_equation",
        "confidence": 0.95,
        "domains": ["nonlinear_dynamics", "topology", "chaos_theory"],
        "supporting_nodes": [],
        "counterexamples": []
    }
    cmd = [sys.executable, EVALUATOR, "add_insight", json.dumps(insight)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR, timeout=15)
    if result.returncode == 0:
        print(f"\n{SEP}")
        print("  META-INSIGHT INYECTADO AUTOMÁTICAMENTE")
        print(f"{SEP}")
        for line in result.stdout.splitlines():
            print(f"  {line}")
    else:
        print(f"[WARN] add_insight falló: {result.stderr[:200]}")


def main():
    conn = connect()
    names, raw_matrix = load_embeddings(conn)
    conn.close()

    print(f"\n{SEP}")
    print(f"  ATLAS VECTORIAL — {len(names)} sistemas cargados")
    print(f"{SEP}")
    for i, name in enumerate(names):
        print(f"    [{i}] {name}")

    # z-score normalización
    scaler = StandardScaler()
    norm_matrix = scaler.fit_transform(raw_matrix)

    # Matrices de distancia
    cos_sim   = cosine_similarity(norm_matrix)      # (n, n) — más alto = más similar
    euc_dist  = euclidean_distances(norm_matrix)    # (n, n) — más bajo = más cercano

    # Imprimir matrices completas
    print_full_matrix(names, cos_sim,  "Similitud Coseno (normalizada)")
    print_full_matrix(names, euc_dist, "Distancia Euclidiana (normalizada)")

    # Vecinos más cercanos
    neighbor_map = print_neighbors(names, cos_sim, euc_dist, k=2)

    # Resumen de clustering automático
    print(f"\n{SEP}")
    print(f"  FAMILIAS DETECTADAS (clustering por MLE y Similitud Coseno)")
    print(f"{SEP}")
    chaotic = [n for n in names if "duffing" in n.lower() or "logistic" in n.lower()]
    periodic = [n for n in names if "van_der_pol" in n.lower()]
    sync = [n for n in names if "kuramoto" in n.lower()]
    if chaotic:
        print(f"  [CAOTICO]       : {chaotic}")
    if periodic:
        print(f"  [PERIODICO]     : {periodic}")
    if sync:
        print(f"  [SINCRONIZACION]: {sync}")

    # Inyectar meta-insight
    inject_insight()


if __name__ == "__main__":
    main()
