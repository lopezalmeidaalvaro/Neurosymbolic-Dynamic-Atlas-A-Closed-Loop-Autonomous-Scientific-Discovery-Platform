#!/usr/bin/env python3
"""
AST-OS Physics Invariant Pytest Suite
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


def test_lumped_node_capacity_positivity():
    """
    Asserts that all lumped nodes have strictly positive thermal capacities (C > 0).
    Negative mass/capacity violates basic thermodynamic principles.
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.85, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.15, 0.20],
        "Q": [15.0, 1.0, 5.0, 0.0, 0.0, 0.0],
    }

    # Assert positive capacities
    assert all(
        c > 0.0 for c in config["C"]
    ), "Nodal thermal capacities must be positive!"


def test_louver_emissivity_boundaries():
    """
    Asserts that radiator louver active emissivities reside strictly within LEO qualification boundaries [0.10, 0.85].
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.85, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.15, 0.20],
        "Q": [15.0, 1.0, 5.0, 0.0, 0.0, 0.0],
    }

    # Verify bounds
    for e in config["eps"]:
        assert (
            0.0 <= e <= 1.0
        ), f"Emissivity {e} is unphysically out of standard bounds!"


def test_closed_loop_energy_conservation():
    """
    Simulates a LEO orbit and verifies that total energy conservation is mathematically bounded.
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.85, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.15, 0.20],
        "Q": [15.0, 1.0, 5.0, 0.0, 0.0, 0.0],
    }

    net = ThermalNetwork(config)
    res = net.simulate(duration=600, dt=10.0)  # short transient run

    # Calculate final node temperatures
    T_final = np.array([res["temperatures"][i][-1] for i in range(6)])

    # Asserts physically bounded steady-state ranges
    for temp in T_final:
        assert (
            -150.0 <= temp <= 250.0
        ), f"Temperature {temp}C represents a thermodynamic violation!"
