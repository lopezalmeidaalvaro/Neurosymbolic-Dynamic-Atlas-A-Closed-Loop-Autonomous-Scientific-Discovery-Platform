import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Capability:
    name: str
    phase_introduced: str
    description: str
    validation_evidence: str

class CapabilityRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CapabilityRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._capabilities = {}
            cls._instance._initialize_defaults()
        return cls._instance

    def __init__(self):
        # Prevent re-initialization if __new__ already ran it
        if not hasattr(self, "_capabilities"):
            self._capabilities = {}
            self._initialize_defaults()

    def _initialize_defaults(self):
        default_capabilities = [
            Capability(
                name="MULTI_DOMAIN_RUNTIME",
                phase_introduced="Phase 0E",
                description="Multi-domain runtime loading dynamic domain plugin adapters.",
                validation_evidence="DomainRegistry and PluginLoader test suites."
            ),
            Capability(
                name="QUANTUM_EXECUTION",
                phase_introduced="Phase 1B.1",
                description="Execution of abstract circuit specs in a Qiskit statevector sandbox.",
                validation_evidence="Qiskit sandbox tests for Bell and GHZ states."
            ),
            Capability(
                name="QUANTUM_FITNESS_FUNCTION",
                phase_introduced="Phase 1B.2",
                description="Physical fidelity evaluation scoring of candidate circuits.",
                validation_evidence="Fidelity mathematical bound tests."
            ),
            Capability(
                name="QUANTUM_EVOLUTION_ENGINE",
                phase_introduced="Phase 1B.3",
                description="Genetic optimization sweep of quantum circuits.",
                validation_evidence="Population convergence tests."
            ),
            Capability(
                name="KNOWLEDGE_DISTILLATION",
                phase_introduced="Phase 1B.4",
                description="Extraction of canonical representations and reusable motif graphs.",
                validation_evidence="Quantum pattern extractor and canonicalizer tests."
            ),
            Capability(
                name="TRANSFER_LEARNING",
                phase_introduced="Phase 1C",
                description="Mutation guiding and transfer learning from sub-problems.",
                validation_evidence="Multi-seed transfer learning benchmark (1.1667x speedup)."
            ),
            Capability(
                name="SCIENTIFIC_OBSERVABILITY",
                phase_introduced="Phase 1D",
                description="Documentation-as-code updates, capability registries, and logs.",
                validation_evidence="Observability and append-only log test verification."
            )
        ]
        for cap in default_capabilities:
            self._capabilities[cap.name] = cap

    def register_capability(self, name: str, phase_introduced: str, description: str, validation_evidence: str) -> None:
        self._capabilities[name] = Capability(
            name=name,
            phase_introduced=phase_introduced,
            description=description,
            validation_evidence=validation_evidence
        )

    def get_capabilities(self) -> List[Capability]:
        return list(self._capabilities.values())

    def get_capability(self, name: str) -> Optional[Capability]:
        return self._capabilities.get(name)

    def export_capabilities_markdown(self) -> str:
        lines = [
            "# Emergent System Capabilities",
            "",
            "This registry documents the capabilities discovered and validated during the project's evolution pipeline.",
            "",
            "| Capability | Phase Introduced | Description | Validation Evidence |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for cap in sorted(self.get_capabilities(), key=lambda c: c.phase_introduced):
            lines.append(f"| **{cap.name}** | {cap.phase_introduced} | {cap.description} | {cap.validation_evidence} |")
        return "\n".join(lines) + "\n"
