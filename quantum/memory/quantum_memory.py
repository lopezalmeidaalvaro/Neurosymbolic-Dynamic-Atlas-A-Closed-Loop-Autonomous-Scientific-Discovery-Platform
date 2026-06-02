from typing import Any
from core.abstractions.base_memory import BaseMemory

class QuantumMemory(BaseMemory):
    """
    Capa de memoria semántica temporal para el dominio cuántico.
    Almacena hipótesis y resultados en memoria (sin persistencia).
    """

    def __init__(self):
        self._store = {}

    def store(self, key: str, value: Any, *args, **kwargs) -> None:
        """
        Almacena un elemento en memoria.
        """
        self._store[key] = value

    def retrieve(self, key: str, *args, **kwargs) -> Any:
        """
        Recupera un elemento de la memoria. Devuelve None si no se encuentra.
        """
        return self._store.get(key, None)
