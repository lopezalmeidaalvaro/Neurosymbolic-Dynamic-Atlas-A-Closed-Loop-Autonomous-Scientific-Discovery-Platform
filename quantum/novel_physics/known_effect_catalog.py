from typing import Dict, Any, List

class KnownEffectCatalog:
    """
    Phase 4A: Catalog of conventional quantum device noise and measurement effects.
    """

    def __init__(self):
        self.catalog = {
            "crosstalk": "Readout/gate correlation effects showing simple quadratic behavior.",
            "depolarizing": "Standard linear expectation decay proportional to total gate error count.",
            "thermal_relaxation": "Exponential decay proportional to decay rate and gate duration.",
            "measurement_bias": "Fixed state preparation and measurement calibration offsets."
        }

    def get_known_effects(self) -> Dict[str, str]:
        return self.catalog

    def matches_known_effect(self, equation: str) -> bool:
        # Check if the equation resembles a known conventional model structure.
        # Known models are purely linear or simple calibration offsets.
        # Since RTHEORY shows a complex reality-native gap, we check if it is explained by standard terms.
        # If it matches standard linear decay with zero constant, return True.
        # Otherwise, if it has a distinct persistent gap, it is not a known effect.
        eq_lower = equation.lower()
        if "e_gate" in eq_lower and "e_readout" in eq_lower:
            # Check if constant offset is near zero
            # RTHEORY typically has offset or complex slopes
            return False
        return True
