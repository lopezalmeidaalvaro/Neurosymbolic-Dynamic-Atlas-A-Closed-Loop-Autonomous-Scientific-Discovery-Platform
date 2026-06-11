# Phase VIII: Core Decoupling Report

This report evaluates the coupling status of [scientist_factory.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/core/orchestration/scientist_factory.py) and details the decoupling design implemented in the repository.

---

## 1. Coupling Status of `scientist_factory.py`

An audit of the imports and code in [scientist_factory.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/core/orchestration/scientist_factory.py) confirms that it has **zero direct imports** to `physics/`, `quantum/`, or `satellite/` modules at import time. 

### 1.1 Dynamic Resolution Analysis
Instead of static imports, the module uses dynamic string-based loading:
*   `DEFAULT_ORCHESTRATOR = "physics.core.autonomous.autonomous_scientist:AutonomousScientist"`
*   A helper function `_load_symbol(path: str)` is defined to resolve and load symbols at execution time:
    ```python
    def _load_symbol(path: str) -> Any:
        module_name, _, attr_name = path.partition(":")
        return getattr(import_module(module_name), attr_name)
    ```
This dynamic resolution ensures that import-time dependency cycles are avoided, allowing the `core` library to load without forcing the presence of any particular domain compiler.

---

## 2. Decoupling & Registry Pattern Review

To maintain the architectural boundary between the core orchestration framework and domain-specific compilers, the monorepo utilizes the **Registry Pattern**:

1.  **Domain Registry**: The `DomainRegistry` (defined in `core/domains/domain_registry.py`) tracks active domain configurations without statically binding to them.
2.  **Plugin Discovery**: The discovery engine (defined in `core/domains/plugin_loader.py`) scans domain directories and yaml files dynamically at runtime, allowing domains to register their respective scientific container factories.
3.  **Domain Factories**: Each domain package implements its own container (e.g. `QuantumScientificContainer` in `quantum/factories/quantum_factory.py`), which packages local generators, critics, sandboxes, and memories.
4.  **Factory Instantiation**: `create_scientist` dynamically loads the domain specification and container, extracts the local classes, and instantiates the orchestrator without any hardcoded logic.

### 2.1 Conclusion
The core factory is fully decoupled. The legacy fallback to the default physics path is expressed as a string literal and resolved lazily, which satisfies the separation requirement. No further modifications were required.
