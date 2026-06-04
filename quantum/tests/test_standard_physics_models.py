import pytest
from quantum.novel_physics.standard_physics_models import StandardPhysicsModel
from quantum.novel_physics.physics_baseline_library import PhysicsBaselineLibrary
from quantum.novel_physics.known_effect_catalog import KnownEffectCatalog

def test_standard_model_predicts_zero():
    model = StandardPhysicsModel()
    assert model.predict_gap(0.01, 0.02) == 0.0
    assert model.predict_gap(0.0, 0.0) == 0.0

def test_baseline_library():
    lib = PhysicsBaselineLibrary()
    records = [{"gate_error": 0.01, "readout_error": 0.02}]
    preds = lib.get_baseline_predictions(records)
    assert len(preds) == 1
    assert preds[0] == 0.0

def test_known_effect_catalog():
    catalog = KnownEffectCatalog()
    effects = catalog.get_known_effects()
    assert len(effects) >= 4
    # RTHEORY-style equations should NOT match known effects
    assert catalog.matches_known_effect("Gap = -1.49 * E_gate + -1.50 * E_readout + -0.002") == False
