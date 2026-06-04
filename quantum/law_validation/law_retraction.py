import os
import json
from typing import Dict, Any, List

class LawRetractionEngine:
    """
    Component L: Law Retraction Engine.
    Manages promotions and retractions: SCIENTIFICALLY_ESTABLISHED, REPLICATED, PROVISIONAL, REVISED, RETRACTED.
    """

    def __init__(self, output_path: str = "law_status_registry.json"):
        self.output_path = output_path
        self.registry: Dict[str, Any] = {}

    def retract_and_update(
        self, 
        replications: List[Dict[str, Any]], 
        simulators: List[Dict[str, Any]], 
        falsifications: List[Dict[str, Any]], 
        meta_validations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        print("Running Law Retraction & Status Registry Engine...")
        
        rep_map = {item["id"]: item for item in replications}
        sim_map = {item["id"]: item for item in simulators}
        fal_map = {item["id"]: item for item in falsifications}
        
        law_statuses = {}
        
        # 1. Evaluate Laws
        for law_id in rep_map:
            rep_rate = rep_map[law_id]["replication_rate"]
            agreement = sim_map.get(law_id, {}).get("agreement_score", 0.80)
            
            # Retrieve falsification score (survival score)
            # Find the match in counterexample discoveries
            survival_score = 0.85 # default
            for f in fal_map.values():
                if f["id"] == law_id:
                    # Survival score is (1.0 - break_rate)
                    survival_score = 1.0 - f.get("law_break_rate", 0.15)
                    break
                    
            # State transition logic:
            if rep_rate < 0.60:
                status = "RETRACTED"
            elif rep_rate < 0.85 or survival_score < 0.50:
                status = "PROVISIONAL"
            elif rep_rate >= 0.90 and agreement >= 0.85 and survival_score >= 0.75:
                status = "SCIENTIFICALLY_ESTABLISHED"
            else:
                status = "REPLICATED"
                
            law_statuses[law_id] = {
                "rule": rep_map[law_id]["rule"],
                "status": status,
                "replication_rate": rep_rate,
                "agreement_score": agreement,
                "survival_score": round(survival_score, 4)
            }
            
        # 2. Evaluate Meta-Laws
        meta_statuses = {}
        for m_item in meta_validations:
            m_id = m_item["id"]
            m_status = m_item["status"] # ESTABLISHED_META_LAW or PROVISIONAL_META_LAW
            
            status = "ESTABLISHED_META_LAW" if m_status == "ESTABLISHED_META_LAW" else "PROVISIONAL_META_LAW"
            
            meta_statuses[m_id] = {
                "statement": m_item["statement"],
                "status": status,
                "bootstrap_survival": m_item["bootstrap_survival_rate"]
            }
            
        self.registry = {
            "laws": law_statuses,
            "meta_laws": meta_statuses
        }
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
            
        print(f"Retraction status updates completed. Registry saved: {self.output_path}")
        return self.registry

if __name__ == "__main__":
    # Test script with dummy inputs
    retraction = LawRetractionEngine()
    retraction.retract_and_update([], [], [], [])
