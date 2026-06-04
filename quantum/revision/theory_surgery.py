import os
import json
import sqlite3
from typing import Dict, Any, List, Tuple
from quantum.theory.theory_memory import TheoryMemory

class TheorySurgeryEngine:
    """
    Component C: Theory Surgery Engine.
    Prunes falsified causal edges and assumptions, yielding revised candidates (REV2 and REV3).
    Tracks removed/preserved assumptions and updates theory confidence based on survival rates.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.memory = TheoryMemory(db_path=db_path)

    def perform_surgery(
        self,
        survival_report_path: str = "surviving_mechanisms.json"
    ) -> List[Dict[str, Any]]:
        
        # Load survival report
        if not os.path.exists(survival_report_path):
            raise FileNotFoundError(f"Survival report not found at {survival_report_path}")
            
        with open(survival_report_path, "r", encoding="utf-8") as f:
            survival_data = json.load(f)
            
        survival_map = {item["theory_id"]: item for item in survival_data}
        
        theories = self.memory.get_all_theories()
        revised_candidates = []

        for theory in theories:
            t_id = theory["id"]
            if t_id not in survival_map:
                continue
                
            report = survival_map[t_id]
            edges = report["edges"]
            overall_survival_rate = report["overall_survival_rate"]
            
            # Identify which edges to prune or adapt
            eliminated_edges = [e for e in edges if e["preservation"] == "ELIMINATED"]
            reversed_edges = [e for e in edges if e["preservation"] == "REVERSED"]
            preserved_edges = [e for e in edges if e["preservation"] == "PRESERVED"]
            
            # Helper to map nodes to assumptions for removal tracking
            removed_assumptions_rev2 = []
            preserved_assumptions_rev2 = []
            
            # Simple keyword matching to associate assumptions with edges
            for assumption in theory.get("assumptions", []):
                lower_ass = assumption.lower()
                # Check if assumption mentions eliminated or reversed edges
                should_remove_rev2 = False
                for edge in eliminated_edges + reversed_edges:
                    src_kw = edge["source"].replace("_", " ")
                    tgt_kw = edge["target"].replace("_", " ")
                    if src_kw in lower_ass or tgt_kw in lower_ass:
                        should_remove_rev2 = True
                        break
                
                if should_remove_rev2:
                    removed_assumptions_rev2.append(assumption)
                else:
                    preserved_assumptions_rev2.append(assumption)
            
            # ----------------------------------------------------
            # THEORY_REV2: Strict Pruning (Remove ELIMINATED and REVERSED edges)
            # ----------------------------------------------------
            rev2_edges = []
            for edge in preserved_edges:
                rev2_edges.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge["sim_weight"]  # keep original sim weight
                })
                
            rev2_graph = {
                "nodes": theory["mechanism_graph"].get("nodes", []),
                "edges": rev2_edges
            }
            
            # Calculate REV2 confidence
            rev2_confidence = round(theory["confidence"] * overall_survival_rate, 4)
            
            rev2_theory = {
                "id": f"{t_id}_REV2",
                "name": f"{theory['name']} (REV2: Pruned)",
                "laws_explained": theory["laws_explained"],
                "mechanism_graph": rev2_graph,
                "assumptions": preserved_assumptions_rev2,
                "predictions": theory["predictions"],
                "confidence": max(0.1, rev2_confidence),
                "status": "CANDIDATE",
                "parent_theory": t_id,
                "removed_assumptions": removed_assumptions_rev2,
                "preserved_assumptions": preserved_assumptions_rev2
            }
            
            # ----------------------------------------------------
            # THEORY_REV3: Adaptation (Prune ELIMINATED, correct REVERSED, update weights)
            # ----------------------------------------------------
            rev3_edges = []
            removed_assumptions_rev3 = []
            preserved_assumptions_rev3 = []
            
            # For REV3, we adjust all preserved and reversed weights to physical correlations
            for edge in preserved_edges:
                rev3_edges.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge["physical_correlation"]
                })
            for edge in reversed_edges:
                rev3_edges.append({
                    "source": edge["source"],
                    "target": edge["target"],
                    "weight": edge["physical_correlation"]  # updated sign and correlation
                })
                
            rev3_graph = {
                "nodes": theory["mechanism_graph"].get("nodes", []),
                "edges": rev3_edges
            }
            
            # Map assumptions for REV3 (reversed edge assumptions are revised, not removed)
            for assumption in theory.get("assumptions", []):
                lower_ass = assumption.lower()
                should_remove_rev3 = False
                for edge in eliminated_edges:
                    src_kw = edge["source"].replace("_", " ")
                    tgt_kw = edge["target"].replace("_", " ")
                    if src_kw in lower_ass or tgt_kw in lower_ass:
                        should_remove_rev3 = True
                        break
                        
                if should_remove_rev3:
                    removed_assumptions_rev3.append(assumption)
                else:
                    # If it's a reversed assumption, append a revised notice
                    is_reversed = False
                    for edge in reversed_edges:
                        src_kw = edge["source"].replace("_", " ")
                        tgt_kw = edge["target"].replace("_", " ")
                        if src_kw in lower_ass or tgt_kw in lower_ass:
                            is_reversed = True
                            break
                    if is_reversed:
                        preserved_assumptions_rev3.append(f"{assumption} [REVISED: Direction inverted in physical hardware]")
                    else:
                        preserved_assumptions_rev3.append(assumption)
            
            # Calculate REV3 confidence (retains more structure, but adjusted. We scale by survival rate of active edges)
            active_survival_rate = (len(preserved_edges) + len(reversed_edges)) / len(edges) if edges else 1.0
            rev3_confidence = round(theory["confidence"] * active_survival_rate, 4)
            
            rev3_theory = {
                "id": f"{t_id}_REV3",
                "name": f"{theory['name']} (REV3: Noise-Augmented)",
                "laws_explained": theory["laws_explained"],
                "mechanism_graph": rev3_graph,
                "assumptions": preserved_assumptions_rev3,
                "predictions": theory["predictions"],
                "confidence": max(0.1, rev3_confidence),
                "status": "CANDIDATE",
                "parent_theory": t_id,
                "removed_assumptions": removed_assumptions_rev3,
                "preserved_assumptions": preserved_assumptions_rev3
            }
            
            # Save revised theories to memory
            self.memory.save_theory(rev2_theory)
            self.memory.save_theory(rev3_theory)
            
            revised_candidates.extend([rev2_theory, rev3_theory])

        # Write to JSON report
        with open("theory_surgery_report.json", "w", encoding="utf-8") as f:
            json.dump(revised_candidates, f, indent=2, ensure_ascii=False)
            
        # Compile docs/THEORY_EVOLUTION_REPORT.md (or append to docs)
        self._write_evolution_report(revised_candidates)
        
        return revised_candidates

    def _write_evolution_report(self, candidates: List[Dict[str, Any]]) -> None:
        lines = [
            "# Theory Evolution Report — Phase 2D / 3A.1",
            "",
            "Documents the automated surgery and evolution of theories following physical hardware falsification.",
            "",
            "## Summary of Evolutionary Transitions",
            "",
            "| Original ID | Revised Candidate ID | Target Action | New Confidence | Removed Assumptions |",
            "| :--- | :--- | :--- | :---: | :--- |"
        ]
        
        for cand in candidates:
            parent = cand["parent_theory"]
            act = "Pruning" if "REV2" in cand["id"] else "Noise-Adaptation"
            removed_str = ", ".join([f"'{a}'" for a in cand["removed_assumptions"]]) if cand["removed_assumptions"] else "*None*"
            lines.append(f"| `{parent}` | `{cand['id']}` | {act} | {cand['confidence']:.4f} | {removed_str} |")
            
        lines.append("")
        lines.append("## Detailed Revised Assumptions & Graph Topology")
        lines.append("")
        
        for cand in candidates:
            lines.append(f"### Theory `{cand['id']}`")
            lines.append(f"- **Name**: {cand['name']}")
            lines.append(f"- **Confidence**: `{cand['confidence']}`")
            lines.append("- **Preserved Assumptions**:")
            for a in cand["preserved_assumptions"]:
                lines.append(f"  - {a}")
            lines.append("- **Mechanism Graph Edges**:")
            for edge in cand["mechanism_graph"]["edges"]:
                lines.append(f"  - `{edge['source']}` $\\rightarrow$ `{edge['target']}` (Weight: `{edge['weight']:.4f}`)")
            lines.append("")
            
        with open("docs/THEORY_EVOLUTION_REPORT.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        print("Generated docs/THEORY_EVOLUTION_REPORT.md")

if __name__ == "__main__":
    eng = TheorySurgeryEngine()
    print("Surgery executed:", len(eng.perform_surgery()))
