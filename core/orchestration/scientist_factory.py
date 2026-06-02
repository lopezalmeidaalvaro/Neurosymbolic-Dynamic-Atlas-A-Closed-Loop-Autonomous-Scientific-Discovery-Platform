from core.domains.domain_registry import DomainRegistry
from core.domains.plugin_loader import discover_domains
from physics.core.autonomous.autonomous_scientist import AutonomousScientist

# Asegurar el autodescubrimiento al importar
discover_domains()

def create_scientist(domain_name: str, **kwargs) -> AutonomousScientist:
    """
    Crea una instancia de AutonomousScientist configurada dinámicamente
    con los componentes del dominio especificado cargados vía DomainRegistry.
    """
    # Ejecutar descubrimiento para garantizar que todos los plugins estén en el registro
    discover_domains()

    # Obtener especificación del dominio y fabricar su contenedor
    spec = DomainRegistry.get_domain(domain_name)
    container = spec.factory()

    # Retornar el orquestador inyectando sus dependencias
    return AutonomousScientist(
        generator=container.generator,
        critic=container.critic,
        sandbox=container.sandbox,
        memory=container.memory,
        llm_reasoner=container.llm_reasoner,
        **kwargs
    )
