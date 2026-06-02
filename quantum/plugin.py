from core.domains.domain_registry import DomainRegistry
from quantum.factories.quantum_factory import create_quantum_container

# Registrar el dominio cuántico con su factoría real
DomainRegistry.register_domain(
    name="quantum",
    version="0.1.0",
    factory=create_quantum_container,
    config_path="configs/domains/quantum.yaml",
    description="Dominio de física cuántica y optimización de circuitos cuánticos."
)
