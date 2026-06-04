import os
from typing import Dict, List, Any
from core.observability.capability_registry import CapabilityRegistry

class ArchitectureSnapshotGenerator:
    @staticmethod
    def generate_snapshot(output_path: str = "docs/ARCHITECTURE.md") -> str:
        registry = CapabilityRegistry()
        active_caps = registry.get_capabilities()
        
        # Sort capabilities by name
        active_caps_sorted = sorted(active_caps, key=lambda c: c.name)
        
        caps_rows = []
        for cap in active_caps_sorted:
            caps_rows.append(f"| **{cap.name}** | {cap.phase_introduced} | {cap.description} |")
            
        caps_table = "\n".join(caps_rows)
        
        content = f"""# System Architecture Snapshot

This document provides a live overview of the discovery platform's components, dependencies, data flows, and active capabilities.

---

## 1. Active Capabilities Matrix

Below are the emergent capabilities verified and registered in the system:

| Capability | Phase Introduced | Description |
| :--- | :---: | :--- |
{caps_table}

---

## 2. Component Directory Structure

The platform is organized into three major layers: the domain-agnostic **Core**, the domain-specific **Scientific Plugins**, and the shared **Observability Layer**.

```mermaid
graph TD
    subgraph Core [Core Orchestration & Interfaces]
        direction TB
        registry[DomainRegistry]
        container[ScientificContainer]
        factory[ScientistFactory]
        abstract[Base Abstractions]
    end
    
    subgraph Observability [Observability & Documentation Layer]
        docman[DocumentationManager]
        capreg[CapabilityRegistry]
        explog[ExperimentLogger]
        dash[KnowledgeDashboard]
        snap[SnapshotGenerator]
    end

    subgraph Plugins [Scientific Domains & Engines]
        direction LR
        quantum[Quantum Domain]
        physics[Physics Domain]
    end

    Core --> Plugins
    Plugins --> Observability
    Core --> Observability
```

### A. Core Layers (`core/`)
* **`core/abstractions/`**: Defines basic abstract classes (`BaseSandbox`, `BaseCritic`, `BaseMemory`, `BaseHypothesisGenerator`) ensuring type safety and interchangeability.
* **`core/domains/`**: Domain loading infrastructure. Implements dynamic adapter scanning and registering.
* **`core/orchestration/`**: Implements the dependency injection container (`ScientificContainer`) and orchestrator instantiators.

### B. Quantum Domain (`quantum/`)
* **`quantum/sandbox/`**: Statevector simulation executor using `Qiskit` to simulate noise-free circuit execution.
* **`quantum/critics/`**: Mathematical evaluation of circuit outputs against targets using physical state vector fidelity.
* **`quantum/evolution/`**: Genetic optimization engine containing selection, crossover/mutation operations, and knowledge-guided mutation injection.
* **`quantum/knowledge/`**: The knowledge distillation loop. Extracts canonical gate subsequences, structural motifs, and maintains the in-memory graph.
* **`quantum/memory/`**: Non-volatile storage of patterns and metrics.

### C. Observability Layer (`core/observability/`)
* **`CapabilityRegistry`**: Tracks active system capabilities across phases.
* **`DocumentationManager`**: Automates roadmaps, phase status, and capability matrix updates.
* **`ExperimentLogger`**: Log benchmark executions chronologically.
* **`KnowledgeDashboard`**: Computes pattern reuse, evolution, and transfer performance.
* **`ArchitectureSnapshotGenerator`**: Generates this document.

---

## 3. Scientific Discovery Loop & Data Flow

The Discovery Engine executes an iterative search and selection flow. Knowledge extracted in past cycles is injected to guide and accelerate future mutations.

```mermaid
sequenceDiagram
    participant S as AutonomousScientist
    participant G as HypothesisGenerator
    participant E as EvolutionEngine
    participant M as DiscoveryMemory
    participant SB as SandboxExecutor
    participant C as Critic Evaluator

    S->>G: Build Context & Propose Circuit
    G->>M: Query Distilled Patterns
    M-->>G: High-Score Motifs (length <= 3)
    G->>E: Start Evolutionary Search
    loop Generation Step
        E->>E: Select Top Genomes
        E->>M: Query Active Patterns (rate 0.2)
        M-->>E: Motifs
        E->>E: Inject Motif into Circuit Mutation
        E->>SB: Execute Circuit
        SB-->>E: Statevector & Metrics
        E->>C: Calculate Fidelity & Score
        C-->>E: Physical Score
        E->>E: Record Survivor Successes
    end
    E-->>S: Best Circuit
    S->>S: Document Phase & Log Metrics
```

---

## 4. Operational Boundaries

* **Sandbox Isolation:** No operations inside the Qiskit sandbox can write to the local filesystem or access network resources.
* **Epistemic Isolation:** The evaluation process is strictly mathematical (fidelity). The search space mutation does not memorize absolute circuits, only local motifs.
"""
        
        # Write to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return content
