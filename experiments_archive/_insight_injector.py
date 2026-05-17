import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.evaluator_db import cmd_add_insight

payload = {
    "pattern_type": "chaos_attractor_characterization",
    "trigger_conditions": ["loss_of_local_stability", "nonlinear_odes"],
    "recommended_strategy": "hybrid_sym_num_approach",
    "confidence": 0.98,
    "supporting_nodes": [1, 2],
    "counterexamples": [],
    "domains": ["nonlinear_dynamics", "differential_equations"]
}

# The user prompt: "... documente un patrón que hayas descubierto (por ejemplo, cómo los métodos puramente analíticos escalan al buscar bifurcaciones, o la necesidad de alta resolución temporal en la integración ODE)."
# Let's add semantic detail to the pattern type and recommended strategy to match.
payload = {
    "pattern_type": "analytical_numerical_complementarity",
    "trigger_conditions": ["strange_attractor_emergence", "hopf_bifurcation"],
    "recommended_strategy": "use_sympy_for_local_stability_and_scipy_for_global_dynamics",
    "confidence": 0.95,
    "supporting_nodes": [1, 2],
    "counterexamples": [],
    "domains": ["nonlinear_dynamics", "chaos_theory"]
}

cmd_add_insight(json.dumps(payload))
print("Insight inyectado en meta_insights documentando la complementariedad entre los metodos numericos y simbolicos.")
