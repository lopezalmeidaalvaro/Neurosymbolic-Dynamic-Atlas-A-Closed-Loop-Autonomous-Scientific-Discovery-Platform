from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - optional fallback
    PdfPages = None
    plt = None

try:
    from physics.core.base_module import ScientificModule
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from core.base_module import ScientificModule


PHYSICS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PHYSICS_ROOT.parent
ARTIFACTS_DIR = PHYSICS_ROOT / "artifacts"


class ExpertValidation(ScientificModule):
    """External review workflow that reuses existing papers and KG infrastructure."""

    reused_modules = [
        "papers/system/representation_aware_system_identification.tex",
        "physics/papers/system_paper.md",
        "physics/auto_paper_generator.py",
        "physics/core/autonomous/research_reporter.py",
        "physics/knowledge_graph.py",
        "physics/core/autonomous/hypothesis_engine.py",
    ]

    def prepare_paper_for_review(self, paper_path: str | Path, anonymize: bool = True) -> dict[str, Any]:
        path = Path(paper_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if not path.exists():
            return {"ok": False, "error": f"paper_not_found: {path}", "pdf_path": None}
        content = path.read_text(encoding="utf-8", errors="replace")
        if anonymize:
            content = _anonymize(content)
        review_dir = PHYSICS_ROOT / "papers"
        review_dir.mkdir(parents=True, exist_ok=True)
        review_source = review_dir / "for_review_source.tex"
        review_source.write_text(content, encoding="utf-8")
        pdf_path = review_dir / "for_review.pdf"
        _write_review_pdf(pdf_path, content)
        return {"ok": True, "source_path": str(review_source), "pdf_path": str(pdf_path), "anonymized": anonymize}

    def generate_reviewer_invitation(self, reviewer_email: str, paper_title: str) -> str:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        template = f"""To: {reviewer_email}
Subject: Request for external scientific review - {paper_title}

Dear reviewer,

We are preparing an external technical review of "{paper_title}". The requested review focuses on methodological validity, evidence level, reproducibility, and overclaiming risk.

Suggested review points:
- Are the claims supported by the presented evidence level?
- Are validation datasets, baselines, and failure modes described clearly?
- Which claims should be weakened, removed, or tested further?
- Which experiments would make the result externally reproducible?

Thank you for considering this review.
"""
        output_path = ARTIFACTS_DIR / "reviewer_invitation_template.txt"
        output_path.write_text(template, encoding="utf-8")
        return str(output_path)

    def parse_reviewer_feedback(self, feedback_text: str) -> list[dict[str, str]]:
        points = []
        chunks = [item.strip(" -\t") for item in re.split(r"[\n;]+", feedback_text or "") if item.strip()]
        for chunk in chunks:
            lowered = chunk.lower()
            if any(token in lowered for token in ["wrong", "invalid", "overclaim", "missing", "flawed", "weak"]):
                label = "CRITICISM"
            elif any(token in lowered for token in ["should", "suggest", "recommend", "could", "add"]):
                label = "SUGGESTION"
            elif "?" in chunk or lowered.startswith(("what", "why", "how", "does")):
                label = "QUESTION"
            elif any(token in lowered for token in ["strong", "clear", "useful", "good"]):
                label = "PRAISE"
            else:
                label = "SUGGESTION"
            points.append({"type": label, "text": chunk})
        return points

    def convert_feedback_to_hypotheses(self, feedback_points: list[dict[str, str]]) -> list[dict[str, Any]]:
        hypotheses = []
        for idx, point in enumerate(feedback_points, start=1):
            if point["type"] not in {"CRITICISM", "SUGGESTION", "QUESTION"}:
                continue
            hypotheses.append(
                {
                    "id": f"expert_review_{idx}",
                    "source": "expert_review",
                    "hypothesis": f"Address reviewer point: {point['text']}",
                    "confidence_prior": 0.5,
                    "status": "proposed",
                }
            )
        kg_path = ARTIFACTS_DIR / "expert_review_hypotheses.json"
        kg_path.write_text(json.dumps(hypotheses, indent=2), encoding="utf-8")
        self._try_register_in_kg(hypotheses)
        return hypotheses

    def track_review_cycle(
        self,
        paper_version: str,
        reviewer: str,
        feedback_points: list[dict[str, str]],
        actions_taken: list[str] | None = None,
    ) -> str:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        path = ARTIFACTS_DIR / "review_cycle_log.md"
        lines = [
            "",
            f"## Review Cycle - {datetime.now().isoformat(timespec='seconds')}",
            "",
            f"- Paper version: `{paper_version}`",
            f"- Reviewer: `{reviewer}`",
            f"- Feedback points: {len(feedback_points)}",
            "",
            "### Feedback",
            "",
        ]
        for point in feedback_points:
            lines.append(f"- **{point['type']}**: {point['text']}")
        lines.extend(["", "### Actions Taken", ""])
        for action in actions_taken or ["Pending triage"]:
            lines.append(f"- {action}")
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return str(path)

    def run(
        self,
        paper_path: str | Path | None = None,
        feedback_text: str | None = None,
        reviewer_email: str = "reviewer@example.org",
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.status = "running"
        paper_path = paper_path or "papers/system/representation_aware_system_identification.tex"
        prepared = self.prepare_paper_for_review(paper_path, anonymize=True)
        invitation = self.generate_reviewer_invitation(reviewer_email, "Neurosymbolic Scientific Discovery")
        feedback_text = feedback_text or "Reviewer should check overclaiming and add external validation details."
        feedback_points = self.parse_reviewer_feedback(feedback_text)
        hypotheses = self.convert_feedback_to_hypotheses(feedback_points)
        review_log = self.track_review_cycle(str(prepared.get("source_path") or paper_path), reviewer_email, feedback_points)
        metrics = {
            "paper_prepared": prepared.get("ok", False),
            "feedback_points": len(feedback_points),
            "hypotheses_created": len(hypotheses),
            "invitation_template": invitation,
            "review_log": review_log,
            "reused_modules": self.reused_modules,
        }
        report_path = self.log_result(metrics, "expert_validation_report.md")
        return {"metrics": metrics, "report_path": report_path, "prepared": prepared}

    def _try_register_in_kg(self, hypotheses: list[dict[str, Any]]) -> None:
        try:
            sys.path.insert(0, str(PHYSICS_ROOT))
            from knowledge_graph import ScientificKnowledgeGraph

            kg = ScientificKnowledgeGraph()
            for item in hypotheses:
                if hasattr(kg, "add_hypothesis"):
                    kg.add_hypothesis(item)
        except Exception:
            return


def _anonymize(content: str) -> str:
    content = re.sub(r"\\author\{[^}]*\}", r"\\author{Anonymous}", content, flags=re.DOTALL)
    content = re.sub(r"\\affiliation\{[^}]*\}", r"\\affiliation{Anonymous Institution}", content, flags=re.DOTALL)
    content = re.sub(r"Alvaro Lopez Almeida|Lopez Almeida, Alvaro|Alvaro", "Anonymous", content, flags=re.IGNORECASE)
    return content


def _write_review_pdf(pdf_path: Path, content: str) -> None:
    if PdfPages is None or plt is None:
        pdf_path.write_bytes(b"%PDF-1.4\n% fallback placeholder\n")
        return
    clean = re.sub(r"\\[a-zA-Z]+(\[[^]]*\])?(\{[^}]*\})?", " ", content)
    clean = re.sub(r"\s+", " ", clean).strip()
    preview = clean[:1800] or "Anonymous review draft."
    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.94, "Anonymous Review Draft", fontsize=16, weight="bold")
        fig.text(0.08, 0.88, "\n".join(_wrap(preview, 92)), fontsize=9, va="top")
        pdf.savefig(fig)
        plt.close(fig)


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    count = 0
    for word in words:
        if count + len(word) + len(current) > width:
            lines.append(" ".join(current))
            current = [word]
            count = len(word)
        else:
            current.append(word)
            count += len(word)
    if current:
        lines.append(" ".join(current))
    return lines


if __name__ == "__main__":
    print(json.dumps(ExpertValidation().run(), indent=2, default=str))
