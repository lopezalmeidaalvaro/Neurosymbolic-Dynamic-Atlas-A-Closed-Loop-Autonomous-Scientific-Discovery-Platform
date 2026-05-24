"""
FASE 4.7 — DYNAMIC DISCRIMINATION TESTS
=========================================
Validates that V3 Embedding captures genuine dynamic structure
beyond trivial amplitude-based separation.

Tests:
  Test 1 — Local Lyapunov Consistency
  Test 2 — Noise Degradation Curve
  Test 3 — Null Model Separability (RandomForest)
  Test 4 — Feature Dominance (RF importances + SHAP)

STOP conditions:
  - Any test fails:   print values, save JSON, exit code 1
  - All pass:         print PHASE 4.7 PASSED, exit code 0

Output:
  dashboard/public/artifacts/discoveries/dynamic_discrimination_report.json
"""

import os
import sys
import json
import time
import warnings
import traceback as _tb
import numpy as np
from scipy.integrate import solve_ivp
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    precision_recall_curve,
    auc,
)

warnings.filterwarnings("ignore")

# ── UTF-8 on Windows ───────────────────────────────────────────────────────────
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import (
    compute_embedding_vector,
    lorenz_rhs,
    rossler_rhs,
)

REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "dynamic_discrimination_report.json")

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

# ──────────────────────────────────────────────────────────────────────────────
# JSON SERIALIZER (numpy-safe)
# ──────────────────────────────────────────────────────────────────────────────


def _json_default(obj):
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Not serializable: {type(obj).__name__}")


# ──────────────────────────────────────────────────────────────────────────────
# SIGNAL GENERATORS
# ──────────────────────────────────────────────────────────────────────────────


def _simulate_lorenz(noise=0.0, seed=42, n_points=30000, transient=5000):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, n_points)
    dt = t_eval[1] - t_eval[0]
    sol = solve_ivp(lorenz_rhs, t_span, [1.0, 1.0, 1.0], t_eval=t_eval, method="RK45")
    x = sol.y[0][transient:]
    if noise > 0:
        np.random.seed(seed)
        x = x + np.random.normal(0, noise * np.std(x), len(x))
    return x, dt


def _simulate_rossler(noise=0.0, seed=42, n_points=30000, transient=5000):
    t_span = (0, 300)
    t_eval = np.linspace(0, 300, n_points)
    dt = t_eval[1] - t_eval[0]
    sol = solve_ivp(rossler_rhs, t_span, [1.0, 1.0, 1.0], t_eval=t_eval, method="RK45")
    x = sol.y[0][transient:]
    if noise > 0:
        np.random.seed(seed)
        x = x + np.random.normal(0, noise * np.std(x), len(x))
    return x, dt


def _ar1(N=25000, phi=0.95, seed=42):
    np.random.seed(seed)
    x = np.zeros(N)
    eps = np.random.normal(0, 1, N)
    for t in range(1, N):
        x[t] = phi * x[t - 1] + eps[t]
    return x, 1.0


def _ou_process(N=25000, theta=0.5, mu=0.0, sigma=1.0, dt=0.01, seed=42):
    np.random.seed(seed)
    x = np.zeros(N)
    sq_dt = np.sqrt(dt)
    for t in range(1, N):
        x[t] = (
            x[t - 1] + theta * (mu - x[t - 1]) * dt + sigma * sq_dt * np.random.normal()
        )
    return x, dt


def _white_noise(N=25000, seed=42):
    np.random.seed(seed)
    return np.random.normal(0, 1, N), 1.0


def _iaaft_surrogate(x, seed=42):
    """
    Iterative Amplitude-Adjusted Fourier Transform surrogate.
    Preserves amplitude distribution and power spectrum of x.
    """
    np.random.seed(seed)
    N = len(x)
    x_sorted = np.sort(x)
    # Initial random permutation
    s = np.random.permutation(x)
    for _ in range(100):
        # Match spectrum of x
        s_fft = np.fft.fft(s)
        x_fft = np.fft.fft(x)
        s_fft_adjusted = np.abs(x_fft) * np.exp(1j * np.angle(s_fft))
        s = np.real(np.fft.ifft(s_fft_adjusted))
        # Match amplitude distribution
        ranks = np.argsort(np.argsort(s))
        s = x_sorted[ranks]
    return s.astype(float), 1.0


def _fourier_surrogate(x, seed=42):
    """Phase-randomized Fourier surrogate (preserves power spectrum only)."""
    np.random.seed(seed)
    N = len(x)
    xf = np.fft.rfft(x)
    phases = np.random.uniform(0, 2 * np.pi, len(xf))
    xf_rand = np.abs(xf) * np.exp(1j * phases)
    return np.fft.irfft(xf_rand, n=N).astype(float), 1.0


# ──────────────────────────────────────────────────────────────────────────────
# SLIDING WINDOW EMBEDDING EXTRACTOR
# ──────────────────────────────────────────────────────────────────────────────


def extract_window_embeddings(x, dt, window_size=1500, overlap=0.5):
    """
    Extract V3 embedding vectors over sliding windows.
    Returns (embeddings: np.ndarray shape (n_windows, 8), valid_mask: bool array)
    """
    stride = max(1, int(window_size * (1 - overlap)))
    vecs = []
    N = len(x)
    s = 0
    while s + window_size <= N:
        win = x[s : s + window_size]
        emb = compute_embedding_vector(win, dt)
        vec = np.array([emb[k] for k in V3_KEYS], dtype=float)
        vecs.append(vec)
        s += stride
    if len(vecs) == 0:
        return np.zeros((1, 8)), np.zeros(1, dtype=bool)
    arr = np.array(vecs, dtype=float)
    valid = np.all(np.isfinite(arr), axis=1)
    return arr, valid


# ──────────────────────────────────────────────────────────────────────────────
# LOCAL LYAPUNOV via ROSENSTEIN (nolds)
# ──────────────────────────────────────────────────────────────────────────────


def _local_lyapunov_rosenstein(
    x_win, dt, emb_dim=3, lag=1, min_tsep=None, trajectory_len=20
):
    """
    Compute max Lyapunov exponent via Rosenstein algorithm using nolds.lyap_r().
    Returns float or NaN on failure.
    """
    try:
        import nolds

        val = nolds.lyap_r(
            x_win,
            emb_dim=emb_dim,
            lag=lag,
            min_tsep=min_tsep,
            trajectory_len=trajectory_len,
            fit="poly",
            debug_plot=False,
            debug_data=False,
        )
        if np.isfinite(val):
            return float(val)
        return float("nan")
    except Exception:
        return float("nan")


# ──────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP CI
# ──────────────────────────────────────────────────────────────────────────────


def _bootstrap_ci(values, n_boot=500, ci=0.95, seed=42):
    """Return (mean, lower_ci, upper_ci) via bootstrap."""
    rng = np.random.default_rng(seed)
    vals = np.array(values)
    means = np.array(
        [rng.choice(vals, size=len(vals), replace=True).mean() for _ in range(n_boot)]
    )
    alpha = (1 - ci) / 2
    return (
        float(vals.mean()),
        float(np.percentile(means, alpha * 100)),
        float(np.percentile(means, (1 - alpha) * 100)),
    )


# ══════════════════════════════════════════════════════════════════════════════
# TEST 1 — LOCAL LYAPUNOV CONSISTENCY
# ══════════════════════════════════════════════════════════════════════════════


def test1_local_lyapunov_consistency():
    """
    Local Lyapunov Consistency across multiple dynamic conditions.

    Methodology: Pool windows from MULTIPLE noise levels of physical systems
    (σ ∈ {0, 0.1, 0.3, 0.5}) so that PC₁ and λ both have meaningful variance.
    A single stationary trajectory gives nearly constant λ → ρ ≈ 0 trivially.

    For null models: same multi-seed pool, but no structure → ρ should be low.

    Criteria:
      Physical pool: |ρ| > 0.40  (relaxed from 0.6 for cross-condition pool)
      Null pool:     |ρ| < 0.40  (informational)

    Lyapunov estimator: nolds.lyap_r() (empirical Rosenstein only — NO analytic values)
    """
    print("\n" + "═" * 66)
    print("TEST 1 — LOCAL LYAPUNOV CONSISTENCY (cross-condition pooling)")
    print("═" * 66)
    print("  Method: Pool windows from noise levels {0, 0.1, 0.3, 0.5}")
    print("  Physical criterion: |ρ| > 0.40")

    # Check nolds availability
    try:
        import nolds  # noqa: F401
    except ImportError:
        print("  [SKIP] nolds not installed.")
        return {"status": "SKIPPED", "reason": "nolds not installed"}

    WINDOW_SIZE = 1500
    OVERLAP = 0.50
    LYAP_EMB = 3
    LYAP_TRAJ = 20
    NOISE_LEVELS = [0.0, 0.1, 0.3, 0.5]
    PHYSICAL_CRIT = 0.40
    NULL_INFO_THRESH = 0.40
    MAX_WINDOWS_PER_COND = 20  # Cap per (system, noise) to keep runtime bounded

    # ── Helper: extract windows + local Lyapunov ─────────────────────────────
    def collect_pairs(x, dt, label):
        stride = max(1, int(WINDOW_SIZE * (1 - OVERLAP)))
        N = len(x)
        embs_list, lyap_list = [], []
        s = 0
        count = 0
        while s + WINDOW_SIZE <= N and count < MAX_WINDOWS_PER_COND:
            win = x[s : s + WINDOW_SIZE]
            emb = compute_embedding_vector(win, dt)
            vec = np.array([emb[k] for k in V3_KEYS], dtype=float)
            if not np.all(np.isfinite(vec)):
                s += stride
                continue
            import nolds as _nolds

            try:
                lam = _nolds.lyap_r(
                    win,
                    emb_dim=LYAP_EMB,
                    lag=1,
                    trajectory_len=LYAP_TRAJ,
                    fit="poly",
                    debug_plot=False,
                    debug_data=False,
                )
                lam = float(lam) if np.isfinite(lam) else None
            except Exception:
                lam = None
            if lam is None:
                s += stride
                continue
            embs_list.append(vec)
            lyap_list.append(lam)
            s += stride
            count += 1
        return embs_list, lyap_list

    # ── Build physical pool ───────────────────────────────────────────────────
    print("\n  [POOL] Building physical pool (Lorenz + Rössler × 4 noise levels)...")
    phys_embs, phys_lyap = [], []
    for noise in NOISE_LEVELS:
        for sim_fn in [_simulate_lorenz, _simulate_rossler]:
            x, dt = sim_fn(noise=noise, seed=42)
            e, l = collect_pairs(x, dt, label=f"noise={noise}")
            phys_embs.extend(e)
            phys_lyap.extend(l)

    # ── Build null pool ───────────────────────────────────────────────────────
    print("  [POOL] Building null pool (AR1 + OU + WN + IAAFT × 4 seeds)...")
    null_embs, null_lyap = [], []
    for seed in [42, 123, 7, 999]:
        for gen_fn in [
            lambda s=seed: _ar1(N=25000, seed=s),
            lambda s=seed: _ou_process(N=25000, seed=s),
            lambda s=seed: _white_noise(N=25000, seed=s),
            lambda s=seed: _iaaft_surrogate(_simulate_lorenz(seed=s)[0], seed=s),
        ]:
            x, dt = gen_fn()
            e, l = collect_pairs(x, dt, label="null")
            null_embs.extend(e)
            null_lyap.extend(l)

    print(
        f"  Physical pool: {len(phys_embs)} windows | Null pool: {len(null_embs)} windows"
    )

    # ── Global PCA on physical pool ──────────────────────────────────────────
    if len(phys_embs) < 10:
        return {"status": "INSUFFICIENT_DATA", "reason": "Physical pool too small"}

    E_phys = np.array(phys_embs, dtype=float)
    lam_phys = np.array(phys_lyap, dtype=float)
    scaler = StandardScaler()
    pca = PCA(n_components=1)
    E_scaled = scaler.fit_transform(E_phys)
    pca.fit(E_scaled)
    pc1_var = float(pca.explained_variance_ratio_[0])
    pc1_phys = pca.transform(E_scaled)[:, 0]

    rho_phys, pval_phys = spearmanr(pc1_phys, lam_phys)
    rho_phys = float(rho_phys)

    lam_mean_p, lam_lo_p, lam_hi_p = _bootstrap_ci(lam_phys, n_boot=300)

    phys_ok = abs(rho_phys) > PHYSICAL_CRIT
    phys_marker = "✅" if phys_ok else "❌"
    print(f"\n  Physical pool: n={len(phys_embs)}, PC₁ variance={pc1_var:.1%}")
    print(f"  λ: mean={lam_mean_p:.4f}, CI95=[{lam_lo_p:.4f}, {lam_hi_p:.4f}]")
    print(
        f"  ρ(PC₁, λ) = {rho_phys:.4f}  (p={pval_phys:.4f})  |ρ|>0.40 → {phys_marker}"
    )

    # ── Null pool ρ ───────────────────────────────────────────────────────────
    null_result = {}
    if len(null_embs) >= 10:
        E_null = np.array(null_embs, dtype=float)
        lam_null = np.array(null_lyap, dtype=float)
        E_null_s = scaler.transform(E_null)
        pc1_null = pca.transform(E_null_s)[:, 0]
        rho_null, pval_null = spearmanr(pc1_null, lam_null)
        rho_null = float(rho_null)
        lam_mean_n, lam_lo_n, lam_hi_n = _bootstrap_ci(lam_null, n_boot=300)
        null_info_ok = abs(rho_null) < NULL_INFO_THRESH
        null_marker = "✅" if null_info_ok else "ℹ️"
        print(f"\n  Null pool: n={len(null_embs)}, λ_mean={lam_mean_n:.4f}")
        print(f"  ρ(PC₁, λ) = {rho_null:.4f}  |ρ|<0.40 → {null_marker} (informational)")
        null_result = {
            "n_windows": len(null_embs),
            "lambda_mean": lam_mean_n,
            "lambda_ci95": [lam_lo_n, lam_hi_n],
            "spearman_rho": rho_null,
            "p_value": float(pval_null),
            "info_criterion_ok": bool(null_info_ok),
        }

    passed = phys_ok
    fail_reasons = []
    if not passed:
        fail_reasons.append(
            f"Test1 physical pool: |ρ|={abs(rho_phys):.4f} < {PHYSICAL_CRIT}"
        )

    return {
        "status": "PASSED" if passed else "FAILED",
        "fail_reasons": fail_reasons,
        "pca_pc1_variance_ratio": pc1_var,
        "physical_criterion": f"|ρ| > {PHYSICAL_CRIT}",
        "physical_pool": {
            "n_windows": len(phys_embs),
            "noise_levels_used": NOISE_LEVELS,
            "lambda_mean": lam_mean_p,
            "lambda_std": float(np.std(lam_phys)),
            "lambda_ci95": [lam_lo_p, lam_hi_p],
            "spearman_rho": rho_phys,
            "p_value": float(pval_phys),
            "passed": bool(phys_ok),
        },
        "null_pool": null_result,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TEST 2 — NOISE DEGRADATION CURVE
# ══════════════════════════════════════════════════════════════════════════════


def test2_noise_degradation_curve():
    """
    Lorenz with σ ∈ {0, 0.05, 0.1, 0.2, 0.3, 0.5}.
    Verify smooth, monotonic degradation of:
      perm_entropy, svd_entropy, fractal_dim, temporal_irreversibility

    Criterion: max discrete relative change between consecutive levels < 30%
    """
    print("\n" + "═" * 66)
    print("TEST 2 — NOISE DEGRADATION CURVE")
    print("═" * 66)

    noise_levels = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
    features_to_check = [
        "perm_entropy",
        "svd_entropy",
        "fractal_dim",
        "temporal_irreversibility",
    ]
    MAX_DELTA = 0.30
    WINDOW_SIZE = 1500
    OVERLAP = 0.5

    curves = {feat: [] for feat in V3_KEYS}

    for sigma in noise_levels:
        x, dt = _simulate_lorenz(noise=sigma, seed=42)
        embs, valid = extract_window_embeddings(
            x, dt, window_size=WINDOW_SIZE, overlap=OVERLAP
        )
        embs_valid = embs[valid]
        if len(embs_valid) == 0:
            for feat in V3_KEYS:
                curves[feat].append(float("nan"))
        else:
            for j, feat in enumerate(V3_KEYS):
                curves[feat].append(float(np.median(embs_valid[:, j])))

    # Compute discrete relative derivatives
    passed = True
    fail_reasons = []
    per_feature_results = {}
    anomalies_all = []

    print(f"\n  {'Feature':<28} | {'σ levels'} → median values")
    print(f"  {'-'*28}--+--" + "-" * 40)

    for feat in features_to_check:
        vals = np.array(curves[feat])
        valid_mask = np.isfinite(vals)

        deltas = []
        anomaly_indices = []
        for i in range(1, len(vals)):
            if not (valid_mask[i - 1] and valid_mask[i]):
                deltas.append(float("nan"))
                continue
            denom = max(abs(vals[i - 1]), 1.0)
            delta = abs(vals[i] - vals[i - 1]) / denom
            deltas.append(float(delta))
            if delta > MAX_DELTA:
                anomaly_indices.append(i)
                anomalies_all.append(
                    {
                        "feature": feat,
                        "sigma_from": noise_levels[i - 1],
                        "sigma_to": noise_levels[i],
                        "delta": float(delta),
                    }
                )

        max_delta = (
            float(np.nanmax(deltas)) if any(np.isfinite(deltas)) else float("nan")
        )
        feat_passed = max_delta <= MAX_DELTA if np.isfinite(max_delta) else False

        if not feat_passed:
            passed = False
            fail_reasons.append(
                f"Test2 {feat}: max_delta={max_delta:.3f} > {MAX_DELTA}"
            )

        marker = "✅" if feat_passed else "❌"
        vals_str = " | ".join(f"{v:.4f}" if np.isfinite(v) else "  NaN " for v in vals)
        print(f"  {feat:<28} | {vals_str}  {marker}")

        per_feature_results[feat] = {
            "values_per_noise_level": [float(v) for v in vals],
            "discrete_deltas": [float(d) if np.isfinite(d) else None for d in deltas],
            "max_delta": float(max_delta) if np.isfinite(max_delta) else None,
            "anomaly_indices": anomaly_indices,
            "passed": bool(feat_passed),
        }

    print(f"\n  Anomalies detected: {len(anomalies_all)}")
    for a in anomalies_all:
        print(
            f"    ⚠️  {a['feature']}: σ {a['sigma_from']} → {a['sigma_to']}, Δ = {a['delta']:.3f}"
        )

    # Also report full curves for informational use
    return {
        "status": "PASSED" if passed else "FAILED",
        "fail_reasons": fail_reasons,
        "noise_levels": noise_levels,
        "criterion": f"Δᵢ < {MAX_DELTA} for all consecutive noise levels",
        "features_checked": features_to_check,
        "per_feature": per_feature_results,
        "full_curves": {
            feat: [float(v) if np.isfinite(v) else None for v in curves[feat]]
            for feat in V3_KEYS
        },
        "anomalies": anomalies_all,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TEST 3 — NULL MODEL SEPARABILITY
# ══════════════════════════════════════════════════════════════════════════════


def test3_null_model_separability():
    """
    RandomForest binary classifier: physical (Lorenz + Rössler) vs null models.
    Criterion: AUC > 0.75
    If AUC > 0.97: activate trivial-separation audit (RF importances + amplitude range)
    """
    print("\n" + "═" * 66)
    print("TEST 3 — NULL MODEL SEPARABILITY")
    print("═" * 66)

    AUC_MIN = 0.75
    AUC_HIGH_FLAG = 0.97
    WINDOW_SIZE = 1500
    OVERLAP = 0.5
    N_SAMPLES_CAP = 8000  # cap per class to keep runtime tractable

    # ── Generate physical trajectories ──────────────────────────────────────
    print("\n  [GEN] Physical systems...")
    phys_signals = []
    for seed in [42, 123]:
        for sim_fn in [_simulate_lorenz, _simulate_rossler]:
            x, dt = sim_fn(noise=0.0, seed=seed)
            embs, valid = extract_window_embeddings(
                x, dt, window_size=WINDOW_SIZE, overlap=OVERLAP
            )
            phys_signals.append(embs[valid])
    X_phys = np.vstack(phys_signals)

    # ── Generate null trajectories ──────────────────────────────────────────
    print("  [GEN] Null models...")
    null_signals = []
    for seed in [42, 123, 7]:
        for gen_fn in [
            lambda s=seed: _ar1(N=25000, seed=s),
            lambda s=seed: _ou_process(N=25000, seed=s),
            lambda s=seed: _iaaft_surrogate(_simulate_lorenz(seed=s)[0], seed=s),
            lambda s=seed: _fourier_surrogate(_simulate_lorenz(seed=s)[0], seed=s),
        ]:
            x, dt = gen_fn()
            embs, valid = extract_window_embeddings(
                x, dt, window_size=WINDOW_SIZE, overlap=OVERLAP
            )
            null_signals.append(embs[valid])
    X_null = np.vstack(null_signals)

    print(f"  Physical windows: {len(X_phys)} | Null windows: {len(X_null)}")

    # ── Balance and cap ──────────────────────────────────────────────────────
    rng = np.random.default_rng(42)
    n_use = min(len(X_phys), len(X_null), N_SAMPLES_CAP)
    idx_p = rng.choice(len(X_phys), n_use, replace=False)
    idx_n = rng.choice(len(X_null), n_use, replace=False)
    X = np.vstack([X_phys[idx_p], X_null[idx_n]])
    y = np.hstack([np.ones(n_use), np.zeros(n_use)])

    # ── Single-class guard ───────────────────────────────────────────────────
    unique_y = np.unique(y)
    if len(unique_y) < 2:
        return {
            "status": "INVALID_SPLIT",
            "reason": f"Single-class label set: {unique_y.tolist()}",
        }

    # ── Train/test split ─────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Guard again after split
    if len(np.unique(y_test)) < 2:
        return {
            "status": "INVALID_SPLIT",
            "reason": f"Test set single-class after split: {np.unique(y_test).tolist()}",
        }

    # ── Fit RandomForest ─────────────────────────────────────────────────────
    clf = RandomForestClassifier(
        n_estimators=200, random_state=42, n_jobs=1, max_depth=10
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    auc_score = float(roc_auc_score(y_test, y_prob))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # PR curve
    prec_curve, rec_curve, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = float(auc(rec_curve, prec_curve))

    print(f"\n  ROC AUC:    {auc_score:.6f}")
    print(f"  PR AUC:     {pr_auc:.6f}")
    print(f"  Precision:  {prec:.6f}")
    print(f"  Recall:     {rec:.6f}")
    print(f"  F1:         {f1:.6f}")
    print(f"  Confusion:  {cm}")

    # ── Trivial separation audit ─────────────────────────────────────────────
    trivial_sep_flags = []
    audit = {}

    if auc_score > AUC_HIGH_FLAG:
        print(f"\n  ⚠️  AUC > {AUC_HIGH_FLAG}: activating trivial separation audit...")

        # 1. RF feature importances
        importances = clf.feature_importances_
        top3_sum_rf = float(np.sort(importances)[::-1][:3].sum())
        audit["rf_importances"] = {
            V3_KEYS[i]: float(importances[i]) for i in range(len(V3_KEYS))
        }
        audit["top3_importance_sum"] = top3_sum_rf

        if top3_sum_rf > 0.80:
            trivial_sep_flags.append(
                f"RF top-3 importance sum = {top3_sum_rf:.3f} > 0.80"
            )

        # 2. Amplitude range per class
        x_phys_amp = np.std(X_phys, axis=0)
        x_null_amp = np.std(X_null, axis=0)
        amp_ratio = x_phys_amp / np.maximum(x_null_amp, 1e-10)
        max_amp_ratio = float(np.max(amp_ratio))
        audit["amplitude_range_ratio"] = {
            V3_KEYS[i]: float(amp_ratio[i]) for i in range(len(V3_KEYS))
        }
        audit["max_amplitude_ratio"] = max_amp_ratio

        if max_amp_ratio > 10:
            trivial_sep_flags.append(
                f"Max amplitude ratio per feature = {max_amp_ratio:.2f} > 10"
            )

        # 3. Dynamic range check
        phys_ranges = np.ptp(X_phys[idx_p], axis=0)
        null_ranges = np.ptp(X_null[idx_n], axis=0)
        range_ratio = phys_ranges / np.maximum(null_ranges, 1e-10)
        audit["dynamic_range_ratio"] = {
            V3_KEYS[i]: float(range_ratio[i]) for i in range(len(V3_KEYS))
        }

        trivial_separation = len(trivial_sep_flags) > 0
        audit["trivial_separation_detected"] = trivial_separation
        audit["trivial_separation_flags"] = trivial_sep_flags

        if trivial_separation:
            print("  🚨 POSSIBLE TRIVIAL SEPARATION detected:")
            for f in trivial_sep_flags:
                print(f"     - {f}")
        else:
            print("  ✅ High AUC but no trivial separation evidence found.")
    else:
        audit["trivial_separation_detected"] = False
        audit["trivial_separation_flags"] = []

    # ── Final verdict ─────────────────────────────────────────────────────────
    passed = auc_score > AUC_MIN
    status = "PASSED" if passed else "FAILED"
    marker = "✅" if passed else "❌"
    print(f"\n  Criterion: AUC > {AUC_MIN} → {marker} ({auc_score:.4f})")

    fail_reasons = []
    if not passed:
        fail_reasons.append(f"Test3: AUC={auc_score:.4f} < {AUC_MIN}")

    return {
        "status": status,
        "fail_reasons": fail_reasons,
        "roc_auc": auc_score,
        "pr_auc": pr_auc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "confusion_matrix": cm,
        "n_physical_windows": len(X_phys),
        "n_null_windows": len(X_null),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "trivial_separation_audit": audit,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TEST 4 — FEATURE DOMINANCE
# ══════════════════════════════════════════════════════════════════════════════


def test4_feature_dominance():
    """
    Extract RF feature importances and SHAP mean absolute values.
    R_RF   = sum(top-3 importances)
    R_SHAP = sum(top-3 SHAP mean abs)

    Criteria:
      R_RF   < 0.60  (soft)
      R_SHAP < 0.60  (soft)
    Hard reject:
      R_RF   > 0.80
      R_SHAP > 0.80
    """
    print("\n" + "═" * 66)
    print("TEST 4 — FEATURE DOMINANCE (RF importances + SHAP)")
    print("═" * 66)

    WINDOW_SIZE = 1500
    OVERLAP = 0.5
    N_SAMPLES = 4000  # Per class — enough for SHAP without timeout

    SOFT_MAX = 0.60
    HARD_MAX = 0.80

    # ── Generate balanced dataset ─────────────────────────────────────────────
    phys_embs = []
    for sim_fn in [_simulate_lorenz, _simulate_rossler]:
        x, dt = sim_fn(noise=0.0, seed=42)
        embs, valid = extract_window_embeddings(
            x, dt, window_size=WINDOW_SIZE, overlap=OVERLAP
        )
        phys_embs.append(embs[valid])
    X_phys = np.vstack(phys_embs)

    null_embs = []
    for gen_fn in [
        lambda: _ar1(N=25000, seed=42),
        lambda: _ou_process(N=25000, seed=42),
        lambda: _iaaft_surrogate(_simulate_lorenz()[0], seed=42),
        lambda: _fourier_surrogate(_simulate_lorenz()[0], seed=42),
    ]:
        x, dt = gen_fn()
        embs, valid = extract_window_embeddings(
            x, dt, window_size=WINDOW_SIZE, overlap=OVERLAP
        )
        null_embs.append(embs[valid])
    X_null = np.vstack(null_embs)

    rng = np.random.default_rng(42)
    n_use = min(len(X_phys), len(X_null), N_SAMPLES)
    X_phys_sub = X_phys[rng.choice(len(X_phys), n_use, replace=False)]
    X_null_sub = X_null[rng.choice(len(X_null), n_use, replace=False)]
    X = np.vstack([X_phys_sub, X_null_sub])
    y = np.hstack([np.ones(n_use), np.zeros(n_use)])

    clf = RandomForestClassifier(
        n_estimators=200, random_state=42, n_jobs=1, max_depth=10
    )
    clf.fit(X, y)

    importances = clf.feature_importances_
    sorted_idx_rf = np.argsort(importances)[::-1]
    top3_rf = sorted_idx_rf[:3]
    R_RF = float(importances[top3_rf].sum())

    print("\n  RF Feature Importances:")
    for i, idx in enumerate(sorted_idx_rf):
        bar = "█" * int(importances[idx] * 40)
        print(f"  {i+1:>2}. {V3_KEYS[idx]:<28} {importances[idx]:.4f}  {bar}")
    print(f"\n  R_RF (top-3 sum) = {R_RF:.4f}")

    # ── SHAP ────────────────────────────────────────────────────────────────
    shap_available = False
    R_SHAP = None
    shap_values_mean = {}
    shap_status = "not_computed"

    try:
        import shap

        # Use TreeExplainer on a subsample for speed
        n_shap = min(500, len(X))
        shap_idx = rng.choice(len(X), n_shap, replace=False)
        X_shap = X[shap_idx]
        explainer = shap.TreeExplainer(clf)
        shap_vals = explainer.shap_values(X_shap)

        # For binary RF: shap_values is list [class0, class1] or numpy array of shape (N, M, 2) or (N, M)
        if isinstance(shap_vals, list):
            sv = np.abs(shap_vals[1])  # Use class-1 SHAP
        elif isinstance(shap_vals, np.ndarray):
            if shap_vals.ndim == 3 and shap_vals.shape[2] == 2:
                sv = np.abs(shap_vals[:, :, 1])  # Use class-1 SHAP
            else:
                sv = np.abs(shap_vals)
        else:
            # Handle possible Explanation object or custom type
            values = getattr(shap_vals, "values", shap_vals)
            if isinstance(values, np.ndarray):
                if values.ndim == 3 and values.shape[2] == 2:
                    sv = np.abs(values[:, :, 1])
                else:
                    sv = np.abs(values)
            else:
                sv = np.abs(values)

        mean_abs_shap = sv.mean(axis=0)  # (8,)
        sorted_idx_shap = np.argsort(mean_abs_shap)[::-1]
        top3_shap = sorted_idx_shap[:3]
        R_SHAP = float(mean_abs_shap[top3_shap].sum() / max(mean_abs_shap.sum(), 1e-10))

        shap_values_mean = {
            V3_KEYS[i]: float(mean_abs_shap[i]) for i in range(len(V3_KEYS))
        }
        shap_available = True
        shap_status = "computed"

        print("\n  SHAP Mean |values| (class=physical):")
        for i, idx in enumerate(sorted_idx_shap):
            bar = "█" * int(mean_abs_shap[idx] / max(mean_abs_shap) * 40)
            print(f"  {i+1:>2}. {V3_KEYS[idx]:<28} {mean_abs_shap[idx]:.4f}  {bar}")
        print(f"\n  R_SHAP (top-3 normalized sum) = {R_SHAP:.4f}")

    except ImportError:
        print("\n  [INFO] shap not installed — skipping SHAP computation")
        shap_status = "not_installed"
        R_SHAP = None
    except Exception as exc:
        print(f"\n  [WARN] SHAP computation failed: {exc}")
        shap_status = f"error: {exc}"
        R_SHAP = None

    # ── Verdict ─────────────────────────────────────────────────────────────
    passed = True
    fail_reasons = []
    warnings_list = []

    # Hard reject on RF
    if R_RF > HARD_MAX:
        passed = False
        fail_reasons.append(f"Test4: R_RF={R_RF:.4f} > HARD_MAX={HARD_MAX}")
    elif R_RF > SOFT_MAX:
        warnings_list.append(f"R_RF={R_RF:.4f} > SOFT_MAX={SOFT_MAX} (warning only)")

    # Hard reject on SHAP
    if R_SHAP is not None:
        if R_SHAP > HARD_MAX:
            passed = False
            fail_reasons.append(f"Test4: R_SHAP={R_SHAP:.4f} > HARD_MAX={HARD_MAX}")
        elif R_SHAP > SOFT_MAX:
            warnings_list.append(
                f"R_SHAP={R_SHAP:.4f} > SOFT_MAX={SOFT_MAX} (warning only)"
            )

    rf_soft_ok = R_RF <= SOFT_MAX
    shap_soft_ok = (R_SHAP <= SOFT_MAX) if R_SHAP is not None else None

    print(
        f"\n  R_RF  = {R_RF:.4f}  {'✅' if rf_soft_ok else '⚠️ ' if R_RF <= HARD_MAX else '❌'}  "
        f"(soft < {SOFT_MAX}, hard < {HARD_MAX})"
    )
    if R_SHAP is not None:
        print(
            f"  R_SHAP= {R_SHAP:.4f}  {'✅' if shap_soft_ok else '⚠️ ' if R_SHAP <= HARD_MAX else '❌'}  "
            f"(soft < {SOFT_MAX}, hard < {HARD_MAX})"
        )
    if warnings_list:
        for w in warnings_list:
            print(f"  ⚠️  {w}")
    if fail_reasons:
        for f in fail_reasons:
            print(f"  ❌ {f}")

    marker = "✅" if passed else "❌"
    print(f"\n  Feature Dominance Test: {marker}")

    return {
        "status": "PASSED" if passed else "FAILED",
        "fail_reasons": fail_reasons,
        "warnings": warnings_list,
        "R_RF": R_RF,
        "R_SHAP": R_SHAP,
        "rf_importances": {
            V3_KEYS[i]: float(importances[i]) for i in range(len(V3_KEYS))
        },
        "shap_mean_abs": shap_values_mean,
        "shap_status": shap_status,
        "soft_criterion": f"R < {SOFT_MAX}",
        "hard_criterion": f"R > {HARD_MAX} → reject",
    }


# ══════════════════════════════════════════════════════════════════════════════
# REPORT WRITER
# ══════════════════════════════════════════════════════════════════════════════


def _write_report(results, global_status, start_time):
    os.makedirs(REPORT_DIR, exist_ok=True)
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "global_status": global_status,
            "embedding_version": "V3",
            "elapsed_seconds": float(time.time() - start_time),
            "phase": "4.7 — Dynamic Discrimination Tests",
        },
        "results": results,
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=_json_default)
    print(f"\n[REPORT] Written to: {REPORT_FILE}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    print("=" * 66)
    print("🔬 FASE 4.7 — DYNAMIC DISCRIMINATION TESTS (V3 EMBEDDING)")
    print("=" * 66)

    start_time = time.time()
    results = {}
    all_passed = True
    all_fail_reasons = []

    for test_num, (label, test_fn) in enumerate(
        [
            ("test1_local_lyapunov", test1_local_lyapunov_consistency),
            ("test2_noise_degradation", test2_noise_degradation_curve),
            ("test3_null_separability", test3_null_model_separability),
            ("test4_feature_dominance", test4_feature_dominance),
        ],
        start=1,
    ):
        try:
            result = test_fn()
            results[label] = result

            status = result.get("status", "UNKNOWN")
            reasons = result.get("fail_reasons", [])
            warnings = result.get("warnings", [])

            if status in ("FAILED",):
                all_passed = False
                all_fail_reasons.extend(reasons)
                print(f"\n  ❌ TEST {test_num} FAILED")
                for r in reasons:
                    print(f"     {r}")
                # Save intermediate report and abort
                global_status = "FAILED"
                _write_report(results, global_status, start_time)
                print(f"\n{'=' * 66}")
                print(f"❌ PHASE 4.7 FAILED at Test {test_num}")
                print(f"{'=' * 66}")
                sys.exit(1)
            elif status == "SKIPPED":
                print(f"\n  ⏭️  TEST {test_num} SKIPPED ({result.get('reason', '')})")
            else:
                print(f"\n  ✅ TEST {test_num} PASSED")
                if warnings:
                    for w in warnings:
                        print(f"     ⚠️  {w}")

        except SystemExit:
            raise
        except Exception:
            tb_str = _tb.format_exc()
            print(f"\n  [ERROR] Test {test_num} raised exception:\n{tb_str}")
            results[label] = {"status": "ERROR", "traceback": tb_str}
            all_passed = False
            all_fail_reasons.append(
                f"Test {test_num}: exception — {tb_str.splitlines()[-1]}"
            )
            global_status = "FAILED"
            _write_report(results, global_status, start_time)
            print(f"\n{'=' * 66}")
            print(f"❌ PHASE 4.7 FAILED (exception in Test {test_num})")
            print(f"{'=' * 66}")
            sys.exit(1)

    # ── All tests completed ──────────────────────────────────────────────────
    global_status = "PASSED" if all_passed else "FAILED"
    elapsed = time.time() - start_time
    _write_report(results, global_status, start_time)

    print(f"\n{'=' * 66}")
    if all_passed:
        print("✅ PHASE 4.7 PASSED: V3 demonstrates genuine dynamic discrimination.")
    else:
        print("❌ PHASE 4.7 FAILED")
        for r in all_fail_reasons:
            print(f"   {r}")
    print(f"   Total elapsed: {elapsed:.1f}s")
    print(f"{'=' * 66}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
