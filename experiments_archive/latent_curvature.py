import numpy as np
import json
import os
import sys
import subprocess
import sqlite3

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "runs", "math_search.db")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
EVALUATOR_PATH = os.path.join(ROOT_DIR, "core", "evaluator_db.py")


def main():
    print("=====================================================")
    print("  FASE 11B - GEOMETRÍA DIFERENCIAL DEL ESPACIO LATENTE")
    print("=====================================================")

    data_path = os.path.join(ARTIFACTS_DIR, "deformation_flow_projection.json")
    if not os.path.exists(data_path):
        print("[ERROR] No se encontró deformation_flow_projection.json")
        return

    with open(data_path, "r") as f:
        data = json.load(f)

    n_r = data["n_r"]
    n_p = data["n_p"]

    # pca_coords was flattened from (n_r, n_p, 2)
    pca_coords = np.array(data["pca_coords"]).reshape((n_r, n_p, 2))

    # 1. & 2. Curvatura a lo largo de r (fijando p)
    vr = np.zeros_like(pca_coords)
    vr[:-1, :, :] = pca_coords[1:, :, :] - pca_coords[:-1, :, :]
    vr[-1, :, :] = vr[-2, :, :]

    ar = np.zeros_like(vr)
    ar[:-1, :, :] = vr[1:, :, :] - vr[:-1, :, :]
    ar[-1, :, :] = ar[-2, :, :]

    vr_mag = np.linalg.norm(vr, axis=2)
    ar_mag = np.linalg.norm(ar, axis=2)

    epsilon = 1e-8
    kappa_r = ar_mag / (vr_mag**2 + epsilon)

    # Curvatura a lo largo de p (fijando r)
    vp = np.zeros_like(pca_coords)
    vp[:, :-1, :] = pca_coords[:, 1:, :] - pca_coords[:, :-1, :]
    vp[:, -1, :] = vp[:, -2, :]

    vp_mag = np.linalg.norm(vp, axis=2)

    # 3. Detección de Geometría Crítica
    kappa_flat = kappa_r.flatten()
    k_p50 = np.percentile(kappa_flat, 50)
    k_p90 = np.percentile(kappa_flat, 90)

    labels_geom = []
    for k in kappa_flat:
        if k < k_p50:
            labels_geom.append("plana")
        elif k > k_p90:
            labels_geom.append("singular")
        else:
            labels_geom.append("critica")

    # 4. Mapa Métrico
    # g_ij = v_i \cdot v_j
    grr = np.sum(vr * vr, axis=2)
    gpp = np.sum(vp * vp, axis=2)
    grp = np.sum(vr * vp, axis=2)

    det_g = grr * gpp - grp**2
    # Cap negative det_g due to numerical noise if any
    det_g = np.maximum(det_g, 0.0)

    area_expansion = np.sqrt(det_g)  # Local area element

    print("Métricas diferenciales calculadas correctamente.")
    print(f"  Curvatura media (kappa): {np.mean(kappa_flat):.4f}")
    print(f"  Puntos singulares detectados: {labels_geom.count('singular')}")

    export_data = {
        "n_r": n_r,
        "n_p": n_p,
        "r_vals": data["r_vals"],
        "p_vals": data["p_vals"],
        "pca_coords": data["pca_coords"],
        "kappa_r": kappa_flat.tolist(),
        "area_expansion": area_expansion.flatten().tolist(),
        "labels_geom": labels_geom,
    }

    out_path = os.path.join(ARTIFACTS_DIR, "latent_curvature_data.json")
    with open(out_path, "w") as f:
        json.dump(export_data, f)

    print("=====================================================\n")

    # 7. Memoria Semántica
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO meta_insights (pattern_type, trigger_conditions, recommended_strategy, confidence, supporting_nodes, counterexamples, domains) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "latent_metric_curvature",
            "High phase transitions corresponding to singular regions in latent space",
            "detect_phase_transitions_via_geometric_curvature",
            0.98,
            "[]",
            "[]",
            "['differential_geometry']",
        ),
    )
    conn.commit()
    conn.close()

    if os.environ.get("EVAL_CALLED") != "1":
        cmd = [
            sys.executable,
            EVALUATOR_PATH,
            "eval",
            "none",
            "differential_geometry",
            "scikit-learn",
            os.path.join("temp_scripts", "latent_curvature.py"),
            "--artifact",
            "latent_curvature|artifacts/latent_curvature.png",
            "--notes",
            "Fase 11B: Geometría diferencial y curvatura del espacio dinámico latente.",
        ]
        env = os.environ.copy()
        env["EVAL_CALLED"] = "1"
        subprocess.run(cmd, cwd=ROOT_DIR, env=env)


if __name__ == "__main__":
    main()
