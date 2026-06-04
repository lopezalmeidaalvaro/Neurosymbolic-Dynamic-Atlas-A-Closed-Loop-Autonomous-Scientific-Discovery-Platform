import json
import time
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory
from quantum.hardware.negative_results_repository import NegativeResultsRepository

class RealityEvolution:
    """
    Component L: Theory Evolution Under Reality.
    Promotes theories that survive hardware tests, revises borderline ones,
    and automatically retires/falsifies theories that fail reality validation.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)
        self.neg_repo = NegativeResultsRepository(db_path=db_path)

    def evolve_theories(
        self,
        tournament_results: List[Dict[str, Any]],
        temporal_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Updates the statuses of all theories in the database based on hardware criteria.
        """
        evolution_records = []
        temp_map = {t["id"]: t for t in temporal_results}
        
        # Hard acceptance criteria thresholds
        # - Replication Rate >= 80%
        # - OOD Hardware Transfer >= 75%
        # - Temporal Stability >= 75%
        # - Mechanistic Validation Passed (YES)
        # - Adversarial Survival >= 75%
        
        for res in tournament_results:
            t_id = res["id"]
            theory_data = self.memory.get_theory(t_id)
            if not theory_data:
                continue
                
            old_status = theory_data.get("status", "CANDIDATE")
            
            # Fetch temporal stability for this theory (average over its predictions)
            t_preds = theory_data.get("predictions", [])
            temp_stabilities = [temp_map.get(p_id, {}).get("temporal_stability_score", 1.0) for p_id in t_preds]
            mean_temp_stability = float(np.mean(temp_stabilities)) if temp_stabilities else 1.0
            
            # Check conditions
            rep_ok = (res["replication_rate"] >= 0.80)
            ood_ok = (res["ood_transfer_score"] >= 0.75)
            temp_ok = (mean_temp_stability >= 0.75)
            mech_ok = (res["mechanism_passed"] == "YES")
            adv_ok = (res["adversarial_survival_rate"] >= 0.75)
            
            all_passed = rep_ok and ood_ok and temp_ok and mech_ok and adv_ok
            
            operation = ""
            new_status = ""
            rationale = ""
            
            if all_passed:
                operation = "RETENTION"
                new_status = "HARDWARE_SUPPORTED_THEORY"
                rationale = "Successfully survived all hardware replication, OOD, temporal, and adversarial stress tests."
            elif rep_ok or ood_ok:
                # Partically verified
                operation = "REVISION"
                new_status = "PARTIALLY_TRANSFERRED_THEORY"
                failures = []
                if not rep_ok: failures.append("Replication Rate < 80%")
                if not ood_ok: failures.append("OOD Transfer < 75%")
                if not temp_ok: failures.append("Temporal Stability < 75%")
                if not mech_ok: failures.append("Mechanistic Audit Failed")
                if not adv_ok: failures.append("Adversarial Survival < 75%")
                rationale = f"Revised for tighter boundary limits due to failures: {', '.join(failures)}."
            else:
                # Retire/falsify theory completely
                operation = "RETIREMENT"
                new_status = "RETIRED" # Database code status
                failures = []
                if not rep_ok: failures.append("Replication Rate < 80%")
                if not ood_ok: failures.append("OOD Transfer < 75%")
                if not mech_ok: failures.append("Mechanistic Audit Failed")
                
                # Determine final classification name
                classification = "SIMULATION_ONLY_THEORY" if res["replication_rate"] > 0.30 else "THEORY_RETRACTED"
                rationale = f"Falsified on real hardware devices. Classification: {classification}. Failures: {', '.join(failures)}"
                
                # Log to negative results repository
                self.neg_repo.record_failure(
                    failure_type="theory",
                    target_id=t_id,
                    reason=f"Failed hardware reality check. Score: {res['tournament_score']}. Rationale: {rationale}"
                )

            # Update database
            theory_data["status"] = new_status
            self.memory.save_theory(theory_data)
            
            evolution_records.append({
                "theory_id": t_id,
                "name": res["name"],
                "evolution_operation": operation,
                "old_status": old_status,
                "new_status": new_status,
                "rationale": rationale
            })
            
        with open("reality_evolution_report.json", "w", encoding="utf-8") as f:
            json.dump(evolution_records, f, indent=2, ensure_ascii=False)
            
        return evolution_records

import numpy as np
