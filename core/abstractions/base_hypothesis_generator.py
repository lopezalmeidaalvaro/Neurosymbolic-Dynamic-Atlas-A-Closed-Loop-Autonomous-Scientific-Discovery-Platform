from abc import ABC, abstractmethod

class BaseHypothesisGenerator(ABC):
    """
    Contrato base abstracto para los generadores de hipótesis científicas.
    Desacopla el motor simbólico o LLM de la física del dominio específico.
    """
    @abstractmethod
    def propose(self, *args, **kwargs):
        pass

    @abstractmethod
    def mutate(self, *args, **kwargs):
        pass
