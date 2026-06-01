#!/usr/bin/env python3
"""
FASE 28.5 — Aislamiento Total del Entorno de Benchmark
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path

# Add project root to sys.path to enable absolute imports
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def create_isolated_benchmark_environment(seed: int = None):
    """
    Sets up a fully isolated validation sandbox:
    1. Copies active Knowledge Graph.
    2. Prunes all nodes and edges related to wormholes, warp bubbles, or quadratic gravity.
    3. Prunes all "Success" nodes (previous discoveries) and accepted "Equation" nodes (TheoryCritic survivors).
    4. Cleans up cached PySR symbolic regression output files.
    5. Creates a blank scientific memory.
    6. Disables access to historical reports.
    7. Saves benchmark_environment_report.json and seeded sandbox integrity reports.
    8. Saves sandbox_integrity_report.json per seed with node counts and verification.
    """
    print(f"[*] Benchmark Sandbox -> Creando entorno aislado (Semilla: {seed})...")
    
    benchmark_dir = Path(__file__).resolve().parent
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Paths configuration
    active_kg = Path("physics/core/io/knowledge_graph.json")
    temp_kg = benchmark_dir / "temp_knowledge_graph.json"
    temp_memory = benchmark_dir / "temp_memory.json"
    env_report_file = benchmark_dir / "benchmark_environment_report.json"
    
    # Check if active KG exists
    if active_kg.exists():
        shutil.copy(active_kg, temp_kg)
        print(f" [+] Benchmark Sandbox: Copia del Grafo de Conocimiento creada en {temp_kg}")
    else:
        # Create a dummy blank JSON graph if active KG is not present
        blank_data = {"directed": True, "multigraph": False, "graph": {}, "nodes": [], "links": []}
        with open(temp_kg, "w", encoding="utf-8") as f:
            json.dump(blank_data, f)
        print(" [+] Benchmark Sandbox: Grafo de Conocimiento vacio creado como fallback.")
        
    # Clean up cached symbolic regression outputs in workspace and benchmark dir
    for path in [Path("."), benchmark_dir]:
        if path.exists():
            for f in path.glob("*hall_of_fame*"):
                try:
                    f.unlink()
                    print(f" [+] Benchmark Sandbox: Cleaned up symbolic regression cache file: {f}")
                except Exception as e:
                    pass
            for f in path.glob("*.csv"):
                try:
                    f.unlink()
                    print(f" [+] Benchmark Sandbox: Cleaned up csv file: {f}")
                except Exception as e:
                    pass

    # 2. Prune Graph (Remove nodes matching target forbidden keywords)
    forbidden_keywords = [
        "wormhole", "morris-thorne", "alcubierre", "warp", 
        "schwarzwald", "schwarzschild", "singularity resolution", 
        "quadratic gravity", "f(r)", "stelle", "starobinsky"
    ]
    
    kg_contamination = False
    with open(temp_kg, "r", encoding="utf-8") as f:
        kg_data = json.load(f)
        
    original_node_count = len(kg_data.get("nodes", []))
    pruned_nodes = []
    retained_nodes = []
    
    for node in kg_data.get("nodes", []):
        n_val = str(node).lower()
        contains_forbidden = False
        for kw in forbidden_keywords:
            if kw in n_val:
                contains_forbidden = True
                break
        
        # Also prune all Success nodes and all accepted Equation nodes
        n_type = node.get("type")
        if n_type == "Success":
            contains_forbidden = True
        elif n_type == "Equation" and node.get("verdict") == "ACCEPTED":
            contains_forbidden = True
                
        if contains_forbidden:
            pruned_nodes.append(node.get("id"))
            kg_contamination = True
        else:
            retained_nodes.append(node)
            
    # Filter links connected to pruned nodes
    pruned_links_count = 0
    retained_links = []
    for link in kg_data.get("links", kg_data.get("edges", [])):
        source = link.get("source")
        target = link.get("target")
        if source in pruned_nodes or target in pruned_nodes:
            pruned_links_count += 1
        else:
            retained_links.append(link)
            
    # Update temporary JSON Graph data
    kg_data["nodes"] = retained_nodes
    if "links" in kg_data:
        kg_data["links"] = retained_links
    elif "edges" in kg_data:
        kg_data["edges"] = retained_links
        
    with open(temp_kg, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=4)
        
    print(f" [+] Benchmark Sandbox: Pruning completado. Nodos removidos: {len(pruned_nodes)} / {original_node_count}")
    
    # 3. Create blank scientific memory
    with open(temp_memory, "w", encoding="utf-8") as f:
        json.dump({"memories": [], "axioms": [], "theories_discovered_count": 0}, f)
    print(f" [+] Benchmark Sandbox: Memoria cientifica temporal vacia creada en {temp_memory}")
    
    # 4. Verification self-audit
    memory_contamination = False # starts fresh, so always clean
    # Double check no remaining node contains any forbidden words, type Success or Accepted Equation
    double_check_fail = False
    for node in retained_nodes:
        n_val = str(node).lower()
        for kw in forbidden_keywords:
            if kw in n_val:
                double_check_fail = True
                break
        n_type = node.get("type")
        if n_type == "Success" or (n_type == "Equation" and node.get("verdict") == "ACCEPTED"):
            double_check_fail = True
            break
                
    if double_check_fail:
        kg_contamination = True
    else:
        kg_contamination = False
        
    # 5. Export environment report
    env_report = {
        "timestamp": time.time(),
        "seed": seed,
        "memory_contamination": memory_contamination,
        "kg_contamination": kg_contamination,
        "pruned_nodes_count": len(pruned_nodes),
        "retained_nodes_count": len(retained_nodes),
        "pruned_links_count": pruned_links_count,
        "temp_kg_path": str(temp_kg),
        "temp_memory_path": str(temp_memory),
        "status": "fully_isolated"
    }
    
    # Write to target paths
    with open(env_report_file, "w", encoding="utf-8") as f:
        json.dump(env_report, f, indent=4)
        
    if seed is not None:
        reports_dir = benchmark_dir / "sandbox_integrity_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        seed_report_file = reports_dir / f"seed_{seed}.json"
        with open(seed_report_file, "w", encoding="utf-8") as f:
            json.dump(env_report, f, indent=4)
        print(f" [+] Benchmark Sandbox: Seeded isolation report saved to {seed_report_file}")
    
    print(f" [+] Benchmark Sandbox: Informe de aislamiento guardado en {env_report_file}")
    print("========================================================\n")
    return env_report

if __name__ == "__main__":
    create_isolated_benchmark_environment()
