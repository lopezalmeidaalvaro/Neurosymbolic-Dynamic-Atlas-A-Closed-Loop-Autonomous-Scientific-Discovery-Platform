from core.abstractions.base_hypothesis_generator import BaseHypothesisGenerator
from physics.agents.hypothesis_generator import HypothesisGenerator

class ClassicalHypothesisGenerator(BaseHypothesisGenerator):
    """
    Adaptador clásico que implementa BaseHypothesisGenerator y encapsula
    el generador de hipótesis original de relatividad general sin modificarlo.
    """
    def __init__(self, *args, **kwargs):
        self.generator = HypothesisGenerator(*args, **kwargs)

    def propose(self, *args, **kwargs):
        return self.generator.propose(*args, **kwargs)

    def mutate(self, *args, **kwargs):
        return self.generator.mutate(*args, **kwargs)
