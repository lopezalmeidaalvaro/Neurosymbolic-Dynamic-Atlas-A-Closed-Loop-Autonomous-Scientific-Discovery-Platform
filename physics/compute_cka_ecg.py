import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

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

# Set global seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

from train_ecg_models import SimpleResNet1D, SimpleLSTM1D, ECGNeuralODE, generate_synthetic_ecg
from neurosymbolic.audit import compute_cka

def main():
    print("=" * 60)
    print("🧠 COMPUTING LAYER-WISE CKA MATRIX FOR ECG MODEL ARCHITECTURES")
    print("=" * 60)

    # 1. Generate common test batch
    print("Generating common test batch (100 samples)...")
    X_test, _ = generate_synthetic_ecg(n_samples=100, seq_len=100, domain_shift=False)
    x_batch = torch.tensor(X_test)

    # Prepare results directory
    os.makedirs("results", exist_ok=True)
    matrix_path = "results/cka_layers.npy"

    # Initialize layer CKA matrix (3 models, 5 layers)
    cka_matrix = np.zeros((3, 5))

    # Define model types and their classes
    model_configs = [
        {"name": "SimpleResNet1D", "class": SimpleResNet1D, "base_pth": "resnet_base.pth", "ft_pth": "resnet_ft.pth", "row": 0},
        {"name": "SimpleLSTM1D", "class": SimpleLSTM1D, "base_pth": "lstm_base.pth", "ft_pth": "lstm_ft.pth", "row": 1},
        {"name": "ECGNeuralODE", "class": ECGNeuralODE, "base_pth": "ode_base.pth", "ft_pth": "ode_ft.pth", "row": 2}
    ]

    for cfg in model_configs:
        print(f"\nEvaluating CKA for {cfg['name']} layers...")
        
        # Instantiate base model and load weights
        model_base = cfg["class"]()
        model_base.load_state_dict(torch.load(f"models/{cfg['base_pth']}"))
        model_base.eval()
        
        # Instantiate fine-tuned model and load weights
        model_ft = cfg["class"]()
        model_ft.load_state_dict(torch.load(f"models/{cfg['ft_pth']}"))
        model_ft.eval()
        
        # Get activations
        with torch.no_grad():
            _, base_acts = model_base.forward_with_activations(x_batch)
            _, ft_acts = model_ft.forward_with_activations(x_batch)
            
        # Compute layer-wise CKA
        model_ckas = []
        for i in range(5):
            act_base = base_acts[i].cpu().numpy()
            act_ft = ft_acts[i].cpu().numpy()
            
            # Compute CKA
            layer_cka = compute_cka(act_base, act_ft)
            model_ckas.append(layer_cka)
            cka_matrix[cfg["row"], i] = layer_cka
            
        print(f"  CKA metrics for the 5 layers: " + ", ".join([f"L{j+1}: {model_ckas[j]:.6f}" for j in range(5)]))

    # Save to results/cka_layers.npy
    np.save(matrix_path, cka_matrix)
    print(f"\n✅ Successfully computed and saved CKA layers matrix to {matrix_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
