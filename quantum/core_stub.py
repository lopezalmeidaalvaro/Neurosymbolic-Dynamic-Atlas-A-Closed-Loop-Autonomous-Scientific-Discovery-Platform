import logging

logger = logging.getLogger("qade")

class ExperimentLogger:
    @staticmethod
    def log_benchmark_run(*args, **kwargs):
        logger.info("ExperimentLogger stub — install ia_core for full logging.")

    @staticmethod
    def log_run(*args, **kwargs):
        logger.info("ExperimentLogger stub — install ia_core for full logging.")

    @staticmethod
    def log_metrics(*args, **kwargs):
        logger.info("ExperimentLogger stub — install ia_core for full logging.")


class DocumentationManager:
    @staticmethod
    def update_documentation(*args, **kwargs):
        logger.info("DocumentationManager stub — install ia_core for full logging.")

    @staticmethod
    def sync_docs(*args, **kwargs):
        logger.info("DocumentationManager stub — install ia_core for full logging.")


class KnowledgeDashboard:
    def __init__(self, *args, **kwargs):
        logger.info("KnowledgeDashboard stub — install ia_core for full dashboard.")

    def render(self, *args, **kwargs):
        pass


class ScientificContainer:
    def __init__(self, *args, **kwargs):
        pass


class BaseCritic:
    def __init__(self, *args, **kwargs):
        pass


class BaseHypothesisGenerator:
    def __init__(self, *args, **kwargs):
        pass


class BaseMemory:
    def __init__(self, *args, **kwargs):
        pass


class BaseSandbox:
    def __init__(self, *args, **kwargs):
        pass


class DomainRegistry:
    _domains = {}

    @classmethod
    def register_domain(cls, name, spec):
        cls._domains[name] = spec

    @classmethod
    def get_domain(cls, name):
        return cls._domains.get(name)

    @classmethod
    def list_domains(cls):
        return list(cls._domains.keys())


def discover_domains(*args, **kwargs):
    logger.info("discover_domains stub — running in standalone mode.")


def create_scientist(*args, **kwargs):
    logger.info("create_scientist stub — install ia_core for full orchestration.")
    return None
