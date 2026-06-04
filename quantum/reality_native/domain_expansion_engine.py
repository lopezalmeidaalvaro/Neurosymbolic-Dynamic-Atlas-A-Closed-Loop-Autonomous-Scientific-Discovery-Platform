import os
import json
import numpy as np
from typing import Dict, Any, List

class DomainExpansionEngine:
    """
    Phase 3C-A: Domain Expansion Engine.
    Generates independent datasets (training, validation, confirmation, reproduction)
    for 10 physical domains.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.domains = [
            "quantum_hardware_noise",
            "calibration_drift",
            "readout_error",
            "gate_error",
            "cross_vendor_transfer",
            "device_aging",
            "hardware_stability",
            "spectator_crosstalk",
            "thermal_relaxation",
            "leakage_rate"
        ]

    def generate_all_domains(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        np.random.seed(self.seed)
        all_data = {}

        # Coefficient dictionary for each domain to model physical ground truth
        domain_coeffs = {
            "quantum_hardware_noise": (-1.4907, -1.5060, -0.0021),
            "calibration_drift": (-1.8500, -1.2500, -0.0050),
            "readout_error": (-0.5000, -2.5000, -0.0100),
            "gate_error": (-3.2000, -0.4000, -0.0030),
            "cross_vendor_transfer": (-1.1000, -1.9000, -0.0060),
            "device_aging": (-2.0500, -1.6500, -0.0080),
            "hardware_stability": (-1.3500, -1.1500, -0.0010),
            "spectator_crosstalk": (-2.4000, -0.9000, -0.0040),
            "thermal_relaxation": (-1.6000, -1.8000, -0.0070),
            "leakage_rate": (-2.9500, -1.3500, -0.0090)
        }

        devices = ["ibm_brisbane", "ibm_sherbrooke", "rigetti_aspen_m3", "ionq_aria", "quantinuum_h1"]
        vendors = {
            "ibm_brisbane": "IBM", "ibm_sherbrooke": "IBM",
            "rigetti_aspen_m3": "Rigetti", "ionq_aria": "IonQ", "quantinuum_h1": "Quantinuum"
        }
        paradigms = {
            "ibm_brisbane": "Superconducting", "ibm_sherbrooke": "Superconducting",
            "rigetti_aspen_m3": "Superconducting", "ionq_aria": "Ion Trap", "quantinuum_h1": "Ion Trap"
        }

        for domain in self.domains:
            a, b, c = domain_coeffs[domain]
            all_data[domain] = {}

            # Generate 4 splits: training, validation, confirmation, reproduction
            splits = {
                "training": 40,
                "validation": 20,
                "confirmation": 15,
                "reproduction": 15
            }

            for split_name, n_samples in splits.items():
                split_list = []
                for idx in range(n_samples):
                    # Random device selection
                    dev = np.random.choice(devices)
                    
                    # Generate realistic error rates based on split name to ensure OOD/variation
                    if split_name == "training":
                        ge = np.random.uniform(0.001, 0.015)
                        re = np.random.uniform(0.005, 0.030)
                    elif split_name == "validation":
                        ge = np.random.uniform(0.012, 0.025)
                        re = np.random.uniform(0.020, 0.045)
                    elif split_name == "confirmation":
                        ge = np.random.uniform(0.002, 0.018)
                        re = np.random.uniform(0.008, 0.035)
                    else: # reproduction
                        ge = np.random.uniform(0.005, 0.020)
                        re = np.random.uniform(0.010, 0.040)

                    simulated_base_val = 0.3694
                    # Calculate gap based on physical domain formula + noise (std=0.0003)
                    noise = np.random.normal(0, 0.0003)
                    observed_gap = a * ge + b * re + c + noise
                    observed_val = simulated_base_val + observed_gap

                    split_list.append({
                        "id": f"RUN_{domain.upper()[:4]}_{split_name.upper()[:4]}_{idx:03d}",
                        "device": dev,
                        "vendor": vendors[dev],
                        "paradigm": paradigms[dev],
                        "gate_error": round(float(ge), 6),
                        "readout_error": round(float(re), 6),
                        "predicted_sim": round(float(simulated_base_val), 6),
                        "observed": round(float(observed_val), 6),
                        "observed_gap": round(float(observed_gap), 6)
                    })
                all_data[domain][split_name] = split_list

        return all_data

if __name__ == "__main__":
    engine = DomainExpansionEngine()
    data = engine.generate_all_domains()
    print("Domains generated:", list(data.keys()))
    print("Sample domain sizes for quantum_hardware_noise:", {k: len(v) for k, v in data["quantum_hardware_noise"].items()})
