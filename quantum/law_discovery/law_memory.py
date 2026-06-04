import os
import json
from typing import Dict, Any, List

class LawMemory:
    """
    Component M: Law Memory System.
    Manages structured storage for accepted_laws.json, candidate_laws.json, and rejected_laws.json.
    """

    def __init__(self, directory: str = "."):
        self.directory = directory
        self.accepted_path = os.path.join(directory, "accepted_laws.json")
        self.candidate_path = os.path.join(directory, "candidate_laws.json")
        self.rejected_path = os.path.join(directory, "rejected_laws.json")
        self.versions_path = os.path.join(directory, "law_versions.json")

    def load_json(self, path: str) -> List[Any]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_json(self, path: str, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def synchronize_memory(self) -> None:
        """
        Synchronizes accepted, rejected, and candidate lists based on the version control ledger.
        """
        versions = self.load_json(self.versions_path)
        candidates = self.load_json(self.candidate_path)
        
        accepted = []
        rejected = []
        
        version_map = {item["law_id"]: item for item in versions}
        
        for cand in candidates:
            law_id = cand["id"]
            if law_id in version_map:
                v_item = version_map[law_id]
                state = v_item["state"]
                
                # Update candidates status
                cand["status"] = state
                
                if state == "ACCEPTED":
                    accepted.append(cand)
                elif state == "REJECTED":
                    rejected.append(cand)
                    
        self.save_json(self.accepted_path, accepted)
        self.save_json(self.rejected_path, rejected)
        self.save_json(self.candidate_path, candidates)
        print(f"Memory synced: {len(accepted)} accepted, {len(rejected)} rejected, {len(candidates)} candidates.")

    def get_accepted_laws(self) -> List[Dict[str, Any]]:
        return self.load_json(self.accepted_path)

    def get_candidate_laws(self) -> List[Dict[str, Any]]:
        return self.load_json(self.candidate_path)

    def get_rejected_laws(self) -> List[Dict[str, Any]]:
        return self.load_json(self.rejected_path)

if __name__ == "__main__":
    mem = LawMemory()
    mem.synchronize_memory()
