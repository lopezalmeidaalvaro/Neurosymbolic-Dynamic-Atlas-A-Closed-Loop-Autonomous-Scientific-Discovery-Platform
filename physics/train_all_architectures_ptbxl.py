import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from torchdiffeq import odeint

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

# ─────────────────────────────────────────────────────────────────────────────
# 1. PTB-XL SYNTHETIC ECG DATASET GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_ptbxl_data(n_samples=300, seq_len=100, domain_shift=False):
    np.random.seed(42 if not domain_shift else 100)
    X = []
    y = []
    t = np.arange(seq_len)
    
    for i in range(n_samples):
        # binary classification: Normal vs Arrhythmia (PVC/Myocardial Infarction proxy)
        label = np.random.choice([0, 1])
        ecg = np.zeros(seq_len)
        shift = np.random.randint(-4, 5)
        
        if label == 0:  # Normal
            ecg += np.exp(-((t - (30 + shift)) / 4.0) ** 2) * 0.25 # P wave
            ecg += np.exp(-((t - (50 + shift)) / 2.0) ** 2) * 1.6  # QRS
            ecg -= np.exp(-((t - (48 + shift)) / 1.0) ** 2) * 0.2
            ecg -= np.exp(-((t - (52 + shift)) / 1.0) ** 2) * 0.2
            ecg += np.exp(-((t - (75 + shift)) / 5.0) ** 2) * 0.35 # T wave
        else:  # Arrhythmia
            # Wide, abnormal QRS
            ecg += np.exp(-((t - (40 + shift)) / 8.0) ** 2) * 0.8  # early, wider QRS
            ecg -= np.exp(-((t - (55 + shift)) / 12.0) ** 2) * 1.4 # inverted T/ST deflection
            
        if domain_shift:
            # Baseline wander (sine wave) + amplitude compression + high noise
            ecg = ecg * 0.75 + 0.1 * np.sin(2 * np.pi * t / 50.0)
            ecg += np.random.normal(0, 0.12, seq_len)
        else:
            ecg += np.random.normal(0, 0.04, seq_len)
            
        X.append(ecg)
        y.append(label)
        
    X = np.array(X, dtype=np.float32)[:, np.newaxis, :]  # shape: (n_samples, 1, seq_len)
    y = np.array(y, dtype=np.int64)
    return X, y

# ─────────────────────────────────────────────────────────────────────────────
# 2. ARCHITECTURE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

# Helper ResNet blocks
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

# 1. SimpleResNet1D (existing 5-layer convolutional ResNet)
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

# 2. SimpleLSTM1D (existing 5-layer stacked LSTM)
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

# 3. ECGNeuralODE (existing 5-step Neural ODE)
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

# 4. PatchTST (Simplified 5-layer 1D Patch Transformer)
class PatchTST(nn.Module):
    def __init__(self, seq_len=100, patch_len=10, stride=10, hidden_dim=32):
        super().__init__()
        torch.manual_seed(42)
        self.patch_len = patch_len
        self.stride = stride
        self.num_patches = seq_len // patch_len
        
        # Linear projection of patches
        self.in_proj = nn.Linear(patch_len, hidden_dim)
        
        # Transformer layers (4 layer blocks)
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=2, dim_feedforward=32, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=4)
        
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.linear = nn.Linear(hidden_dim, 2)
        
    def forward_with_activations(self, x):
        # x shape: (batch, 1, seq_len)
        batch_size = x.size(0)
        
        # Unfold patches
        # shape: (batch, num_patches, patch_len)
        patches = x.squeeze(1).unfold(1, self.patch_len, self.stride)
        
        # Project patches
        x_proj = self.in_proj(patches) # shape: (batch, num_patches, hidden_dim)
        
        # Feed through transformer layers one by one to extract intermediate representations
        # To be fully self-contained, we pass through each transformer encoder block
        act1 = self.pool(x_proj.transpose(1, 2)).squeeze(-1)
        
        curr = x_proj
        acts = []
        for i in range(3):
            # Evaluate single block
            curr = self.transformer.layers[i](curr)
            acts.append(self.pool(curr.transpose(1, 2)).squeeze(-1))
            
        curr = self.transformer.layers[3](curr)
        act4 = self.pool(curr.transpose(1, 2)).squeeze(-1)
        
        logits = self.linear(act4)
        act5 = logits
        
        return logits, [act1, acts[0], acts[1], act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# 5. TimesNet (Simplified 1D Multi-Frequency Times Block network)
class TimesBlock(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        # 2D Conv block to perform multi-frequency temporal convolution
        self.conv2d = nn.Sequential(
            nn.Conv2d(1, hidden_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(hidden_dim),
            nn.ReLU(),
            nn.Conv2d(hidden_dim, 1, kernel_size=3, padding=1, bias=False)
        )
    def forward(self, x, period):
        # Reshape 1D to 2D
        batch, channels, length = x.shape
        p = period
        if length % p != 0:
            # Pad to make divisible
            pad_len = p - (length % p)
            x_padded = nn.functional.pad(x, (0, pad_len))
        else:
            x_padded = x
            pad_len = 0
            
        new_len = x_padded.shape[-1]
        x_2d = x_padded.reshape(batch * channels, 1, p, new_len // p)
        out_2d = self.conv2d(x_2d)
        out = out_2d.reshape(batch, channels, new_len)
        if pad_len > 0:
            out = out[:, :, :-pad_len]
        return out + x

class TimesNet(nn.Module):
    def __init__(self, seq_len=100, hidden_dim=32):
        super().__init__()
        torch.manual_seed(42)
        self.in_proj = nn.Conv1d(1, 32, kernel_size=3, padding=1, bias=False)
        self.in_bn = nn.BatchNorm1d(32)
        self.relu = nn.ReLU()
        
        # 4 Times blocks for multi-periods (periods: 10, 20, 25, 50)
        self.block1 = TimesBlock(32)
        self.block2 = TimesBlock(32)
        self.block3 = TimesBlock(32)
        self.block4 = TimesBlock(32)
        
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.linear = nn.Linear(32, 2)
        
    def forward_with_activations(self, x):
        out = self.in_proj(x)
        out = self.in_bn(out)
        out = self.relu(out)
        
        act1_raw = self.block1(out, period=10)
        act1 = self.pool(act1_raw).squeeze(-1)
        
        act2_raw = self.block2(act1_raw, period=20)
        act2 = self.pool(act2_raw).squeeze(-1)
        
        act3_raw = self.block3(act2_raw, period=25)
        act3 = self.pool(act3_raw).squeeze(-1)
        
        act4_raw = self.block4(act3_raw, period=50)
        act4 = self.pool(act4_raw).squeeze(-1)
        
        logits = self.linear(act4)
        act5 = logits
        
        return logits, [act1, act2, act3, act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# 6. ResNet18_1D (Standard deep residual 1D classifier)
class ResNet18_1D(nn.Module):
    def __init__(self):
        super().__init__()
        torch.manual_seed(42)
        self.in_conv = nn.Conv1d(1, 16, kernel_size=3, padding=1, bias=False)
        self.in_bn = nn.BatchNorm1d(16)
        self.relu = nn.ReLU()
        
        # 4 stages of residual blocks
        self.stage1 = nn.Sequential(
            ResidualBlock1D(16, 16),
            ResidualBlock1D(16, 16)
        )
        self.stage2 = nn.Sequential(
            ResidualBlock1D(16, 32, stride=2),
            ResidualBlock1D(32, 32)
        )
        self.stage3 = nn.Sequential(
            ResidualBlock1D(32, 64, stride=2),
            ResidualBlock1D(64, 64)
        )
        self.stage4 = nn.Sequential(
            ResidualBlock1D(64, 128, stride=2),
            ResidualBlock1D(128, 128)
        )
        
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.linear = nn.Linear(128, 2)
        
    def forward_with_activations(self, x):
        out = self.in_conv(x)
        out = self.in_bn(out)
        out = self.relu(out)
        
        act1_raw = self.stage1(out)
        act1 = self.pool(act1_raw).squeeze(-1)
        
        act2_raw = self.stage2(act1_raw)
        act2 = self.pool(act2_raw).squeeze(-1)
        
        act3_raw = self.stage3(act2_raw)
        act3 = self.pool(act3_raw).squeeze(-1)
        
        act4_raw = self.stage4(act3_raw)
        act4 = self.pool(act4_raw).squeeze(-1)
        
        logits = self.linear(act4)
        act5 = logits
        
        return logits, [act1, act2, act3, act4, act5]
        
    def forward(self, x):
        logits, _ = self.forward_with_activations(x)
        return logits

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRAINING ROUTINE
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
    print("🩺 TRAINING ALL 6 ARCHITECTURES ON SYNTHETIC PTB-XL ECG")
    print("=" * 60)

    # A. Generate datasets
    print("Generating synthetic PTB-XL datasets...")
    X_base, y_base = generate_ptbxl_data(n_samples=300, seq_len=100, domain_shift=False)
    X_ft, y_ft = generate_ptbxl_data(n_samples=300, seq_len=100, domain_shift=True)

    base_dataset = TensorDataset(torch.tensor(X_base), torch.tensor(y_base))
    ft_dataset = TensorDataset(torch.tensor(X_ft), torch.tensor(y_ft))

    base_loader = DataLoader(base_dataset, batch_size=64, shuffle=True)
    ft_loader = DataLoader(ft_dataset, batch_size=64, shuffle=True)

    # Save models directory
    os.makedirs("models/ptbxl", exist_ok=True)

    # Architectures
    models = {
        "resnet": SimpleResNet1D(),
        "lstm": SimpleLSTM1D(),
        "ode": ECGNeuralODE(),
        "patchtst": PatchTST(),
        "timesnet": TimesNet(),
        "resnet18": ResNet18_1D()
    }

    # Training loop
    for name, model in models.items():
        print(f"\n--- Training {name.upper()} (Base Classifier) ---")
        train_model(model, base_loader, epochs=5)
        torch.save(model.state_dict(), f"models/ptbxl/{name}_base.pth")
        print(f"Saved models/ptbxl/{name}_base.pth")

        print(f"\n--- Fine-tuning {name.upper()} (Domain Shifted) ---")
        train_model(model, ft_loader, epochs=5, lr=0.002)
        torch.save(model.state_dict(), f"models/ptbxl/{name}_ft.pth")
        print(f"Saved models/ptbxl/{name}_ft.pth")

    print("\n✅ Successfully trained all 6 architectures and saved models.")
    print("=" * 60)

if __name__ == "__main__":
    main()
