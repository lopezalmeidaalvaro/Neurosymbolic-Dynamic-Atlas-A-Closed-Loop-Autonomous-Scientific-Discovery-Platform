from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class DomainSpec:
    """
    Especificación de un dominio científico en el sistema.
    """
    name: str
    version: str
    factory: Callable[[], Any]
    config_path: str
    description: str
