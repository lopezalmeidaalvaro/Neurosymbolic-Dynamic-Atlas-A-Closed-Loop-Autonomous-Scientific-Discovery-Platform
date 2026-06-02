from core.orchestration.scientific_container import ScientificContainer
from physics.adapters.classical_hypothesis_generator import ClassicalHypothesisGenerator
from physics.adapters.classical_physics_critic import ClassicalPhysicsCritic
from physics.core.autonomous.sandbox_executor import SandboxExecutor
from physics.scientific_memory_advanced import ScientificMemoryAdvanced
from physics.core.autonomous.llm_reasoner import LLMReasoner

def create_classical_container():
    """
    Ensambla y configura los componentes clásicos legacy en un ScientificContainer
    para inyectarlos en el orquestador principal.
    """
    container = ScientificContainer()
    
    # 1. Registrar componentes del dominio de física clásica
    container.register_generator(ClassicalHypothesisGenerator())
    container.register_critic(ClassicalPhysicsCritic())
    container.register_sandbox(SandboxExecutor())
    container.register_memory(ScientificMemoryAdvanced())
    container.register_llm_reasoner(LLMReasoner())
    
    return container
