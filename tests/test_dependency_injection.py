import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from core.orchestration.scientific_container import ScientificContainer
from physics.factories.classical_factory import create_classical_container
from physics.core.autonomous.autonomous_scientist import AutonomousScientist
from core.abstractions.base_hypothesis_generator import BaseHypothesisGenerator
from core.abstractions.base_critic import BaseCritic
from core.abstractions.base_sandbox import BaseSandbox
from core.abstractions.base_memory import BaseMemory


# 1. Define Stubs/Mocks for testing DI
class MockGenerator(BaseHypothesisGenerator):
    def propose(self, *args, **kwargs):
        return {"hypothesis_text": "Mocked", "prediction": "Mocked Pred"}

    def mutate(self, *args, **kwargs):
        pass


class MockCritic(BaseCritic):
    def validate(self, *args, **kwargs):
        return {"verdict": "ACCEPTED"}


class MockSandbox(BaseSandbox):
    def execute(self, code, input_data=None):
        return {
            "success": True,
            "result": {"output": "Mock success"},
            "execution_time": 0.05,
        }


class MockMemory(BaseMemory):
    def store(self, *args, **kwargs):
        pass

    def retrieve(self, *args, **kwargs):
        return []


class MockLLMReasoner:
    def generate_hypothesis(self, context):
        return {
            "hypothesis_text": "Mock LLM",
            "prediction": "Mock LLM Pred",
            "confidence_prior": 0.8,
        }

    def design_experiment(self, hypothesis, data, methods):
        return {
            "experiment_description": "Mock LLM Exp",
            "dataset": "synthetic_lorenz",
            "method": "koopman",
            "falsification_criterion": "test",
            "python_code": "print('ok')",
        }

    def interpret_results(self, hypothesis, experiment, results):
        return {
            "verdict": "validated",
            "confidence_posterior": 0.9,
            "reasoning": "Mock LLM Interpretation",
        }


def test_orchestrator_accepts_mocks():
    """Verifica que el orquestador acepta mocks inyectados y los almacena correctamente."""
    generator = MockGenerator()
    critic = MockCritic()
    sandbox = MockSandbox()
    memory = MockMemory()
    llm = MockLLMReasoner()

    scientist = AutonomousScientist(
        generator=generator,
        critic=critic,
        sandbox=sandbox,
        memory=memory,
        llm_reasoner=llm,
    )

    assert scientist.generator is generator
    assert scientist.critic is critic
    assert scientist.sandbox is sandbox
    assert scientist.memory is memory
    assert scientist.llm is llm


def test_orchestrator_works_with_classical_container():
    """Verifica que el orquestador se puede construir usando el contenedor de la factoría clásica."""
    container = create_classical_container()

    scientist = AutonomousScientist(
        generator=container.generator,
        critic=container.critic,
        sandbox=container.sandbox,
        memory=container.memory,
        llm_reasoner=container.llm_reasoner,
    )

    assert isinstance(scientist.generator, BaseHypothesisGenerator)
    assert isinstance(scientist.critic, BaseCritic)
    assert isinstance(scientist.sandbox, BaseSandbox)
    assert isinstance(scientist.memory, BaseMemory)
    assert scientist.llm is container.llm_reasoner


def test_orchestrator_backward_compatibility():
    """Verifica que el orquestador tiene compatibilidad retroactiva cuando no se inyecta nada."""
    # Al no inyectar nada, debe instanciar los componentes legacy por defecto
    scientist = AutonomousScientist(use_docker=False)

    assert scientist.generator is None
    assert scientist.memory is None
    assert scientist.sandbox is not None
    assert scientist.llm is not None

    # Comprobar que son las clases reales legacy de physics
    from physics.core.autonomous.sandbox_executor import SandboxExecutor
    from physics.core.autonomous.llm_reasoner import LLMReasoner

    assert isinstance(scientist.sandbox, SandboxExecutor)
    assert isinstance(scientist.llm, LLMReasoner)


def test_orchestrator_agnostic_imports():
    """Verifica que el archivo del orquestador no realiza imports concretos de agentes/críticos en cabecera."""
    import inspect
    import physics.core.autonomous.autonomous_scientist as am

    source = inspect.getsource(am)

    # No debe importar agentes ni críticos clásicos de forma directa en cabecera
    assert (
        "from physics.agents.hypothesis_generator import HypothesisGenerator"
        not in source
    )
    assert "from physics.agents.theory_critic import TheoryCritic" not in source
