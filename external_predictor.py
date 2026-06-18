# Automatically generated independent clean-room reconstruction
def predict(predicted_sim: float, E_gate: float, E_readout: float) -> float:
    a = -1.5
    b = -1.5
    c = -0.002
    gap = a * E_gate + b * E_readout + c
    return round(predicted_sim + gap, 6)
