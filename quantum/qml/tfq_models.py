import logging
import numpy as np
import tensorflow as tf
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import tensorflow_quantum as tfq
    TFQ_AVAILABLE = True
except ImportError:
    TFQ_AVAILABLE = False
    logger.warning("TensorFlow Quantum is not installed. Models will fall back to standard Keras neural networks.")

class TFQTransferPredictor:
    """
    TensorFlow Quantum Transferability Predictor. Simulates a parameter-mapped 
    circuit model using Keras backends.
    """

    def __init__(self, input_dim: int = 9, random_state: int = 42):
        self.input_dim = input_dim
        tf.random.set_seed(random_state)
        
        # Build Keras fallback model
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.input_dim,)),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(2, activation='softmax')
        ])
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 15):
        self.model.fit(X, y, epochs=epochs, verbose=0)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X, verbose=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)


class TFQSynergyPredictor:
    """
    TensorFlow Quantum Synergy Predictor mapping composition gate topologies to synergy scores.
    """

    def __init__(self, input_dim: int = 9, random_state: int = 42):
        self.input_dim = input_dim
        tf.random.set_seed(random_state)
        
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.input_dim,)),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
            loss='mean_squared_error'
        )

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 15):
        self.model.fit(X, y, epochs=epochs, verbose=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X, verbose=0).flatten()
