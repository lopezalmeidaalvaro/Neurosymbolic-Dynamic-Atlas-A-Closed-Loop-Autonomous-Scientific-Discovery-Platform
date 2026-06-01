#!/usr/bin/env python3
"""
Phase 1: Autonomous Scientific Cycle Orchestrator
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import yaml
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from physics.core.io.knowledge_graph import ScientificKnowledgeGraph

class AutonomousScientificOrchestrator:
    """
    Central Director directing the closed-loop neurosymbolic discovery cycle.
    """
    def __init__(self, config_path="physics/core/config.yaml"):
        # 1. Load config
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        self.persistence_path = self.config["paths"]["knowledge_graph"]
        self.kg = ScientificKnowledgeGraph(self.persistence_path)
        
        # Heuristic targets
        self.target_metric = self.config.get("physics", {}).get("goals", {}).get("target_metric", "wormhole")
        self.curiosity_threshold = 0.25
        self.goal_met = False
        
        # Placeholders for initialized agents
        self.hypo_gen = None
        self.theory_critic = None
        self.exp_planner = None
        self.metric_analyst = None

    def initialize_agents(self, hypo_gen, theory_critic, exp_planner, metric_analyst):
        """
        Dynamically registers the actual agent modules into the orchestrator.
        """
        self.hypo_gen = hypo_gen
        self.theory_critic = theory_critic
        self.exp_planner = exp_planner
        self.metric_analyst = metric_analyst
        print("[+] Orchestrator: Agentes registrados y listos para ejecucion.")

    def run_cycle(self, max_iterations=5):
        """
        Main closed-loop discovery loop.
        """
        print("\n========================================================")
        print("  INICIANDO CICLO CIENTIFICO AUTONOMO MULTIAGENTE")
        print(f"  OBJETIVO DE BUSQUEDA: {self.target_metric.upper()}")
        print("========================================================\n")
        
        iteration = 0
        context = {"exploration_history": []}
        
        while not self.goal_met and iteration < max_iterations:
            iteration += 1
            print(f"\n--- [ITERACION {iteration:02d}] ---")
            
            # Step 1: Hypothesis Generation
            print("[*] Orquestador -> Solicitando hipotesis a HypoGen...")
            hypothesis = self.hypo_gen.propose(context, metric_type=self.target_metric)
            hypo_id = f"H_iter_{iteration}_{int(time.time())}"
            
            # Register Hypothesis in Knowledge Graph
            self.kg.add_node(hypo_id, "Hypothesis", {
                "author": "HypoGen",
                "expression": hypothesis.expression,
                "confidence": hypothesis.confidence,
                "metric_type": hypothesis.metric_type
            })
            
            # Step 2: Theory Validation (Criticism)
            print(f"[*] Orquestador -> Enviando hipotesis {hypo_id} a TheoryCritic...")
            verdict = self.theory_critic.validate(hypothesis)
            
            critic_id = f"C_iter_{iteration}_{int(time.time())}"
            self.kg.add_node(critic_id, "Equation", {
                "author": "TheoryCritic",
                "verdict": verdict.verdict,
                "wec_violation": verdict.wec_violation,
                "singularities_count": len(verdict.singularities)
            })
            self.kg.add_edge(hypo_id, critic_id, "validated_by")
            
            if verdict.verdict == "REJECTED":
                print(f"[-] Orquestador -> Hipotesis RECHAZADA por TheoryCritic. Razon: Singularidad o Inconsistencia.")
                self.kg.add_node(f"Fail_{iteration}", "Failure", {"reason": "Rechazo del Critico Teorico"})
                self.kg.add_edge(hypo_id, f"Fail_{iteration}", "leads_to")
                continue
                
            print(f"[+] Orquestador -> Hipotesis ACEPTADA por el Critico. Planificando Experimento...")
            
            # Step 3: Experiment Planning
            print(f"[*] Orquestador -> Solicitando plan experimental a ExpPlanner...")
            plan = self.exp_planner.plan(hypothesis)
            plan_id = f"P_iter_{iteration}_{int(time.time())}"
            
            self.kg.add_node(plan_id, "Experiment", {
                "author": "ExpPlanner",
                "loss_config": str(plan["loss_config"]),
                "epochs": plan["epochs"]
            })
            self.kg.add_edge(hypo_id, plan_id, "tested_by")
            
            # Step 4: Metric Analysis & Simulation
            print(f"[*] Orquestador -> Solicitando ejecucion y metricas a MetricAnalyst...")
            results = self.metric_analyst.execute(plan)
            res_id = f"M_iter_{iteration}_{int(time.time())}"
            
            self.kg.add_node(res_id, "Metric", {
                "author": "MetricAnalyst",
                "energy_total": results.energy_total,
                "stability_score": results.stability_score,
                "results_files": results.plots_paths
            })
            self.kg.add_edge(plan_id, res_id, "yields")
            
            # Step 5: Curiosity Mechanism
            # Check for anomaly/unexpected results: difference between predicted and actual metrics
            predicted_energy = verdict.analytical_energy if hasattr(verdict, "analytical_energy") else 0.0
            actual_energy = results.energy_total
            discrepancy = abs(predicted_energy - actual_energy)
            
            print(f"[*] Mecanismo de Curiosidad -> Discrepancia detectada: {discrepancy:.4f} (Limite: {self.curiosity_threshold})")
            if discrepancy > self.curiosity_threshold:
                print(f"[!] ANOMALIA DETECTADA! Curiosidad cientifica disparada. Reorientando busqueda...")
                curious_id = f"Curiosity_Anomaly_{iteration}"
                self.kg.add_node(curious_id, "Success", {
                    "author": "Orchestrator_Curiosity",
                    "discrepancy": discrepancy,
                    "target_region": hypothesis.expression
                })
                self.kg.add_edge(res_id, curious_id, "triggers_curiosity")
                
                # Mutate search context to reward anomalous exploring
                context["exploration_history"].append({
                    "anomalous_equation": hypothesis.expression,
                    "exploring": True
                })
            else:
                context["exploration_history"].append({
                    "equation": hypothesis.expression,
                    "exploring": False
                })
                
            # Log successes
            if results.stability_score > 0.85:
                success_id = f"Discovery_Success_{iteration}"
                self.kg.add_node(success_id, "Success", {
                    "equation": results.best_equation,
                    "energy": results.energy_total
                })
                self.kg.add_edge(res_id, success_id, "proves_success")
                self.goal_met = True
                print(f"\n[+] [META COMPLETADA!] Descubrimiento exitoso estabilizado: {results.best_equation}\n")
                break
                
        print("\n========================================================")
        print("  CICLO CIENTIFICO FINALIZADO. MEMORIA PERSISTIDA")
        print("========================================================\n")
        self.kg.save_to_disk()

if __name__ == "__main__":
    # Test stub imports in verification run
    print("[*] Iniciando verificacion local del Orquestador...")
    orch = AutonomousScientificOrchestrator()
    print("[+] Configuracion cargada con exito.")
