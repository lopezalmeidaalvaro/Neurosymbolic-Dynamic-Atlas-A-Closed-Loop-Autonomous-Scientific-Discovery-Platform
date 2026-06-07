from importlib import import_module
from typing import Any

from core.domains.domain_registry import DomainRegistry
from core.domains.plugin_loader import discover_domains


DEFAULT_ORCHESTRATOR = "physics.core.autonomous.autonomous_scientist:AutonomousScientist"


def _load_symbol(path: str) -> Any:
    """Load "module:attribute" without importing any domain at module import time."""
    module_name, _, attr_name = path.partition(":")
    if not module_name or not attr_name:
        raise ValueError(f"Invalid orchestrator path: {path!r}")
    return getattr(import_module(module_name), attr_name)


def create_scientist(domain_name: str, **kwargs) -> Any:
    """
    Create a domain scientist from the domain registry.

    Core stays domain-neutral: domain orchestrators are resolved lazily from a
    container-provided class/path or, for legacy compatibility, from the default
    physics AutonomousScientist path.
    """
    discover_domains()

    spec = DomainRegistry.get_domain(domain_name)
    container = spec.factory()

    orchestrator_cls = getattr(container, "orchestrator_class", None)
    if orchestrator_cls is None:
        orchestrator_path = kwargs.pop(
            "orchestrator_path",
            getattr(container, "orchestrator_path", DEFAULT_ORCHESTRATOR),
        )
        orchestrator_cls = _load_symbol(orchestrator_path)

    return orchestrator_cls(
        generator=container.generator,
        critic=container.critic,
        sandbox=container.sandbox,
        memory=container.memory,
        llm_reasoner=container.llm_reasoner,
        **kwargs,
    )
