import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import spearmanr


def generate_noisy_signals(signal, snr_levels=[30, 20, 15, 10, 5, 0, -5]):
    """
    Injects additive white Gaussian noise to match a target SNR (in dB).
    """
    x = np.asarray(signal, dtype=float)
    p_signal = np.mean(x**2)
    if p_signal < 1e-12:
        p_signal = 1e-12

    noisy_dict = {}
    for snr in snr_levels:
        p_noise = p_signal / (10.0 ** (snr / 10.0))
        sigma_noise = np.sqrt(p_noise)

        np.random.seed(42)
        noise = np.random.normal(0, sigma_noise, len(x))
        noisy_dict[snr] = x + noise
    return noisy_dict


def linear_cka(X, Y):
    """
    Linear Centered Kernel Alignment (CKA) - Dual formulation for efficiency.
    """
    X_c = X - np.mean(X, axis=0)
    Y_c = Y - np.mean(Y, axis=0)

    num = np.linalg.norm(X_c.T @ Y_c, "fro") ** 2
    den_x = np.linalg.norm(X_c.T @ X_c, "fro")
    den_y = np.linalg.norm(Y_c.T @ Y_c, "fro")

    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0
    return num / (den_x * den_y)


def compute_cka_degradation(X_clean, X_noisy_dict):
    """
    Computes CKA degradation across SNR levels for both original and extended features.
    """
    from core.autonomous.latent_snapshot_exporter import extract_ev3_features

    # Extract clean features
    X_clean_orig = np.nan_to_num(
        np.array([extract_ev3_features(x, extended=False) for x in X_clean]), nan=0.0
    )
    X_clean_ext = np.nan_to_num(
        np.array([extract_ev3_features(x, extended=True) for x in X_clean]), nan=0.0
    )

    records = []
    # Identify SNR levels
    snrs = list(X_noisy_dict.keys())
    for snr in snrs:
        noisy_signals = X_noisy_dict[snr]
        X_noisy_orig = np.nan_to_num(
            np.array([extract_ev3_features(x, extended=False) for x in noisy_signals]),
            nan=0.0,
        )
        X_noisy_ext = np.nan_to_num(
            np.array([extract_ev3_features(x, extended=True) for x in noisy_signals]),
            nan=0.0,
        )

        cka_orig = linear_cka(X_clean_orig, X_noisy_orig)
        cka_ext = linear_cka(X_clean_ext, X_noisy_ext)

        records.append({"snr": snr, "cka_original": cka_orig, "cka_extended": cka_ext})

    return pd.DataFrame(records)


def compute_shap_stability(
    model, X_clean_features, X_noisy_features_dict, feature_names
):
    """
    Computes Spearman rank correlation of feature importances between clean and noisy datasets.
    """
    # Baseline ranking
    try:
        import shap

        explainer = shap.TreeExplainer(model)
        shap_clean = explainer.shap_values(X_clean_features)
        if isinstance(shap_clean, list):
            shap_clean_imp = np.mean(
                [np.mean(np.abs(s), axis=0) for s in shap_clean], axis=0
            )
        else:
            shap_clean_imp = np.mean(np.abs(shap_clean), axis=0)
    except Exception:
        # Fallback to model's Gini importances
        shap_clean_imp = model.feature_importances_

    records = []
    for snr, X_noisy_feat in X_noisy_features_dict.items():
        try:
            import shap

            explainer = shap.TreeExplainer(model)
            shap_noisy = explainer.shap_values(X_noisy_feat)
            if isinstance(shap_noisy, list):
                shap_noisy_imp = np.mean(
                    [np.mean(np.abs(s), axis=0) for s in shap_noisy], axis=0
                )
            else:
                shap_noisy_imp = np.mean(np.abs(shap_noisy), axis=0)
        except Exception:
            # Fallback to retrained model Gini importances
            try:
                model_noisy = RandomForestClassifier(n_estimators=100, random_state=42)
                model_noisy.fit(X_noisy_feat, np.ones(len(X_noisy_feat)))
                shap_noisy_imp = model_noisy.feature_importances_
            except Exception:
                shap_noisy_imp = shap_clean_imp

        r_val, _ = spearmanr(shap_clean_imp, shap_noisy_imp)
        if not np.isfinite(r_val):
            r_val = 0.0
        records.append({"snr": snr, "spearman_r": float(r_val)})

    return pd.DataFrame(records)


def run_full_robustness_study(signal_generator_func, n_signals=50):
    """
    Runs a systematic degradation study on a population of generated signals.
    """
    print(f"Running robustness audit on {n_signals} signals...")
    X_clean, y_clean = signal_generator_func(n_signals)

    from core.autonomous.latent_snapshot_exporter import extract_ev3_features

    # Extract clean features
    X_clean_orig = []
    X_clean_ext = []
    for sig in X_clean:
        X_clean_orig.append(extract_ev3_features(sig, extended=False))
        X_clean_ext.append(extract_ev3_features(sig, extended=True))

    X_clean_orig = np.nan_to_num(np.array(X_clean_orig), nan=0.0)
    X_clean_ext = np.nan_to_num(np.array(X_clean_ext), nan=0.0)

    snr_levels = [30, 20, 15, 10, 5, 0, -5]
    X_noisy_orig_dict = {snr: [] for snr in snr_levels}
    X_noisy_ext_dict = {snr: [] for snr in snr_levels}

    # Populate noisy features
    for sig in X_clean:
        noisy_signals = generate_noisy_signals(sig, snr_levels=snr_levels)
        for snr, n_sig in noisy_signals.items():
            X_noisy_orig_dict[snr].append(extract_ev3_features(n_sig, extended=False))
            X_noisy_ext_dict[snr].append(extract_ev3_features(n_sig, extended=True))

    for snr in snr_levels:
        X_noisy_orig_dict[snr] = np.nan_to_num(
            np.array(X_noisy_orig_dict[snr]), nan=0.0
        )
        X_noisy_ext_dict[snr] = np.nan_to_num(np.array(X_noisy_ext_dict[snr]), nan=0.0)

    # Compute CKA similarity
    cka_results = []
    for snr in snr_levels:
        cka_orig = linear_cka(X_clean_orig, X_noisy_orig_dict[snr])
        cka_ext = linear_cka(X_clean_ext, X_noisy_ext_dict[snr])
        cka_results.append(
            {"snr": snr, "cka_original": cka_orig, "cka_extended": cka_ext}
        )

    # Random Forest models
    y_clean_numeric = np.array(y_clean, dtype=int)
    # Binary class mapping to avoid negative class label issues in standard RF models
    y_clean_numeric = np.where(y_clean_numeric <= 0, 0, 1)

    model_orig = RandomForestClassifier(n_estimators=100, random_state=42)
    model_orig.fit(X_clean_orig, y_clean_numeric)

    model_ext = RandomForestClassifier(n_estimators=100, random_state=42)
    model_ext.fit(X_clean_ext, y_clean_numeric)

    # SHAP Rankings stability
    orig_names = [f"orig_{i}" for i in range(8)]
    ext_names = [f"ext_{i}" for i in range(15)]

    df_shap_orig = compute_shap_stability(
        model_orig, X_clean_orig, X_noisy_orig_dict, orig_names
    )
    df_shap_ext = compute_shap_stability(
        model_ext, X_clean_ext, X_noisy_ext_dict, ext_names
    )

    results = []
    for i, snr in enumerate(snr_levels):
        r_orig = df_shap_orig.loc[df_shap_orig["snr"] == snr, "spearman_r"].values[0]
        r_ext = df_shap_ext.loc[df_shap_ext["snr"] == snr, "spearman_r"].values[0]

        results.append(
            {
                "snr": snr,
                "cka_original": cka_results[i]["cka_original"],
                "cka_extended": cka_results[i]["cka_extended"],
                "shap_stability_original": r_orig,
                "shap_stability_extended": r_ext,
            }
        )

    return pd.DataFrame(results)


def plot_degradation_curves(
    results_df, output_path="figures/robustness_degradation.pdf"
):
    """
    Plots the degradation curves of CKA and SHAP feature importance stability.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    snrs = results_df["snr"].values

    # Panel A: CKA
    ax1.plot(
        snrs,
        results_df["cka_original"],
        "o-",
        color="#3b82f6",
        label="EV3 Original (8D)",
        linewidth=2.5,
        markersize=7,
    )
    ax1.plot(
        snrs,
        results_df["cka_extended"],
        "s-",
        color="#8b5cf6",
        label="EV3 Extended (15D)",
        linewidth=2.5,
        markersize=7,
    )
    ax1.set_xlabel("SNR (dB)", fontsize=12)
    ax1.set_ylabel("Centered Kernel Alignment (CKA)", fontsize=12)
    ax1.set_title(
        "(a) Latent Space Alignment Degradation", fontsize=13, fontweight="bold", pad=12
    )
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(fontsize=10, loc="lower right")

    # Panel B: Spearman
    ax2.plot(
        snrs,
        results_df["shap_stability_original"],
        "o-",
        color="#10b981",
        label="EV3 Original (8D)",
        linewidth=2.5,
        markersize=7,
    )
    ax2.plot(
        snrs,
        results_df["shap_stability_extended"],
        "s-",
        color="#ec4899",
        label="EV3 Extended (15D)",
        linewidth=2.5,
        markersize=7,
    )
    ax2.set_xlabel("SNR (dB)", fontsize=12)
    ax2.set_ylabel("Spearman Rank Correlation", fontsize=12)
    ax2.set_title(
        "(b) SHAP Feature Importance Stability", fontsize=13, fontweight="bold", pad=12
    )
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(fontsize=10, loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✅ Successfully saved paper-ready degradation curve to {output_path}")


def export_robustness_results(
    results_df, output_path="artifacts/robustness_results.json"
):
    """
    Exports the robustness results into a standard JSON file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = results_df.to_dict(orient="records")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Exported robustness study data to {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 RUNNING SYSTEMATIC ROBUSTNESS AUDIT (GAUSSIAN NOISE DEGRADATION)")
    print("=" * 60)

    from ucr_loader import load_ucr_dataset

    def dataset_generator(n_signals=50):
        # We load the representative UCR ECG200 dataset
        data = load_ucr_dataset("ECG200")
        X = data["X_train"]
        y = data["y_train"]

        # Subsample or repeat
        np.random.seed(42)
        if len(X) < n_signals:
            indices = np.random.choice(len(X), size=n_signals, replace=True)
        else:
            indices = np.random.choice(len(X), size=n_signals, replace=False)
        return X[indices], y[indices]

    df_results = run_full_robustness_study(dataset_generator, n_signals=20)

    # Output visualizations and JSON data
    plot_degradation_curves(
        df_results, output_path="figures/robustness_degradation.pdf"
    )
    export_robustness_results(
        df_results, output_path="artifacts/robustness_results.json"
    )
    print("=" * 60)
