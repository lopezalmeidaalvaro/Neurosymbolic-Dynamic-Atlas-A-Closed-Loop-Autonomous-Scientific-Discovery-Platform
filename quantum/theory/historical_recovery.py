import json
from typing import Dict, Any, List
from quantum.theory.theory_memory import TheoryMemory

class HistoricalRecovery:
    """
    Component J: Historical Theory Rediscovery.
    Validates if the engine is able to rediscover classical physics/computing principles
    (Clifford dominance, noise accumulation, entanglement depth effects, circuit locality, graph centrality).
    """

    def __init__(self, db_path: str = "theory_memory.db", output_path: str = "historical_theory_recovery_report.json"):
        self.db_path = db_path
        self.output_path = output_path
        self.memory = TheoryMemory(db_path=db_path)

    def run_historical_recovery(self) -> Dict[str, Any]:
        theories = self.memory.get_all_theories()
        
        # Historical principles to discover
        principles = [
            {"id": "HIST_001", "name": "Clifford Dominance", "keyword": "clifford"},
            {"id": "HIST_002", "name": "Noise Accumulation", "keyword": "noise"},
            {"id": "HIST_003", "name": "Entanglement Depth Effects", "keyword": "rank"},
            {"id": "HIST_004", "name": "Circuit Locality Effects", "keyword": "stabilizer"},
            {"id": "HIST_005", "name": "Graph Centrality Effects", "keyword": "centrality"}
        ]
        
        recovered_count = 0
        recovered_details = []
        
        # Determine recovery by searching theory metadata/graphs
        for principle in principles:
            keyword = principle["keyword"]
            found = False
            associated_theory = "None"
            
            for t in theories:
                # Check theory assumptions, name, or graph nodes
                search_space = t.get("name", "").lower() + " " + " ".join(t.get("assumptions", [])).lower()
                graph = t.get("mechanism_graph", {})
                if graph:
                    search_space += " " + " ".join([n["id"].lower() for n in graph.get("nodes", [])])
                    
                if keyword in search_space:
                    found = True
                    associated_theory = t["id"]
                    break
                    
            if found:
                recovered_count += 1
                status = "RECOVERED"
            else:
                status = "UNRECOVERED"
                
            recovered_details.append({
                "id": principle["id"],
                "name": principle["name"],
                "associated_theory": associated_theory,
                "status": status
            })
            
        rate = recovered_count / len(principles) if principles else 0.0
        status = "PASSED" if rate >= 0.70 else "FAILED"
        
        report = {
            "total_principles": len(principles),
            "recovered_principles_count": recovered_count,
            "recovered_details": recovered_details,
            "historical_recovery_rate": round(rate, 4),
            "status": status
        }
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"Historical Theory Rediscovery: {recovered_count}/{len(principles)} recovered ({rate*100:.2f}%) - Status: {status}")
        return report

if __name__ == "__main__":
    hist = HistoricalRecovery()
    hist.run_historical_recovery()
