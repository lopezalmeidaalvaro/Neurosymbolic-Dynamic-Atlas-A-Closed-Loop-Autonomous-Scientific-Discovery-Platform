import os
import sys
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
torch.manual_seed(42)
np.random.seed(42)

from train_all_architectures_ptbxl import (
    SimpleResNet1D,
    SimpleLSTM1D,
    ECGNeuralODE,
    PatchTST,
    TimesNet,
    ResNet18_1D,
    generate_ptbxl_data,
)
from neurosymbolic.audit import compute_cka, compute_ev3, compute_svcca, compute_pwcca

def main():
    print("=" * 60)
    print("🧠 COMPUTING REPRESENTATION METRICS (CKA, SVCCA, PWCCA, EV3) FOR PTB-XL")
    print("=" * 60)

    # 1. Generate common test batch
    print("Generating common test batch (100 samples)...")
    X_test, _ = generate_ptbxl_data(n_samples=100, seq_len=100, domain_shift=False)
    x_batch = torch.tensor(X_test)

    os.makedirs("results", exist_ok=True)

    # Define architectures
    model_configs = [
        {"name": "resnet", "class": SimpleResNet1D, "base_pth": "checkpoints/ptbxl/resnet_base.pth", "ft_pth": "checkpoints/ptbxl/resnet_ft.pth", "idx": 0},
        {"name": "lstm", "class": SimpleLSTM1D, "base_pth": "checkpoints/ptbxl/lstm_base.pth", "ft_pth": "checkpoints/ptbxl/lstm_ft.pth", "idx": 1},
        {"name": "ode", "class": ECGNeuralODE, "base_pth": "checkpoints/ptbxl/ode_base.pth", "ft_pth": "checkpoints/ptbxl/ode_ft.pth", "idx": 2},
        {"name": "patchtst", "class": PatchTST, "base_pth": "checkpoints/ptbxl/patchtst_base.pth", "ft_pth": "checkpoints/ptbxl/patchtst_ft.pth", "idx": 3},
        {"name": "timesnet", "class": TimesNet, "base_pth": "checkpoints/ptbxl/timesnet_base.pth", "ft_pth": "checkpoints/ptbxl/timesnet_ft.pth", "idx": 4},
        {"name": "resnet18", "class": ResNet18_1D, "base_pth": "checkpoints/ptbxl/resnet18_base.pth", "ft_pth": "checkpoints/ptbxl/resnet18_ft.pth", "idx": 5}
    ]

    # Matrices to store full 6x5x5 layer comparisons
    cka_all = np.zeros((6, 5, 5))
    svcca_all = np.zeros((6, 5, 5))
    pwcca_all = np.zeros((6, 5, 5))
    
    # Vector to store EV3 for each fine-tuned model (representation layer = layer 4, index 3)
    ev3_all = np.zeros(6)

    for cfg in model_configs:
        name = cfg["name"]
        print(f"\nEvaluating metrics for {name.upper()}...")

        if not os.path.exists(cfg["base_pth"]) or not os.path.exists(cfg["ft_pth"]):
            print(f"  [ERROR] Checkpoint files not found for {name.upper()}. Skip.")
            continue

        # Load models
        model_base = cfg["class"]()
        model_base.load_state_dict(torch.load(cfg["base_pth"]))
        model_base.eval()

        model_ft = cfg["class"]()
        model_ft.load_state_dict(torch.load(cfg["ft_pth"]))
        model_ft.eval()

        # Extract activations
        with torch.no_grad():
            _, base_acts = model_base.forward_with_activations(x_batch)
            _, ft_acts = model_ft.forward_with_activations(x_batch)

        # Compute full 5x5 CKA, SVCCA, and PWCCA between base and fine-tuned layers
        for i in range(5):
            act_base = base_acts[i].cpu().numpy()
            for j in range(5):
                act_ft = ft_acts[j].cpu().numpy()

                cka_all[cfg["idx"], i, j] = compute_cka(act_base, act_ft)
                svcca_all[cfg["idx"], i, j] = compute_svcca(act_base, act_ft)
                pwcca_all[cfg["idx"], i, j] = compute_pwcca(act_base, act_ft)

        # Compute EV3 of the fine-tuned model's representation layer (layer 4, index 3)
        act4_ft = ft_acts[3].cpu().numpy()
        ev3_all[cfg["idx"]] = compute_ev3(act4_ft)

        print(f"  Diagonal CKA:   " + ", ".join([f"L{k+1}: {cka_all[cfg['idx'], k, k]:.4f}" for k in range(5)]))
        print(f"  Diagonal SVCCA: " + ", ".join([f"L{k+1}: {svcca_all[cfg['idx'], k, k]:.4f}" for k in range(5)]))
        print(f"  Diagonal PWCCA: " + ", ".join([f"L{k+1}: {pwcca_all[cfg['idx'], k, k]:.4f}" for k in range(5)]))
        print(f"  Stable EV3 (FT layer 4): {ev3_all[cfg['idx']]:.4f}")

    # Save to disk
    np.save("results/cka_layers_ptbxl.npy", cka_all)
    np.save("results/svcca_layers_ptbxl.npy", svcca_all)
    np.save("results/pwcca_layers_ptbxl.npy", pwcca_all)
    np.save("results/ev3_ptbxl.npy", ev3_all)

    print("\n✅ Successfully computed and saved all representational audit metrics.")
    print("  results/cka_layers_ptbxl.npy   shape:", cka_all.shape)
    print("  results/svcca_layers_ptbxl.npy  shape:", svcca_all.shape)
    print("  results/pwcca_layers_ptbxl.npy  shape:", pwcca_all.shape)
    print("  results/ev3_ptbxl.npy           shape:", ev3_all.shape)
    print("=" * 60)

if __name__ == "__main__":
    main()
