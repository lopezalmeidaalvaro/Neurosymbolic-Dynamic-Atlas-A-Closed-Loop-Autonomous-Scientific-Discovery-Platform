#!/usr/bin/env python3
"""
Phase 4: Experiment Planner Agent (ExpPlanner)
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

class ExperimentPlanner:
    """
    ExpPlanner Agent: Translates abstract physical hypotheses into virtual
    experimental configurations, PINN loss functions, and simulation setups.
    """
    def __init__(self, config_path="physics/core/config.yaml"):
        # Load yaml config if it exists
        self.config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
            except Exception as e:
                print(f"[-] ExpPlanner: Warning reading config.yaml: {e}")
                
        # Default fallback values
        planner_cfg = self.config.get("agents", {}).get("exp_planner", {})
        self.default_epochs = planner_cfg.get("pinn_epochs", 500)
        self.default_lr = planner_cfg.get("pinn_lr", 0.005)

    def plan(self, hypothesis):
        """
        Translates a Hypothesis into a numeric optimization plan.
        """
        print(f"    [ExpPlanner] Planificando experimento para la hipotesis de tipo: {hypothesis.metric_type}")
        
        # Define default loss configurations based on metric type
        if hypothesis.metric_type == "wormhole":
            loss_config = {
                "bc_weight": 1.0,         # Boundary condition weight
                "energy_weight": 0.05,    # Exotic energy stress minimization weight
                "data_weight": 0.1,       # Dev/ansatz data preservation weight
                "domain": [0.5, 1.5],     # Radial domain coordinate range
                "collocation_points": 200
            }
            r0 = 0.5
        elif hypothesis.metric_type == "warp":
            loss_config = {
                "bc_weight": 1.0,
                "energy_weight": 0.02,
                "data_weight": 0.15,
                "domain": [0.0, 1.0],
                "collocation_points": 250
            }
            r0 = 0.0
        elif hypothesis.metric_type == "black_hole":
            loss_config = {
                "bc_weight": 1.0,
                "data_weight": 0.5,
                "energy_weight": 0.01,
                "domain": [0.01, 3.0],    # Avoid absolute r=0 coordinate singularity
                "collocation_points": 300
            }
            r0 = 0.0
        else:
            loss_config = {
                "bc_weight": 1.0,
                "energy_weight": 0.05,
                "data_weight": 0.1,
                "domain": [0.0, 2.0],
                "collocation_points": 200
            }
            r0 = 0.0

        # Construct final plan
        experiment_plan = {
            "expression": hypothesis.expression,
            "metric_type": hypothesis.metric_type,
            "epochs": self.default_epochs,
            "lr": self.default_lr,
            "loss_config": loss_config,
            "r_0": r0,
            "confidence_initial": hypothesis.confidence
        }
        
        print(f"    [ExpPlanner] Experimento planificado con {experiment_plan['epochs']} epocas y lr={experiment_plan['lr']}.")
        return experiment_plan

if __name__ == "__main__":
    from physics.agents.hypothesis_generator import Hypothesis
    print("[*] Levantando agente ExpPlanner...")
    planner = ExperimentPlanner()
    h = Hypothesis("b(r) = 0.5*exp(-3.0*r**2)", confidence=0.7, metric_type="wormhole")
    p = planner.plan(h)
    print(f" [+] Plan generado con exito: {p}")
