import sys
import os
import numpy as np
import pandas as pd

# Ensure root path is imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    print("=" * 70)
    print("[TEST] RUNNING COMPREHENSIVE PHASE 1 INTEGRATION TEST")
    print("=" * 70)

    # 1. Imports
    print("[TEST 1/5] Importing newly developed modules...")
    try:
        from core.autonomous.latent_snapshot_exporter import (
            extract_ev3_features,
            compute_lyapunov_exponent,
            compute_correlation_dimension,
            compute_rqa,
            compute_multiscale_entropy,
        )
        import ucr_loader
        import robustness_audit

        print("  Import successful!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)

    # 2. Load ECG200 Dataset
    print("\n[TEST 2/5] Loading UCR ECG200 dataset...")
    try:
        dataset_info = ucr_loader.load_ucr_dataset("ECG200")
        X_train = dataset_info["X_train"]
        y_train = dataset_info["y_train"]
        print(f"  ECG200 loaded successfully. Train shape: {X_train.shape}")
        assert len(X_train) > 0, "No training samples loaded."
    except Exception as e:
        print(f"[ERROR] Failed loading dataset: {e}")
        sys.exit(1)

    # 3. Feature Extraction
    print(
        "\n[TEST 3/5] Extracting EV3 (8D) and EV3_EXTENDED (15D) from the first 20 signals..."
    )
    try:
        X_clean_subset = X_train[:20]

        orig_features = []
        ext_features = []

        for sig in X_clean_subset:
            orig_features.append(extract_ev3_features(sig, extended=False))
            ext_features.append(extract_ev3_features(sig, extended=True))

        orig_features = np.array(orig_features)
        ext_features = np.array(ext_features)

        print(f"  EV3 Original shape: {orig_features.shape} (Expected: (20, 8))")
        print(f"  EV3 Extended shape: {ext_features.shape} (Expected: (20, 15))")

        assert orig_features.shape == (
            20,
            8,
        ), f"Incorrect original shape: {orig_features.shape}"
        assert ext_features.shape == (
            20,
            15,
        ), f"Incorrect extended shape: {ext_features.shape}"

        # 4. Check for excessive NaNs
        nan_fraction_orig = np.isnan(orig_features).mean()
        nan_fraction_ext = np.isnan(ext_features).mean()

        print(f"  NaN Fraction - Original: {nan_fraction_orig * 100:.2f}%")
        print(f"  NaN Fraction - Extended: {nan_fraction_ext * 100:.2f}%")

        assert (
            nan_fraction_orig <= 0.5
        ), f"Excessive NaNs in original space: {nan_fraction_orig * 100:.2f}%"
        assert (
            nan_fraction_ext <= 0.5
        ), f"Excessive NaNs in extended space: {nan_fraction_ext * 100:.2f}%"
        print("  NaN checks passed!")
    except Exception as e:
        print(f"[ERROR] Feature extraction failed: {e}")
        sys.exit(1)

    # 5. CKA Degradation
    print("\n[TEST 5/5] Running CKA degradation computation...")
    try:
        snr_levels = [30, 20, 15, 10, 5, 0, -5]
        X_noisy_dict = {snr: [] for snr in snr_levels}

        for sig in X_clean_subset:
            noisy_sigs = robustness_audit.generate_noisy_signals(sig, snr_levels)
            for snr, n_sig in noisy_sigs.items():
                X_noisy_dict[snr].append(n_sig)

        df_cka = robustness_audit.compute_cka_degradation(X_clean_subset, X_noisy_dict)
        print("  CKA degradation results:")
        print(df_cka.to_string(index=False))

        assert isinstance(df_cka, pd.DataFrame), "Result must be a pandas DataFrame."
        assert len(df_cka) == len(
            snr_levels
        ), f"DataFrame must have {len(snr_levels)} rows (one per SNR level)."
        assert (
            "cka_original" in df_cka.columns
        ), "DataFrame must contain 'cka_original'."
        assert (
            "cka_extended" in df_cka.columns
        ), "DataFrame must contain 'cka_extended'."

        print("  CKA degradation test passed successfully!")
    except Exception as e:
        print(f"[ERROR] CKA degradation calculation failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("SUCCESS: Fase 1 integrada correctamente")
    print("=" * 70)


if __name__ == "__main__":
    main()
