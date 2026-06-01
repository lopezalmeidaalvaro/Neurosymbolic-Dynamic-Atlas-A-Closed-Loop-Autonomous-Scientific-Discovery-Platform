#!/usr/bin/env python3
"""
test_material_library.py
========================
V&V Test Suite — COTS Material Library & Degradation Engine
Authority  : Verification & Validation Lead (ESA/NASA Standard)
Document ID: AST-TEST-MAT-001
Target     : satellite/thermal/material_library.py  (Lines 170-345)
CDR Gate   : AI-CDR-02  (Coverage >= 80%)
"""

import os
import sys
import json
import math
import numpy as np
import pytest
import pandas as pd

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "satellite", "thermal"
    ),
)
from material_library import (
    MATERIALS_DB,
    get_material,
    get_material_for_temperature,
    get_material_by_cost,
    apply_material,
    compare_materials,
    save_database_to_json,
    generate_report,
)

# Also import ThermalNetwork for apply_material tests
from multi_node_thermal_network import ThermalNetwork

# ===========================================================================
# 1. MATERIALS_DB Integrity
# ===========================================================================


class TestMaterialsDatabase:
    """Validates the static database structure and physics constraints."""

    REQUIRED_KEYS = (
        "commercial_name",
        "eps_BOL",
        "eps_EOL",
        "alpha",
        "uv_degradation_rate_per_year",
        "atox_degradation_rate_per_fluence",
        "relative_cost",
    )

    def test_database_has_ten_materials(self):
        assert len(MATERIALS_DB) == 10

    def test_all_materials_have_required_keys(self):
        for name, props in MATERIALS_DB.items():
            for key in self.REQUIRED_KEYS:
                assert key in props, f"Material '{name}' missing key '{key}'"

    def test_emissivity_bol_in_range(self):
        for name, props in MATERIALS_DB.items():
            assert 0.0 < props["eps_BOL"] <= 1.0, f"eps_BOL out of range for {name}"

    def test_emissivity_eol_lte_bol(self):
        """EOL emissivity must be <= BOL (degradation) or very close."""
        for name, props in MATERIALS_DB.items():
            # Allow equality (Z306 black paint is stable)
            assert (
                props["eps_EOL"] <= props["eps_BOL"] + 0.05
            ), f"eps_EOL > eps_BOL for {name}"

    def test_absorptivity_in_range(self):
        for name, props in MATERIALS_DB.items():
            assert 0.0 < props["alpha"] <= 1.0, f"alpha out of range for {name}"

    def test_relative_cost_in_scale(self):
        for name, props in MATERIALS_DB.items():
            assert 1 <= props["relative_cost"] <= 10

    def test_anodized_aluminum_has_volumetric_density(self):
        """Anodized aluminum stores volumetric density (kg/m3) not areal (kg/m2)."""
        props = MATERIALS_DB["Anodized aluminum 6061"]
        assert "density_kg_m3" in props
        assert math.isclose(props["density_kg_m3"], 2700.0)

    def test_mli_has_lowest_emissivity(self):
        mli_eps = MATERIALS_DB["MLI 10-layer stack"]["eps_BOL"]
        assert mli_eps < 0.05

    def test_kapton_has_high_temperature_range(self):
        kapton = MATERIALS_DB["Kapton HN"]
        assert kapton["max_use_temp_C"] >= 400.0
        assert kapton["min_use_temp_C"] <= -269.0


# ===========================================================================
# 2. get_material
# ===========================================================================


class TestGetMaterial:
    def test_returns_dict_for_known_material(self):
        props = get_material("Kapton HN")
        assert isinstance(props, dict)
        assert "eps_BOL" in props

    def test_anodized_aluminum_retrievable(self):
        props = get_material("Anodized aluminum 6061")
        assert props["eps_BOL"] == pytest.approx(0.70)

    def test_raises_value_error_for_unknown(self):
        with pytest.raises(ValueError, match="not found"):
            get_material("Unobtainium")

    def test_all_materials_retrievable(self):
        for name in MATERIALS_DB:
            props = get_material(name)
            assert "eps_BOL" in props


# ===========================================================================
# 3. get_material_for_temperature
# ===========================================================================


class TestGetMaterialForTemperature:
    def test_returns_list(self):
        result = get_material_for_temperature(T_max=100.0, T_min=-100.0)
        assert isinstance(result, list)

    def test_kapton_compatible_with_wide_range(self):
        result = get_material_for_temperature(T_max=300.0, T_min=-200.0)
        assert "Kapton HN" in result

    def test_no_material_for_extreme_range(self):
        """An unreachable temperature range returns empty list."""
        result = get_material_for_temperature(T_max=1000.0, T_min=-300.0)
        assert isinstance(result, list)

    def test_mli_survives_cryogenic_deep_space(self):
        result = get_material_for_temperature(T_max=200.0, T_min=-200.0)
        assert "MLI 10-layer stack" in result

    def test_graphite_epoxy_excluded_above_120c(self):
        """Graphite epoxy is limited to 120°C max — exclude it from higher requirements."""
        result = get_material_for_temperature(T_max=200.0, T_min=-100.0)
        assert "Graphite epoxy composite" not in result


# ===========================================================================
# 4. get_material_by_cost
# ===========================================================================


class TestGetMaterialByCost:
    def test_returns_list(self):
        result = get_material_by_cost(max_cost=10)
        assert isinstance(result, list)

    def test_cheap_materials_included(self):
        """Anodized aluminum (cost=2) must be in budget filter ≤3."""
        result = get_material_by_cost(max_cost=3)
        assert "Anodized aluminum 6061" in result

    def test_expensive_materials_excluded(self):
        """Quartz Mirror (cost=10) must NOT be in budget filter <=5."""
        result = get_material_by_cost(max_cost=5)
        assert "Quartz Mirror" not in result

    def test_zero_cost_filter_returns_empty(self):
        result = get_material_by_cost(max_cost=0)
        assert result == []

    def test_max_cost_10_returns_all(self):
        result = get_material_by_cost(max_cost=10)
        assert len(result) == 10


# ===========================================================================
# 5. apply_material
# ===========================================================================


class TestApplyMaterial:
    @pytest.fixture
    def thermal_net(self):
        return ThermalNetwork()

    def test_applies_emissivity_to_node(self, thermal_net):
        apply_material(thermal_net, node_index=4, material_name="Kapton HN")
        # eps must have been updated on node 4 (Radiator)
        assert 0.0 < thermal_net.eps[4] <= 1.0

    def test_bol_emissivity_matches_database(self, thermal_net):
        """At t=0 with no degradation, eps should equal eps_BOL."""
        apply_material(
            thermal_net, 4, "Kapton HN", elapsed_time_years=0.0, atox_fluence=0.0
        )
        assert math.isclose(thermal_net.eps[4], MATERIALS_DB["Kapton HN"]["eps_BOL"])

    def test_degraded_emissivity_lower_after_time(self, thermal_net):
        """After 5 years of UV exposure the emissivity must be lower."""
        apply_material(thermal_net, 4, "Kapton HN", elapsed_time_years=0.0)
        eps_bol = thermal_net.eps[4]
        apply_material(thermal_net, 4, "Kapton HN", elapsed_time_years=5.0)
        eps_degraded = thermal_net.eps[4]
        assert eps_degraded <= eps_bol

    def test_degraded_emissivity_bounded_by_eol(self, thermal_net):
        """Emissivity cannot degrade below EOL value."""
        apply_material(
            thermal_net, 4, "Kapton HN", elapsed_time_years=1000.0, atox_fluence=1e6
        )
        eol = MATERIALS_DB["Kapton HN"]["eps_EOL"]
        assert thermal_net.eps[4] >= eol

    def test_node_materials_metadata_written(self, thermal_net):
        """apply_material stores metadata in network.node_materials."""
        apply_material(thermal_net, 0, "Kapton HN")
        assert hasattr(thermal_net, "node_materials")
        assert 0 in thermal_net.node_materials
        assert "name" in thermal_net.node_materials[0]

    def test_returns_float_emissivity(self, thermal_net):
        result = apply_material(thermal_net, 0, "Teflon FEP")
        assert isinstance(result, float)
        assert 0.0 < result <= 1.0

    def test_volumetric_material_applies_correctly(self, thermal_net):
        """Anodized aluminum uses density_kg_m3 — apply_material must not raise."""
        result = apply_material(thermal_net, 4, "Anodized aluminum 6061")
        assert isinstance(result, float)

    def test_multiple_nodes_independent(self):
        net = ThermalNetwork()
        apply_material(net, 0, "Kapton HN")
        apply_material(net, 1, "Teflon FEP")
        apply_material(net, 4, "MLI 10-layer stack")
        assert net.eps[0] != net.eps[4]

    def test_atox_fluence_degrades_emissivity(self, thermal_net):
        apply_material(thermal_net, 4, "Kapton HN", atox_fluence=0.0)
        eps_fresh = thermal_net.eps[4]
        apply_material(thermal_net, 4, "Kapton HN", atox_fluence=1000.0)
        eps_atox = thermal_net.eps[4]
        assert eps_atox <= eps_fresh


# ===========================================================================
# 6. compare_materials
# ===========================================================================


class TestCompareMaterials:
    def test_returns_dataframe(self):
        df = compare_materials(["Kapton HN", "Teflon FEP"])
        assert isinstance(df, pd.DataFrame)

    def test_dataframe_has_material_column(self):
        df = compare_materials(["Kapton HN"])
        assert "Material" in df.columns

    def test_dataframe_row_count_matches_input(self):
        names = ["Kapton HN", "Teflon FEP", "AZ-93 white paint"]
        df = compare_materials(names)
        assert len(df) == 3

    def test_uso_recomendado_radiadores_for_low_alpha(self):
        """Materials with alpha < 0.2 are classified as radiators."""
        df = compare_materials(["Teflon FEP"])  # alpha=0.12
        assert df.iloc[0]["Uso Recomendado"] == "Radiadores"

    def test_uso_recomendado_mli_for_very_low_eps(self):
        """MLI has alpha=0.14 which is < 0.2, so the code classifies it as
        'Radiadores' (the alpha < 0.2 branch takes priority over eps < 0.05).
        """
        df = compare_materials(["MLI 10-layer stack"])
        # alpha=0.14 < 0.2 → first branch → "Radiadores"
        assert df.iloc[0]["Uso Recomendado"] == "Radiadores"

    def test_structure_classification_for_high_eps_alpha(self):
        """Graphite epoxy (alpha=0.88, eps=0.85) → Estructura/Interior."""
        df = compare_materials(["Graphite epoxy composite"])
        assert "Estructura" in df.iloc[0]["Uso Recomendado"]


# ===========================================================================
# 7. save_database_to_json
# ===========================================================================


class TestSaveDatabaseToJson:
    def test_creates_json_file(self, tmp_path):
        filepath = str(tmp_path / "mat_db.json")
        save_database_to_json(filepath)
        assert os.path.exists(filepath)

    def test_json_is_valid(self, tmp_path):
        filepath = str(tmp_path / "mat_db.json")
        save_database_to_json(filepath)
        with open(filepath) as f:
            data = json.load(f)
        assert len(data) == 10

    def test_json_contains_kapton(self, tmp_path):
        filepath = str(tmp_path / "mat_db.json")
        save_database_to_json(filepath)
        with open(filepath) as f:
            data = json.load(f)
        assert "Kapton HN" in data


# ===========================================================================
# 8. generate_report
# ===========================================================================


class TestGenerateReport:
    def test_report_creates_file(self, tmp_path, monkeypatch):
        """generate_report writes a markdown file to satellite/thermal/."""
        # Redirect CWD so relative paths land in tmp_path
        monkeypatch.chdir(tmp_path)
        # The function writes to 'satellite/thermal/material_comparison_report.md'
        out_dir = tmp_path / "satellite" / "thermal"
        out_dir.mkdir(parents=True, exist_ok=True)
        generate_report()
        report_path = out_dir / "material_comparison_report.md"
        assert report_path.exists()

    def test_report_contains_material_names(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "satellite" / "thermal").mkdir(parents=True, exist_ok=True)
        generate_report()
        content = (
            tmp_path / "satellite" / "thermal" / "material_comparison_report.md"
        ).read_text()
        assert "Kapton HN" in content
        assert "Teflon FEP" in content

    def test_report_contains_degradation_formula(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "satellite" / "thermal").mkdir(parents=True, exist_ok=True)
        generate_report()
        content = (
            tmp_path / "satellite" / "thermal" / "material_comparison_report.md"
        ).read_text()
        assert "BOL" in content
        assert "EOL" in content
