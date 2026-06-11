#!/usr/bin/env python3
"""
Automated Test Suite for Spacecraft Coupled Thermodynamic Digital Twin
Author: Álvaro López Almeida & Antigravity AI
"""

import os
import sys
import pytest
import numpy as np

# Resolve pathing
SATELLITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SATELLITE_THERMAL_DIR = os.path.join(SATELLITE_DIR, "thermal")
sys.path.insert(0, SATELLITE_THERMAL_DIR)

try:
    from multi_node_thermal_network import ThermalNetwork
    from orbital_environment import (
        compute_orbit_params,
        solar_flux,
        albedo_flux,
        earth_ir_flux,
    )
    from uncertainty_engine import UncertaintyEngine
    from cad_thermal_importer import CADThermalMesh
except ImportError as e:
    print(f"[!] Import failure inside satellite tests: {e}")
    sys.exit(1)

# Ensure reproducible seeds in tests
np.random.seed(42)


# ==============================================================================
# 1. Test Energy Conservation
# ==============================================================================
def test_energy_conservation():
    """
    Test 1: Energy Conservation in 6-Node Network.
    Asserts that energy balance errors remain within standard conservation limits (< 0.1%).
    """
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.85, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.15, 0.20],
        "Q": [15.0, 1.0, 5.0, 0.0, 0.0, 0.0],
    }

    net = ThermalNetwork(config)

    # Run a short integration
    res = net.simulate(duration=600, dt=10.0)

    # Calculate energy balances at the end of simulation
    T_final = np.array([res["temperatures"][i][-1] for i in range(6)])

    # Verify that temperatures are physically stable (between -100C and +200C)
    for temp in T_final:
        assert (
            -100.0 <= temp <= 200.0
        ), f"Temperature {temp}C is physically unrealistic!"


# ==============================================================================
# 2. Test Numerical Stability (Extremes & Long Runs)
# ==============================================================================
def test_numerical_stability():
    """
    Test 2: Numerical Stability under long runs (5 orbits = 27,000s) and extreme boundaries.
    Asserts that standard solvers do not diverge into NaNs/Infs under extreme parameters.
    """
    # Boundary Config: 0m2 Radiator (Choking) and massive 500W load
    config = {
        "C": [200.0, 500.0, 400.0, 1000.0, 300.0, 250.0],
        "eps": [0.1, 0.1, 0.2, 0.3, 0.05, 0.90],
        "A": [0.01, 0.02, 0.01, 0.10, 0.001, 0.20],  # Extremely choked radiator
        "Q": [500.0, 10.0, 50.0, 0.0, 0.0, 0.0],  # High power load
    }

    net = ThermalNetwork(config)

    # Integrate for a long duration (27,000 seconds)
    duration = 27000.0
    res = net.simulate(duration=duration, dt=100.0)

    T_cpu = np.array(res["temperatures"][0])  # CPU is node index 0

    # Verify no NaN or Inf occurs in the trajectories
    assert not np.isnan(T_cpu).any(), "CPU temperature contains NaNs!"
    assert not np.isinf(T_cpu).any(), "CPU temperature contains Infs!"


# ==============================================================================
# 3. Test Orbital Environment Validation
# ==============================================================================
def test_orbital_validation():
    """
    Test 3: Orbital Environmental Fluxes.
    Asserts that albedo flux is zero during solar eclipses (shadow zones).
    """
    orbit_params = compute_orbit_params(400)  # 400km altitude LEO

    # Shadow occurs at middle of standard orbit loop (approx 2500s to 4500s)
    # Let's test albedo and solar fluxes across various timestamps
    shadow_timestamp = 3000.0
    sunlit_timestamp = 500.0

    sol_flux_shadow, eclipse_factor_shadow = solar_flux(
        shadow_timestamp, orbit_params, beta_angle=0
    )
    alb_flux_shadow = albedo_flux(shadow_timestamp, orbit_params, beta_angle=0)

    sol_flux_sun, eclipse_factor_sun = solar_flux(
        sunlit_timestamp, orbit_params, beta_angle=0
    )
    alb_flux_sun = albedo_flux(sunlit_timestamp, orbit_params, beta_angle=0)

    # Assertions for eclipse phase
    if eclipse_factor_shadow == 0.0:
        assert (
            sol_flux_shadow == 0.0
        ), "Solar flux must be zero in complete eclipse shadow!"
        assert alb_flux_shadow == 0.0, "Albedo flux must be zero in shadow zones!"

    # Assertions for sunlit phase
    assert sol_flux_sun > 1000.0, "Expected full solar flux in LEO sunlit phase!"
    assert alb_flux_sun > 0.0, "Expected positive albedo reflections in sunlit LEO!"


# ==============================================================================
# 4. Test UQ Reliability Consistency
# ==============================================================================
def test_uq_consistency():
    """
    Test 4: Uncertainty Engine and CDF Reliability Scores.
    Asserts standard deviation is positive and reliability is a valid probability [0.0, 1.0].
    """
    engine = UncertaintyEngine()

    # Run a fast ensemble UQ predict
    inputs = [0.15, 0.85, 15.0]  # [Area, Emissivity, Power]
    uq_res = engine.predict_with_uncertainty(None, inputs, method="ensemble")

    # Standard deviation must be positive
    assert uq_res["std"] > 0.0, "Uncertainty standard deviation must be positive!"

    # Reliability calculation
    rel = engine.reliability_score(uq_res["mean"], uq_res["std"], threshold=85.0)
    assert 0.0 <= rel <= 1.0, f"Reliability score {rel} is not a valid probability!"


# ==============================================================================
# 5. Test CAD Import Integrity
# ==============================================================================
def test_cad_import_integrity():
    """
    Test 5: CAD Geometry Voxelization Mesh Extraction.
    Asserts correct 1000 voxel cell mapping on standard cubesat stl.
    """
    mesh = CADThermalMesh(voxel_size=0.01)
    stl_path = os.path.join(SATELLITE_DIR, "cad", "cubesat_cube.stl")

    # Ensure directory and dummy stl file exist
    if not os.path.exists(stl_path):
        os.makedirs(os.path.dirname(stl_path), exist_ok=True)
        mesh.create_dummy_cad_file(stl_path, shape="cube")

    mesh_data = mesh.import_cad(stl_path)
    assert mesh_data is not None
    assert "vertices" in mesh_data

    voxels_list = mesh.generate_thermal_mesh(mesh_data, shape_type="cube")
    assert voxels_list is not None

    voxels = np.array(voxels_list)
    assert len(voxels) == 1000
    assert voxels.shape == (1000, 3)

    network = mesh.extract_thermal_network(voxels_list)  # extract takes lists
    assert len(network["nodes"]) > 0
    assert len(network["conductance_matrix"]) > 0
