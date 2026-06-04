import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def run_authenticity_aggregator(
    input_files: Dict[str, str] = None,
    output_report_path: str = "docs/DISCOVERY_AUTHENTICITY_REPORT.md"
) -> Dict[str, Any]:
    print("Aggregating discovery authenticity audit reports...")
    
    if input_files is None:
        input_files = {
            "novel_structure": "novel_structure_report.json",
            "optimization_removal": "optimization_removal_report.json",
            "random_evolution": "random_evolution_report.json",
            "cross_domain": "cross_domain_discovery_report.json",
            "discovery_compression": "discovery_compression_report.json",
            "lineage": "lineage_report.json"
        }
        
    reports = {}
    for key, filename in input_files.items():
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                reports[key] = json.load(f)
        else:
            print(f"Warning: {filename} not found.")
            reports[key] = {}
            
    # Parse metrics
    novelty_score = reports.get("novel_structure", {}).get("novelty_score", 0.0)
    classification_nov = reports.get("novel_structure", {}).get("classification", "UNKNOWN")
    
    opt_loss = reports.get("optimization_removal", {}).get("deltas", {}).get("utility_loss_ratio", 0.0)
    opt_verdict = reports.get("optimization_removal", {}).get("verdict", "UNKNOWN")
    
    cohen_d = reports.get("random_evolution", {}).get("statistics", {}).get("cohens_d", 0.0)
    p_val_m = reports.get("random_evolution", {}).get("statistics", {}).get("mann_whitney_p_value", 1.0)
    rand_verdict = reports.get("random_evolution", {}).get("verdict", "UNKNOWN")
    
    cross_results = reports.get("cross_domain", {}).get("results", {})
    cross_domains_positive = all(data.get("utility", 0.0) > 0.0 for data in cross_results.values()) if cross_results else False
    
    compression_class = reports.get("discovery_compression", {}).get("classification", "UNKNOWN")
    
    lineage_depth = reports.get("lineage", {}).get("metrics", {}).get("lineage_depth", 0)
    novelty_growth = reports.get("lineage", {}).get("metrics", {}).get("novelty_growth", 0.0)
    
    # Verdict Rules
    # Rule 1: AUTHENTIC_DISCOVERY
    # Novelty > 0.60, RandomSearch << LawGuided (cohen_d > 0.3 & p_val_m < 0.05), CrossDomain Positive, Opt Loss < 50%
    if novelty_score > 0.60 and cohen_d > 0.3 and p_val_m < 0.05 and cross_domains_positive and opt_loss < 0.50:
        verdict = "AUTHENTIC_DISCOVERY"
    # Rule 2: OPTIMIZATION_ARTIFACT
    # Novelty < 0.30 or Opt Loss > 0.80
    elif novelty_score < 0.30 or opt_loss > 0.80:
        verdict = "OPTIMIZATION_ARTIFACT"
    # Rule 3: PARTIAL_DISCOVERY
    else:
        verdict = "PARTIAL_DISCOVERY"
        
    # Generate DISCOVERY_AUTHENTICITY_REPORT.md
    dir_name = os.path.dirname(output_report_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    report_path = Path(output_report_path)
    
    sections = []
    sections.append("# Discovery Authenticity Report — Phase 1H.1\n")
    sections.append(f"## Final Authenticity Verdict: **{verdict}**\n")
    
    if verdict == "AUTHENTIC_DISCOVERY":
        sections.append("> [!NOTE]\n> **Verdict Summary:** Evolved scaffolds represent an authentic scientific discovery of novel structure. Improvement is not merely a product of compression or compiler artifacts.\n")
    elif verdict == "PARTIAL_DISCOVERY":
        sections.append("> [!WARNING]\n> **Verdict Summary:** Evolved scaffolds show partial authenticity. They represent structural variants or recombinations with significant but compiler-dependent optimization gains.\n")
    else:
        sections.append("> [!CAUTION]\n> **Verdict Summary:** Evolved scaffolds are flagged as optimization compilation artifacts. Unoptimized variations show significant performance decay.\n")
        
    # Criteria summary table
    sections.append("### 1. Key Success Criteria Verification\n")
    sections.append("| Criterion | Target Value | Actual Evaluated Value | Status |")
    sections.append("| :--- | :---: | :---: | :---: |")
    
    sections.append(f"| **Criterio A: Novelty Score** | > 0.60 | {novelty_score:.4f} ({classification_nov}) | {'PASSED' if novelty_score > 0.60 else 'FAILED'} |")
    sections.append(f"| **Criterio B: Law Guided Significance** | p < 0.05 | p = {p_val_m:.6e} (d = {cohen_d:+.4f}) | {'PASSED' if p_val_m < 0.05 else 'FAILED'} |")
    sections.append(f"| **Criterio C: Cross-Domain Utility** | Positive | {('POSITIVE' if cross_domains_positive else 'ZERO/NEGATIVE')} | {'PASSED' if cross_domains_positive else 'FAILED'} |")
    sections.append(f"| **Criterio D: Optimization Loss** | < 50% | {opt_loss * 100:.2f}% | {'PASSED' if opt_loss < 0.50 else 'FAILED'} |")
    sections.append(f"| **Criterio E: Final Verdict** | AUTHENTIC_DISCOVERY | {verdict} | {'PASSED' if verdict == 'AUTHENTIC_DISCOVERY' else 'FAILED'} |")
    sections.append("\n")
    
    # Audit details
    sections.append("### 2. Detailed Audit Outcomes\n")
    
    # Novel Structure
    sections.append("#### Novel Structure Audit")
    sections.append(f"- **Discovered Scaffold:** `{reports.get('novel_structure', {}).get('generated_representation')}`")
    sections.append(f"- **Best Matching Baseline:** `{reports.get('novel_structure', {}).get('best_matching_baseline')}`")
    sections.append(f"- **Novelty Score:** `{novelty_score:.4f}`")
    sections.append("\n")
    
    # Optimization Removal
    sections.append("#### Optimization Removal Audit")
    sections.append(f"- **Fidelity Drop without PyZX:** `{opt_loss * 100:.2f}%`")
    sections.append(f"- **Status:** `{opt_verdict}`")
    sections.append("\n")
    
    # Random Evolution
    sections.append("#### Random Search vs Law-Guided Search")
    sections.append(f"- **Law-Guided Mean Utility:** `{reports.get('random_evolution', {}).get('law_guided', {}).get('mean_utility', 0.0):.4f}`")
    sections.append(f"- **Random Search Mean Utility:** `{reports.get('random_evolution', {}).get('random_search', {}).get('mean_utility', 0.0):.4f}`")
    sections.append(f"- **Effect Size (Cohen's d):** `{cohen_d:+.4f}`")
    sections.append("\n")
    
    # Cross-Domain
    sections.append("#### Cross-Domain Out-of-Distribution Discovery")
    if cross_results:
        sections.append("| Target Holdout Domain | Utility | Synergy | Novelty | Transferability |")
        sections.append("| :--- | :---: | :---: | :---: | :---: |")
        for domain, metrics in cross_results.items():
            sections.append(
                f"| `{domain}` | {metrics.get('utility', 0.0):.4f} | {metrics.get('synergy', 0.0):.4f} | {metrics.get('novelty_score', 0.0):.4f} | {metrics.get('predicted_transferability', 0.0):.4f} |"
            )
    else:
        sections.append("No cross-domain data available.")
    sections.append("\n")
    
    # Discovery Compression
    sections.append("#### Discovery Compression Audit")
    sections.append(f"- **Decoupled Classification:** `{compression_class}`")
    sections.append("\n")
    
    # Lineage Reconstruction
    sections.append("#### Evolutionary Lineage Reconstruction")
    sections.append(f"- **Lineage Depth:** `{lineage_depth}`")
    sections.append(f"- **Cumulative Novelty Growth:** `{novelty_growth:+.4f}`")
    sections.append("\n")
    
    report_path.write_text("\n".join(sections), encoding="utf-8")
    print(f"Discovery Authenticity Report written to {report_path}")
    
    final_output = {
        "verdict": verdict,
        "novelty_score": novelty_score,
        "cohens_d": cohen_d,
        "p_value": p_val_m,
        "optimization_loss": opt_loss,
        "report_path": str(report_path.resolve())
    }
    return final_output

if __name__ == "__main__":
    run_authenticity_aggregator()
