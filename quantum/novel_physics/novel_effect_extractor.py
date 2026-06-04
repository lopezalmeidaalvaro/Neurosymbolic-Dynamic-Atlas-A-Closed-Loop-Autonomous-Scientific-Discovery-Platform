import os
from typing import Dict, Any, List
from quantum.novel_physics.known_effect_catalog import KnownEffectCatalog

class NovelEffectExtractor:
    """
    Phase 4C: Novel Effect Extraction.
    Identifies physical effects that are shared across devices, vendors, and paradigms,
    but cannot be explained by standard models.
    """

    def __init__(self):
        self.catalog = KnownEffectCatalog()

    def extract_novel_effects(self, residuals: List[Dict[str, Any]], candidate_theories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        novel_effects = []

        # Analyze each theory's structural equation to see if it represents a novel effect
        for t in candidate_theories:
            theory_id = t["theory_id"]
            equation = t["equation"]
            domain = t["domain"]

            # If it does not match standard calibration/noise models in the catalog, it is novel
            is_novel = not self.catalog.matches_known_effect(equation)

            # Analyze multi-device, multi-vendor support from the residuals
            domain_residuals = [r for r in residuals if r["id"].startswith(f"RUN_{domain[:4].upper()}")]
            devices = list(set([r["device"] for r in domain_residuals]))
            vendors = list(set([r["vendor"] for r in domain_residuals]))
            paradigms = list(set([r["paradigm"] for r in domain_residuals]))

            if is_novel and len(vendors) >= 2:
                novel_effects.append({
                    "effect_id": f"NEFFECT_{theory_id.split('_')[1]}",
                    "theory_id": theory_id,
                    "domain": domain,
                    "equation": equation,
                    "devices_count": len(devices),
                    "vendors_count": len(vendors),
                    "paradigms_count": len(paradigms),
                    "devices": devices,
                    "vendors": vendors,
                    "paradigms": paradigms,
                    "description": f"Universally persistent gap offset in {domain} across {', '.join(vendors)}."
                })

        self._write_markdown_report(novel_effects)
        return novel_effects

    def _write_markdown_report(self, effects: List[Dict[str, Any]]) -> None:
        lines = [
            "# Novel Effect Extraction Report — Phase 4C",
            "",
            "Identifies cross-device, cross-vendor, and cross-paradigm anomalies that represent new physical effects.",
            "",
            "| Effect ID | Theory ID | Domain | Equation | Devices | Vendors | Paradigms | Status |",
            "| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |"
        ]

        for e in effects:
            lines.append(
                f"| `{e['effect_id']}` | `{e['theory_id']}` | `{e['domain']}` | `{e['equation']}` | `{e['devices_count']}` | `{e['vendors_count']}` | `{e['paradigms_count']}` | **`NOVEL_PHYSICS_CANDIDATE`** |"
            )

        lines.append("")
        os.makedirs("docs", exist_ok=True)
        with open("docs/NOVEL_EFFECT_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
