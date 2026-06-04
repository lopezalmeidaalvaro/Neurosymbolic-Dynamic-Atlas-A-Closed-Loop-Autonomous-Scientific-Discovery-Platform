import os
import time
from typing import List, Any, Dict
from core.observability.capability_registry import CapabilityRegistry
from core.observability.snapshot_generator import ArchitectureSnapshotGenerator

class DocumentationManager:
    @staticmethod
    def record_phase_completion(
        phase_id: str,
        capabilities_enabled: List[str],
        validation_results: Any,
        benchmark_outcomes: Any,
        test_counts: int,
        docs_dir: str = "docs"
    ) -> None:
        """
        Maintains chronological history of phase completions across ROADMAP.md,
        PHASE_STATUS.md, CAPABILITIES.md, and triggers ARCHITECTURE.md snapshot updates.
        """
        os.makedirs(docs_dir, exist_ok=True)
        completion_date = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Update docs/ROADMAP.md (Append table row or initialize table if needed)
        roadmap_path = os.path.join(docs_dir, "ROADMAP.md")
        roadmap_exists = os.path.exists(roadmap_path)
        caps_enabled_summary = ", ".join(capabilities_enabled)
        
        roadmap_row = f"| {phase_id} | COMPLETED | {completion_date} | Enabled: {caps_enabled_summary}. |"
        
        if not roadmap_exists:
            with open(roadmap_path, "w", encoding="utf-8") as f:
                f.write(f"""# Project Roadmap

Timeline of the Neurosymbolic Dynamic Atlas developmental phases.

| Phase | Status | Completion Date | Key Accomplishments |
| :--- | :---: | :--- | :--- |
""")
                
        with open(roadmap_path, "a", encoding="utf-8") as f:
            f.write(roadmap_row + "\n")
            
        # 2. Update docs/PHASE_STATUS.md (Chronological log, never overwrite, append new section)
        status_path = os.path.join(docs_dir, "PHASE_STATUS.md")
        status_exists = os.path.exists(status_path)
        
        val_str = json.dumps(validation_results, indent=2) if isinstance(validation_results, dict) else str(validation_results)
        bench_str = json.dumps(benchmark_outcomes, indent=2) if isinstance(benchmark_outcomes, dict) else str(benchmark_outcomes)
        
        status_entry = f"""
## [{phase_id}] - Completed on {completion_date}
- **Status:** COMPLETED
- **Capabilities Enabled:** {", ".join([f"`{c}`" for c in capabilities_enabled])}
- **Test Count:** {test_counts}
- **Validation Evidence:**
```
{val_str}
```
- **Benchmark Outcomes:**
```
{bench_str}
```

---
"""
        mode = "a" if status_exists else "w"
        with open(status_path, mode, encoding="utf-8") as f:
            if not status_exists:
                f.write(f"""# Phase Status Log

Chronological ledger of phase transitions, test suites ran, and scientific validation states.

---
""")
            f.write(status_entry)

        # 3. Update docs/CAPABILITIES.md (Regenerated from CapabilityRegistry as source of truth)
        caps_path = os.path.join(docs_dir, "CAPABILITIES.md")
        registry = CapabilityRegistry()
        # Register new capabilities dynamically if they are passed but not in registry yet
        for cap_name in capabilities_enabled:
            if not registry.get_capability(cap_name):
                registry.register_capability(
                    name=cap_name,
                    phase_introduced=phase_id,
                    description="Emergent capability enabled dynamically during phase completion.",
                    validation_evidence="Phase transition validation verification."
                )
                
        caps_markdown = registry.export_capabilities_markdown()
        with open(caps_path, "w", encoding="utf-8") as f:
            f.write(caps_markdown)

        # 4. Trigger Architecture Snapshot Update (Generates docs/ARCHITECTURE.md)
        arch_path = os.path.join(docs_dir, "ARCHITECTURE.md")
        ArchitectureSnapshotGenerator.generate_snapshot(output_path=arch_path)
        
        # 5. Initialize docs/EXPERIMENT_LOG.md if it does not exist
        explog_path = os.path.join(docs_dir, "EXPERIMENT_LOG.md")
        if not os.path.exists(explog_path):
            with open(explog_path, "w", encoding="utf-8") as f:
                f.write(f"""# Scientific Experiment Log

This file acts as a chronological, immutable ledger of all scientific experiments, benchmark executions, and training runs.

---
""")

        print(f"[INFO] DocumentationManager: Successfully logged completion of {phase_id} to roadmaps and status registries.")
import json
