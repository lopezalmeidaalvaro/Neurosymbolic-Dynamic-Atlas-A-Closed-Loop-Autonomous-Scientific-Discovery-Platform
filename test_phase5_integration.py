import os
import sys
import json
import sqlite3
import time

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add current folder to path
sys.path.insert(0, os.getcwd())

from llm_reasoner import LLMReasoner
from sandbox_executor import SandboxExecutor
from autonomous_scientist import AutonomousScientist


def print_result(test_name, status, details=""):
    color_start = (
        "\033[92m"
        if status == "PASS"
        else ("\033[93m" if status == "SKIP" else "\033[91m")
    )
    color_end = "\033[0m"
    print(f"[{color_start}{status}{color_end}] {test_name:<40} {details}")


def main():
    print("=" * 70)
    print("🚀 CORRIENDO LA SUITE DE PRUEBAS DE INTEGRACIÓN DE LA FASE 5 (TESTS 1 - 6)")
    print("=" * 70)

    # Track test statuses
    test_results = {}

    # Cleanup previous database to ensure clean run
    if os.path.exists("scientific_kb.db"):
        try:
            os.remove("scientific_kb.db")
        except Exception:
            pass

    # ----------------------------------------------------
    # TEST 1 - LLM Connection
    # ----------------------------------------------------
    try:
        reasoner = LLMReasoner(provider="openai")
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

        if not openai_key and not anthropic_key:
            print_result(
                "TEST 1 - LLM Connection",
                "SKIP",
                "No API key configured in environment variables.",
            )
            test_results["TEST 1"] = "SKIP"
        else:
            # We have keys configured, make a simple live call
            print("  Connecting to live LLM for Test 1...")
            response = reasoner.query(
                "Eres un asistente. Responde exactamente con la palabra 'OK' y nada más.",
                "Di 'OK'",
            )
            if "OK" in response:
                print_result(
                    "TEST 1 - LLM Connection",
                    "PASS",
                    "Live API connection established successfully.",
                )
                test_results["TEST 1"] = "PASS"
            else:
                print_result(
                    "TEST 1 - LLM Connection",
                    "FAIL",
                    f"Unexpected LLM response: {response}",
                )
                test_results["TEST 1"] = "FAIL"
    except Exception as e:
        print_result("TEST 1 - LLM Connection", "FAIL", f"Connection error: {e}")
        test_results["TEST 1"] = "FAIL"

    # ----------------------------------------------------
    # TEST 2 - Sandbox Safety
    # ----------------------------------------------------
    try:
        executor = SandboxExecutor(use_docker=False)

        # 1. Run safe code
        safe_code = "import json\nprint(json.dumps({'result': 42}))"
        res_safe = executor.execute(safe_code)

        # 2. Run dangerous code
        dangerous_code = "import os\nos.system('echo hacked')"
        is_safe, warnings = executor.validate_code_safety(dangerous_code)

        if res_safe["success"] and res_safe["result"] == {"result": 42} and not is_safe:
            print_result(
                "TEST 2 - Sandbox Safety",
                "PASS",
                "Safe code executed; dangerous code blocked successfully.",
            )
            test_results["TEST 2"] = "PASS"
        else:
            details = f"Safe Success: {res_safe['success']}, Safe Result: {res_safe['result']}, Dangerous Safe Flag: {is_safe}"
            print_result("TEST 2 - Sandbox Safety", "FAIL", details)
            test_results["TEST 2"] = "FAIL"
    except Exception as e:
        print_result("TEST 2 - Sandbox Safety", "FAIL", f"Error: {e}")
        test_results["TEST 2"] = "FAIL"

    # ----------------------------------------------------
    # TEST 3 - Hypothesis Generation (Mock LLM)
    # ----------------------------------------------------
    try:
        reasoner = LLMReasoner(provider="openai")
        reasoner.simulation_mode = True  # Force mock/simulation mode

        context = {
            "domain": "Lorenz bifurcation parameter sweeps",
            "observations": "Chaos detected in systems.",
            "knowledge_graph_summary": "Empty",
            "previous_hypotheses": "[]",
            "goal": "Explain Lyapunov scaling behavior.",
        }

        hypothesis = reasoner.generate_hypothesis(context)
        expected_keys = [
            "hypothesis_text",
            "prediction",
            "variables_involved",
            "confidence_prior",
        ]
        missing_keys = [k for k in expected_keys if k not in hypothesis]

        if not missing_keys:
            print_result(
                "TEST 3 - Hypothesis Generation",
                "PASS",
                f"Hypothesis generated: '{hypothesis['hypothesis_text'][:50]}...'",
            )
            test_results["TEST 3"] = "PASS"
        else:
            print_result(
                "TEST 3 - Hypothesis Generation",
                "FAIL",
                f"Missing keys: {missing_keys}",
            )
            test_results["TEST 3"] = "FAIL"
    except Exception as e:
        print_result("TEST 3 - Hypothesis Generation", "FAIL", f"Error: {e}")
        test_results["TEST 3"] = "FAIL"

    # ----------------------------------------------------
    # TEST 4 - Experiment Design (Mock LLM)
    # ----------------------------------------------------
    try:
        reasoner = LLMReasoner(provider="openai")
        reasoner.simulation_mode = True  # Force mock/simulation mode

        mock_hypothesis = {
            "hypothesis_text": "Monotonic growth of Lyapunov exponents in Lorenz system.",
            "prediction": "Lyapunov correlation > 0.8",
            "variables_involved": ["rho", "lambda_max"],
            "confidence_prior": 0.78,
        }

        available_data = ["synthetic_lorenz"]
        available_methods = ["koopman", "topological"]
        experiment = reasoner.design_experiment(
            mock_hypothesis, available_data, available_methods
        )

        expected_keys = [
            "experiment_description",
            "dataset",
            "method",
            "metrics",
            "falsification_criterion",
            "python_code",
        ]
        missing_keys = [k for k in expected_keys if k not in experiment]

        # Verify python code is present and contains imports
        has_code = "python_code" in experiment and len(experiment["python_code"]) > 20

        if not missing_keys and has_code:
            print_result(
                "TEST 4 - Experiment Design",
                "PASS",
                f"Experiment designed with Python code string ({len(experiment['python_code'])} chars).",
            )
            test_results["TEST 4"] = "PASS"
        else:
            print_result(
                "TEST 4 - Experiment Design",
                "FAIL",
                f"Missing keys: {missing_keys}, Code valid: {has_code}",
            )
            test_results["TEST 4"] = "FAIL"
    except Exception as e:
        print_result("TEST 4 - Experiment Design", "FAIL", f"Error: {e}")
        test_results["TEST 4"] = "FAIL"

    # ----------------------------------------------------
    # TEST 5 - End-to-end mini cycle (Mock LLM)
    # ----------------------------------------------------
    try:
        scientist = AutonomousScientist(llm_provider="openai", use_docker=False)
        scientist.kg_active = False  # Bypassing Neo4j for clean local testing
        scientist._init_local_db()
        scientist.llm.simulation_mode = True  # Force mock mode
        scientist.auto_mode = True  # Enable automated approval

        domain = "Lorenz attractor stability parameters"
        goal = "Discover bifurcations and Lyapunov exponents scaling laws"

        # Run exactly 1 iteration
        res = scientist.run_discovery_cycle(domain, goal, max_iterations=1, patience=1)

        if res["iterations"] == 1 and len(res["session_history"]) == 1:
            verdict = res["session_history"][0]["interpretation"]["verdict"]
            gain = res["session_history"][0]["epistemic_gain"]
            print_result(
                "TEST 5 - End-to-end mini cycle",
                "PASS",
                f"Cycle completed successfully. Verdict: {verdict.upper()} (Epistemic Gain: {gain:.4f})",
            )
            test_results["TEST 5"] = "PASS"
        else:
            print_result(
                "TEST 5 - End-to-end mini cycle",
                "FAIL",
                f"Iterations count: {res['iterations']}",
            )
            test_results["TEST 5"] = "FAIL"
    except Exception as e:
        print_result("TEST 5 - End-to-end mini cycle", "FAIL", f"Error: {e}")
        test_results["TEST 5"] = "FAIL"

    # ----------------------------------------------------
    # TEST 6 - Knowledge Graph / Database Logging
    # ----------------------------------------------------
    try:
        # Check SQLite storage from Test 5
        conn = sqlite3.connect("scientific_kb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hypotheses")
        hyp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM experiments")
        exp_count = cursor.fetchone()[0]
        conn.close()

        # Check Neo4j if active
        neo4j_logged = False
        if scientist.kg_active:
            # We had Neo4j connected during Test 5, so it logged there too
            neo4j_logged = True

        if hyp_count == 1 and exp_count == 1:
            details = "Logged 1 Hypothesis and 1 Experiment to local SQLite DB."
            if neo4j_logged:
                details += " Also tracked in live Neo4j."
            print_result("TEST 6 - Knowledge Graph Logging", "PASS", details)
            test_results["TEST 6"] = "PASS"
        else:
            print_result(
                "TEST 6 - Knowledge Graph Logging",
                "FAIL",
                f"Hypotheses stored: {hyp_count}, Experiments stored: {exp_count}",
            )
            test_results["TEST 6"] = "FAIL"
    except Exception as e:
        print_result("TEST 6 - Knowledge Graph Logging", "FAIL", f"Error: {e}")
        test_results["TEST 6"] = "FAIL"

    print("\n" + "=" * 70)
    print("RESUMEN GENERAL DE PRUEBAS:")
    print("=" * 70)
    all_passed = True
    for test, status in sorted(test_results.items()):
        color = (
            "\033[92m"
            if status == "PASS"
            else ("\033[93m" if status == "SKIP" else "\033[91m")
        )
        print(f"  - {test:<30}: [{color}{status}\033[0m]")
        if status == "FAIL":
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("\033[92mÉXITO: Todos los tests de la Fase 5 pasaron con éxito.\033[0m")
        sys.exit(0)
    else:
        print("\033[91mFALLO: Algunos tests de la Fase 5 fallaron.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
