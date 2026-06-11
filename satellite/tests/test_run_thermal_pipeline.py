#!/usr/bin/env python3
"""
test_run_thermal_pipeline.py
============================
V&V Test Suite — Satellite Thermal Pipeline Orchestrator
Authority  : Verification & Validation Lead (ESA/NASA Standard)
Document ID: AST-TEST-PIPE-001
Target     : satellite/run_thermal_pipeline.py  (Lines 8-110)
CDR Gate   : AI-CDR-02  (Coverage >= 80%)
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# ---------------------------------------------------------------------------
# Patch config import so the module loads without requiring the real config.py
# being in a specific location relative to CWD.
# ---------------------------------------------------------------------------
# We must add the project root to sys.path so that `import config` works.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
# We need to import from satellite/, not tests/
SATELLITE_DIR = PROJECT_ROOT / "satellite"
sys.path.insert(0, str(SATELLITE_DIR.parent))

import importlib
import types

# Build a minimal mock config module so the pipeline module imports cleanly
mock_config = types.ModuleType("config")
mock_config.SATELLITE_DIR = SATELLITE_DIR
sys.modules.setdefault("config", mock_config)

# Now import the pipeline
import satellite.run_thermal_pipeline as rtp
from satellite.run_thermal_pipeline import STAGES, print_step, main

# ===========================================================================
# 1. STAGES Dictionary
# ===========================================================================


class TestStagesDictionary:
    """Validates the static pipeline stage registry."""

    def test_stages_is_dict(self):
        assert isinstance(STAGES, dict)

    def test_stages_has_expected_keys(self):
        expected = {
            "T9",
            "T11",
            "T17",
            "T21",
            "T22",
            "T23",
            "T24",
            "T25",
            "T26",
            "T27",
            "T28",
        }
        assert expected == set(STAGES.keys())

    def test_all_values_are_strings(self):
        for key, val in STAGES.items():
            assert isinstance(val, str), f"Stage {key} value is not a string"

    def test_t9_is_thermal_network(self):
        assert "multi_node_thermal_network" in STAGES["T9"]

    def test_t11_is_geometry_optimizer(self):
        assert "geometry_topology_optimizer" in STAGES["T11"]

    def test_all_stages_end_with_py(self):
        for key, val in STAGES.items():
            assert val.endswith(".py"), f"Stage {key} path does not end with .py"


# ===========================================================================
# 2. print_step
# ===========================================================================


class TestPrintStep:
    def test_print_step_does_not_raise(self, capsys):
        print_step("T9")
        captured = capsys.readouterr()
        assert "T9" in captured.out
        assert STAGES["T9"] in captured.out

    def test_print_step_outputs_separator(self, capsys):
        print_step("T11")
        captured = capsys.readouterr()
        assert "=" * 10 in captured.out

    def test_print_step_t28(self, capsys):
        print_step("T28")
        captured = capsys.readouterr()
        assert "T28" in captured.out


# ===========================================================================
# 3. main() — Argument Parsing & Stage Selection
# ===========================================================================


class TestMainArgumentParsing:
    """Tests main() with mocked subprocess so no scripts are actually executed."""

    def _run_main(self, args, monkeypatch):
        """Helper: patch sys.argv and subprocess.run, then call main()."""
        monkeypatch.setattr(sys, "argv", ["pipeline"] + args)
        results = []

        def fake_run(cmd, cwd, check):
            # Record what was called without executing
            results.append(cmd)
            return MagicMock(returncode=0)

        with patch(
            "satellite.run_thermal_pipeline.subprocess.run", side_effect=fake_run
        ):
            with patch(
                "satellite.run_thermal_pipeline.time.time", side_effect=[0.0, 1.0] * 20
            ):
                main()

        return results

    def test_default_runs_all_stages(self, monkeypatch, capsys):
        """Default (--from-stage T9 --to-stage T28) must run all 11 stages."""
        calls = self._run_main([], monkeypatch)
        assert len(calls) == 11

    def test_single_stage_run(self, monkeypatch):
        """--from-stage T9 --to-stage T9 must run only T9."""
        calls = self._run_main(["--from-stage", "T9", "--to-stage", "T9"], monkeypatch)
        assert len(calls) == 1

    def test_subset_stages(self, monkeypatch):
        """T9 to T11 = 2 stages."""
        calls = self._run_main(["--from-stage", "T9", "--to-stage", "T11"], monkeypatch)
        assert len(calls) == 2

    def test_stage_script_uses_python_executable(self, monkeypatch):
        """Each subprocess call must invoke the current Python executable."""
        calls = self._run_main(["--from-stage", "T9", "--to-stage", "T9"], monkeypatch)
        assert calls[0][0] == sys.executable

    def test_summary_printed_after_run(self, monkeypatch, capsys):
        self._run_main(["--from-stage", "T9", "--to-stage", "T9"], monkeypatch)
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out

    def test_stage_failure_calls_sys_exit(self, monkeypatch):
        """A failed subprocess must trigger sys.exit(1)."""
        monkeypatch.setattr(
            sys, "argv", ["pipeline", "--from-stage", "T9", "--to-stage", "T9"]
        )

        def failing_run(cmd, cwd, check):
            raise subprocess.CalledProcessError(1, cmd)

        with patch(
            "satellite.run_thermal_pipeline.subprocess.run", side_effect=failing_run
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 1

    def test_elapsed_time_logged(self, monkeypatch, capsys):
        self._run_main(["--from-stage", "T9", "--to-stage", "T9"], monkeypatch)
        captured = capsys.readouterr()
        assert "SUCCESS" in captured.out
