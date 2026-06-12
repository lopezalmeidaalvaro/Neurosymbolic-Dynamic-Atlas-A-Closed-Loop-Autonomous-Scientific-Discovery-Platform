import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from core.abstractions.base_hypothesis_generator import BaseHypothesisGenerator
from core.abstractions.base_critic import BaseCritic
from core.abstractions.base_sandbox import BaseSandbox
from core.abstractions.base_memory import BaseMemory
from physics.adapters.classical_hypothesis_generator import ClassicalHypothesisGenerator
from physics.adapters.classical_physics_critic import ClassicalPhysicsCritic
from physics.agents.hypothesis_generator import Hypothesis


# Stubs para verificar instanciabilidad de BaseSandbox y BaseMemory
class StubSandbox(BaseSandbox):
    def execute(self, code, input_data=None):
        return {"success": True, "result": {"value": 42}}


class StubMemory(BaseMemory):
    def __init__(self):
        self.db = {}

    def store(self, key, value):
        self.db[key] = value

    def retrieve(self, key):
        return self.db.get(key)


def test_abstractions_instantiation():
    """Verifica que las interfaces no se instancien directamente pero sí mediante stubs."""
    with pytest.raises(TypeError):
        BaseSandbox()

    with pytest.raises(TypeError):
        BaseMemory()

    sandbox = StubSandbox()
    assert sandbox.execute("print(42)")["success"] is True

    memory = StubMemory()
    memory.store("test_key", "test_val")
    assert memory.retrieve("test_key") == "test_val"


def test_classical_hypothesis_generator_adapter():
    """Verifica la instanciación y delegación del ClassicalHypothesisGenerator."""
    adapter = ClassicalHypothesisGenerator(exploration_rate=0.5)
    assert isinstance(adapter, BaseHypothesisGenerator)

    # Mock context to avoid heavy graph loading in HypoGen propose method
    context = {"exploration_history": []}
    hypo = adapter.propose(context, metric_type="wormhole")
    assert isinstance(hypo, Hypothesis)
    assert hypo.metric_type == "wormhole"
    assert len(hypo.expression) > 0


def test_classical_physics_critic_adapter():
    """Verifica la instanciación y delegación del ClassicalPhysicsCritic."""
    adapter = ClassicalPhysicsCritic(r0=0.5)
    assert isinstance(adapter, BaseCritic)

    # Valid wormhole hypothesis that passes fast throat closed check (no spaces around equal sign)
    h = Hypothesis(
        "b(r)=0.5*exp(-3.2*(r-0.5)**2)", confidence=0.8, metric_type="wormhole"
    )
    verdict = adapter.validate(h)
    assert verdict.verdict == "ACCEPTED"
    assert verdict.wec_violation >= 0.0
