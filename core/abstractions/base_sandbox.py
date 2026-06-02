from abc import ABC, abstractmethod

class BaseSandbox(ABC):
    """
    Contrato base abstracto para los entornos de ejecución y sandboxes de experimentos.
    Permite correr código de forma segura y recopilar sus resultados en JSON.
    """
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
