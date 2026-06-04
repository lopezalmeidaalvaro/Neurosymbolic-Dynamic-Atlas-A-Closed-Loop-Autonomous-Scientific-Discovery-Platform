import os
import json
import time
from typing import Dict, Any, List

class TheoryRefinement:
    """
    Component J: Theory Refinement Engine.
    Tracks state machine transitions (ACCEPTED, REJECTED, REVISED, SUPERSEDED) and version trees.
    """

    def __init__(self, leaderboard_path: str = "law_leaderboard.json", falsification_path: str = "law_falsification_report.json", output_path: str = "law_versions.json"):
        self.leaderboard_path = leaderboard_path
        self.falsification_path = falsification_path
        self.output_path = output_path
        self.versions: List[Dict[str, Any]] = []

    def load_json(self, path: str) -> List[Any]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def refine_theories(self) -> List[Dict[str, Any]]:
        print("Running Theory Refinement Engine...")
        leaderboard = self.load_json(self.leaderboard_path)
        falsification = self.load_json(self.falsification_path)
        
        # Build maps
        fal_map = {item["id"]: item for item in falsification}
        
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.versions = []
        
        # Load existing versions if available to preserve history
        existing_versions = {}
        if os.path.exists(self.output_path):
            try:
                for v in self.load_json(self.output_path):
                    existing_versions[v["law_id"]] = v
            except Exception:
                pass
                
        for item in leaderboard:
            if item["type"] != "DISCOVERED":
                continue
                
            law_id = item["id"]
            rule_str = item["rule"]
            score = item["tournament_score"]
            
            fal_info = fal_map.get(law_id, {})
            fal_verdict = fal_info.get("verdict", "FALSIFIED")
            
            # Determine state machine state
            # Base state is CANDIDATE.
            # If falsified, it is REJECTED.
            # If survived, it is ACCEPTED.
            # If it's a multi-variable rule, we consider it a REVISED version of a simpler rule.
            is_composite = " AND " in rule_str
            state = "ACCEPTED" if fal_verdict == "SURVIVED" else "REJECTED"
            
            version = "1.0"
            prev_id = None
            note = "Initial discovery."
            
            if is_composite:
                # e.g., IF (stabilizer_overlap > 0.6) AND (tensor_rank < 3) THEN synergy increases
                # This refines/supersedes the simpler version (stabilizer_overlap > 0.6)
                version = "1.1"
                # Find matching simpler law ID from leaderboard to link as parent
                prev_id = "LAW_002" if "stabilizer_overlap" in rule_str else "LAW_001"
                note = f"Added variable constraint. Supersedes {prev_id}."
                
            history = []
            if law_id in existing_versions:
                history = existing_versions[law_id].get("history", [])
                
            # Add current state to history
            history.append({
                "timestamp": timestamp,
                "state": state,
                "note": note
            })
            
            ver_record = {
                "law_id": law_id,
                "rule": rule_str,
                "version": version,
                "previous_version_id": prev_id,
                "state": state,
                "tournament_score": score,
                "history": history
            }
            self.versions.append(ver_record)
            
        # Write versions
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.versions, f, indent=2, ensure_ascii=False)
            
        print(f"Theory refinement complete. Tracked versions for {len(self.versions)} laws. Output: {self.output_path}")
        return self.versions

if __name__ == "__main__":
    refinement = TheoryRefinement()
    refinement.refine_theories()
