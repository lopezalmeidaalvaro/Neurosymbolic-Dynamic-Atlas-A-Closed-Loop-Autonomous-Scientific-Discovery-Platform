class ScientificContainer:
    """
    Contenedor agnóstico para registrar componentes del ciclo científico autónomo
    (generador, crítico, sandbox, memoria, y llm_reasoner).
    """
    def __init__(self):
        self.generator = None
        self.critic = None
        self.sandbox = None
        self.memory = None
        self.llm_reasoner = None
        self.evolution_engine = None

    def register_generator(self, generator):
        self.generator = generator

    def register_critic(self, critic):
        self.critic = critic

    def register_sandbox(self, sandbox):
        self.sandbox = sandbox

    def register_memory(self, memory):
        self.memory = memory

    def register_llm_reasoner(self, llm_reasoner):
        self.llm_reasoner = llm_reasoner

    def register_evolution_engine(self, evolution_engine):
        self.evolution_engine = evolution_engine
