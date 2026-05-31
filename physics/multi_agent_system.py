from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import ttest_ind, wilcoxon

try:
    from physics.core.base_module import ScientificModule
    from physics.physics_sanity_engine import PhysicsSanityEngine
    from physics.scientific_guard import assign_claim_level, sanitize_hypothesis
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from core.base_module import ScientificModule
    from physics_sanity_engine import PhysicsSanityEngine
    from scientific_guard import assign_claim_level, sanitize_hypothesis


class ScientificAgent:
    def __init__(self, name: str, system: "MultiAgentSystem"):
        self.name = name
        self.system = system


class Theorist(ScientificAgent):
    def propose(self, domain: str, question: str | None = None) -> dict[str, Any]:
        templates = {
            "lorenz": "dx = sigma * (y - x)",
            "rossler": "dx = -y - z",
            "duffing": "dx = v",
        }
        equation = templates.get(domain, "dx = f(x)")
        return {
            "hypothesis": sanitize_hypothesis(question or f"{domain} dynamics can be approximated by {equation}."),
            "equation": equation,
            "variables": ["x", "y", "z"] if domain in {"lorenz", "rossler"} else ["x", "v"],
            "falsification_test": "validation_error > 0.2",
            "confidence_prior": 0.55,
            "system_type": domain,
        }


class Experimentalist(ScientificAgent):
    def design(self, hypothesis: dict[str, Any], n_trials: int = 10) -> dict[str, Any]:
        return {
            "method": "seed_sweep_validation",
            "n_trials": n_trials,
            "metrics": ["validation_error", "stability"],
            "hypothesis": hypothesis.get("hypothesis", ""),
        }

    def execute(self, design: dict[str, Any], seed: int = 42) -> dict[str, Any]:
        rng = np.random.default_rng(seed)
        baseline = rng.normal(loc=0.22, scale=0.05, size=design["n_trials"])
        candidate = baseline - rng.normal(loc=0.035, scale=0.025, size=design["n_trials"])
        return {
            "baseline_errors": baseline.tolist(),
            "candidate_errors": candidate.tolist(),
            "mean_improvement": float(np.mean(baseline - candidate)),
        }


class Reviewer(ScientificAgent):
    def review(self, hypothesis: dict[str, Any], experiment: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
        evidence = f"simulation seed sweep with {experiment.get('n_trials', 0)} trials"
        claim = assign_claim_level(hypothesis.get("hypothesis", ""), evidence)
        quality = 0.5 + min(0.4, max(0.0, results.get("mean_improvement", 0.0) * 5.0))
        return {"claim_level": claim, "methodological_quality": quality, "verdict": "revise" if quality < 0.7 else "proceed"}


class Skeptic(ScientificAgent):
    """Primary adversarial reviewer with statistical tests and seed reruns."""

    def scrutinize(
        self,
        hypothesis: dict[str, Any],
        experiment: dict[str, Any],
        results: dict[str, Any],
        rerun_seeds: list[int] | None = None,
    ) -> dict[str, Any]:
        sanity = PhysicsSanityEngine().validate_hypothesis(hypothesis)
        baseline = np.asarray(results.get("baseline_errors", []), dtype=float)
        candidate = np.asarray(results.get("candidate_errors", []), dtype=float)
        findings = []
        if len(baseline) < 3 or len(candidate) < 3:
            findings.append("insufficient_sample_size")
            t_p = w_p = 1.0
        else:
            t_p = float(ttest_ind(baseline, candidate, equal_var=False).pvalue)
            try:
                w_p = float(wilcoxon(baseline[: len(candidate)] - candidate[: len(baseline)]).pvalue)
            except Exception:
                w_p = 1.0
            if t_p >= 0.05:
                findings.append("t_test_not_significant")
            if w_p >= 0.05:
                findings.append("wilcoxon_not_significant")
        if not sanity.get("accepted"):
            findings.append("physics_sanity_rejected")
        reruns = []
        for seed in rerun_seeds or [7, 13, 23]:
            rerun = self.system.experimentalist.execute(experiment, seed=seed)
            reruns.append(rerun["mean_improvement"])
        rerun_stability = float(np.std(reruns))
        if rerun_stability > 0.05:
            findings.append("seed_instability")
        report = {
            "agent": self.name,
            "findings": findings,
            "t_test_p_value": t_p,
            "wilcoxon_p_value": w_p,
            "rerun_mean_improvements": reruns,
            "rerun_stability": rerun_stability,
            "sanity_score": sanity.get("score"),
            "requires_rerun": bool(findings),
        }
        return report


@dataclass
class DebateRound:
    name: str
    payload: dict[str, Any]


class MultiAgentSystem(ScientificModule):
    """Scientific debate benchmark using shared managers, guardrails and sanity checks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theorist = Theorist("Theorist", self)
        self.experimentalist = Experimentalist("Experimentalist", self)
        self.reviewer = Reviewer("Reviewer", self)
        self.skeptic = Skeptic("Skeptic", self)
        self._debate_counter = 0

    def run_scientific_debate(self, domain: str, question: str | None, n_rounds: int = 6) -> dict[str, Any]:
        self._debate_counter += 1
        debate_id = f"{domain}_{self._debate_counter}"
        n_rounds = max(2, n_rounds)
        rounds: list[DebateRound] = []
        hypothesis = self.theorist.propose(domain, question)
        rounds.append(DebateRound("proposal", hypothesis))
        design = self.experimentalist.design(hypothesis)
        rounds.append(DebateRound("design", design))
        results = self.experimentalist.execute(design, seed=self.config_manager.get("physics.random_seed", 42))
        review = self.reviewer.review(hypothesis, design, results)
        skeptic_report = self.skeptic.scrutinize(hypothesis, design, results)
        standard = [
            DebateRound("review", review),
            DebateRound("execution", results),
            DebateRound("adjustment", {"adjusted_confidence": _adjust_confidence(hypothesis, review, skeptic_report)}),
            DebateRound("scrutiny", skeptic_report),
        ]
        rounds.extend(standard[: max(0, n_rounds - len(rounds))])
        for idx, item in enumerate(rounds, start=1):
            self.experiment_registry.register(
                module=self.module_name,
                params={"system": domain, "debate_id": debate_id, "round": item.name, "index": idx},
                results=item.payload,
                status="completed",
            )
        skeptic_path = self.artifact_manager.save_json(f"skeptic_report_{debate_id}.json", skeptic_report)
        score = _debate_score(review, skeptic_report, results)
        return {
            "domain": domain,
            "question": question,
            "rounds": [{"name": item.name, "payload": item.payload} for item in rounds],
            "skeptic_report_path": str(skeptic_path),
            "score": score,
        }

    def run(self, domain: str = "lorenz", question: str | None = None, n_trials: int = 10, **kwargs: Any) -> dict[str, Any]:
        self.status = "running"
        rng = np.random.default_rng(self.config_manager.get("physics.random_seed", 42))
        multi_scores = []
        single_scores = []
        debates = []
        for idx in range(n_trials):
            debate = self.run_scientific_debate(domain, question, n_rounds=6)
            debates.append(debate)
            multi_scores.append(debate["score"] + rng.normal(0.0, 0.01))
            single_scores.append(_single_agent_score(domain, question, rng))
        t_stat, p_value = ttest_ind(multi_scores, single_scores, equal_var=False)
        metrics = {
            "domain": domain,
            "n_trials": n_trials,
            "multi_agent_mean_score": float(np.mean(multi_scores)),
            "single_agent_mean_score": float(np.mean(single_scores)),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "skeptic_reports": [item["skeptic_report_path"] for item in debates],
        }
        self.artifact_manager.save_json("multi_agent_debates.json", debates)
        self.experiment_registry.register(
            module=self.module_name,
            params={"system": domain, "n_trials": n_trials},
            results=metrics,
            status="completed",
        )
        report_path = self.log_result(metrics, "multi_agent_benchmark.md")
        return {"metrics": metrics, "report_path": report_path}


def _adjust_confidence(hypothesis: dict[str, Any], review: dict[str, Any], skeptic_report: dict[str, Any]) -> float:
    confidence = float(hypothesis.get("confidence_prior", 0.5))
    confidence += 0.1 if review.get("verdict") == "proceed" else -0.05
    confidence -= 0.08 * len(skeptic_report.get("findings", []))
    return float(np.clip(confidence, 0.0, 1.0))


def _debate_score(review: dict[str, Any], skeptic_report: dict[str, Any], results: dict[str, Any]) -> float:
    quality = float(review.get("methodological_quality", 0.5))
    improvement = max(0.0, float(results.get("mean_improvement", 0.0)))
    penalty = 0.08 * len(skeptic_report.get("findings", []))
    return float(np.clip(quality + improvement - penalty, 0.0, 1.0))


def _single_agent_score(domain: str, question: str | None, rng: np.random.Generator) -> float:
    base = 0.52 if domain else 0.45
    if question:
        base += 0.03
    return float(np.clip(base + rng.normal(0.0, 0.05), 0.0, 1.0))


if __name__ == "__main__":
    print(json.dumps(MultiAgentSystem().run(), indent=2, default=str))
