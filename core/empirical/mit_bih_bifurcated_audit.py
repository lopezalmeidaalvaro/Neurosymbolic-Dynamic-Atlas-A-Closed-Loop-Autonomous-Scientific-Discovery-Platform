import os
import sys
import json
import time
import urllib.request
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import shap

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import compute_embedding_vector

# Paths
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "mit_bih_bifurcated_report.json")
DATA_DIR = os.path.join(ROOT_DIR, "data", "mitdb")

# AAMI strict partitions
TRAIN_RECORDS = [
    101,
    106,
    108,
    109,
    112,
    114,
    115,
    116,
    118,
    119,
    122,
    124,
    201,
    203,
    205,
    207,
    208,
    209,
    215,
    220,
    223,
    230,
]
TEST_RECORDS = [
    100,
    103,
    105,
    111,
    113,
    117,
    121,
    123,
    200,
    202,
    210,
    212,
    213,
    214,
    219,
    221,
    222,
    228,
    231,
    232,
    233,
    234,
]
ALL_RECORDS = TRAIN_RECORDS + TEST_RECORDS

# Feature definitions
V3_KEYS = [
    "perm_entropy",
    "spectral_entropy",
    "svd_entropy",
    "fractal_dim",
    "autocorr_decay",
    "robust_skewness",
    "robust_kurtosis",
    "temporal_irreversibility",
]

THEORETICAL_RANKING = [
    "perm_entropy",
    "svd_entropy",
    "robust_kurtosis",
    "temporal_irreversibility",
    "spectral_entropy",
    "robust_skewness",
    "fractal_dim",
    "autocorr_decay",
]

# Max beats of each class (Normal, PVC) per patient to ensure speed + class balance
MAX_BEATS_PER_CLASS_PER_PATIENT = 120

# ─────────────────────────────────────────────────────────────────────────────
# 1. LIVE EMPIRICAL INGESTION (PHYSIOCACHE) & DOWNLOADER
# ─────────────────────────────────────────────────────────────────────────────


def download_mitdb_files():
    """
    Downloads only the required files (.hea, .dat, .atr) for the 44 AAMI records
    directly from PhysioNet. Caches them locally in data/mitdb/ to prevent leakages
    and unnecessary downloads.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    base_url = "https://physionet.org/files/mitdb/1.0.0/"
    exts = [".hea", ".dat", ".atr"]

    print(f"\n[TEST 1] Initializing Live Ingestion Cache at {DATA_DIR}...")

    # Check if wfdb is installed
    try:
        import wfdb
    except ImportError:
        print("  Installing 'wfdb' dependency dynamically...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "wfdb"])
        import wfdb

    download_count = 0
    for r in ALL_RECORDS:
        rec_str = str(r)
        for ext in exts:
            filename = f"{rec_str}{ext}"
            local_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
                url = f"{base_url}{filename}"
                print(f"  Downloading {filename} ...")
                try:
                    urllib.request.urlretrieve(url, local_path)
                    download_count += 1
                except Exception as e:
                    print(
                        f"  ⚠️ Error downloading {filename} via urllib: {e}. Trying wfdb fallback."
                    )
                    # Fallback to wfdb dl_files
                    try:
                        wfdb.dl_files("mitdb", DATA_DIR, [filename])
                        download_count += 1
                    except Exception as e2:
                        raise RuntimeError(
                            f"Failed to ingest record file {filename}: {e2}"
                        )

    if download_count > 0:
        print(f"  ✅ Finished downloading {download_count} files from PhysioNet.")
    else:
        print("  ✅ All required MIT-BIH records found in local PhysioCache.")


# ─────────────────────────────────────────────────────────────────────────────
# 2. BUTTERWORTH FILTER & PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return filtfilt(b, a, data)


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENTROPY, NMI & METRIC ESTIMATORS
# ─────────────────────────────────────────────────────────────────────────────


def compute_discrete_entropy(x, bins=20):
    hist, _ = np.histogram(x, bins=bins, density=False)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log(p))


def compute_discrete_mutual_information(x, y, bins=20):
    hist_2d, _, _ = np.histogram2d(x, y, bins=bins)
    p_xy = hist_2d / np.sum(hist_2d)
    p_x = p_xy.sum(axis=1)
    p_y = p_xy.sum(axis=0)

    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
    return mi


def compute_nmi(x, y, bins=20):
    mi = compute_discrete_mutual_information(x, y, bins=bins)
    h_x = compute_discrete_entropy(x, bins=bins)
    h_y = compute_discrete_entropy(y, bins=bins)
    denom = np.sqrt(h_x * h_y)
    if denom <= 1e-12:
        return 0.0
    return float(mi / denom)


def compute_linear_cka(A: np.ndarray, B: np.ndarray) -> float:
    """
    Linear Centered Kernel Alignment (CKA) between two latent representations.
    A and B have shape (N, D).
    """
    A_centered = A - np.mean(A, axis=0)
    B_centered = B - np.mean(B, axis=0)
    dot_product = np.linalg.norm(B_centered.T @ A_centered, ord="fro") ** 2
    norm_A = np.linalg.norm(A_centered.T @ A_centered, ord="fro")
    norm_B = np.linalg.norm(B_centered.T @ B_centered, ord="fro")
    if norm_A * norm_B == 0:
        return 0.0
    return float(dot_product / (norm_A * norm_B))


# ─────────────────────────────────────────────────────────────────────────────
# 4. DATA LOADER & BIFURCATED PIPELINE
# ─────────────────────────────────────────────────────────────────────────────


def load_and_preprocess_windows(records):
    """
    Loads records, extracts 1000-sample windows centered around annotations.
    Separates into two channels:
      Canal A: Raw signal (NaN deletion + local Z-score).
      Canal B: Minimal physiological (0.5 - 45 Hz Butterworth filter + local Z-score).
    """
    import wfdb

    X_raw_list = []
    X_filt_list = []
    y_list = []

    window_half = 500

    for r in records:
        rec_path = os.path.join(DATA_DIR, str(r))

        # Read signal (lead 0, Modified Lead II is usually channel 0)
        record = wfdb.rdrecord(rec_path)
        signal_raw = record.p_signal[:, 0]
        fs = record.fs
        dt = 1.0 / fs

        # Canal B continuous filtering (before window slicing to prevent edge transients)
        signal_filtered = butter_bandpass_filter(signal_raw, 0.5, 45, fs=fs, order=4)

        # Read annotations
        annotation = wfdb.rdann(rec_path, "atr")
        sample_indices = annotation.sample
        symbols = annotation.symbol

        # Count beats per class for this record to maintain balance
        n_count = 0
        v_count = 0

        for idx, sym in zip(sample_indices, symbols):
            if sym not in ("N", "V"):
                continue

            # Class-balancing cap
            if sym == "N":
                if n_count >= MAX_BEATS_PER_CLASS_PER_PATIENT:
                    continue
                label = 1
            else:  # sym == 'V'
                if v_count >= MAX_BEATS_PER_CLASS_PER_PATIENT:
                    continue
                label = 0

            # Check boundaries
            if idx - window_half < 0 or idx + window_half > len(signal_raw):
                continue

            # Extract Canal A (Raw)
            win_raw = signal_raw[idx - window_half : idx + window_half]
            # Eliminate NaNs
            win_raw = win_raw[~np.isnan(win_raw)]
            if len(win_raw) < 1000:
                continue

            # Extract Canal B (Filtered)
            win_filt = signal_filtered[idx - window_half : idx + window_half]
            # Eliminate NaNs
            win_filt = win_filt[~np.isnan(win_filt)]
            if len(win_filt) < 1000:
                continue

            # Z-score local standardization
            win_raw_std = (win_raw - np.mean(win_raw)) / (np.std(win_raw) + 1e-12)
            win_filt_std = (win_filt - np.mean(win_filt)) / (np.std(win_filt) + 1e-12)

            # Feature extraction V3
            emb_raw = compute_embedding_vector(win_raw_std, dt)
            emb_filt = compute_embedding_vector(win_filt_std, dt)

            vec_raw = [emb_raw.get(k, 0.0) for k in V3_KEYS]
            vec_filt = [emb_filt.get(k, 0.0) for k in V3_KEYS]

            X_raw_list.append(vec_raw)
            X_filt_list.append(vec_filt)
            y_list.append(label)

            if sym == "N":
                n_count += 1
            else:
                v_count += 1

    return np.array(X_raw_list), np.array(X_filt_list), np.array(y_list), 1.0 / 360.0


# ─────────────────────────────────────────────────────────────────────────────
# 5. DUAL CAUSAL AUDIT
# ─────────────────────────────────────────────────────────────────────────────


def run_causal_audit(X_train, X_test, y_train, y_test, channel_name):
    """
    Executes the frozen V3 -> RandomForest -> NMI -> TreeSHAP -> Bootstrap
    causal workflow independently for the given channel.
    """
    print(f"\n⚡ Conducting Causal Audit for {channel_name}...")

    # 1. Train primary Random Forest
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_prob = clf.predict_proba(X_test)[:, 1]
    auc_score = float(roc_auc_score(y_test, y_prob))
    print(f"  [{channel_name}] test split ROC-AUC: {auc_score:.6f}")

    # 2. TreeSHAP Attribution
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_test)

    if isinstance(shap_values, list):
        shap_vals_c1 = shap_values[1]
    elif len(shap_values.shape) == 3:
        shap_vals_c1 = shap_values[:, :, 1]
    else:
        shap_vals_c1 = shap_values

    global_shap_importances = np.mean(np.abs(shap_vals_c1), axis=0)
    max_shap = np.max(global_shap_importances)
    normalized_shap_importances = global_shap_importances / (
        max_shap if max_shap > 0 else 1.0
    )

    # 3. Non-linear redundancy NMI
    R_nmi_matrix = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            R_nmi_matrix[i, j] = compute_nmi(X_train[:, i], X_train[:, j])

    redundancy_nmi_scores = {}
    for i, name in enumerate(V3_KEYS):
        redundancy_nmi_scores[name] = float((np.sum(R_nmi_matrix[i]) - 1.0) / 7.0)

    # 4. Bootstrap TreeSHAP stability audit (M=50)
    M = 50
    bootstrap_shap = np.zeros((M, 8))
    n_samples = len(X_train)

    for m in range(M):
        np.random.seed(m)
        indices = np.random.choice(n_samples, n_samples, replace=True)
        X_boot = X_train[indices]
        y_boot = y_train[indices]

        clf_boot = RandomForestClassifier(n_estimators=20, random_state=None)
        clf_boot.fit(X_boot, y_boot)

        exp_boot = shap.TreeExplainer(clf_boot)
        vals_boot = exp_boot.shap_values(X_test)

        if isinstance(vals_boot, list):
            vals_c1 = vals_boot[1]
        elif len(vals_boot.shape) == 3:
            vals_c1 = vals_boot[:, :, 1]
        else:
            vals_c1 = vals_boot

        bootstrap_shap[m] = np.mean(np.abs(vals_c1), axis=0)

    stability_shap_results = {}
    for i, name in enumerate(V3_KEYS):
        mu_i = float(np.mean(bootstrap_shap[:, i]))
        sigma_i = float(np.std(bootstrap_shap[:, i]))
        cv_i = float(sigma_i / mu_i) if mu_i > 0 else 0.0
        stability_shap_results[name] = cv_i

    # 5. Isolated Sufficiency AUC_i
    sufficiency_aucs = {}
    for i, name in enumerate(V3_KEYS):
        X_train_io = X_train[:, [i]]
        X_test_io = X_test[:, [i]]
        clf_io = RandomForestClassifier(n_estimators=100, random_state=42)
        clf_io.fit(X_train_io, y_train)
        y_prob_io = clf_io.predict_proba(X_test_io)[:, 1]
        sufficiency_aucs[name] = float(roc_auc_score(y_test, y_prob_io))

    # 6. Causal Score Ci
    purified_ranking = []
    for i, name in enumerate(V3_KEYS):
        I_i = normalized_shap_importances[i]
        AUC_i = sufficiency_aucs[name]
        R_i = redundancy_nmi_scores[name]
        CV_i = stability_shap_results[name]

        C_i = 0.35 * I_i + 0.35 * AUC_i - 0.15 * R_i - 0.15 * CV_i

        if CV_i > 0.5:
            role = "UNSTABLE_COMPONENT"
        elif I_i > 0.05 and AUC_i > 0.85:
            role = "CRITICAL_COMPONENT"
        elif R_i > 0.60:
            role = "REDUNDANT_COMPONENT"
        elif I_i > 0.0 and AUC_i > 0.60:
            role = "SUPPORTING_COMPONENT"
        else:
            role = "AUXILIARY_COMPONENT"

        purified_ranking.append(
            {
                "component": name,
                "score": C_i,
                "role": role,
                "shap_importance": I_i,
                "sufficiency": AUC_i,
                "redundancy_nmi": R_i,
                "instability": CV_i,
            }
        )

    # Sort descending by empirical C_i
    purified_ranking = sorted(purified_ranking, key=lambda x: x["score"], reverse=True)
    empirical_ranking = [r["component"] for r in purified_ranking]

    # Calculate Spearman correlation vs Theoretical Ranking
    ranks_theo = [THEORETICAL_RANKING.index(k) for k in V3_KEYS]
    ranks_emp = [empirical_ranking.index(k) for k in V3_KEYS]
    s_causal, _ = spearmanr(ranks_theo, ranks_emp)

    return {
        "auc": auc_score,
        "ranking": purified_ranking,
        "empirical_ranking_list": empirical_ranking,
        "normalized_shap": normalized_shap_importances.tolist(),
        "nmi_matrix": R_nmi_matrix.tolist(),
        "s_causal": float(s_causal),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION ROUTINE
# ─────────────────────────────────────────────────────────────────────────────


def main():
    t_start = time.time()

    print("=" * 80)
    print(
        "🔬 COMPUTATIONAL PHYSICS AUDITOR & CLINICAL VALIDATION — MIT-BIH BIFURCATED AUDIT"
    )
    print("=" * 80)

    # TEST 1: Live empirical ingestion (caching)
    download_mitdb_files()

    # TEST 2 & 3: Load, Preprocess & Dual Audit
    print(
        "\n[TEST 2] Parsing and slice-windowing datasets (Canal A Raw vs Canal B Filtered)..."
    )

    # Train AAMI windows
    print("  Processing DS1 (Train patients)...")
    X_train_raw, X_train_filt, y_train, dt = load_and_preprocess_windows(TRAIN_RECORDS)

    # Test AAMI windows
    print("  Processing DS2 (Test patients)...")
    X_test_raw, X_test_filt, y_test, dt = load_and_preprocess_windows(TEST_RECORDS)

    print("  Partition summary:")
    print(f"    - DS1 (Train) : {len(y_train)} windows")
    print(f"    - DS2 (Test)  : {len(y_test)} windows")

    # Run audit independently for RAW (Canal A) and FILTERED (Canal B)
    audit_raw = run_causal_audit(
        X_train_raw, X_test_raw, y_train, y_test, "CANAL A (RAW_CLINICAL)"
    )
    audit_filt = run_causal_audit(
        X_train_filt, X_test_filt, y_train, y_test, "CANAL B (MINIMAL_PHYSIOLOGICAL)"
    )

    # TEST 4: Robustness & Statistical Metrics
    print("\n[TEST 4] Calculating Robustness & Statistical Metrics...")
    delta_auc = audit_filt["auc"] - audit_raw["auc"]
    s_causal_raw = audit_raw["s_causal"]
    s_causal_filtered = audit_filt["s_causal"]

    print(f"  ΔAUC (noise)      : {delta_auc:+.6f}")
    print(f"  S_causal (raw)    : {s_causal_raw:.6f}")
    print(f"  S_causal (filtered): {s_causal_filtered:.6f}")

    # TEST 5: Internal Geometry & Causal Stability
    print("\n[TEST 5] Assessing Latent Geometry & Causal Stability...")
    # CKA on test embeddings (DS2)
    cka_val = compute_linear_cka(X_test_raw, X_test_filt)
    d_emb = 1.0 - cka_val

    # Spearman on global SHAP attributions
    global_shap_raw = audit_raw["normalized_shap"]
    global_shap_filt = audit_filt["normalized_shap"]
    coef, _ = spearmanr(global_shap_raw, global_shap_filt)
    d_shap = 1.0 - float(coef)

    # Interpretations
    geom_status = "GEOMETRY_STABLE" if d_emb < 0.1 else "GEOMETRY_REORGANIZED"
    causal_status = (
        "CAUSAL_MECHANISM_STABLE" if d_shap < 0.1 else "CAUSAL_MECHANISM_REORGANIZED"
    )

    print(f"  D_emb (latent deformation) : {d_emb:.6f} ──> {geom_status}")
    print(f"  D_SHAP (causal stability)  : {d_shap:.6f} ──> {causal_status}")

    # Save Report JSON
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "MIT-BIH Bifurcated Clinical Audit",
            "version": "V3",
            "aami_strict_partitioning": {
                "train_records": TRAIN_RECORDS,
                "test_records": TEST_RECORDS,
                "train_windows": len(y_train),
                "test_windows": len(y_test),
            },
        },
        "canal_a_raw": {
            "auc": audit_raw["auc"],
            "s_causal": s_causal_raw,
            "empirical_ranking": audit_raw["empirical_ranking_list"],
            "ranking_details": audit_raw["ranking"],
        },
        "canal_b_filtered": {
            "auc": audit_filt["auc"],
            "s_causal": s_causal_filtered,
            "empirical_ranking": audit_filt["empirical_ranking_list"],
            "ranking_details": audit_filt["ranking"],
        },
        "robustness_metrics": {
            "delta_auc_noise": delta_auc,
            "s_causal_raw": s_causal_raw,
            "s_causal_filtered": s_causal_filtered,
        },
        "latent_space_deformation": {
            "d_emb": d_emb,
            "d_shap": d_shap,
            "geometry_status": geom_status,
            "causal_mechanism_status": causal_status,
        },
    }

    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n📂 Successfully compiled and exported JSON report to: {REPORT_FILE}")

    # ── REQUIRED TERMINAL DUMP (INDICATOR SURVIVAL PANEL) ─────────────────────
    print("\n" + "═" * 80)
    print("🏆 FINAL CLINICAL SURVIVAL METRICS & LATENT DEFORMATION DIAGNOSES")
    print("═" * 80)
    print(f"  Survival AUC (Raw)           : {audit_raw['auc']:.6f}")
    print(f"  Survival AUC (Filtered)      : {audit_filt['auc']:.6f}")
    print(f"  Statistical ΔAUC         : {delta_auc:+.6f}")
    print(f"  Causal Spearman (Raw)        : {s_causal_raw:.6f}")
    print(f"  Causal Spearman (Filtered)   : {s_causal_filtered:.6f}")
    print("  " + "─" * 76)
    print(f"  Latent Space Deformation (D_emb)  : {d_emb:.6f} ──> {geom_status}")
    print(f"  Causal Mech Deformation (D_SHAP) : {d_shap:.6f} ──> {causal_status}")
    print("═" * 80)

    t_end = time.time()
    print(f"Clinical Audit completed in {t_end - t_start:.2f} seconds.\n")


if __name__ == "__main__":
    main()
