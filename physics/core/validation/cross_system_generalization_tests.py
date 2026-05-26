"""
PHASE 4.8 - CROSS-SYSTEM GENERALIZATION TESTS
=============================================

Reconstructs Phase 4.8 as a reproducible validation artifact for the V3
embedding. The script generates physical dynamical systems and null models,
runs five validation tests, writes a JSON report, and exits with code 1 if
any criterion fails.

Output:
  dashboard/public/artifacts/discoveries/cross_system_generalization_report.json
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from dataclasses import dataclass
from typing import Callable

import numpy as np
import umap
from scipy.integrate import solve_ivp
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.manifold import trustworthiness
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from core.autonomous.latent_snapshot_exporter import (
    compute_embedding_vector,
)  # noqa: E402

REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "cross_system_generalization_report.json")

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

PHYSICAL_SYSTEMS = [
    "lorenz",
    "rossler",
    "henon",
    "duffing",
    "van_der_pol",
    "logistic_map",
]
NULL_MODELS = ["ar1", "ou", "iaaft", "fourier_surrogate", "block_bootstrap"]

DATASET_SEEDS = [42, 1337, 9001]
HELD_OUT_NULL_SEEDS = [2027, 31415]
WINDOW_SIZE = 1000
WINDOW_OVERLAP = 0.5

TEST1_AUC_MIN = 0.75
TEST2_SILHOUETTE_MIN = 0.30
TEST2_TRUSTWORTHINESS_MIN = 0.95
TEST2_DISTANCE_CORRELATION_MIN = 0.80
TEST3_DELTA_AUC_MAX = 0.05
TEST4_NOISE_LEVELS = [0.01, 0.05, 0.10, 0.20]
TEST4_MAX_JUMP = 0.30
TEST5_DISTANCE_MIN = 0.25


@dataclass(frozen=True)
class Signal:
    values: np.ndarray
    dt: float


def _json_default(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _finite_float(value: float) -> float:
    return float(value) if np.isfinite(value) else 0.0


def _standardize_signal(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sigma = float(np.std(x))
    if sigma <= 1e-12:
        return x - float(np.mean(x))
    return (x - float(np.mean(x))) / sigma


def _inject_noise(x: np.ndarray, noise: float, seed: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if noise <= 0:
        return x.copy()
    rng = np.random.default_rng(seed)
    sigma = float(np.std(x))
    return x + rng.normal(0.0, noise * sigma, size=len(x))


def _lorenz_rhs(_t, state):
    x, y, z = state
    return [10.0 * (y - x), x * (28.0 - z) - y, x * y - (8.0 / 3.0) * z]


def _rossler_rhs(_t, state):
    x, y, z = state
    return [-y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)]


def _duffing_rhs(t, state):
    x, y = state
    return [y, x - x**3 - 0.3 * y + 0.5 * np.cos(1.2 * t)]


def _van_der_pol_rhs(_t, state):
    x, y = state
    mu = 5.0
    return [y, mu * (1.0 - x**2) * y - x]


def _simulate_ode(
    rhs: Callable,
    y0: list[float],
    t_end: float,
    n_points: int,
    transient: int,
    noise: float,
    seed: int,
) -> Signal:
    t_eval = np.linspace(0.0, t_end, n_points)
    dt = float(t_eval[1] - t_eval[0])
    sol = solve_ivp(rhs, (0.0, t_end), y0, t_eval=t_eval, method="RK45")
    if not sol.success:
        raise RuntimeError(f"ODE solver failed: {sol.message}")
    x = np.asarray(sol.y[0][transient:], dtype=float)
    return Signal(_inject_noise(x, noise, seed), dt)


def _simulate_henon(
    noise: float, seed: int, n_points: int = 18000, transient: int = 3000
) -> Signal:
    a = 1.4
    b = 0.3
    x = 0.1
    y = 0.0
    values = []
    for i in range(n_points + transient):
        x_next = 1.0 - a * x * x + y
        y_next = b * x
        x, y = x_next, y_next
        if i >= transient:
            values.append(x)
    return Signal(_inject_noise(np.asarray(values, dtype=float), noise, seed), 1.0)


def _simulate_logistic_map(
    noise: float, seed: int, n_points: int = 18000, transient: int = 3000
) -> Signal:
    r = 3.9
    x = 0.37
    values = []
    for i in range(n_points + transient):
        x = r * x * (1.0 - x)
        if i >= transient:
            values.append(x)
    return Signal(_inject_noise(np.asarray(values, dtype=float), noise, seed), 1.0)


def simulate_physical(system: str, noise: float, seed: int) -> Signal:
    if system == "lorenz":
        return _simulate_ode(
            _lorenz_rhs, [1.0, 1.0, 1.0], 220.0, 22000, 4000, noise, seed
        )
    if system == "rossler":
        return _simulate_ode(
            _rossler_rhs, [1.0, 1.0, 1.0], 260.0, 22000, 4000, noise, seed
        )
    if system == "henon":
        return _simulate_henon(noise, seed)
    if system == "duffing":
        return _simulate_ode(_duffing_rhs, [0.1, 0.0], 500.0, 26000, 5000, noise, seed)
    if system == "van_der_pol":
        return _simulate_ode(
            _van_der_pol_rhs, [0.5, 0.0], 320.0, 24000, 4000, noise, seed
        )
    if system == "logistic_map":
        return _simulate_logistic_map(noise, seed)
    raise ValueError(f"Unknown physical system: {system}")


def generate_ar1(length: int, seed: int, phi: float = 0.85) -> Signal:
    rng = np.random.default_rng(seed)
    x = np.zeros(length, dtype=float)
    eps = rng.normal(0.0, 1.0, length)
    for t in range(1, length):
        x[t] = phi * x[t - 1] + eps[t]
    return Signal(_standardize_signal(x), 1.0)


def generate_ou(
    length: int, seed: int, theta: float = 0.25, sigma: float = 0.5, dt: float = 0.01
) -> Signal:
    rng = np.random.default_rng(seed)
    x = np.zeros(length, dtype=float)
    for t in range(1, length):
        x[t] = (
            x[t - 1]
            + theta * (0.0 - x[t - 1]) * dt
            + sigma * np.sqrt(dt) * rng.normal()
        )
    return Signal(_standardize_signal(x), dt)


def generate_iaaft(
    base_signal: np.ndarray, seed: int, max_iter: int = 100
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.asarray(base_signal, dtype=float)
    x_sorted = np.sort(x)
    amplitudes = np.abs(np.fft.rfft(x))
    y = rng.permutation(x)
    for _ in range(max_iter):
        y_fft = np.fft.rfft(y)
        y = np.fft.irfft(amplitudes * np.exp(1j * np.angle(y_fft)), n=len(x))
        ranks = np.argsort(np.argsort(y))
        y_next = x_sorted[ranks]
        if np.array_equal(y, y_next):
            break
        y = y_next
    return _standardize_signal(y)


def generate_fourier_surrogate(base_signal: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.asarray(base_signal, dtype=float)
    xf = np.fft.rfft(x)
    phases = rng.uniform(-np.pi, np.pi, len(xf))
    phases[0] = 0.0
    if len(x) % 2 == 0:
        phases[-1] = 0.0
    y = np.fft.irfft(np.abs(xf) * np.exp(1j * phases), n=len(x))
    return _standardize_signal(y)


def generate_block_bootstrap(
    base_signal: np.ndarray, seed: int, block_size: int = 400
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.asarray(base_signal, dtype=float)
    n_blocks = int(np.ceil(len(x) / block_size))
    starts = rng.integers(0, max(1, len(x) - block_size + 1), size=n_blocks)
    blocks = [x[start : start + block_size] for start in starts]
    y = np.concatenate(blocks)[: len(x)]
    return _standardize_signal(y)


def simulate_null(model: str, seed: int, length: int) -> Signal:
    if model == "ar1":
        return generate_ar1(length, seed)
    if model == "ou":
        return generate_ou(length, seed)

    base = simulate_physical("lorenz", noise=0.0, seed=seed).values[:length]
    if model == "iaaft":
        return Signal(generate_iaaft(base, seed), 1.0)
    if model == "fourier_surrogate":
        return Signal(generate_fourier_surrogate(base, seed), 1.0)
    if model == "block_bootstrap":
        return Signal(generate_block_bootstrap(base, seed), 1.0)
    raise ValueError(f"Unknown null model: {model}")


def extract_v3(
    signal: Signal, standardize_before_embedding: bool = False
) -> np.ndarray:
    x = (
        _standardize_signal(signal.values)
        if standardize_before_embedding
        else np.asarray(signal.values, dtype=float)
    )
    stride = max(1, int(WINDOW_SIZE * (1.0 - WINDOW_OVERLAP)))
    rows = []
    for start in range(0, len(x) - WINDOW_SIZE + 1, stride):
        emb = compute_embedding_vector(x[start : start + WINDOW_SIZE], signal.dt)
        rows.append([_finite_float(emb[key]) for key in V3_KEYS])
    if not rows:
        raise RuntimeError("No V3 windows extracted")
    arr = np.asarray(rows, dtype=float)
    mask = np.all(np.isfinite(arr), axis=1)
    if not np.any(mask):
        raise RuntimeError("All V3 windows contained non-finite values")
    return arr[mask]


def build_physical_dataset(
    noise: float = 0.0, standardize_before_embedding: bool = False
) -> dict[str, np.ndarray]:
    dataset = {}
    for system in PHYSICAL_SYSTEMS:
        system_rows = []
        for seed in DATASET_SEEDS:
            signal = simulate_physical(system, noise=noise, seed=seed)
            system_rows.append(extract_v3(signal, standardize_before_embedding))
        dataset[system] = np.vstack(system_rows)
        print(
            f"  physical {system:<13} noise={noise:.2f}: {len(dataset[system])} V3 windows"
        )
    return dataset


def build_null_dataset(
    seeds: list[int], standardize_before_embedding: bool = False
) -> dict[str, np.ndarray]:
    dataset = {}
    length = 18000
    for model in NULL_MODELS:
        model_rows = []
        for seed in seeds:
            signal = simulate_null(model, seed=seed, length=length)
            model_rows.append(extract_v3(signal, standardize_before_embedding))
        dataset[model] = np.vstack(model_rows)
        print(f"  null     {model:<13}: {len(dataset[model])} V3 windows")
    return dataset


def stack_nulls(null_dataset: dict[str, np.ndarray]) -> np.ndarray:
    return np.vstack([null_dataset[name] for name in NULL_MODELS])


def evaluate_loso(
    physical_dataset: dict[str, np.ndarray],
    train_nulls: np.ndarray,
    test_nulls: np.ndarray,
) -> dict:
    folds = {}
    auc_values = []
    for excluded in PHYSICAL_SYSTEMS:
        x_train_phys = np.vstack(
            [physical_dataset[name] for name in PHYSICAL_SYSTEMS if name != excluded]
        )
        x_train = np.vstack([x_train_phys, train_nulls])
        y_train = np.concatenate(
            [
                np.ones(len(x_train_phys), dtype=int),
                np.zeros(len(train_nulls), dtype=int),
            ]
        )

        x_test_phys = physical_dataset[excluded]
        x_test = np.vstack([x_test_phys, test_nulls])
        y_test = np.concatenate(
            [np.ones(len(x_test_phys), dtype=int), np.zeros(len(test_nulls), dtype=int)]
        )

        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)

        clf = RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=1,
            class_weight="balanced_subsample",
        )
        clf.fit(x_train_scaled, y_train)
        prob = clf.predict_proba(x_test_scaled)[:, 1]
        pred = (prob >= 0.5).astype(int)

        auc_val = float(roc_auc_score(y_test, prob))
        precision = float(precision_score(y_test, pred, zero_division=0))
        recall = float(recall_score(y_test, pred, zero_division=0))
        f1 = float(f1_score(y_test, pred, zero_division=0))
        cm = confusion_matrix(y_test, pred, labels=[0, 1])
        passed = auc_val > TEST1_AUC_MIN
        auc_values.append(auc_val)

        folds[excluded] = {
            "status": "PASSED" if passed else "FAILED",
            "criterion": f"AUC > {TEST1_AUC_MIN}",
            "roc_auc": auc_val,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "confusion_matrix": cm.tolist(),
            "n_train_physical": int(len(x_train_phys)),
            "n_train_null": int(len(train_nulls)),
            "n_test_physical": int(len(x_test_phys)),
            "n_test_null": int(len(test_nulls)),
            "delta_to_criterion": float(auc_val - TEST1_AUC_MIN),
        }
        marker = "PASS" if passed else "FAIL"
        print(
            f"  {excluded:<13} AUC={auc_val:.6f} precision={precision:.6f} "
            f"recall={recall:.6f} f1={f1:.6f} [{marker}]"
        )

    return {
        "status": (
            "PASSED"
            if all(fold["status"] == "PASSED" for fold in folds.values())
            else "FAILED"
        ),
        "criterion": f"AUC > {TEST1_AUC_MIN} for all folds",
        "mean_auc": float(np.mean(auc_values)),
        "min_auc": float(np.min(auc_values)),
        "folds": folds,
    }


def compute_distance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    x = np.atleast_2d(np.asarray(x, dtype=float))
    y = np.atleast_2d(np.asarray(y, dtype=float))
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    a = squareform(pdist(x))
    b = squareform(pdist(y))
    a_centered = (
        a - a.mean(axis=0, keepdims=True) - a.mean(axis=1, keepdims=True) + a.mean()
    )
    b_centered = (
        b - b.mean(axis=0, keepdims=True) - b.mean(axis=1, keepdims=True) + b.mean()
    )
    dcov2 = np.maximum(0.0, np.mean(a_centered * b_centered))
    dvarx2 = np.maximum(0.0, np.mean(a_centered * a_centered))
    dvary2 = np.maximum(0.0, np.mean(b_centered * b_centered))
    denom = np.sqrt(dvarx2 * dvary2)
    if denom <= 1e-12:
        return 0.0
    return float(np.sqrt(dcov2 / denom))


def run_test1(
    physical_dataset: dict[str, np.ndarray],
    train_nulls: np.ndarray,
    test_nulls: np.ndarray,
) -> dict:
    print("\nTEST 1 - LEAVE-ONE-SYSTEM-OUT GENERALIZATION")
    result = evaluate_loso(physical_dataset, train_nulls, test_nulls)
    if result["status"] == "FAILED":
        for system, fold in result["folds"].items():
            if fold["status"] == "FAILED":
                print(
                    f"  FAIL VALUE: {system} AUC={fold['roc_auc']:.6f}; "
                    f"criterion>{TEST1_AUC_MIN}; delta={fold['delta_to_criterion']:.6f}"
                )
    return result


def run_test2(physical_dataset: dict[str, np.ndarray]) -> dict:
    print("\nTEST 2 - LATENT MANIFOLD COHERENCE")
    x = np.vstack([physical_dataset[name] for name in PHYSICAL_SYSTEMS])
    labels = np.concatenate(
        [
            np.full(len(physical_dataset[name]), idx, dtype=int)
            for idx, name in enumerate(PHYSICAL_SYSTEMS)
        ]
    )

    scaled = StandardScaler().fit_transform(x)
    n_pca = min(5, scaled.shape[1], scaled.shape[0] - 1)
    pca = PCA(n_components=n_pca, random_state=42)
    x_pca = pca.fit_transform(scaled)

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=20,
        min_dist=0.05,
        metric="euclidean",
        random_state=42,
        n_epochs=500,
    )
    x_umap = reducer.fit_transform(x_pca)

    sil = float(silhouette_score(x_umap, labels))
    trust = float(trustworthiness(x_pca, x_umap, n_neighbors=15))
    dcor = compute_distance_correlation(x_pca, x_umap)

    criteria = {
        "silhouette": {
            "value": sil,
            "threshold": TEST2_SILHOUETTE_MIN,
            "delta": sil - TEST2_SILHOUETTE_MIN,
            "passed": bool(sil > TEST2_SILHOUETTE_MIN),
        },
        "trustworthiness": {
            "value": trust,
            "threshold": TEST2_TRUSTWORTHINESS_MIN,
            "delta": trust - TEST2_TRUSTWORTHINESS_MIN,
            "passed": bool(trust > TEST2_TRUSTWORTHINESS_MIN),
        },
        "distance_correlation": {
            "value": dcor,
            "threshold": TEST2_DISTANCE_CORRELATION_MIN,
            "delta": dcor - TEST2_DISTANCE_CORRELATION_MIN,
            "passed": bool(dcor > TEST2_DISTANCE_CORRELATION_MIN),
        },
    }
    passed = all(item["passed"] for item in criteria.values())

    print(
        f"  Silhouette={sil:.6f} criterion>{TEST2_SILHOUETTE_MIN} delta={sil - TEST2_SILHOUETTE_MIN:.6f}"
    )
    print(
        f"  Trustworthiness={trust:.6f} criterion>{TEST2_TRUSTWORTHINESS_MIN} delta={trust - TEST2_TRUSTWORTHINESS_MIN:.6f}"
    )
    print(
        f"  Distance Correlation={dcor:.6f} criterion>{TEST2_DISTANCE_CORRELATION_MIN} delta={dcor - TEST2_DISTANCE_CORRELATION_MIN:.6f}"
    )

    for name, item in criteria.items():
        if not item["passed"]:
            print(
                f"  FAIL VALUE: {name}={item['value']:.6f}; "
                f"criterion>{item['threshold']}; delta={item['delta']:.6f}"
            )

    return {
        "status": "PASSED" if passed else "FAILED",
        "pipeline": "V3 -> StandardScaler -> PCA -> UMAP",
        "n_samples": int(len(x)),
        "n_features": int(x.shape[1]),
        "pca_components": int(n_pca),
        "pca_explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "criteria": criteria,
    }


def run_test3(
    baseline_result: dict,
    train_nulls_standardized: np.ndarray,
    test_nulls_standardized: np.ndarray,
) -> dict:
    print("\nTEST 3 - HIDDEN LEAKAGE AUDIT")
    standardized_physical = build_physical_dataset(
        noise=0.0, standardize_before_embedding=True
    )
    standardized_result = evaluate_loso(
        standardized_physical, train_nulls_standardized, test_nulls_standardized
    )

    folds = {}
    deltas = []
    for system in PHYSICAL_SYSTEMS:
        baseline_auc = float(baseline_result["folds"][system]["roc_auc"])
        standardized_auc = float(standardized_result["folds"][system]["roc_auc"])
        delta_auc = standardized_auc - baseline_auc
        abs_delta = abs(delta_auc)
        passed = abs_delta < TEST3_DELTA_AUC_MAX
        deltas.append(abs_delta)
        folds[system] = {
            "status": "PASSED" if passed else "FAILED",
            "baseline_auc": baseline_auc,
            "standardized_before_v3_auc": standardized_auc,
            "delta_auc": float(delta_auc),
            "abs_delta_auc": float(abs_delta),
            "criterion": f"|delta_auc| < {TEST3_DELTA_AUC_MAX}",
            "delta_to_criterion": float(TEST3_DELTA_AUC_MAX - abs_delta),
        }
        marker = "PASS" if passed else "FAIL"
        print(
            f"  {system:<13} baseline_auc={baseline_auc:.6f} standardized_auc={standardized_auc:.6f} "
            f"delta_auc={delta_auc:.6f} abs_delta={abs_delta:.6f} [{marker}]"
        )
        if not passed:
            print(
                f"  FAIL VALUE: {system} |delta_auc|={abs_delta:.6f}; "
                f"criterion<{TEST3_DELTA_AUC_MAX}; margin={TEST3_DELTA_AUC_MAX - abs_delta:.6f}"
            )

    return {
        "status": (
            "PASSED"
            if all(fold["status"] == "PASSED" for fold in folds.values())
            else "FAILED"
        ),
        "criterion": f"|delta_auc| < {TEST3_DELTA_AUC_MAX} for all folds",
        "max_abs_delta_auc": float(np.max(deltas)),
        "folds": folds,
    }


def run_test4(train_nulls: np.ndarray, test_nulls: np.ndarray) -> dict:
    print("\nTEST 4 - PERTURBATION ROBUSTNESS")
    by_noise = {}
    mean_aucs = []
    for noise in TEST4_NOISE_LEVELS:
        print(f"  Evaluating perturbation noise={noise:.2%}")
        physical_dataset = build_physical_dataset(
            noise=noise, standardize_before_embedding=False
        )
        result = evaluate_loso(physical_dataset, train_nulls, test_nulls)
        by_noise[f"{noise:.2f}"] = {
            "status": result["status"],
            "mean_auc": result["mean_auc"],
            "min_auc": result["min_auc"],
            "fold_auc": {
                name: fold["roc_auc"] for name, fold in result["folds"].items()
            },
        }
        mean_aucs.append(float(result["mean_auc"]))

    jumps = []
    for prev, curr, prev_noise, curr_noise in zip(
        mean_aucs[:-1], mean_aucs[1:], TEST4_NOISE_LEVELS[:-1], TEST4_NOISE_LEVELS[1:]
    ):
        jump = abs(curr - prev) / max(abs(prev), 1e-12)
        jumps.append(
            {
                "from_noise": prev_noise,
                "to_noise": curr_noise,
                "from_mean_auc": prev,
                "to_mean_auc": curr,
                "relative_jump": float(jump),
                "passed": bool(jump <= TEST4_MAX_JUMP),
                "delta_to_criterion": float(TEST4_MAX_JUMP - jump),
            }
        )
        marker = "PASS" if jump <= TEST4_MAX_JUMP else "FAIL"
        print(
            f"  jump {prev_noise:.2%}->{curr_noise:.2%}: {jump:.6f}; "
            f"criterion<={TEST4_MAX_JUMP} [{marker}]"
        )
        if jump > TEST4_MAX_JUMP:
            print(
                f"  FAIL VALUE: relative_jump={jump:.6f}; "
                f"criterion<={TEST4_MAX_JUMP}; margin={TEST4_MAX_JUMP - jump:.6f}"
            )

    passed = all(jump["passed"] for jump in jumps)
    return {
        "status": "PASSED" if passed else "FAILED",
        "criterion": f"no consecutive mean AUC jump > {TEST4_MAX_JUMP}",
        "noise_levels": TEST4_NOISE_LEVELS,
        "by_noise": by_noise,
        "jumps": jumps,
        "max_relative_jump": float(
            max([j["relative_jump"] for j in jumps], default=0.0)
        ),
    }


def run_test5() -> dict:
    print("\nTEST 5 - TEMPORAL CAUSALITY SANITY CHECK")
    per_system = {}
    distances = []
    for system in PHYSICAL_SYSTEMS:
        original_rows = []
        shuffled_rows = []
        for seed in DATASET_SEEDS:
            signal = simulate_physical(system, noise=0.0, seed=seed)
            original = extract_v3(signal, standardize_before_embedding=False)

            rng = np.random.default_rng(seed + 100000)
            shuffled_values = np.asarray(signal.values, dtype=float).copy()
            rng.shuffle(shuffled_values)
            shuffled = extract_v3(
                Signal(shuffled_values, signal.dt), standardize_before_embedding=False
            )

            n = min(len(original), len(shuffled))
            original_rows.append(original[:n])
            shuffled_rows.append(shuffled[:n])

        original_all = np.vstack(original_rows)
        shuffled_all = np.vstack(shuffled_rows)
        scaler = StandardScaler()
        combined = scaler.fit_transform(np.vstack([original_all, shuffled_all]))
        original_scaled = combined[: len(original_all)]
        shuffled_scaled = combined[len(original_all) :]
        original_mean = np.mean(original_scaled, axis=0)
        shuffled_mean = np.mean(shuffled_scaled, axis=0)
        distance = float(
            np.linalg.norm(original_mean - shuffled_mean) / np.sqrt(len(V3_KEYS))
        )
        passed = distance > TEST5_DISTANCE_MIN
        distances.append(distance)
        per_system[system] = {
            "status": "PASSED" if passed else "FAILED",
            "distance": distance,
            "criterion": f"distance > {TEST5_DISTANCE_MIN}",
            "delta_to_criterion": float(distance - TEST5_DISTANCE_MIN),
            "n_original_windows": int(len(original_all)),
            "n_shuffled_windows": int(len(shuffled_all)),
        }
        marker = "PASS" if passed else "FAIL"
        print(
            f"  {system:<13} distance={distance:.6f}; "
            f"criterion>{TEST5_DISTANCE_MIN} delta={distance - TEST5_DISTANCE_MIN:.6f} [{marker}]"
        )
        if not passed:
            print(
                f"  FAIL VALUE: {system} distance={distance:.6f}; "
                f"criterion>{TEST5_DISTANCE_MIN}; delta={distance - TEST5_DISTANCE_MIN:.6f}"
            )

    return {
        "status": (
            "PASSED"
            if all(item["status"] == "PASSED" for item in per_system.values())
            else "FAILED"
        ),
        "criterion": f"distance > {TEST5_DISTANCE_MIN} for all physical systems",
        "min_distance": float(np.min(distances)),
        "per_system": per_system,
    }


def write_report(report: dict) -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=_json_default)
        f.write("\n")


def main() -> int:
    started = time.time()
    print("=" * 72)
    print("PHASE 4.8 - CROSS-SYSTEM GENERALIZATION TESTS")
    print("=" * 72)
    print(f"Report target: {REPORT_FILE}")
    print(f"Physical systems: {', '.join(PHYSICAL_SYSTEMS)}")
    print(f"Null models: {', '.join(NULL_MODELS)}")
    print(f"Seeds: {DATASET_SEEDS}; held-out null seeds: {HELD_OUT_NULL_SEEDS}")

    report = {
        "metadata": {
            "phase": "4.8",
            "embedding_version": "V3",
            "generated_at_unix": started,
            "physical_systems": PHYSICAL_SYSTEMS,
            "null_models": NULL_MODELS,
            "dataset_seeds": DATASET_SEEDS,
            "held_out_null_seeds": HELD_OUT_NULL_SEEDS,
            "window_size": WINDOW_SIZE,
            "window_overlap": WINDOW_OVERLAP,
            "criteria": {
                "test1_auc_min": TEST1_AUC_MIN,
                "test2_silhouette_min": TEST2_SILHOUETTE_MIN,
                "test2_trustworthiness_min": TEST2_TRUSTWORTHINESS_MIN,
                "test2_distance_correlation_min": TEST2_DISTANCE_CORRELATION_MIN,
                "test3_abs_delta_auc_max": TEST3_DELTA_AUC_MAX,
                "test4_max_consecutive_relative_jump": TEST4_MAX_JUMP,
                "test5_distance_min": TEST5_DISTANCE_MIN,
            },
        },
        "tests": {},
    }

    try:
        print("\n[DATA] Building baseline physical dataset")
        physical_dataset = build_physical_dataset(
            noise=0.0, standardize_before_embedding=False
        )
        print("\n[DATA] Building train null dataset")
        train_null_dataset = build_null_dataset(
            DATASET_SEEDS, standardize_before_embedding=False
        )
        print("\n[DATA] Building held-out null dataset")
        test_null_dataset = build_null_dataset(
            HELD_OUT_NULL_SEEDS, standardize_before_embedding=False
        )

        train_nulls = stack_nulls(train_null_dataset)
        test_nulls = stack_nulls(test_null_dataset)

        report["tests"]["test1_leave_one_system_out_generalization"] = run_test1(
            physical_dataset, train_nulls, test_nulls
        )
        report["tests"]["test2_latent_manifold_coherence"] = run_test2(physical_dataset)

        print("\n[DATA] Building standardized train null dataset for leakage audit")
        train_nulls_standardized = stack_nulls(
            build_null_dataset(DATASET_SEEDS, standardize_before_embedding=True)
        )
        print("\n[DATA] Building standardized held-out null dataset for leakage audit")
        test_nulls_standardized = stack_nulls(
            build_null_dataset(HELD_OUT_NULL_SEEDS, standardize_before_embedding=True)
        )
        report["tests"]["test3_hidden_leakage_audit"] = run_test3(
            report["tests"]["test1_leave_one_system_out_generalization"],
            train_nulls_standardized,
            test_nulls_standardized,
        )
        report["tests"]["test4_perturbation_robustness"] = run_test4(
            train_nulls, test_nulls
        )
        report["tests"]["test5_temporal_causality_sanity_check"] = run_test5()

        failed = [
            name
            for name, result in report["tests"].items()
            if result.get("status") != "PASSED"
        ]
        report["metadata"]["runtime_seconds"] = float(time.time() - started)
        report["metadata"]["global_status"] = "PASSED" if not failed else "FAILED"
        report["metadata"]["failed_tests"] = failed
        write_report(report)

        print("\n" + "=" * 72)
        print(f"JSON saved: {REPORT_FILE}")
        if failed:
            print("PHASE 4.8 FAILED")
            print("Failed tests:")
            for name in failed:
                print(f"  - {name}")
            return 1

        print("PHASE 4.8 PASSED")
        return 0

    except Exception:
        tb = traceback.format_exc()
        print("\n[ERROR] Phase 4.8 raised an exception:")
        print(tb)
        report["metadata"]["runtime_seconds"] = float(time.time() - started)
        report["metadata"]["global_status"] = "ERROR"
        report["metadata"]["traceback"] = tb
        write_report(report)
        print(f"JSON saved after exception: {REPORT_FILE}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
