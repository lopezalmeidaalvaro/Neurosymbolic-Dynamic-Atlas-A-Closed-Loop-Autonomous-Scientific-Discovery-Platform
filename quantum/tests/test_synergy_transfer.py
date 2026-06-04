import pytest
import math
from quantum.analysis.synergy_transfer_registry import SynergyTransferRegistry
from quantum.benchmarks.benchmark_synergy_transfer import (
    randomize_scaffold_sequence, benjamini_hochberg_correction
)

def test_synergy_transfer_registry_filtering():
    scaffolds = [
        {
            "representation": "H->CNOT->H(q0)->CNOT(q0,q1)",
            "sequence": ["H", "CNOT", "H", "CNOT"],
            "context": {"task_name": "bell_state", "qubit_count": 2},
            "confidence_score": 0.5,
            "utility_scaffold": 0.3,
            "scaffold_novelty": 0.4
        },
        {
            "representation": "X->Y->Z",
            "sequence": ["X", "Y", "Z"],
            "context": {"task_name": "bell_state", "qubit_count": 2},
            "confidence_score": 0.8,
            "utility_scaffold": 0.5,
            "scaffold_novelty": 0.2 # Below novelty threshold (0.30)
        }
    ]
    pairwise_records = [
        {
            "pattern_a": "H->CNOT",
            "pattern_b": "H(q0)->CNOT(q0,q1)",
            "interaction_type": "STATE_PREPARATION_EXTENSION",
            "synergy_score": 0.478,
            "novelty": 0.4
        },
        {
            "pattern_a": "X",
            "pattern_b": "Y->Z",
            "interaction_type": "UNKNOWN",
            "synergy_score": 0.2,
            "novelty": 0.2
        }
    ]

    registry = SynergyTransferRegistry(novelty_threshold=0.30)
    candidates = registry.build_transfer_registry(scaffolds, pairwise_records)

    # Only the first candidate passes (synergy > 0, novelty (0.4) >= 0.30, interaction type approved)
    assert len(candidates) == 1
    assert candidates[0]["representation"] == "H->CNOT->H(q0)->CNOT(q0,q1)"
    assert candidates[0]["synergy_score"] == pytest.approx(0.478)

def test_randomize_scaffold_sequence():
    rep = "H->CNOT->RY"
    rand_sc = randomize_scaffold_sequence(rep)

    assert rand_sc["is_scaffold"] is True
    # The gates are shuffled, but they should be same length and types
    assert len(rand_sc["sequence"]) == 3
    assert set(rand_sc["sequence"]) == {"H", "CNOT", "RY"}

def test_benjamini_hochberg_correction():
    # Test typical p-values to check that correction works
    p_values = [0.01, 0.04, 0.03, 0.15]
    adjusted = benjamini_hochberg_correction(p_values)

    assert len(adjusted) == 4
    # The smallest p-value should have rank 1, so adjusted = p * n / rank
    # For 0.01, rank 1 -> 0.01 * 4 / 1 = 0.04
    # For 0.03, rank 2 -> 0.03 * 4 / 2 = 0.06
    # For 0.04, rank 3 -> 0.04 * 4 / 3 = 0.053
    # Adjusted must be monotonic, so adjusted p-value for 0.03 is min(adjusted[0.04], bh_val) = min(0.053, 0.06) = 0.053
    # Let's verify monotonicity
    assert adjusted[0] < adjusted[3]
    for p in adjusted:
        assert 0.0 <= p <= 1.0
