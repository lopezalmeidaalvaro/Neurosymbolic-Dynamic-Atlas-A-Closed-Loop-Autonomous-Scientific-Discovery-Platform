from abc import ABC, abstractmethod

class BaseMemory(ABC):
    """
    Contrato base abstracto para los sistemas de memoria y bases de conocimiento.
    Permite almacenar y recuperar información científica estructurada o vectorial.
    """
    @abstractmethod
    def store(self, *args, **kwargs):
        pass

    @abstractmethod
    def retrieve(self, *args, **kwargs):
        pass
