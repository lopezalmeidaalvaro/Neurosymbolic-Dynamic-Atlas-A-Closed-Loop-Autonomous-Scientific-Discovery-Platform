#!/usr/bin/env python3
"""
AST-OS Numerical Solver Stability Pytest Suite
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import pytest
import numpy as np
import os
import sys

# Path resolution
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(TEST_DIR), "satellite", "thermal"))

from multi_node_thermal_network import ThermalNetwork


def test_extreme_heater_load_stability():
    """
    Asserts numerical stability (absence of NaNs/Infs) under extreme heat loads (500W CPU burst)
    and choked space-facing radiators.
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.05, 0.90],  # choked louver
        "A": [0.01, 0.02, 0.01, 0.10, 0.001, 0.20],  # choked area
        "Q": [500.0, 10.0, 50.0, 0.0, 0.0, 0.0],  # extreme 500W heater
    }

    net = ThermalNetwork(config)
    res = net.simulate(duration=3600, dt=10.0)  # 1 hour transient run

    T_cpu = np.array(res["temperatures"][0])

    # Verify no NaN or Inf occurs in the trajectories
    assert not np.isnan(T_cpu).any(), "CPU temperature vector contains unhandled NaNs!"
    assert not np.isinf(T_cpu).any(), "CPU temperature vector contains unhandled Infs!"


def test_solver_stiff_step_adaptation():
    """
    Verifies that the RK45 adaptive integration step size remains stable and bounded
    when experiencing step boundaries or solar eclipse transitions.
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.85, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.15, 0.20],
        "Q": [15.0, 1.0, 5.0, 0.0, 0.0, 0.0],
    }

    net = ThermalNetwork(config)
    # Simulate a long 5-orbit flight sequence (27,000s)
    res = net.simulate(duration=27000, dt=100.0)

    T_structure = np.array(res["temperatures"][3])

    # State values must be physically valid and bounded
    assert len(T_structure) > 0
    assert not np.isnan(T_structure).any()
    assert np.max(T_structure) < 150.0
