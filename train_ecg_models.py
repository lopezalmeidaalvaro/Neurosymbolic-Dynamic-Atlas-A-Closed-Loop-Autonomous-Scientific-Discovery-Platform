import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

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

from torchdiffeq import odeint

# ─────────────────────────────────────────────────────────────────────────────
# 1. SYNTHETIC ECG WAVEFORM GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_synthetic_ecg(n_samples=400, seq_len=100, domain_shift=False, noise_level=0.05):
    np.random.seed(42 if not domain_shift else 100)
    X = []
    y = []
    t = np.arange(seq_len)
    
    for i in range(n_samples):
        # 50% normal, 50% PVC
        label = np.random.choice([0, 1])
        ecg = np.zeros(seq_len)
        
        # Random time shift to prevent absolute alignment
        shift = np.random.randint(-5, 6)
        
        if label == 0:  # Normal
            # P wave
            ecg += np.exp(-((t - (30 + shift)) / 4.0) ** 2) * 0.2
            # QRS complex (sharp, positive)
            ecg += np.exp(-((t - (50 + shift)) / 2.0) ** 2) * 1.5
            ecg -= np.exp(-((t - (48 + shift)) / 1.0) ** 2) * 0.2
            ecg -= np.exp(-((t - (52 + shift)) / 1.0) ** 2) * 0.2
            # T wave
            ecg += np.exp(-((t - (75 + shift)) / 6.0) ** 2) * 0.35
        else:  # PVC
            # Wide, inverted QRS
            ecg -= np.exp(-((t - (45 + shift)) / 8.0) ** 2) * 1.3
            # T wave
            ecg += np.exp(-((t - (75 + shift)) / 10.0) ** 2) * 0.4
            
        # Apply amplitude shift and extra noise if domain shift is active
        if domain_shift:
            ecg = ecg * 0.8 + 0.2  # amplitude compression and baseline shift
            ecg += np.random.normal(0, noise_level * 2.0, seq_len)
        else:
            ecg += np.random.normal(0, noise_level, seq_len)
            
        X.append(ecg)
        y.append(label)
        
    X = np.array(X, dtype=np.float32)[:, np.newaxis, :]  # shape: (n_samples, 1, seq_len)
    y = np.array(y, dtype=np.int64)
    return X, y

# ─────────────────────────────────────────────────────────────────────────────
# 2. MODEL DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# A. SimpleResNet1D
class ResidualBlock1D(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm1d(out_channels)
        
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )
            
    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            residual = self.downsample(residual)
        out += residual
        out = self.relu(out)
        return out

class SimpleResNet1D(nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(42)
        self.in_conv = nn.Conv1d(1, 16, kernel_size=3, padding=1, bias=False)
        self.in_bn = nn.BatchNorm1d(16)
        self.relu = nn.ReLU()
        
        self.block1 = ResidualBlock1D(16, 16)
        self.block2 = ResidualBlock1D(16, 32, stride=2)
        self.block3 = ResidualBlock1D(32, 64, stride=2)
        self.block4 = ResidualBlock1D(64, 64)
        
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.linear = nn.Linear(64, 2)
        
    def forward_with_activations(self, x):
        out = self.in_conv(x)
        out = self.in_bn(out)
        out = self.relu(out)
        
        act1_raw = self.block1(out)
        act1 = self.pool(act1_raw).squeeze(-1)
        
        act2_raw = self.block2(act1_raw)
        act2 = self.pool(act2_raw).squeeze(-1)
        
        act3_raw = self.block3(act2_raw)
        act3 = self.pool(act3_raw).squeeze(-1)
        
        act4_raw = self.block4(act3_raw)
        act4 = self.pool(act4_raw).squeeze(-1)
        
        logits = self.linear(act4)
        act5 = logits
        
        return logits, [act1, act2, act3, act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# B. SimpleLSTM1D
class SimpleLSTM1D(nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(42)
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, num_layers=5, batch_first=True)
        self.linear = nn.Linear(32, 2)
        
    def forward_with_activations(self, x):
        x_lstm = x.transpose(1, 2)
        out, (h_n, c_n) = self.lstm(x_lstm)
        
        act1 = h_n[0]
        act2 = h_n[1]
        act3 = h_n[2]
        act4 = h_n[3]
        
        logits = self.linear(h_n[4])
        act5 = logits
        
        return logits, [act1, act2, act3, act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# C. ECGNeuralODE
class ODEFuncECG(nn.Module):
    def __init__(self, dim):
        super().__init__()
        torch.manual_seed(42)
        self.net = nn.Sequential(
            nn.Linear(dim, dim),
            nn.Tanh(),
            nn.Linear(dim, dim)
        )
        
    def forward(self, t, x):
        return self.net(x)

class ECGNeuralODE(nn.Module):
    def __init__(self, input_len=100, hidden_dim=32):
        super().__init__()
        torch.manual_seed(42)
        self.in_proj = nn.Sequential(
            nn.Linear(input_len, hidden_dim),
            nn.Tanh()
        )
        self.ode_func = ODEFuncECG(hidden_dim)
        self.linear = nn.Linear(hidden_dim, 2)
        
    def forward_with_activations(self, x):
        x_flat = x.squeeze(1)
        h0 = self.in_proj(x_flat)
        
        t = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0], dtype=torch.float32).to(x.device)
        h_all = odeint(self.ode_func, h0, t, method="rk4")
        
        act1 = h_all[0]
        act2 = h_all[1]
        act3 = h_all[2]
        act4 = h_all[3]
        
        logits = self.linear(h_all[4])
        act5 = logits
        
        return logits, [act1, act2, act3, act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRAINING AND FINE-TUNING LOOP
# ─────────────────────────────────────────────────────────────────────────────
def train_model(model, dataloader, epochs=5, lr=0.005):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == batch_y).sum().item()
            total += batch_x.size(0)
            
        epoch_loss = total_loss / total
        epoch_acc = correct / total
        print(f"  Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.4f} | Acc: {epoch_acc:.4f}")

def main():
    print("=" * 60)
    print("🩺 TRAINING ECG MODELS (BASE & FINE-TUNING)")
    print("=" * 60)

    # A. Generate datasets
    print("Generating synthetic ECG datasets...")
    X_base, y_base = generate_synthetic_ecg(n_samples=400, seq_len=100, domain_shift=False)
    X_ft, y_ft = generate_synthetic_ecg(n_samples=400, seq_len=100, domain_shift=True)

    base_dataset = TensorDataset(torch.tensor(X_base), torch.tensor(y_base))
    ft_dataset = TensorDataset(torch.tensor(X_ft), torch.tensor(y_ft))

    base_loader = DataLoader(base_dataset, batch_size=64, shuffle=True)
    ft_loader = DataLoader(ft_dataset, batch_size=64, shuffle=True)

    # Save checkpoints directory
    os.makedirs("checkpoints", exist_ok=True)

    # Models dict
    models = {
        "resnet": SimpleResNet1D(),
        "lstm": SimpleLSTM1D(),
        "ode": ECGNeuralODE()
    }

    # Training
    for name, model in models.items():
        print(f"\n--- Training {name.upper()} on Base Dataset ---")
        train_model(model, base_loader, epochs=5)
        # Save base checkpoint
        torch.save(model.state_dict(), f"checkpoints/{name}_base.pth")
        print(f"Saved checkpoints/{name}_base.pth")

        print(f"\n--- Fine-tuning {name.upper()} on Shifted Dataset ---")
        # Fine-tune
        train_model(model, ft_loader, epochs=5, lr=0.002)
        # Save fine-tuned checkpoint
        torch.save(model.state_dict(), f"checkpoints/{name}_ft.pth")
        print(f"Saved checkpoints/{name}_ft.pth")

    print("\n✅ Successfully trained all models and saved checkpoints.")
    print("=" * 60)

if __name__ == "__main__":
    main()
