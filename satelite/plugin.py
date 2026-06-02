from core.domains.domain_registry import DomainRegistry
from core.orchestration.scientific_container import ScientificContainer

def create_satellite_container():
    """
    Stub factory para el dominio de telemetría y control térmico de satélites.
    """
    return ScientificContainer()

# Registrar el dominio de satélites stub
DomainRegistry.register_domain(
    name="satellite",
    version="1.0.0",
    factory=create_satellite_container,
    config_path="configs/domains/satellite.yaml",
    description="Dominio de telemetría de satélites y calibración de EKF (Stub)."
)
