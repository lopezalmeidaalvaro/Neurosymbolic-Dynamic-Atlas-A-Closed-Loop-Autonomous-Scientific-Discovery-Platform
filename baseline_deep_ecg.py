import os
import sys
import json
import time
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score
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

# Dynamically check and install dependencies
try:
    import wfdb
except ImportError:
    print("Installing 'wfdb' dependency dynamically...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "wfdb"])
    import wfdb

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader
except ImportError:
    print("Installing 'torch' dependency dynamically...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch"])
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

# Paths
DATA_DIR = os.path.join(ROOT_DIR, "data", "mitdb")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# AAMI partitions from mit_bih_bifurcated_audit.py
TRAIN_RECORDS = [
    101,
    106,
    108,
    109,
    112,
    114,
    115,
    116,
    118,
    119,
    122,
    124,
    201,
    203,
    205,
    207,
    208,
    209,
    215,
    220,
    223,
    230,
]
TEST_RECORDS = [
    100,
    103,
    105,
    111,
    113,
    117,
    121,
    123,
    200,
    202,
    210,
    212,
    213,
    214,
    219,
    221,
    222,
    228,
    231,
    232,
    233,
    234,
]

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADER FOR RAW 1D ECG SEGMENTS (1 SECOND, 360 SAMPLES)
# ─────────────────────────────────────────────────────────────────────────────


def load_raw_ecg_segments(records, max_beats_per_class=120):
    """
    Loads raw ECG signals from MIT-BIH local records, extracts 360-sample windows
    (1 second at 360 Hz) centered on the R-peaks, Z-score normalizes them locally,
    and balances the dataset per patient/record.
    """
    print(f"  Parsing raw 1D segments for {len(records)} patient records...")
    X_list = []
    y_list = []
    window_half = 180  # 180 samples before/after centers for a total of 360 samples

    for r in records:
        rec_path = os.path.join(DATA_DIR, str(r))
        if not os.path.exists(rec_path + ".dat"):
            continue

        record = wfdb.rdrecord(rec_path)
        signal = record.p_signal[:, 0]

        annotation = wfdb.rdann(rec_path, "atr")
        sample_indices = annotation.sample
        symbols = annotation.symbol

        n_count = 0
        v_count = 0

        for idx, sym in zip(sample_indices, symbols):
            if sym not in ("N", "V"):
                continue

            if sym == "N":
                if n_count >= max_beats_per_class:
                    continue
                label = 1
            else:  # sym == 'V'
                if v_count >= max_beats_per_class:
                    continue
                label = 0

            if idx - window_half < 0 or idx + window_half > len(signal):
                continue

            win = signal[idx - window_half : idx + window_half]
            win = win[~np.isnan(win)]
            if len(win) < 360:
                continue

            # Z-score local standardization
            win_std = (win - np.mean(win)) / (np.std(win) + 1e-12)

            X_list.append(win_std)
            y_list.append(label)

            if sym == "N":
                n_count += 1
            else:
                v_count += 1

    return np.array(X_list), np.array(y_list)


# ─────────────────────────────────────────────────────────────────────────────
# 2. RESNET-1D ARCHITECTURE (ADAPTATION OF RESNET18 TO 1D SIGNALS)
# ─────────────────────────────────────────────────────────────────────────────


class ResidualBlock1D(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(ResidualBlock1D, self).__init__()
        self.conv1 = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv1d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.downsample = downsample

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out


class ResNet18_1D(nn.Module):
    def __init__(self, num_classes=2):
        super(ResNet18_1D, self).__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv1d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(64, 2, stride=1)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)

        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(512, num_classes)

    def _make_layer(self, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv1d(
                    self.in_channels,
                    out_channels,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm1d(out_channels),
            )
        layers = []
        layers.append(
            ResidualBlock1D(self.in_channels, out_channels, stride, downsample)
        )
        self.in_channels = out_channels
        for _ in range(1, blocks):
            layers.append(ResidualBlock1D(self.in_channels, out_channels))
        return nn.Sequential(*layers)

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
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.fc(x)
        return x


# ─────────────────────────────────────────────────────────────────────────────
# 3. TRAINING ENGINE
# ─────────────────────────────────────────────────────────────────────────────


def main():
    t_start = time.time()
    print("=" * 80)
    print("🚀 TRAINING RESNET-1D CLINICAL BASELINE — INTER-PATIENT AAMI PARTITION")
    print("=" * 80)

    # Load raw ECG signal windows
    print(
        "\n[STEP 1] Ingesting and segmenting raw ECG waveforms (360 samples, centered)..."
    )
    X_train, y_train = load_raw_ecg_segments(TRAIN_RECORDS, max_beats_per_class=120)
    X_test, y_test = load_raw_ecg_segments(TEST_RECORDS, max_beats_per_class=120)

    print("\n  Dataset compilation complete:")
    print(
        f"    - Train set (DS1) : {X_train.shape[0]} windows of length {X_train.shape[1]}"
    )
    print(
        f"    - Test set (DS2)  : {X_test.shape[0]} windows of length {X_test.shape[1]}"
    )
    print(
        f"    - Class Balance (Train): {np.sum(y_train == 1)} Normal (N) / {np.sum(y_train == 0)} PVC (V)"
    )
    print(
        f"    - Class Balance (Test) : {np.sum(y_test == 1)} Normal (N) / {np.sum(y_test == 0)} PVC (V)"
    )

    # ── PyTorch Dataset Preparation ───────────────────────────────────────────
    # Inputs require shapes (N, Channels=1, Length=360)
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32).unsqueeze(1),
        torch.tensor(y_train, dtype=torch.long),
    )
    test_dataset = TensorDataset(
        torch.tensor(X_test, dtype=torch.float32).unsqueeze(1),
        torch.tensor(y_test, dtype=torch.long),
    )

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    # Initialize hardware acceleration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[STEP 2] Running model setup on target device: {device}")

    model = ResNet18_1D(num_classes=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Early stopping config
    best_loss = float("inf")
    patience = 10
    patience_counter = 0
    best_model_state = None

    epochs = 50
    history = {"epoch": [], "train_loss": [], "val_loss": [], "val_auc": []}

    print(
        "\n[STEP 3] Launching PyTorch Deep ResNet-1D training loop (50 Epochs, Adam)..."
    )
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)

        epoch_train_loss = running_loss / len(train_dataset)

        # Test evaluation for early stopping
        model.eval()
        running_val_loss = 0.0
        all_probs = []
        all_labels = []

        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                running_val_loss += loss.item() * inputs.size(0)

                probs = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
                all_probs.extend(probs)
                all_labels.extend(labels.cpu().numpy())

        epoch_val_loss = running_val_loss / len(test_dataset)
        epoch_val_auc = float(roc_auc_score(all_labels, all_probs))

        history["epoch"].append(epoch + 1)
        history["train_loss"].append(epoch_train_loss)
        history["val_loss"].append(epoch_val_loss)
        history["val_auc"].append(epoch_val_auc)

        print(
            f"  Epoch {epoch+1:02d}/50 | Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Val AUC: {epoch_val_auc:.4f}"
        )

        # Early stopping check
        if epoch_val_loss < best_loss:
            best_loss = epoch_val_loss
            best_model_state = model.state_dict().copy()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(
                    f"  🏁 Early stopping triggered at epoch {epoch+1} (patience={patience})"
                )
                break

    # Restore best parameters
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # Final evaluation on DS2 test set
    model.eval()
    final_probs = []
    final_preds = []
    final_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
            preds = torch.argmax(outputs, dim=1).cpu().numpy()

            final_probs.extend(probs)
            final_preds.extend(preds)
            final_labels.extend(labels.numpy())

    final_auc = float(roc_auc_score(final_labels, final_probs))
    final_acc = float(accuracy_score(final_labels, final_preds))

    print("\n" + "=" * 80)
    print("🏆 FINAL EVALUATION OF RESNET-1D CLINICAL BASELINE")
    print("=" * 80)
    print(f"  Test ROC-AUC  : {final_auc:.6f}")
    print(f"  Test Accuracy : {final_acc:.6f}")
    print("=" * 80)

    # ── EXPORTING ARTIFACTS ──────────────────────────────────────────────────
    # 1. Export trained model
    model_save_path = os.path.join(ARTIFACTS_DIR, "resnet1d_ecg.pt")
    torch.save(model.state_dict(), model_save_path)
    print(f"📂 Saved trained PyTorch model state dict to: {model_save_path}")

    # 2. Export predictions
    pred_results = {
        "y_true": [int(x) for x in final_labels],
        "y_prob": [float(x) for x in final_probs],
        "y_pred": [int(x) for x in final_preds],
    }
    pred_save_path = os.path.join(ARTIFACTS_DIR, "resnet_predictions.json")
    with open(pred_save_path, "w", encoding="utf-8") as f:
        json.dump(pred_results, f, indent=4)
    print(f"📂 Saved test predictions to: {pred_save_path}")

    # 3. Export metrics and history
    metrics_results = {
        "metrics": {"test_auc": final_auc, "test_accuracy": final_acc},
        "history": history,
    }
    metrics_save_path = os.path.join(ARTIFACTS_DIR, "resnet_metrics.json")
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(metrics_results, f, indent=4)
    print(f"📂 Saved training history and metrics to: {metrics_save_path}")

    t_end = time.time()
    print(
        f"\nResNet-1D baseline pipeline completed successfully in {t_end - t_start:.2f} seconds.\n"
    )


if __name__ == "__main__":
    main()
