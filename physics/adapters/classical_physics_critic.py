from core.abstractions.base_critic import BaseCritic
from physics.agents.theory_critic import TheoryCritic

class ClassicalPhysicsCritic(BaseCritic):
    """
    Adaptador clásico que implementa BaseCritic y encapsula
    el validador TheoryCritic original sin modificarlo.
    """
    def __init__(self, *args, **kwargs):
        self.critic = TheoryCritic(*args, **kwargs)

    def validate(self, *args, **kwargs):
        return self.critic.validate(*args, **kwargs)
