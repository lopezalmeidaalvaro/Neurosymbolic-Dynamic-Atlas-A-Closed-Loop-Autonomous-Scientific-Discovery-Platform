import os
import sys
import numpy as np


class BaseHILAndSensorInterface:
    """
    Common base class for Hardware-in-the-Loop (HIL) and TVAC Chamber sensor data telemetry.
    Unifies physical sensor reading emulations, noise injection, and correlation metrics.
    """

    def __init__(self, noise_std=0.5):
        self.noise_std = noise_std
        # Ensure reproducibility
        np.random.seed(42)

    def read_sensor_with_noise(self, true_temp, custom_noise=None):
        """
        Applies normal distributed Gaussian noise to represent standard physical thermocouples (PT100).
        """
        sigma = custom_noise if custom_noise is not None else self.noise_std
        return true_temp + np.random.normal(0.0, sigma)

    def calculate_correlation_error(self, measured, predicted):
        """
        Computes absolute prediction residuals between physical sensors and digital twin estimates.
        """
        return float(np.abs(measured - predicted))
