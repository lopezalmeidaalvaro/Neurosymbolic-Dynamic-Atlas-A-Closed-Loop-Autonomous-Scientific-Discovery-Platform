import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from core.domains.domain_spec import DomainSpec
from core.domains.domain_registry import DomainRegistry
from core.domains.plugin_loader import discover_domains
from core.orchestration.scientist_factory import create_scientist
from core.orchestration.scientific_container import ScientificContainer
from physics.core.autonomous.autonomous_scientist import AutonomousScientist

def test_registry_registration_and_unregistration():
    """Valida el registro manual, obtención y desregistro de dominios en DomainRegistry."""
    def dummy_factory():
        return ScientificContainer()

    spec = DomainSpec(
        name="test_domain",
        version="2.1.0",
        factory=dummy_factory,
        config_path="configs/domains/test_domain.yaml",
        description="Dominio de prueba unitaria"
    )

    DomainRegistry.register_domain(spec)
    assert "test_domain" in DomainRegistry.list_domains()

    retrieved = DomainRegistry.get_domain("test_domain")
    assert retrieved.name == "test_domain"
    assert retrieved.version == "2.1.0"
    assert retrieved.factory is dummy_factory

    DomainRegistry.unregister_domain("test_domain")
    assert "test_domain" not in DomainRegistry.list_domains()


def test_registry_register_with_kwargs():
    """Valida que register_domain funciona también pasando argumentos nombrados directamente (ejemplo del prompt)."""
    def dummy_factory():
        return ScientificContainer()

    DomainRegistry.register_domain(
        name="test_kwargs",
        factory=dummy_factory,
        config="configs/domains/test_kwargs.yaml",
        version="1.2.3"
    )

    assert "test_kwargs" in DomainRegistry.list_domains()
    retrieved = DomainRegistry.get_domain("test_kwargs")
    assert retrieved.name == "test_kwargs"
    assert retrieved.factory is dummy_factory
    assert retrieved.config_path == "configs/domains/test_kwargs.yaml"
    assert retrieved.version == "1.2.3"

    DomainRegistry.unregister_domain("test_kwargs")


def test_plugin_loader_discovers_plugins():
    """Valida que discover_domains() encuentra y carga al menos el dominio de physics, satellite y quantum."""
    discovered = discover_domains()
    assert "physics" in discovered
    assert "satelite" in discovered or "satellite" in discovered
    assert "quantum" in discovered
    
    # physics, satellite y quantum deben estar registrados
    registered = DomainRegistry.list_domains()
    assert "physics" in registered
    assert "satellite" in registered
    assert "quantum" in registered


def test_create_scientist_instantiation():
    """Valida que create_scientist("physics") instancia correctamente un AutonomousScientist con el contenedor clásico."""
    scientist = create_scientist("physics", use_docker=False)
    assert isinstance(scientist, AutonomousScientist)
    # Verificar que el sandbox y llm no sean None (cargados mediante el contenedor)
    assert scientist.sandbox is not None
    assert scientist.llm is not None


def test_domains_isolation():
    """Valida el aislamiento entre las fábricas y configuraciones de cada dominio."""
    spec_phys = DomainRegistry.get_domain("physics")
    spec_sat = DomainRegistry.get_domain("satellite")
    spec_quant = DomainRegistry.get_domain("quantum")

    assert spec_phys.name == "physics"
    assert spec_sat.name == "satellite"
    assert spec_quant.name == "quantum"

    # Fábricas diferentes
    assert spec_phys.factory is not spec_sat.factory
    assert spec_phys.factory is not spec_quant.factory
    assert spec_sat.factory is not spec_quant.factory
