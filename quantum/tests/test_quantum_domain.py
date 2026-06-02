import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from core.domains.domain_registry import DomainRegistry
from core.domains.plugin_loader import discover_domains
from core.orchestration.scientist_factory import create_scientist
from core.orchestration.scientific_container import ScientificContainer
from physics.core.autonomous.autonomous_scientist import AutonomousScientist
from core.abstractions.base_hypothesis_generator import BaseHypothesisGenerator
from core.abstractions.base_critic import BaseCritic
from core.abstractions.base_sandbox import BaseSandbox
from core.abstractions.base_memory import BaseMemory

def test_quantum_domain_registration():
    """Verifica que el dominio quantum se descubre y registra correctamente."""
    discover_domains()
    assert "quantum" in DomainRegistry.list_domains()
    
    spec = DomainRegistry.get_domain("quantum")
    assert spec.name == "quantum"
    assert spec.version == "0.1.0"
    assert spec.config_path == "configs/domains/quantum.yaml"


def test_create_scientist_quantum():
    """Verifica que create_scientist('quantum') devuelve una instancia funcional de AutonomousScientist."""
    scientist = create_scientist("quantum", use_docker=False)
    assert isinstance(scientist, AutonomousScientist)
    
    # Verificar que los componentes inyectados corresponden al dominio cuántico
    assert isinstance(scientist.generator, BaseHypothesisGenerator)
    assert isinstance(scientist.critic, BaseCritic)
    assert isinstance(scientist.sandbox, BaseSandbox)
    assert isinstance(scientist.memory, BaseMemory)
    
    # Comprobar que son las implementaciones cuánticas concretas
    from quantum.generators.quantum_hypothesis_generator import QuantumHypothesisGenerator
    from quantum.critics.quantum_critic import QuantumCritic
    from quantum.sandbox.qiskit_quantum_sandbox import QiskitQuantumSandbox
    from quantum.memory.quantum_memory import QuantumMemory
    
    assert isinstance(scientist.generator, QuantumHypothesisGenerator)
    assert isinstance(scientist.critic, QuantumCritic)
    assert isinstance(scientist.sandbox, QiskitQuantumSandbox)
    assert isinstance(scientist.memory, QuantumMemory)


def test_quantum_scientific_loop():
    """Verifica la ejecución básica de un ciclo científico de descubrimiento en el dominio cuántico."""
    scientist = create_scientist("quantum", use_docker=False)
    
    # Configurar modo automático para no pausar por interactividad
    scientist.auto_mode = True
    
    domain = "quantum"
    goal = "Optimize Bell state circuit depth"
    
    # Ejecutar 1 iteración
    results = scientist.run_discovery_cycle(domain, goal, max_iterations=1, patience=1)
    
    assert results["iterations"] == 1
    assert len(results["session_history"]) == 1
    
    history_item = results["session_history"][0]
    
    # Validar que los resultados del sandbox y la interpretación correspondan al dominio cuántico
    assert history_item["execution"]["success"] is True
    assert history_item["execution"]["result"]["gate_count"] == 2
    assert history_item["execution"]["result"]["depth"] == 2
    assert history_item["execution"]["result"]["qubits"] == 2
    assert history_item["execution"]["result"]["status"] == "compiled_successfully"
    
    assert history_item["interpretation"]["verdict"] == "validated"
    assert history_item["epistemic_gain"] > 0.0
