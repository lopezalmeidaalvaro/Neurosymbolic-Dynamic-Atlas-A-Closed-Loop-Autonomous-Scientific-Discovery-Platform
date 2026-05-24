import os
import sys
import json
import time
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# Import the baseline components
from baseline_deep_ecg import ResNet18_1D, load_raw_ecg_segments, TEST_RECORDS

# Import CKA and EV3 builders from continuity audit
from core.empirical.causal_continuity_audit import (
    build_domain_a_synthetic,
    build_domain_b_composite,
    build_domain_c_clinical,
    compute_linear_cka,
    simulate_lorenz,
    simulate_duffing,
    generate_biophysical_window,
)

# Paths
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "resnet1d_ecg.pt")
REPORT_FILE = os.path.join(ARTIFACTS_DIR, "deep_cka_comparison.json")

# ─────────────────────────────────────────────────────────────────────────────
# 1. RAW DOMAIN BUILDERS FOR 1D SEGMENTS (360 SAMPLES)
# ─────────────────────────────────────────────────────────────────────────────


def build_raw_domain_a(n_windows=500):
    print("  Generating Domain A (Synthetic Lorenz/Duffing) raw 1D waveforms...")
    sig_lorenz = simulate_lorenz()
    sig_duffing = simulate_duffing()
    X = []

    # Lorenz
    start = 5000
    for _ in range(n_windows):
        win = sig_lorenz[start : start + 360]
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        X.append(win_std)
        start += 200

    # Duffing
    start = 5000
    for _ in range(n_windows):
        win = sig_duffing[start : start + 360]
        win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)
        X.append(win_std)
        start += 200

    return np.array(X)


def build_raw_domain_b(n_windows=500):
    print("  Generating Domain B (Composite Biophysical) raw 1D waveforms...")
    X = []

    # Normal
    for s in range(n_windows):
        win = generate_biophysical_window(label=1, seed=s)
        win_360 = win[320:680]  # center 360 samples of 1000-sample window
        win_std = (win_360 - np.mean(win_360)) / (np.std(win_360) + 1e-12)
        X.append(win_std)

    # PVC
    for s in range(n_windows):
        win = generate_biophysical_window(label=0, seed=s + 2000)
        win_360 = win[320:680]
        win_std = (win_360 - np.mean(win_360)) / (np.std(win_360) + 1e-12)
        X.append(win_std)

    return np.array(X)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FEATURE EXTRACTOR WRAPPER
# ─────────────────────────────────────────────────────────────────────────────


class ResNetFeatureExtractor(nn.Module):
    def __init__(self, original_model):
        super(ResNetFeatureExtractor, self).__init__()
        self.conv1 = original_model.conv1
        self.bn1 = original_model.bn1
        self.relu = original_model.relu
        self.maxpool = original_model.maxpool
        self.layer1 = original_model.layer1
        self.layer2 = original_model.layer2
        self.layer3 = original_model.layer3
        self.layer4 = original_model.layer4
        self.avgpool = original_model.avgpool

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        return x.view(x.size(0), -1)


# ─────────────────────────────────────────────────────────────────────────────
# 3. MAIN AUDIT ENGINE
# ─────────────────────────────────────────────────────────────────────────────


def main():
    t_start = time.time()
    print("=" * 80)
    print(
        "🔬 PRINCIPAL COMPUTATIONAL PHYSICS AUDITOR — DEEP REPRESENTATION AUDIT (ResNet-1D)"
    )
    print("=" * 80)

    # ── STEP 1: Load Raw 1D Waveforms for Domains A, B, and C ────────────────
    print("\n[STEP 1] Generating raw 1D segments for Domains A, B, and C...")
    X_A_raw = build_raw_domain_a()
    X_B_raw = build_raw_domain_b()
    X_C_raw, _ = load_raw_ecg_segments(TEST_RECORDS, max_beats_per_class=120)

    print("  Raw Domain counts:")
    print(f"    - Domain A (Synthetic) : {X_A_raw.shape[0]} windows")
    print(f"    - Domain B (Composite) : {X_B_raw.shape[0]} windows")
    print(f"    - Domain C (Clinical)  : {X_C_raw.shape[0]} windows")

    # ── STEP 2: Load Trained ResNet-1D Model and Setup Extractor ─────────────
    print("\n[STEP 2] Initializing ResNet-1D and loading weights...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained ResNet-1D model state dict not found at: {MODEL_PATH}"
        )

    model = ResNet18_1D(num_classes=2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()

    # Create feature extractor (pulls 512D vectors prior to linear fc layer)
    extractor = ResNetFeatureExtractor(model).to(device)

    # ── STEP 3: Deep Feature Extraction ──────────────────────────────────────
    print(
        "\n[STEP 3] Slicing deep representations from intermediate avg pooling layer..."
    )

    def extract_deep_features(X_raw):
        # Convert to tensor and shape (N, Channels=1, Length=360)
        tensor_in = torch.tensor(X_raw, dtype=torch.float32).unsqueeze(1).to(device)
        feats_list = []
        # Process in batches to avoid GPU memory overflow
        batch_size = 128
        with torch.no_grad():
            for i in range(0, len(X_raw), batch_size):
                batch = tensor_in[i : i + batch_size]
                feats = extractor(batch)
                feats_list.append(feats.cpu().numpy())
        return np.concatenate(feats_list, axis=0)

    feats_A = extract_deep_features(X_A_raw)
    feats_B = extract_deep_features(X_B_raw)
    feats_C = extract_deep_features(X_C_raw)

    print("  Extracted Deep Feature Shapes:")
    print(f"    - Domain A : {feats_A.shape}")
    print(f"    - Domain B : {feats_B.shape}")
    print(f"    - Domain C : {feats_C.shape}")

    # ── STEP 4: CKA on Deep Representations ──────────────────────────────────
    print("\n[STEP 4] Calculating Linear CKA on Deep Representations...")

    # Truncate to align sizes for CKA
    min_AC = min(len(feats_A), len(feats_C))
    min_BC = min(len(feats_B), len(feats_C))

    cka_deep_AC = compute_linear_cka(feats_A[:min_AC], feats_C[:min_AC])
    cka_deep_BC = compute_linear_cka(feats_B[:min_BC], feats_C[:min_BC])

    d_emb_deep_AC = 1.0 - cka_deep_AC
    d_emb_deep_BC = 1.0 - cka_deep_BC

    print("  Deep Representation Shift (D_emb = 1 - CKA):")
    print(
        f"    - Pairs A-C (Synthetic -> Clinical) : {d_emb_deep_AC:.6f}  (CKA: {cka_deep_AC:.6f})"
    )
    print(
        f"    - Pairs B-C (Composite -> Clinical) : {d_emb_deep_BC:.6f}  (CKA: {cka_deep_BC:.6f})"
    )

    # ── STEP 5: Load EV3 Representations for Comparison ─────────────────────
    print("\n[STEP 5] Generating EV3 features to compare representational shifts...")
    X_A_ev3, _ = build_domain_a_synthetic()
    X_B_ev3, _ = build_domain_b_composite()
    X_C_ev3, _ = build_domain_c_clinical()

    # Truncate to align sizes for CKA
    min_ev3_AC = min(len(X_A_ev3), len(X_C_ev3))
    min_ev3_BC = min(len(X_B_ev3), len(X_C_ev3))

    cka_ev3_AC = compute_linear_cka(X_A_ev3[:min_ev3_AC], X_C_ev3[:min_ev3_AC])
    cka_ev3_BC = compute_linear_cka(X_B_ev3[:min_ev3_BC], X_C_ev3[:min_ev3_BC])

    d_emb_ev3_AC = 1.0 - cka_ev3_AC
    d_emb_ev3_BC = 1.0 - cka_ev3_BC

    print("  EV3 Representation Shift (D_emb = 1 - CKA):")
    print(
        f"    - Pairs A-C (Synthetic -> Clinical) : {d_emb_ev3_AC:.6f}  (CKA: {cka_ev3_AC:.6f})"
    )
    print(
        f"    - Pairs B-C (Composite -> Clinical) : {d_emb_ev3_BC:.6f}  (CKA: {cka_ev3_BC:.6f})"
    )

    # ── STEP 6: Compile and Export Comparison Report ────────────────────────
    report = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "audit_type": "Deep vs EV3 Representational CKA Comparison",
            "model_architecture": "ResNet18-1D",
            "extracted_layer": "AdaptiveAvgPool1d",
        },
        "deep_representation_shift": {
            "CKA_A_C": cka_deep_AC,
            "D_emb_A_C": d_emb_deep_AC,
            "CKA_B_C": cka_deep_BC,
            "D_emb_B_C": d_emb_deep_BC,
        },
        "ev3_representation_shift": {
            "CKA_A_C": cka_ev3_AC,
            "D_emb_A_C": d_emb_ev3_AC,
            "CKA_B_C": cka_ev3_BC,
            "D_emb_B_C": d_emb_ev3_BC,
        },
        "comparison_analysis": {
            "difference_D_emb_A_C": abs(d_emb_deep_AC - d_emb_ev3_AC),
            "difference_D_emb_B_C": abs(d_emb_deep_BC - d_emb_ev3_BC),
            "degradation_in_deep_space": bool(d_emb_deep_AC > d_emb_ev3_AC),
        },
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("\n" + "=" * 80)
    print("🏆 FINAL COMPARATIVE REPRESENTATIONAL GEOMETRY PANEL")
    print("=" * 80)
    print(
        f"  A-C (Synthetic -> Clinical) | Deep D_emb: {d_emb_deep_AC:.6f}  vs  EV3 D_emb: {d_emb_ev3_AC:.6f}"
    )
    print(
        f"  B-C (Composite -> Clinical) | Deep D_emb: {d_emb_deep_BC:.6f}  vs  EV3 D_emb: {d_emb_ev3_BC:.6f}"
    )
    print("  " + "─" * 76)
    print(
        f"  Deep Space Deformation Degradation: {report['comparison_analysis']['degradation_in_deep_space']}"
    )
    print(
        f"  Deformation Change Magnitude (A-C): {report['comparison_analysis']['difference_D_emb_A_C']:.6f}"
    )
    print(
        f"  Deformation Change Magnitude (B-C): {report['comparison_analysis']['difference_D_emb_B_C']:.6f}"
    )
    print("=" * 80)
    print(
        f"📂 Compiled deep representation report successfully exported to: {REPORT_FILE}"
    )

    t_end = time.time()
    print(f"\nDeep Representation Audit completed in {t_end - t_start:.2f} seconds.\n")


if __name__ == "__main__":
    main()
