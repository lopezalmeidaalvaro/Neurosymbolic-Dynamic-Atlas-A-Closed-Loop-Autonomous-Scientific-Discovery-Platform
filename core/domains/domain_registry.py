from typing import Dict, List, Optional, Callable, Any
from core.domains.domain_spec import DomainSpec

class DomainRegistry:
    """
    Registro central global para los dominios científicos cargados.
    """
    _registry: Dict[str, DomainSpec] = {}

    @classmethod
    def register_domain(
        cls,
        spec: Optional[DomainSpec] = None,
        name: Optional[str] = None,
        factory: Optional[Callable[[], Any]] = None,
        config: Optional[str] = None,
        config_path: Optional[str] = None,
        version: str = "1.0.0",
        description: str = "",
    ) -> None:
        """
        Registra un dominio científico. Acepta un DomainSpec o argumentos individuales.
        """
        if spec is not None:
            cls._registry[spec.name] = spec
        else:
            if name is None or factory is None:
                raise ValueError("El nombre y la factoría son requeridos para registrar un dominio.")
            
            cfg_path = config_path or config or ""
            domain_spec = DomainSpec(
                name=name,
                version=version,
                factory=factory,
                config_path=cfg_path,
                description=description
            )
            cls._registry[name] = domain_spec

    @classmethod
    def unregister_domain(cls, name: str) -> None:
        """
        Elimina un dominio del registro.
        """
        if name in cls._registry:
            del cls._registry[name]

    @classmethod
    def get_domain(cls, name: str) -> DomainSpec:
        """
        Obtiene la especificación de un dominio por su nombre.
        """
        if name not in cls._registry:
            raise KeyError(f"El dominio '{name}' no está registrado.")
        return cls._registry[name]

    @classmethod
    def list_domains(cls) -> List[str]:
        """
        Devuelve una lista con los nombres de todos los dominios registrados.
        """
        return list(cls._registry.keys())
