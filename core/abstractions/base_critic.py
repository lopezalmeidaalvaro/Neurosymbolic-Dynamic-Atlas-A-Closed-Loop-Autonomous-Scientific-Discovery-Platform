from abc import ABC, abstractmethod

class BaseCritic(ABC):
    """
    Contrato base abstracto para los agentes críticos y validadores científicos.
    Permite contrastar hipótesis simbólicas contra las restricciones del dominio.
    """
    @abstractmethod
    def validate(self, *args, **kwargs):
        pass
