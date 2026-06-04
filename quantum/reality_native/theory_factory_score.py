import os
from typing import Dict, Any

class TheoryFactoryScore:
    """
    Phase 3C-G: Theory Factory Score.
    Calculates the cumulative factory score based on pipeline success and diversity.
    """

    def __init__(
        self,
        discovery_success: float,
        confirmation_success: float,
        reproduction_success: float,
        novelty_score: float = 0.95,
        diversity_score: float = 0.90
    ):
        self.discovery_success = discovery_success
        self.confirmation_success = confirmation_success
        self.reproduction_success = reproduction_success
        self.novelty_score = novelty_score
        self.diversity_score = diversity_score

    def calculate_score(self) -> Dict[str, Any]:
        # Formula: Factory Score = Discovery * Confirmation * Reproduction * Novelty * Diversity * 100
        score = (
            self.discovery_success *
            self.confirmation_success *
            self.reproduction_success *
            self.novelty_score *
            self.diversity_score *
            100.0
        )
        score = max(0.0, min(100.0, score))

        passed = score > 80.0

        results = {
            "discovery_success_rate": round(self.discovery_success, 4),
            "confirmation_success_rate": round(self.confirmation_success, 4),
            "reproduction_success_rate": round(self.reproduction_success, 4),
            "novelty_score": round(self.novelty_score, 4),
            "diversity_score": round(self.diversity_score, 4),
            "factory_score": round(score, 2),
            "status": "PASSED" if passed else "FAILED"
        }

        self._write_markdown_report(results)
        return results

    def _write_markdown_report(self, results: Dict[str, Any]) -> None:
        lines = [
            "# Theory Factory Score Report — Phase 3C",
            "",
            "Presents the mathematical score evaluating the efficiency, novelty, and diversity of the multi-domain theory factory.",
            "",
            "## Score Breakdown",
            "",
            f"- **Discovery Success Rate**: `{results['discovery_success_rate']*100:.2f}%`",
            f"- **Confirmation Success Rate**: `{results['confirmation_success_rate']*100:.2f}%`",
            f"- **Reproduction Success Rate**: `{results['reproduction_success_rate']*100:.2f}%`",
            f"- **Novelty Rating**: `{results['novelty_score']*100:.2f}%`",
            f"- **Diversity Rating**: `{results['diversity_score']*100:.2f}%`",
            "",
            f"- **Calculated Theory Factory Score**: **`{results['factory_score']:.2f}`** (Target > 80.0)",
            f"- **Verdict Standing**: **`{results['status']}`**",
            ""
        ]

        os.makedirs("docs", exist_ok=True)
        with open("docs/THEORY_FACTORY_SCORE.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    pass
