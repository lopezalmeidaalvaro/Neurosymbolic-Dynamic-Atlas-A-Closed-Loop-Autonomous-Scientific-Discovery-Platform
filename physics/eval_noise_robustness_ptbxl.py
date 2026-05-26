import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import csv
import numpy as np
import torch

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Set seeds
np.random.seed(42)
torch.manual_seed(42)

from train_all_architectures_ptbxl import (
    SimpleResNet1D,
    SimpleLSTM1D,
    ECGNeuralODE,
    PatchTST,
    TimesNet,
    ResNet18_1D,
    generate_ptbxl_data,
)
from neurosymbolic.audit import compute_ev3

def main():
    print("=" * 60)
    print("🩺 RUNNING PTB-XL MODEL AUDIT: EV3 vs NOISE ROBUSTNESS")
    print("=" * 60)

    # 1. Generate clean and noisy test datasets (100 samples)
    X_clean, y_clean = generate_ptbxl_data(n_samples=100, seq_len=100, domain_shift=False)
    # Add 20% noise (0.15 std)
    X_noisy = X_clean + np.random.normal(0, 0.15, X_clean.shape)

    x_clean_tensor = torch.tensor(X_clean, dtype=torch.float32)
    x_noisy_tensor = torch.tensor(X_noisy, dtype=torch.float32)
    y_tensor = torch.tensor(y_clean, dtype=torch.int64)

    # Model configs for the 6 architectures
    model_configs = [
        {"name": "SimpleResNet1D", "class": SimpleResNet1D, "pth": "models/ptbxl/resnet_base.pth"},
        {"name": "SimpleLSTM1D", "class": SimpleLSTM1D, "pth": "models/ptbxl/lstm_base.pth"},
        {"name": "ECGNeuralODE", "class": ECGNeuralODE, "pth": "models/ptbxl/ode_base.pth"},
        {"name": "PatchTST", "class": PatchTST, "pth": "models/ptbxl/patchtst_base.pth"},
        {"name": "TimesNet", "class": TimesNet, "pth": "models/ptbxl/timesnet_base.pth"},
        {"name": "ResNet18_1D", "class": ResNet18_1D, "pth": "models/ptbxl/resnet18_base.pth"}
    ]

    results = []

    for cfg in model_configs:
        name = cfg["name"]
        print(f"\nAuditing {name}...")
        
        if not os.path.exists(cfg["pth"]):
            print(f"  [ERROR] Checkpoint not found for {name}. Skip.")
            continue

        model = cfg["class"]()
        model.load_state_dict(torch.load(cfg["pth"]))
        model.eval()

        # Evaluate on clean dataset
        with torch.no_grad():
            logits_clean, acts_clean = model.forward_with_activations(x_clean_tensor)
            preds_clean = torch.argmax(logits_clean, dim=1)
            acc_clean = (preds_clean == y_tensor).sum().item() / 100.0

            # Evaluate on noisy dataset
            logits_noisy, _ = model.forward_with_activations(x_noisy_tensor)
            preds_noisy = torch.argmax(logits_noisy, dim=1)
            acc_noisy = (preds_noisy == y_tensor).sum().item() / 100.0

            # Compute EV3 of the representation layer (layer 4, index 3) on clean acts
            rep_acts = acts_clean[3].cpu().numpy()
            ev3_val = compute_ev3(rep_acts)

        acc_drop = acc_clean - acc_noisy
        print(f"  Clean Acc: {acc_clean:.2%} | Noisy Acc: {acc_noisy:.2%} | Drop: {acc_drop:.2%}")
        print(f"  EV3: {ev3_val:.6e}")

        results.append({
            "Model": name,
            "EV3": f"{ev3_val:.6e}",
            "Accuracy_Clean": f"{acc_clean:.2%}",
            "Accuracy_Noisy": f"{acc_noisy:.2%}",
            "Accuracy_Drop": f"{acc_drop:.2%}"
        })

    # Save to experiments/ptbxl_noise_robustness.csv
    os.makedirs("experiments", exist_ok=True)
    csv_path = "experiments/ptbxl_noise_robustness.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Model", "EV3", "Accuracy_Clean", "Accuracy_Noisy", "Accuracy_Drop"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"\n✅ PTB-XL audit results successfully saved to {csv_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
