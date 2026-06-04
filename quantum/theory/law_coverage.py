import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class LawCoverage:
    """
    Component E: Law Coverage Analysis.
    Evaluates whether the active theories cover more than 80% of all accepted scientific laws.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.db_path = db_path
        self.memory = TheoryMemory(db_path=db_path)

    def evaluate_coverage(self) -> Dict[str, Any]:
        theories = self.memory.get_all_theories()
        
        # Total established laws in the registry (Phase 2B output)
        total_laws = 27
        
        explained_laws = set()
        for t in theories:
            # Only consider active/supported or candidate theories (exclude rejected ones)
            if t.get("status") != "REJECTED":
                for l_id in t.get("laws_explained", []):
                    explained_laws.add(l_id)
                    
        num_explained = len(explained_laws)
        coverage_ratio = num_explained / total_laws if total_laws > 0 else 0.0
        
        status = "PASSED" if coverage_ratio >= 0.80 else "FAILED"
        
        report = {
            "total_laws": total_laws,
            "explained_laws_count": num_explained,
            "explained_laws_list": sorted(list(explained_laws)),
            "coverage_ratio": round(coverage_ratio, 4),
            "status": status
        }
        
        with open("law_coverage_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"Law coverage evaluation: {num_explained}/{total_laws} explained ({coverage_ratio*100:.2f}%) - Status: {status}")
        return report

if __name__ == "__main__":
    cov = LawCoverage()
    cov.evaluate_coverage()
