import subprocess
import json

insight = {
    "pattern_type": "structural_universality",
    "trigger_conditions": [
        "El sistema es de naturaleza iterativa discreta",
        "Se evalua la transición al caos por periodo duplicado"
    ],
    "recommended_strategy": "Calcular la constante de Feigenbaum (delta_n) y comparar si el límite es 4.6692016... ya que esto trasciende la forma algebraica del mapa (polinómico vs trascendental).",
    "confidence": 0.99,
    "supporting_nodes": [2],
    "counterexamples": [],
    "domains": ["nonlinear_dynamics", "universality", "chaos_theory"]
}

json_str = json.dumps(insight)
print("Injecting insight...")
result = subprocess.run(
    ["python", "core/evaluator_db.py", "add_insight", json_str],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print(f"Error: {result.stderr}")
