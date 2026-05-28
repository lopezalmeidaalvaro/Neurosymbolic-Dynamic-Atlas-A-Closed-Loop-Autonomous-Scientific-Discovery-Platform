import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import re
import json
import sqlite3
import math
import time
from physics.core.autonomous.llm_reasoner import LLMReasoner
from physics.core.autonomous.sandbox_executor import SandboxExecutor

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class AutonomousScientist:
    """
    Orchestrates the Autonomous Scientific Discovery Loop.
    Performs iterative hypothesis generation, experimental design, execution in sandbox,
    results interpretation, epistemic gain computation, and knowledge base tracking.
    """

    def __init__(self, llm_provider="openai", use_docker=True, knowledge_graph=None):
        self.llm = LLMReasoner(provider=llm_provider)
        self.sandbox = SandboxExecutor(use_docker=use_docker)
        self.session_history = []
        self.epistemic_gain = 0.0
        self.auto_mode = False  # Starts paused if interactive_mode is used

        # Setup Knowledge Graph (Neo4j if provided, else attempt connection, fallback to SQLite)
        self.kg = knowledge_graph
        self.kg_active = False

        if self.kg:
            self.kg_active = True
        else:
            try:
                from knowledge_graph import ScientificKnowledgeGraph

                # Attempt default connection
                self.kg = ScientificKnowledgeGraph(
                    uri="bolt://localhost:7687", user="neo4j", password="password"
                )
                # Try a quick test write or schemas to check online status
                self.kg.initialize_schema()
                self.kg_active = True
                print(
                    "[INFO] AutonomousScientist: Successfully connected to Neo4j Knowledge Graph."
                )
            except Exception as e:
                print(
                    f"[WARNING] AutonomousScientist: Neo4j connection failed ({e}). Falling back to local SQLite database."
                )
                self.kg = None
                self._init_local_db()

    def _init_local_db(self):
        """
        Initializes a local SQLite database to store hypotheses and experiments when Neo4j is offline.
        """
        conn = sqlite3.connect("scientific_kb.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                id TEXT PRIMARY KEY,
                text TEXT,
                prediction TEXT,
                confidence_prior REAL,
                confidence_posterior REAL,
                state TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                description TEXT,
                dataset TEXT,
                method TEXT,
                falsification_criterion TEXT,
                success INTEGER,
                execution_time REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                source_id TEXT,
                target_id TEXT,
                type TEXT,
                PRIMARY KEY (source_id, target_id, type)
            )
        """)
        conn.commit()
        conn.close()

    def build_context(self, domain, goal):
        """
        Builds the dictionary context describing available methods, datasets, and history.
        """
        # Retrieve previous hypotheses
        previous_hypotheses = []
        if self.kg_active:
            try:
                hyps = self.kg.get_all_hypotheses()
                for h in hyps:
                    previous_hypotheses.append(
                        {"text": h.get("text"), "state": h.get("state")}
                    )
            except Exception:
                pass
        else:
            try:
                conn = sqlite3.connect("scientific_kb.db")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT text, state FROM hypotheses")
                for row in cursor.fetchall():
                    previous_hypotheses.append(
                        {"text": row["text"], "state": row["state"]}
                    )
                conn.close()
            except Exception:
                pass

        # If empty, extract from session history
        if not previous_hypotheses:
            for item in self.session_history:
                previous_hypotheses.append(
                    {
                        "text": item["hypothesis"].get("hypothesis") or item["hypothesis"].get("hypothesis_text") or "",
                        "state": item.get("verdict", "pending"),
                    }
                )

        # Describe available datasets in the project
        available_data = [
            "synthetic_lorenz (Lorenz 3D chaotic attractor timeseries)",
            "synthetic_rossler (Rossler attractor timeseries)",
            "ecg_data (Arrhythmic and normal sinus rhythm electrocardiogram records)",
            "ucr_datasets (Standard benchmarks for time series classification)",
        ]

        # Describe available methods
        available_methods = [
            "topological (Takens phase space reconstruction, persistent homology Betti-0/1 curves)",
            "geometric (Ollivier-Ricci graph curvature, Laplace-Beltrami spectral mapping, diffusion maps)",
            "koopman (Dynamic Mode Decomposition, Koopman operator spectral eigenvalues)",
            "symbolic (SINDy and PySR equations discovery, sparse regression)",
        ]

        context = {
            "domain": domain,
            "observations": "Dynamic chaos and nonlinear behaviors under different noise regimes.",
            "knowledge_graph_summary": f"Currently holds {len(previous_hypotheses)} hypotheses in scientific memory.",
            "previous_hypotheses": json.dumps(previous_hypotheses, indent=2),
            "goal": goal,
            "available_data": available_data,
            "available_methods": available_methods,
        }
        return context

    def compute_epistemic_gain(self, hypothesis_before, hypothesis_after, results):
        """
        Calculates mathematical epistemic gain using prior-posterior Shannon entropy differences,
        textual Jaccard novelty distances, and empirical utility scores.
        """
        p_prior = float(hypothesis_before.get("confidence_prior", 0.5))
        p_post = float(hypothesis_after.get("confidence_posterior", 0.5))

        # Clamp confidence to avoid math domain errors in log2
        p_prior = min(max(p_prior, 0.01), 0.99)
        p_post = min(max(p_post, 0.01), 0.99)

        # Shannon Entropy
        entropy_prior = -(
            p_prior * math.log2(p_prior) + (1.0 - p_prior) * math.log2(1.0 - p_prior)
        )
        entropy_post = -(
            p_post * math.log2(p_post) + (1.0 - p_post) * math.log2(1.0 - p_post)
        )

        # Uncertainty reduction: difference in entropy
        uncertainty_reduction = max(0.0, entropy_prior - entropy_post)

        # Jaccard Novelty distance against all previous hypotheses
        new_text = hypothesis_before.get("hypothesis_text", "")
        novelty_score = 1.0

        previous_texts = [
            item["hypothesis"]["hypothesis_text"] for item in self.session_history
        ]
        if previous_texts:
            jaccard_distances = []
            for prev_text in previous_texts:
                w1 = set(re.findall(r"\b\w+\b", new_text.lower()))
                w2 = set(re.findall(r"\b\w+\b", prev_text.lower()))
                if not w1 or not w2:
                    dist = 1.0
                else:
                    intersection = w1.intersection(w2)
                    union = w1.union(w2)
                    dist = 1.0 - (len(intersection) / len(union))
                jaccard_distances.append(dist)
            novelty_score = min(jaccard_distances)

        # Utility based on empirical result success and verdict
        verdict = hypothesis_after.get("verdict", "inconclusive").lower()
        if verdict == "validated":
            utility = 1.0
        elif verdict == "rejected":
            utility = 0.3  # Eliminating incorrect models is still useful
        else:
            utility = 0.0

        # Composite Epistemic Gain
        gain = 0.4 * uncertainty_reduction + 0.4 * novelty_score + 0.2 * utility
        return float(gain)

    def execute_experiment(self, experiment_design):
        """
        Executes code inside the sandbox. Implements a 2-retry correction loop if execution fails.
        """
        python_code = experiment_design.get("python_code")

        # Prepare inputs (we can pass synthetic systems or configuration)
        input_data = {
            "config": {
                "noise_level": 0.05,
                "timesteps": 1000,
                "bifurcation_sweep": True,
            }
        }

        # First execution attempt
        execution_res = self.sandbox.execute(python_code, input_data=input_data)
        if execution_res["success"]:
            return execution_res

        # If it fails, start the self-correction loop
        print(
            "[WARNING] Experiment execution failed. Initiating LLM code self-correction..."
        )
        for attempt in range(2):
            error_details = execution_res.get("error", "Unknown error")
            stderr = execution_res.get("stderr", "")
            stdout = execution_res.get("stdout", "")

            system_prompt = (
                "Eres un depurador de código experto. Se ejecutó el experimento diseñado "
                "pero falló con un error de ejecución o de formato de salida.\n"
                "Corrige el código Python para resolver el problema.\n"
                "REGLAS:\n"
                "1. El código DEBE importar los módulos necesarios.\n"
                "2. El código DEBE al final imprimir un objeto JSON con los resultados a stdout (e.g. `print(json.dumps(resultado))`) y NADA MÁS en stdout.\n"
                "3. Corrige la sintaxis y los nombres de variables.\n"
                "Debes responder en formato JSON con la siguiente estructura exacta:\n"
                "{\n"
                '  "experiment_description": "Explicación del ajuste.",\n'
                '  "dataset": "...",\n'
                '  "method": "...",\n'
                '  "metrics": [...],\n'
                '  "falsification_criterion": "...",\n'
                '  "python_code": "Código corregido con todos los escapes de cadenas correctos."\n'
                "}"
            )

            user_prompt = (
                f"El código falló durante la ejecución.\n"
                f"Código original:\n{python_code}\n\n"
                f"Error reportado:\n{error_details}\n\n"
                f"Stderr:\n{stderr}\n\n"
                f"Stdout:\n{stdout}\n\n"
                f"Por favor, corrige el código Python y devuélvelo en el mismo formato JSON."
            )

            try:
                corrected_design = self.llm._query_json(
                    system_prompt,
                    user_prompt,
                    [
                        "experiment_description",
                        "dataset",
                        "method",
                        "metrics",
                        "falsification_criterion",
                        "python_code",
                    ],
                )
                python_code = corrected_design.get("python_code")

                # Re-execute corrected code
                execution_res = self.sandbox.execute(python_code, input_data=input_data)
                if execution_res["success"]:
                    print(
                        f"  [SUCCESS] LLM self-correction successfully resolved execution error on attempt {attempt + 1}!"
                    )
                    # Update design fields with corrected ones
                    experiment_design.update(corrected_design)
                    return execution_res
            except Exception as e:
                print(f"  [ERROR] Code correction attempt {attempt + 1} failed: {e}")

        return execution_res

    def update_knowledge_graph(self, hypothesis, experiment, results, verdict):
        """
        Saves the discovery node to Neo4j if available, or falls back to local SQLite.
        """
        import uuid
        from scientific_guard import sanitize_hypothesis

        hyp_id = f"hyp_{uuid.uuid4().hex[:8]}"
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"

        # Robust support for both default and rigid QG JSON formats
        hyp_text = hypothesis.get("hypothesis") or hypothesis.get("hypothesis_text") or ""
        hyp_text = sanitize_hypothesis(hyp_text)
        equation = hypothesis.get("equation") or hypothesis.get("prediction") or ""
        confidence_prior = float(hypothesis.get("confidence_prior", 0.5))

        # 1. Update Neo4j Knowledge Graph if connected
        if self.kg_active and self.kg:
            try:
                self.kg.create_hypothesis(
                    hypothesis_id=hyp_id,
                    text=hyp_text,
                    confidence=confidence_prior,
                    state=verdict,
                )
                self.kg.create_experiment(
                    experiment_id=exp_id,
                    description=experiment.get("experiment_description"),
                    dataset_name=experiment.get("dataset"),
                    method=experiment.get("method"),
                )
                self.kg.relate_experiment_to_hypothesis(
                    experiment_id=exp_id,
                    hypothesis_id=hyp_id,
                    outcome=f"Verdict: {verdict}",
                )
                # Relate refinement if present
                if len(self.session_history) > 0:
                    prev_hyp_id = (
                        f"hyp_{int(time.time()) - 100}"  # dummy lookup approximation
                    )
                    # We can link it if we tracked actual IDs
                    pass
                print("[INFO] Saved hypothesis and experiment to Neo4j database.")
                return
            except Exception as e:
                print(
                    f"[WARNING] Failed to write to Neo4j ({e}). Falling back to local SQLite."
                )

        # 2. Local SQLite fallback
        try:
            conn = sqlite3.connect("scientific_kb.db")
            cursor = conn.cursor()

            # Save Hypothesis
            cursor.execute(
                "INSERT INTO hypotheses (id, text, prediction, confidence_prior, confidence_posterior, state) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    hyp_id,
                    hyp_text,
                    equation,
                    confidence_prior,
                    (
                        float(results.get("confidence_posterior", 0.5))
                        if isinstance(results, dict)
                        else 0.5
                    ),
                    verdict,
                ),
            )

            # Save Experiment
            cursor.execute(
                "INSERT INTO experiments (id, description, dataset, method, falsification_criterion, success, execution_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    exp_id,
                    experiment.get("experiment_description"),
                    experiment.get("dataset"),
                    experiment.get("method"),
                    experiment.get("falsification_criterion"),
                    1 if results else 0,
                    (
                        float(results.get("execution_time", 0.0))
                        if isinstance(results, dict)
                        else 0.0
                    ),
                ),
            )

            # Relate Experiment to Hypothesis
            cursor.execute(
                "INSERT INTO relations (source_id, target_id, type) VALUES (?, ?, ?)",
                (exp_id, hyp_id, "EVALUATES"),
            )

            conn.commit()
            conn.close()
            print("[INFO] Saved hypothesis and experiment to local SQLite database.")
        except Exception as e:
            print(
                f"[ERROR] Failed to save scientific data to local SQLite database: {e}"
            )

    def run_discovery_cycle(self, domain, goal, max_iterations=3, patience=2):
        """
        Runs the full autonomous scientist discovery loop.
        """
        print("\n" + "=" * 70)
        print("STARTING AUTONOMOUS SCIENTIFIC DISCOVERY LOOP")
        print(f"Goal: {goal}")
        print("=" * 70)

        no_gain_iterations = 0

        for iteration in range(max_iterations):
            print(f"\n--- ITERATION {iteration + 1}/{max_iterations} ---")

            # 1. Build context
            context = self.build_context(domain, goal)

            # 2. Generate Hypothesis
            print("  Generating original hypothesis...")
            try:
                hypothesis = self.llm.generate_hypothesis(context)
            except Exception as e:
                print(f"  [ERROR] Hypothesis generation failed: {e}")
                break

            print(f"  Hypothesis Text: '{hypothesis['hypothesis_text']}'")
            print(f"  Prediction: '{hypothesis['prediction']}'")
            print(f"  Prior Confidence: {hypothesis['confidence_prior']}")

            # Interactive Mode approval
            if not self.auto_mode:
                user_input = self.interactive_mode(hypothesis)
                if user_input == "abort":
                    print("  [ABORT] Discovery cycle aborted by user.")
                    break

            # 3. Design Experiment
            print("  Designing computational experiment...")
            try:
                experiment = self.llm.design_experiment(
                    hypothesis, context["available_data"], context["available_methods"]
                )
            except Exception as e:
                print(f"  [ERROR] Experiment design failed: {e}")
                break

            print(f"  Experiment Method: {experiment['method']}")
            print(f"  Falsification Criterion: {experiment['falsification_criterion']}")

            # 4. Execute Experiment in Sandbox
            print("  Running experiment in sandboxed environment...")
            execution_res = self.execute_experiment(experiment)

            if not execution_res["success"]:
                print(
                    f"  [ERROR] Experiment execution failed permanently: {execution_res['error']}"
                )
                continue

            print(
                f"  Execution completed in {execution_res['execution_time']:.2f} seconds."
            )
            print(f"  Raw Results: {json.dumps(execution_res['result'], indent=2)}")

            # 5. Interpret Results
            print("  Interpreting results...")
            try:
                interpretation = self.llm.interpret_results(
                    hypothesis, experiment, execution_res["result"]
                )
            except Exception as e:
                print(f"  [ERROR] Result interpretation failed: {e}")
                continue

            verdict = interpretation["verdict"]
            print(
                f"  Verdict: {verdict.upper()} (Posterior Confidence: {interpretation['confidence_posterior']})"
            )
            print(f"  Reasoning: {interpretation['reasoning']}")

            # 6. Calculate Epistemic Gain
            gain = self.compute_epistemic_gain(
                hypothesis, interpretation, execution_res["result"]
            )
            self.epistemic_gain += gain
            print(f"  Calculated Epistemic Gain for Iteration: {gain:.4f}")
            print(f"  Total Cumulative Epistemic Gain: {self.epistemic_gain:.4f}")

            # 7. Update Knowledge Graph/Database
            self.update_knowledge_graph(
                hypothesis, experiment, execution_res["result"], verdict
            )

            # Save iteration details to history
            self.session_history.append(
                {
                    "iteration": iteration + 1,
                    "hypothesis": hypothesis,
                    "experiment": experiment,
                    "execution": {
                        "success": execution_res["success"],
                        "execution_time": execution_res["execution_time"],
                        "result": execution_res["result"],
                    },
                    "interpretation": interpretation,
                    "epistemic_gain": gain,
                }
            )

            # Check stopping criteria
            if gain < 0.02:
                no_gain_iterations += 1
            else:
                no_gain_iterations = 0

            if no_gain_iterations >= patience:
                print(
                    f"\n[INFO] Convergence reached: Epistemic gain stagnated for {patience} consecutive iterations."
                )
                break

        # Generate final outputs
        os.makedirs("artifacts", exist_ok=True)
        self.generate_discovery_report()
        self.save_session()

        return {
            "iterations": len(self.session_history),
            "total_epistemic_gain": self.epistemic_gain,
            "session_history": self.session_history,
        }

    def interactive_mode(self, hypothesis):
        """
        Interactive review interface allowing human scientists to inspect, approve, or inject knowledge.
        """
        print("\n" + "-" * 50)
        print("HUMAN-IN-THE-LOOP INTERACTIVE REVIEW REQUIRED:")
        print(f"Proposed Hypothesis: {hypothesis.get('hypothesis_text')}")
        print(f"Prediction: {hypothesis.get('prediction')}")
        print("-" * 50)
        print(
            "Options: [Enter] to Approve, 'auto' to enable autonomous mode, 'abort' to terminate."
        )

        # Under non-interactive automated test environments, we automatically continue.
        # Check if stdin is a TTY to avoid blocking automated pipelines.
        if not sys.stdin.isatty():
            print(
                "[INFO] Non-TTY environment detected. Automatically approving hypothesis."
            )
            return "approve"

        try:
            choice = input("Enter option: ").strip().lower()
            if choice == "auto":
                self.auto_mode = True
                print(
                    "Autonomous mode enabled. Scientist will now proceed without pausing."
                )
                return "approve"
            elif choice == "abort":
                return "abort"
            else:
                return "approve"
        except (KeyboardInterrupt, EOFError):
            print("\n[INFO] Keyboard interrupt detected. Resuming automatically.")
            return "approve"

    def generate_discovery_report(self, output_path="artifacts/discovery_report.md"):
        """
        Generates a premium structured Markdown scientific report summarizing findings.
        """
        total_hypotheses = len(self.session_history)
        validated = sum(
            1
            for item in self.session_history
            if item["interpretation"]["verdict"] == "validated"
        )
        rejected = sum(
            1
            for item in self.session_history
            if item["interpretation"]["verdict"] == "rejected"
        )
        inconclusive = sum(
            1
            for item in self.session_history
            if item["interpretation"]["verdict"] == "inconclusive"
        )

        report = (
            f"# Scientific Discovery Loop Report\n\n"
            f"Generated autonomously by the Antigravity Scientist Engine on {time.strftime('%Y-%m-%d %H:%M:%S')}.\n\n"
            f"## Summary of Accomplishments\n"
            f"- **Total Hypotheses Explored**: {total_hypotheses}\n"
            f"- **Validated**: {validated}\n"
            f"- **Rejected**: {rejected}\n"
            f"- **Inconclusive**: {inconclusive}\n"
            f"- **Cumulative Epistemic Gain**: {self.epistemic_gain:.4f}\n\n"
            f"---\n\n"
            f"## Validated Discoveries\n\n"
        )

        if validated == 0:
            report += "No hypotheses were fully validated during this cycle.\n\n"
        else:
            for item in self.session_history:
                if item["interpretation"]["verdict"] == "validated":
                    report += (
                        f"### Hypothesis {item['iteration']}: {item['hypothesis']['hypothesis_text']}\n"
                        f"- **Prediction**: {item['hypothesis']['prediction']}\n"
                        f"- **Method Used**: {item['experiment']['method']}\n"
                        f"- **Posterior Confidence**: {item['interpretation']['confidence_posterior']}\n"
                        f"- **Reasoning**: {item['interpretation']['reasoning']}\n\n"
                    )

        report += "## Lessons Learned & Rejected Hypotheses\n\n"
        if rejected == 0:
            report += "No hypotheses were rejected during this cycle.\n\n"
        else:
            for item in self.session_history:
                if item["interpretation"]["verdict"] == "rejected":
                    report += (
                        f"### Rejected Hypothesis {item['iteration']}: {item['hypothesis']['hypothesis_text']}\n"
                        f"- **Original Prediction**: {item['hypothesis']['prediction']}\n"
                        f"- **Refutation Reasoning**: {item['interpretation']['reasoning']}\n"
                        f"- **Refined Hypothesis Suggestion**: {item['interpretation'].get('refined_hypothesis', 'None provided')}\n\n"
                    )

        report += "## History of Scientific Exploration\n\n"
        report += "| Iteration | Method | Verdict | Epistemic Gain |\n"
        report += "|---|---|---|---|\n"
        for item in self.session_history:
            report += f"| {item['iteration']} | {item['experiment']['method']} | {item['interpretation']['verdict']} | {item['epistemic_gain']:.4f} |\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[INFO] Discovery Report compiled successfully to: {output_path}")

    def save_session(self, output_path="artifacts/autonomous_session.json"):
        """
        Saves the session history to a structured JSON file.
        """
        data = {
            "timestamp": time.time(),
            "total_epistemic_gain": self.epistemic_gain,
            "history": self.session_history,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[INFO] Autonomous Session data saved successfully to: {output_path}")
