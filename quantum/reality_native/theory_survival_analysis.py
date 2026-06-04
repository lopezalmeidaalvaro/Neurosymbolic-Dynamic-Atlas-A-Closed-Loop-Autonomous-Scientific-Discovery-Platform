import os
from typing import Dict, Any, List

class TheorySurvivalAnalysis:
    """
    Phase 3C-F: Survival Analysis.
    Calculates the throughput metrics and survival rates of theories inside the pipeline.
    """

    def __init__(
        self,
        discovery_count: int,
        confirmation_count: int,
        reproduction_count: int
    ):
        self.discovery_count = discovery_count
        self.confirmation_count = confirmation_count
        self.reproduction_count = reproduction_count

    def analyze_survival(self) -> Dict[str, Any]:
        # A theory survives if it is both confirmed and reproduced successfully
        final_survivors = self.reproduction_count # Since reproduction is the final filter
        survival_rate = final_survivors / self.discovery_count if self.discovery_count > 0 else 0.0

        results = {
            "discovery_count": self.discovery_count,
            "confirmation_count": self.confirmation_count,
            "reproduction_count": self.reproduction_count,
            "final_survival_count": final_survivors,
            "theory_survival_rate": round(survival_rate * 100.0, 2)
        }

        self._write_markdown_report(results)
        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Theory Survival Analysis Report — Phase 3C",
            "",
            "Tracks the retention and falsification of theories as they progress through automated discovery, confirmation, and reproduction filters.",
            "",
            "## Pipeline Throughput Funnel",
            "",
            "```mermaid",
            "graph TD",
            f"    A[\"Discovery Count: {results['discovery_count']}\"] --> B[\"Confirmation Count: {results['confirmation_count']}\"]",
            f"    B --> C[\"Reproduction Count: {results['reproduction_count']}\"]",
            f"    C --> D[\"Final Survival Count: {results['final_survival_count']}\"]",
            "```",
            "",
            "## Summary Metrics",
            "",
            f"- **Discovery Count**: `{results['discovery_count']}` theories",
            f"- **Confirmation Count**: `{results['confirmation_count']}` theories",
            f"- **Reproduction Count**: `{results['reproduction_count']}` theories",
            f"- **Final Survival Count**: `{results['final_survival_count']}` theories",
            f"- **Overall Theory Survival Rate**: **`{results['theory_survival_rate']:.2f}%`**",
            ""
        ]

        os.makedirs("docs", exist_ok=True)
        with open("docs/SURVIVAL_ANALYSIS_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    pass
