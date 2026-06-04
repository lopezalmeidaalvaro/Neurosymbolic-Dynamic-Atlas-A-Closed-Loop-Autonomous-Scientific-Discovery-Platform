import math
import pytest
from quantum.knowledge.context_schema import Context
from quantum.memory.quantum_memory import QuantumMemory

def test_context_matching():
    """Validates that context similarity is correctly computed based on task_name and qubit_count."""
    memory = QuantumMemory()
    c_bell = Context(task_name="bell_state", qubit_count=2, converged=True)
    c_bell_not_conv = Context(task_name="bell_state", qubit_count=2, converged=False)
    c_ghz = Context(task_name="ghz_state", qubit_count=3, converged=True)
    c_fake_bell = Context(task_name="bell_state", qubit_count=3, converged=True)
    c_fake_ghz = Context(task_name="ghz_state", qubit_count=2, converged=True)

    # Populate memory with a pattern for c_bell
    patterns = [
        {
            "pattern_id": "pat_1",
            "representation": "H->CNOT",
            "sequence": ["H", "CNOT"],
            "context": c_bell.to_dict(),
            "P_convergence": 1.0,
            "survival_probability": 1.0,
            "mean_delta_score": 0.0
        }
    ]
    memory.store("quantum:distillation:patterns", patterns)

    # 1. Exact match (converged status does not affect similarity)
    retrieved = memory.retrieve_patterns(c_bell)
    assert len(retrieved) == 1
    assert retrieved[0]["retrieval_score"] == pytest.approx(1.0)

    retrieved_not_conv = memory.retrieve_patterns(c_bell_not_conv)
    assert len(retrieved_not_conv) == 1
    assert retrieved_not_conv[0]["retrieval_score"] == pytest.approx(1.0)

    # 2. Soft matching task mismatch, qubit match (e.g. c_fake_ghz has 2 qubits, search context is c_bell)
    patterns[0]["context"] = c_fake_ghz.to_dict()
    memory.store("quantum:distillation:patterns", patterns)
    retrieved_soft = memory.retrieve_patterns(c_bell)
    assert len(retrieved_soft) == 1
    assert retrieved_soft[0]["retrieval_score"] == pytest.approx(0.5)

    # 3. Soft matching task match, qubit mismatch (e.g. c_fake_bell has 3 qubits, search context is c_bell)
    patterns[0]["context"] = c_fake_bell.to_dict()
    memory.store("quantum:distillation:patterns", patterns)
    retrieved_soft_qubit = memory.retrieve_patterns(c_bell)
    assert len(retrieved_soft_qubit) == 1
    assert retrieved_soft_qubit[0]["retrieval_score"] == pytest.approx(0.2)

    # 4. Full mismatch
    patterns[0]["context"] = c_ghz.to_dict()
    memory.store("quantum:distillation:patterns", patterns)
    retrieved_mismatch = memory.retrieve_patterns(c_bell)
    assert len(retrieved_mismatch) == 1
    assert retrieved_mismatch[0]["retrieval_score"] == pytest.approx(0.1)

def test_hard_filtering():
    """Validates that hard context filtering prohibits cross-context retrievals entirely."""
    memory = QuantumMemory()
    c_bell = Context(task_name="bell_state", qubit_count=2, converged=True)
    c_fake_ghz = Context(task_name="ghz_state", qubit_count=2, converged=True)

    # Pattern context is ghz state, but search context is bell state
    patterns = [
        {
            "pattern_id": "pat_1",
            "representation": "H->CNOT",
            "sequence": ["H", "CNOT"],
            "context": c_fake_ghz.to_dict(),
            "P_convergence": 1.0,
            "survival_probability": 1.0,
            "mean_delta_score": 0.0
        }
    ]
    memory.store("quantum:distillation:patterns", patterns)

    # With soft matching enabled
    retrieved_soft = memory.retrieve_patterns(c_bell, allow_cross_context=True)
    assert len(retrieved_soft) == 1

    # With hard matching enabled (allow_cross_context=False)
    retrieved_hard = memory.retrieve_patterns(c_bell, allow_cross_context=False)
    assert len(retrieved_hard) == 0

def test_retrieval_ranking():
    """Validates that retrieved patterns are properly scored and sorted descending by retrieval_score."""
    memory = QuantumMemory()
    c_bell = Context(task_name="bell_state", qubit_count=2, converged=True)

    patterns = [
        {
            "pattern_id": "pat_low",
            "representation": "X->X",
            "sequence": ["X", "X"],
            "context": c_bell.to_dict(),
            "P_convergence": 0.1,
            "survival_probability": 0.2,
            "mean_delta_score": -0.5
        },
        {
            "pattern_id": "pat_high",
            "representation": "H->CNOT",
            "sequence": ["H", "CNOT"],
            "context": c_bell.to_dict(),
            "P_convergence": 0.9,
            "survival_probability": 0.9,
            "mean_delta_score": 0.2
        }
    ]
    memory.store("quantum:distillation:patterns", patterns)

    retrieved = memory.retrieve_patterns(c_bell)
    assert len(retrieved) == 2
    assert retrieved[0]["pattern_id"] == "pat_high"
    assert retrieved[1]["pattern_id"] == "pat_low"

    # Compare mathematically calculated scores
    high_score = 0.9 * 0.9 * math.exp(0.2)
    low_score = 0.1 * 0.2 * math.exp(-0.5)
    assert retrieved[0]["retrieval_score"] == pytest.approx(high_score)
    assert retrieved[1]["retrieval_score"] == pytest.approx(low_score)

def test_context_purity_metrics():
    """Validates manual calculations of Context Match Rate, Wrong Context Injection Rate, and Context Purity."""
    # Let's mock a simple function to calculate these from causal records to verify formulas
    causal_records = [
        {"pattern": "H->CNOT", "source_context": {"task_name": "bell_state", "qubit_count": 2, "converged": True}}, # Correct
        {"pattern": "H->CNOT", "source_context": {"task_name": "ghz_state", "qubit_count": 3, "converged": True}}, # Wrong
        {"pattern": "X->X", "source_context": None}, # Legacy/Agnostic (Wrong/Cross)
        {"pattern": "H->CNOT", "source_context": {"task_name": "bell_state", "qubit_count": 2, "converged": False}} # Correct
    ]

    target_task = "bell_state"
    target_qubits = 2

    matching = 0
    cross = 0
    total = len(causal_records)

    for r in causal_records:
        ctx_data = r.get("source_context")
        if ctx_data:
            if ctx_data.get("task_name") == target_task and ctx_data.get("qubit_count") == target_qubits:
                matching += 1
            else:
                cross += 1
        else:
            cross += 1

    match_rate = matching / total
    wrong_rate = cross / total
    purity = matching / total # since retrieved == total retrievals here

    assert match_rate == 0.50
    assert wrong_rate == 0.50
    assert purity == 0.50

def test_migration_compatibility():
    """Validates that legacy patterns (without context) remain loadable and retrieve under soft matching."""
    memory = QuantumMemory()
    c_bell = Context(task_name="bell_state", qubit_count=2, converged=True)

    legacy_patterns = [
        {
            "pattern_id": "pat_legacy",
            "representation": "H->CNOT",
            "sequence": ["H", "CNOT"],
            # No context field
            "avg_score": 0.8
        }
    ]
    memory.store("quantum:distillation:patterns", legacy_patterns)

    # 1. Soft retrieval: legacy patterns should return with a baseline similarity of 0.5
    retrieved_soft = memory.retrieve_patterns(c_bell, allow_cross_context=True)
    assert len(retrieved_soft) == 1
    assert retrieved_soft[0]["pattern_id"] == "pat_legacy"
    # score = max(1e-4, P_conv * surv_prob * exp(mean_delta)) * similarity
    # P_conv = avg_score (0.8), surv_prob = default (0.5), mean_delta = default (0.0), similarity = 0.5
    expected_score = 0.8 * 0.5 * 1.0 * 0.5
    assert retrieved_soft[0]["retrieval_score"] == pytest.approx(expected_score)

    # 2. Hard retrieval: legacy patterns should be skipped completely (prohibited)
    retrieved_hard = memory.retrieve_patterns(c_bell, allow_cross_context=False)
    assert len(retrieved_hard) == 0
