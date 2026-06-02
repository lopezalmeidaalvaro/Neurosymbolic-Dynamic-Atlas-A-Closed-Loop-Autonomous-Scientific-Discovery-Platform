from core.domains.domain_registry import DomainRegistry
from physics.factories.classical_factory import create_classical_container

# Registrar el dominio clásico de física general
DomainRegistry.register_domain(
    name="physics",
    version="1.0.0",
    factory=create_classical_container,
    config_path="configs/domains/physics.yaml",
    description="Dominio clásico de física general, relatividad y caos determinista."
)
