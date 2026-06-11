#!/usr/bin/env python3
"""
test_cad_conduct_math.py
========================
V&V Test Suite — CAD Conductive Heat Flow Solver
Authority  : Verification & Validation Lead (ESA/NASA Standard)
Document ID: AST-TEST-CAD-001
Target     : satellite/thermal/cad_thermal_importer.py  (Lines 275-385)
CDR Gate   : AI-CDR-02  (Coverage >= 80%)

Coverage targets:
  - CADThermalMesh.create_dummy_cad_file
  - CADThermalMesh.import_cad
  - CADThermalMesh.generate_thermal_mesh (cube / plate_with_fins / cylinder)
  - CADThermalMesh.extract_thermal_network
  - CADThermalMesh.simulate_3d_thermal_loop   (Lines 275-323)
  - CADThermalMesh.simulate_3d_thermal vectorized (Lines 325-385)
  - CADThermalMesh.visualize_3d_heatmap
  - optimize_geometry
"""

import os
import sys
import json
import math
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "satellite", "thermal"
    ),
)
from cad_thermal_importer import CADThermalMesh, optimize_geometry, K_AL, RHO_AL, CP_AL

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture(scope="module")
def mesh():
    return CADThermalMesh(voxel_size=0.01)


@pytest.fixture(scope="module")
def stl_file(tmp_path_factory):
    """Creates a temporary STL file for import testing."""
    tmp = tmp_path_factory.mktemp("stl")
    stl_path = str(tmp / "test_cube.stl")
    m = CADThermalMesh()
    m.create_dummy_cad_file(stl_path, shape="cube")
    return stl_path


@pytest.fixture(scope="module")
def cube_mesh_data(mesh, stl_file):
    return mesh.import_cad(stl_file)


@pytest.fixture(scope="module")
def cube_voxels(mesh, cube_mesh_data):
    return mesh.generate_thermal_mesh(cube_mesh_data, shape_type="cube")


@pytest.fixture(scope="module")
def cube_network(mesh, cube_voxels):
    return mesh.extract_thermal_network(cube_voxels)


# ===========================================================================
# 1. STL File Generation
# ===========================================================================


class TestCreateDummyCadFile:
    def test_creates_file(self, tmp_path):
        m = CADThermalMesh()
        path = str(tmp_path / "cube.stl")
        m.create_dummy_cad_file(path, shape="cube")
        assert os.path.exists(path)

    def test_file_contains_solid_keyword(self, tmp_path):
        m = CADThermalMesh()
        path = str(tmp_path / "cube2.stl")
        m.create_dummy_cad_file(path)
        with open(path) as f:
            content = f.read()
        assert "solid cubesat_part" in content
        assert "endsolid cubesat_part" in content

    def test_file_contains_facets(self, tmp_path):
        m = CADThermalMesh()
        path = str(tmp_path / "cube3.stl")
        m.create_dummy_cad_file(path)
        with open(path) as f:
            content = f.read()
        assert "facet normal" in content
        assert "vertex" in content

    def test_creates_parent_directories(self, tmp_path):
        m = CADThermalMesh()
        path = str(tmp_path / "subdir" / "model.stl")
        m.create_dummy_cad_file(path)
        assert os.path.exists(path)


# ===========================================================================
# 2. CAD Import
# ===========================================================================


class TestImportCad:
    def test_import_returns_dict_with_keys(self, cube_mesh_data):
        for key in (
            "vertices",
            "faces",
            "min_coords",
            "max_coords",
            "volume_m3",
            "surface_area_m2",
            "center_of_mass",
        ):
            assert key in cube_mesh_data

    def test_vertices_shape(self, cube_mesh_data):
        verts = cube_mesh_data["vertices"]
        assert verts.ndim == 2 and verts.shape[1] == 3

    def test_faces_shape(self, cube_mesh_data):
        faces = cube_mesh_data["faces"]
        assert faces.ndim == 2 and faces.shape[1] == 3

    def test_volume_approximately_correct(self, cube_mesh_data):
        # 10x10x10 cm cube = 0.001 m3
        assert math.isclose(cube_mesh_data["volume_m3"], 0.001, rel_tol=1e-3)

    def test_surface_area_approximately_correct(self, cube_mesh_data):
        # 6 faces * (0.1m)^2 = 0.06 m2
        assert math.isclose(cube_mesh_data["surface_area_m2"], 0.06, rel_tol=1e-3)

    def test_auto_generates_missing_cad(self, tmp_path):
        """import_cad creates a dummy STL if the file is missing."""
        m = CADThermalMesh()
        missing = str(tmp_path / "not_here.stl")
        data = m.import_cad(missing)
        assert "vertices" in data
        assert os.path.exists(missing)


# ===========================================================================
# 3. Thermal Mesh Voxelization
# ===========================================================================


class TestGenerateThermalMesh:
    def test_cube_voxel_count(self, mesh, cube_mesh_data):
        voxels = mesh.generate_thermal_mesh(cube_mesh_data, shape_type="cube")
        assert len(voxels) == 1000  # 10^3

    def test_plate_with_fins_voxel_count(self, mesh, cube_mesh_data):
        voxels = mesh.generate_thermal_mesh(
            cube_mesh_data, shape_type="plate_with_fins"
        )
        # Base: 10*3*10=300 + Fins: 5 fins * 10 * 5 = 250 -> 550 (some overlap at y=3-7)
        # Actual: unique occupancy. Just verify it's in range and non-zero.
        assert 300 <= len(voxels) <= 700

    def test_cylinder_voxel_count(self, mesh, cube_mesh_data):
        voxels = mesh.generate_thermal_mesh(cube_mesh_data, shape_type="cylinder")
        # Cylinder of radius 4.5 in 10x10 grid: ~636 voxels
        assert 400 <= len(voxels) <= 800

    def test_voxels_are_tuples(self, cube_voxels):
        assert all(isinstance(v, tuple) and len(v) == 3 for v in cube_voxels)

    def test_voxel_coords_within_grid(self, cube_voxels):
        for x, y, z in cube_voxels:
            assert 0 <= x < 10 and 0 <= y < 10 and 0 <= z < 10


# ===========================================================================
# 4. Thermal Network Extraction
# ===========================================================================


class TestExtractThermalNetwork:
    def test_network_has_nodes_and_matrix(self, cube_network):
        assert "nodes" in cube_network
        assert "conductance_matrix" in cube_network

    def test_node_count_matches_voxels(self, cube_voxels, cube_network):
        assert len(cube_network["nodes"]) == len(cube_voxels)

    def test_node_thermal_capacity(self, cube_network):
        """Each voxel's thermal capacity: C = V * rho * Cp."""
        expected_C = (0.01**3) * RHO_AL * CP_AL
        for node in cube_network["nodes"]:
            assert math.isclose(node["C"], expected_C, rel_tol=1e-4)

    def test_cpu_node_has_heat_load(self, cube_network):
        """Node at (4, 4, 4) carries 15W internal heat load."""
        cpu_nodes = [n for n in cube_network["nodes"] if n["grid_coords"] == (4, 4, 4)]
        assert len(cpu_nodes) == 1
        assert math.isclose(cpu_nodes[0]["Q"], 15.0)

    def test_interior_nodes_no_radiation(self, cube_network):
        """Interior nodes (is_boundary=False) have zero radiating area."""
        interior = [n for n in cube_network["nodes"] if not n["is_boundary"]]
        assert len(interior) > 0
        for n in interior:
            assert n["A_rad"] == pytest.approx(0.0)
            assert n["eps"] == pytest.approx(0.0)

    def test_boundary_nodes_have_radiation(self, cube_network):
        """Boundary nodes must have A_rad > 0 and eps > 0."""
        boundary = [n for n in cube_network["nodes"] if n["is_boundary"]]
        assert len(boundary) > 0
        for n in boundary:
            assert n["A_rad"] > 0.0
            assert n["eps"] > 0.0

    def test_conductance_matrix_symmetric(self, cube_network):
        k = np.array(cube_network["conductance_matrix"])
        assert np.allclose(k, k.T, atol=1e-9)

    def test_conductance_base_value(self, cube_network):
        """Adjacent voxel conductance = K_AL * voxel_size = 167 * 0.01 = 1.67 W/K."""
        k = np.array(cube_network["conductance_matrix"])
        nonzero = k[k > 0.0]
        assert np.allclose(nonzero, K_AL * 0.01, rtol=1e-4)

    def test_network_json_written(self, tmp_path, monkeypatch):
        """extract_thermal_network writes cad_thermal_network.json."""
        monkeypatch.chdir(tmp_path)
        m = CADThermalMesh(voxel_size=0.05)  # Use large voxels for speed (2^3=8 voxels)
        small_voxels = [(x, y, z) for x in range(2) for y in range(2) for z in range(2)]
        m.extract_thermal_network(small_voxels)
        assert os.path.exists(tmp_path / "cad_thermal_network.json")


# ===========================================================================
# 5. 3D Thermal Simulation — Loop Version (Lines 275-323)
# ===========================================================================


class TestSimulate3dThermalLoop:
    """Targets the loop-based ODE solver branch (simulate_3d_thermal_loop)."""

    @pytest.fixture(scope="class")
    def small_network(self):
        """Tiny 8-node network for fast loop-solver tests."""
        m = CADThermalMesh(voxel_size=0.05)
        voxels = [(x, y, z) for x in range(2) for y in range(2) for z in range(2)]
        return m, m.extract_thermal_network(voxels)

    def test_loop_solver_returns_array(self, small_network):
        m, network = small_network
        temps = m.simulate_3d_thermal_loop(network, duration=60)
        assert isinstance(temps, np.ndarray)

    def test_loop_solver_shape(self, small_network):
        m, network = small_network
        n_nodes = len(network["nodes"])
        temps = m.simulate_3d_thermal_loop(network, duration=60)
        assert temps.shape == (n_nodes,)

    def test_loop_solver_temperatures_in_celsius_range(self, small_network):
        m, network = small_network
        temps = m.simulate_3d_thermal_loop(network, duration=60)
        # Should be in Celsius after subtracting 273.15 from Kelvin initial
        assert np.all(temps > -100.0)
        assert np.all(temps < 500.0)

    def test_loop_solver_no_nans(self, small_network):
        m, network = small_network
        temps = m.simulate_3d_thermal_loop(network, duration=60)
        assert not np.any(np.isnan(temps))

    def test_simulate_3d_thermal_non_vectorized_calls_loop(self, small_network):
        """simulate_3d_thermal(vectorized=False) must delegate to loop solver."""
        m, network = small_network
        temps = m.simulate_3d_thermal(network, duration=60, vectorized=False)
        assert isinstance(temps, np.ndarray)
        assert temps.shape == (len(network["nodes"]),)


# ===========================================================================
# 6. 3D Thermal Simulation — Vectorized Version (Lines 325-385)
# ===========================================================================


class TestSimulate3dThermalVectorized:
    """Targets the vectorized ODE solver and CSV export branch."""

    @pytest.fixture(scope="class")
    def tiny_result(self, tmp_path_factory):
        """Fast 8-node simulation with CSV output."""
        tmp = tmp_path_factory.mktemp("cad_sim")
        m = CADThermalMesh(voxel_size=0.05)
        voxels = [(x, y, z) for x in range(2) for y in range(2) for z in range(2)]
        network = m.extract_thermal_network(voxels)
        # Run simulation from tmp directory so CSV lands in tmp
        original = os.getcwd()
        os.chdir(str(tmp))
        temps = m.simulate_3d_thermal(network, duration=120, vectorized=True)
        os.chdir(original)
        return temps, tmp

    def test_vectorized_returns_array(self, tiny_result):
        temps, _ = tiny_result
        assert isinstance(temps, np.ndarray)

    def test_vectorized_shape(self, tiny_result):
        temps, _ = tiny_result
        assert temps.ndim == 1
        assert temps.shape[0] == 8

    def test_vectorized_temperatures_finite(self, tiny_result):
        temps, _ = tiny_result
        assert np.all(np.isfinite(temps))

    def test_vectorized_csv_generated(self, tiny_result):
        _, tmp = tiny_result
        csv_path = tmp / "cad_simulation_results.csv"
        assert csv_path.exists()

    def test_vectorized_csv_has_time_column(self, tiny_result):
        import pandas as pd

        _, tmp = tiny_result
        df = pd.read_csv(str(tmp / "cad_simulation_results.csv"))
        assert "Time_s" in df.columns

    def test_vectorized_temperatures_in_plausible_range(self, tiny_result):
        temps, _ = tiny_result
        # Starting at 20°C (293.15K), 2-minute sim should not exceed 200°C
        assert np.all(temps < 200.0)
        assert np.all(temps > -273.0)


# ===========================================================================
# 7. 3D Heatmap Visualisation
# ===========================================================================


class TestVisualize3dHeatmap:
    def test_saves_png_file(self, tmp_path):
        m = CADThermalMesh(voxel_size=0.05)
        voxels = [(x, y, z) for x in range(2) for y in range(2) for z in range(2)]
        network = m.extract_thermal_network(voxels)
        # Uniform temperatures array (length = 8 nodes)
        temps = np.full(8, 20.0)
        output = str(tmp_path / "heatmap.png")
        m.visualize_3d_heatmap(network, temps, output)
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0


# ===========================================================================
# 8. optimize_geometry (report generation)
# ===========================================================================


class TestOptimizeGeometry:
    def test_optimize_geometry_creates_report(self, tmp_path):
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            optimize_geometry()
        finally:
            os.chdir(original)
        report = tmp_path / "cad_optimization_report.md"
        assert report.exists()

    def test_report_contains_geometry_section(self, tmp_path):
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            optimize_geometry()
        finally:
            os.chdir(original)
        with open(str(tmp_path / "cad_optimization_report.md")) as f:
            content = f.read()
        assert "Geometry" in content or "geometry" in content
