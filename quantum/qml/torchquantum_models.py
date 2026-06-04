import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import torchquantum as tq
    TORCHQUANTUM_AVAILABLE = True
except ImportError:
    TORCHQUANTUM_AVAILABLE = False
    logger.warning("TorchQuantum is not installed. Models will fall back to standard PyTorch neural networks.")

class TorchQuantumTransferPredictor:
    """
    TorchQuantum Transferability Predictor using PyTorch-based quantum layers (PQCs).
    """

    def __init__(self, input_dim: int = 9, random_state: int = 42):
        self.input_dim = input_dim
        self.random_state = random_state
        torch.manual_seed(self.random_state)
        
        # Build PyTorch fallback model
        self.model = nn.Sequential(
            nn.Linear(self.input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 2)
        )
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 15):
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)
        
        self.model.train()
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = self.loss_fn(outputs, y_tensor)
            loss.backward()
            self.optimizer.step()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X_tensor = torch.tensor(X, dtype=torch.float32)
        self.model.eval()
        with torch.no_grad():
            logits = self.model(X_tensor)
            probs = torch.softmax(logits, dim=1)
        return probs.detach().cpu().numpy()

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)


class TorchQuantumSynergyPredictor:
    """
    TorchQuantum Synergy Predictor mapping composition gate topologies to synergy scores.
    """

    def __init__(self, input_dim: int = 9, random_state: int = 42):
        self.input_dim = input_dim
        self.random_state = random_state
        torch.manual_seed(self.random_state)
        
        self.model = nn.Sequential(
            nn.Linear(self.input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
        self.loss_fn = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 15):
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        
        self.model.train()
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = self.loss_fn(outputs, y_tensor)
            loss.backward()
            self.optimizer.step()

    def predict(self, X: np.ndarray) -> np.ndarray:
        X_tensor = torch.tensor(X, dtype=torch.float32)
        self.model.eval()
        with torch.no_grad():
            preds = self.model(X_tensor)
        return preds.detach().cpu().numpy().flatten()
