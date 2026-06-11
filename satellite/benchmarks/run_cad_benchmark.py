#!/usr/bin/env python3
"""
AST-OS Standalone CAD Vectorization Benchmark
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import time
import numpy as np
import pandas as pd

BENCH_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(BENCH_DIR), "satellite", "thermal"))

from cad_thermal_importer import CADThermalMesh


def run_benchmark():
    print("[*] Benchmarking Vectorized CAD Solver...")
    results = []

    # Node sizes to benchmark
    for N in [100, 1000]:
        np.random.seed(42)
        y = np.random.uniform(250.0, 350.0, N)
        C = np.random.uniform(1.0, 10.0, N)
        Q = np.random.uniform(0.0, 15.0, N)
        eps = np.random.uniform(0.0, 0.9, N)
        A_rad = np.random.uniform(0.0, 0.01, N)
        SIGMA = 5.67e-8
        T_space = 2.7

        k_matrix = np.zeros((N, N))
        for i in range(N):
            neighbors = np.random.choice(N, min(6, N), replace=False)
            for nb in neighbors:
                if nb != i:
                    k_matrix[i, nb] = 1.67
                    k_matrix[nb, i] = 1.67

        # Loop version
        t0 = time.perf_counter()
        dy_loop = np.zeros(N)
        for i in range(N):
            Q_cond = 0.0
            for j in range(N):
                if k_matrix[i, j] > 0.0:
                    Q_cond += k_matrix[i, j] * (y[j] - y[i])
            Q_rad = eps[i] * SIGMA * A_rad[i] * (y[i] ** 4 - T_space**4)
            dy_loop[i] = (Q[i] + Q_cond - Q_rad) / C[i]
        t_loop = time.perf_counter() - t0

        # Vectorized version
        t0 = time.perf_counter()
        k_matrix_row_sums = np.sum(k_matrix, axis=1)
        Q_cond_vec = k_matrix.dot(y) - y * k_matrix_row_sums
        Q_rad_vec = eps * SIGMA * A_rad * (y**4 - T_space**4)
        dy_vec = (Q + Q_cond_vec - Q_rad_vec) / C
        t_vec = time.perf_counter() - t0

        speedup = t_loop / t_vec
        results.append(
            {
                "Nodes": N,
                "Loop_Time_s": t_loop,
                "Vectorized_Time_s": t_vec,
                "Speedup": speedup,
            }
        )

    df = pd.DataFrame(results)
    csv_path = os.path.join(BENCH_DIR, "cad_benchmark_output.csv")
    df.to_csv(csv_path, index=False)
    print(f"[+] CAD Benchmark finished successfully. Saved to: {csv_path}")


if __name__ == "__main__":
    run_benchmark()
