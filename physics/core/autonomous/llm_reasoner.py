import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import re
import uuid
import json
import json5
from tenacity import retry, stop_after_attempt, wait_exponential

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class LLMReasoner:
    """
    Manages communication with reasoning LLMs (OpenAI o1/o3, Anthropic Claude).
    Includes a resilient mock simulation mode when API keys are absent.
    """

    def __init__(self, provider="openai", model=None, temperature=0.1):
        self.provider = provider.lower()
        self.temperature = temperature
        self.simulation_mode = False
        self.sessions = {}

        if self.provider == "openai":
            self.model = model or "o3-mini"
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                print(
                    "[WARNING] OPENAI_API_KEY is missing. LLMReasoner is running in Mock Simulation Mode."
                )
                self.simulation_mode = True
            else:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            self.model = model or "claude-3-5-sonnet-20241022"
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                print(
                    "[WARNING] ANTHROPIC_API_KEY is missing. LLMReasoner is running in Mock Simulation Mode."
                )
                self.simulation_mode = True
            else:
                from anthropic import Anthropic

                self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def query(self, system_prompt, user_prompt, max_tokens=4096):
        """
        Sends the query to the reasoning LLM with exponential backoff retry.
        Uses simulation fallback if no API key is configured.
        """
        if self.simulation_mode:
            return self._mock_query(system_prompt, user_prompt)

        return self._query_api_with_retry(system_prompt, user_prompt, max_tokens)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _query_api_with_retry(self, system_prompt, user_prompt, max_tokens):
        if self.provider == "openai":
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            kwargs = {
                "model": self.model,
                "messages": messages,
            }
            # Handle o1 / o3-mini specific parameters
            if "o1" in self.model or "o3" in self.model:
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["temperature"] = self.temperature
                kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text

    def _query_json(self, system_prompt, user_prompt, expected_keys, max_retries=3):
        """
        Performs a query, extracts JSON, parses using json5, and verifies expected keys.
        Auto-corrects malformed JSON by feeding back parsing errors to the LLM.
        """
        current_user_prompt = user_prompt

        for attempt in range(max_retries):
            try:
                response_text = self.query(system_prompt, current_user_prompt)

                # Extract JSON block using regex
                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if not json_match:
                    raise ValueError(
                        "No JSON block (delimited by '{' and '}') found in the LLM response."
                    )

                json_str = json_match.group(0)

                # Parse with json5 to be highly permissive with trailing commas and comments
                parsed_data = json5.loads(json_str)

                # Ensure it is a dictionary
                if not isinstance(parsed_data, dict):
                    raise ValueError("Parsed JSON is not a dictionary / JSON object.")

                # Verify expected keys
                missing_keys = [k for k in expected_keys if k not in parsed_data]
                if missing_keys:
                    raise ValueError(f"Missing required JSON keys: {missing_keys}")

                return parsed_data

            except Exception as e:
                error_msg = str(e)
                print(
                    f"[LLM Correction Attempt {attempt + 1}/{max_retries}] JSON parsing failed: {error_msg}"
                )
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"Failed to obtain valid JSON from LLM after {max_retries} attempts. Last error: {error_msg}"
                    )

                # Update user prompt with error details for the correction loop
                current_user_prompt = (
                    f"{user_prompt}\n\n"
                    f"--- ATTEMPT {attempt + 1} CORRECTION REQUIRED ---\n"
                    f"Your previous response was malformed or invalid.\n"
                    f"Error detail: {error_msg}\n"
                    f"Please output ONLY a valid, parseable JSON object containing all required keys: {expected_keys}."
                )

    def _mock_query(self, system_prompt, user_prompt):
        """
        Mock simulation generator that parses prompt content and returns realistic,
        scientifically rich JSON objects or textual responses.
        """
        user_prompt_lower = user_prompt.lower()

        # 1. Hypothesis Generation Prompt
        if (
            "genera una hipótesis" in user_prompt_lower
            or "generate_hypothesis" in user_prompt_lower
            or "confidence_prior" in user_prompt_lower
            or "falsable" in user_prompt_lower
        ):
            # Check domain
            domain = "Lorenz"
            if "ecg" in user_prompt_lower or "electrocardiogram" in user_prompt_lower:
                domain = "ECG"
            elif "quantum_gravity" in user_prompt_lower or "quantum_gravity" in system_prompt.lower() or "toy_models" in user_prompt_lower:
                domain = "QG"

            if domain == "QG":
                data = {
                    "hypothesis": "The emergent spectral dimension in causal layered graphs transitions near p_intra = 0.35 and is highly correlated with average slice curvature.",
                    "equation": "d_s \\approx c_1 \\cdot p_{intra} + c_2 \\cdot \\langle R \\rangle",
                    "variables": ["p_intra", "spectral_dimension", "mean_curvature"],
                    "falsification_test": "R^2 < 0.80",
                    "confidence_prior": 0.85
                }
            elif domain == "ECG":
                data = {
                    "hypothesis_text": "The topological persistence of ECG phase space reconstructions exhibits a reduction in H1 dimension during arrhythmic episodes compared to normal sinus rhythm.",
                    "prediction": "The Wasserstein distance between persistent homology diagrams of normal vs arrhythmic states is greater than 0.25, and mean Betti-1 curvature is lower.",
                    "variables_involved": [
                        "arrhythmia_indicator",
                        "wasserstein_distance",
                        "betti_1_curvature",
                    ],
                    "confidence_prior": 0.82,
                }
            else:
                data = {
                    "hypothesis_text": "The maximum Lyapunov exponent of the Lorenz system increases monotonically as a function of the bifurcation parameter rho in the chaotic regime [20, 28].",
                    "prediction": "Lyapunov exponent lambda_max is positive and shows a positive correlation with rho (Pearson correlation > 0.8).",
                    "variables_involved": ["rho", "lyapunov_exponent"],
                    "confidence_prior": 0.78,
                }
            return json.dumps(data, indent=2)

        # 2. Experiment Design Prompt
        elif (
            "diseña un experimento" in user_prompt_lower
            or "design_experiment" in user_prompt_lower
            or "python_code" in user_prompt_lower
        ):
            if "p_intra" in user_prompt_lower or "spectral_dimension" in user_prompt_lower or "quantum_gravity" in user_prompt_lower or "boundary_area" in user_prompt_lower:
                python_code = """import numpy as np
import pandas as pd
import json
import sys
import os

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    # Safe mock computation using the project's actual ensembles
    causal_path = "data/causal_layered_ensemble.csv"
    if os.path.exists(causal_path):
        df = pd.read_csv(causal_path)
        corr_val = float(df["p_intra"].corr(df["spectral_dimension"]))
        mean_ds = float(df["spectral_dimension"].mean())
    else:
        corr_val = 0.875
        mean_ds = 1.42

    results = {
        "success": True,
        "pearson_correlation": corr_val,
        "mean_spectral_dimension": mean_ds,
        "r_squared": corr_val ** 2,
        "falsified": corr_val ** 2 < 0.80
    }
except Exception as e:
    results = {
        "success": False,
        "error": str(e)
    }

print(json.dumps(results))
"""
                data = {
                    "experiment_description": "Analyze causal layered graph simulation logs, fit spectral dimension curves, compute Pearson correlation and R^2 coefficient with transitivity metrics to test scaling constraints.",
                    "dataset": "causal_layered_ensemble",
                    "method": "geometric_analysis",
                    "metrics": ["r_squared", "pearson_correlation"],
                    "falsification_criterion": "R_squared between transitivity and spectral dimension is < 0.80.",
                    "python_code": python_code
                }
                return json.dumps(data, indent=2)

            python_code = """import numpy as np
import json
import sys

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Safe mock computation using the project's actual synthetic systems
try:
    from synthetic_systems import generate_lorenz
    
    # Run integration for varying rho
    rhos = [20, 22, 24, 26, 28]
    lambdas = []
    
    for r in rhos:
        # Generate synthetic data
        sys_data = generate_lorenz(n_timesteps=1000, dt=0.01, rho=r)
        # Mocking Lyapunov exponent computation using variance and decay as proxy
        std_val = np.std(sys_data["x"])
        lyapunov_est = 0.5 + 0.015 * r + 0.05 * np.random.randn()
        lambdas.append(float(lyapunov_est))
        
    correlation = np.corrcoef(rhos, lambdas)[0, 1]
    
    results = {
        "success": True,
        "rhos": rhos,
        "lyapunov_exponents": lambdas,
        "pearson_correlation": float(correlation),
        "mean_lyapunov": float(np.mean(lambdas)),
        "divergence_rate": 0.125
    }
except Exception as e:
    results = {
        "success": False,
        "error": str(e)
    }

print(json.dumps(results))
"""
            data = {
                "experiment_description": "Integrate the 3D Lorenz equations for a parameter sweep of rho from 20 to 28, extract timeseries snapshots, estimate Lyapunov exponents using delay embeddings, and compute their correlation coefficient.",
                "dataset": "synthetic_lorenz",
                "method": "koopman",
                "metrics": ["pearson_correlation", "mean_lyapunov"],
                "falsification_criterion": "Pearson correlation coefficient between rho and Lyapunov exponents is <= 0.8.",
                "python_code": python_code,
            }
            return json.dumps(data, indent=2)

        # 3. Interpret Results Prompt
        elif (
            "analiza los resultados" in user_prompt_lower
            or "interpret_results" in user_prompt_lower
            or "verdict" in user_prompt_lower
        ):
            data = {
                "verdict": "validated",
                "confidence_posterior": 0.91,
                "reasoning": "The experiment showed a strong positive linear correlation (Pearson coefficient = 0.94) between the bifurcation parameter rho and the maximum Lyapunov exponent, which exceeded our falsification threshold of 0.8.",
                "refined_hypothesis": "The maximum Lyapunov exponent of the Lorenz system scales power-law-like in the transition to chaos before saturating.",
                "next_steps": "Analyze the scaling exponent at the boundary of chaos (rho = 22 to 24.5) with a finer grid resolution.",
            }
            return json.dumps(data, indent=2)

        else:
            return "This is a mock response from the simulated LLM Reasoner. Please configure your API keys to enable live responses."

    # --- SECTION B: Prompts especializados ---
    def generate_hypothesis(self, context):
        """
        Generates an original, falsifiable, quantitative scientific hypothesis.
        """
        domain = context.get("domain", "")
        if domain == "quantum_gravity_toy_models":
            system_prompt = (
                "Eres un físico teórico y computacional especializado en Gravedad Cuántica y modelos de juguete analógicos (analogue gravity).\n"
                "Tu tarea es proponer una hipótesis científica rigurosa, cuantitativa y original basándote en el contexto.\n"
                "Debes responder en formato JSON con la siguiente estructura exacta:\n"
                "{\n"
                '  "hypothesis": "Descripción detallada de la hipótesis en lenguaje natural (max 200 chars).",\n'
                '  "equation": "Máximo UNA ecuación en LaTeX representando la relación física propuesta.",\n'
                '  "variables": ["lista", "de", "variables"],\n'
                '  "falsification_test": "Criterio numérico explícito de rechazo (ej: R^2 < 0.5, p > 0.05).",\n'
                '  "confidence_prior": 0.5\n'
                "}\n"
                "REGLAS CRÍTICAS:\n"
                "1. NO uses frases como 'theory of everything', 'proof of quantum gravity', 'discovered fundamental law', o 'real spacetime'.\n"
                "2. Asegura que la hipótesis sea falsable mediante un experimento empírico y define variables que coincidan con las simulaciones."
            )
            expected_keys = [
                "hypothesis",
                "equation",
                "variables",
                "falsification_test",
                "confidence_prior"
            ]
        else:
            system_prompt = (
                "Eres un científico computacional especializado en sistemas dinámicos caóticos, "
                "análisis de series temporales y topología matemática.\n"
                "Tu tarea es proponer una hipótesis científica rigurosa, cuantitativa y original basándote en el contexto.\n"
                "Debes responder en formato JSON con la siguiente estructura exacta:\n"
                "{\n"
                '  "hypothesis_text": "Texto detallado de la hipótesis.",\n'
                '  "prediction": "Predicción matemática o estadística clara y contrastable.",\n'
                '  "variables_involved": ["lista", "de", "variables"],\n'
                '  "confidence_prior": 0.75\n'
                "}\n"
                "Asegúrate de que la hipótesis sea falsable mediante un experimento empírico."
            )
            expected_keys = [
                "hypothesis_text",
                "prediction",
                "variables_involved",
                "confidence_prior",
            ]

        user_prompt = (
            f"Por favor, genera una hipótesis basada en este contexto:\n"
            f"Domain: {context.get('domain')}\n"
            f"Observations: {context.get('observations')}\n"
            f"Knowledge Graph Summary: {context.get('knowledge_graph_summary')}\n"
            f"Previous Hypotheses: {context.get('previous_hypotheses')}\n"
            f"Goal: {context.get('goal')}\n"
        )

        return self._query_json(system_prompt, user_prompt, expected_keys)

    def design_experiment(self, hypothesis, available_data, available_methods):
        """
        Designs a computational experiment to test the hypothesis and generates execution code.
        """
        system_prompt = (
            "Eres un desarrollador y científico de datos experto. Debes diseñar un experimento "
            "computacional preciso para contrastar la hipótesis científica provista.\n"
            "Escribe código Python limpio y ejecutable que corra el experimento de forma aislada.\n"
            "REGLAS DE CÓDIGO:\n"
            "1. El código DEBE importar los módulos del proyecto si es necesario (e.g. `synthetic_systems`, `topological_analysis`, `geometric_analysis`, `koopman_analysis`, `symbolic_discovery`).\n"
            "2. El código debe cargar o generar los datos, aplicar el método seleccionado, y evaluar las métricas.\n"
            "3. IMPORTANTE: El código DEBE al final imprimir un objeto JSON con los resultados a stdout (e.g. `print(json.dumps(resultado))`) y NADA MÁS en stdout.\n"
            "4. Asegura que el JSON de salida contenga una clave 'success': true/false y las métricas numéricas calculadas.\n"
            "Debes responder en formato JSON con la siguiente estructura exacta:\n"
            "{\n"
            '  "experiment_description": "Explicación del diseño del experimento.",\n'
            '  "dataset": "nombre_del_dataset_o_synthetic",\n'
            '  "method": "método_seleccionado",\n'
            '  "metrics": ["metricas", "a", "evaluar"],\n'
            '  "falsification_criterion": "Regla lógica de falsación (ej: pearson_correlation <= 0.8)",\n'
            '  "python_code": "Código Python completo formateado como una única cadena de texto con escapes correctos."\n'
            "}"
        )

        user_prompt = (
            f"Diseña un experimento para contrastar esta hipótesis:\n"
            f"Hypothesis: {hypothesis.get('hypothesis_text')}\n"
            f"Prediction: {hypothesis.get('prediction')}\n"
            f"Variables Involved: {hypothesis.get('variables_involved')}\n\n"
            f"Datasets disponibles: {available_data}\n"
            f"Métodos analíticos disponibles: {available_methods}\n"
        )

        expected_keys = [
            "experiment_description",
            "dataset",
            "method",
            "metrics",
            "falsification_criterion",
            "python_code",
        ]
        return self._query_json(system_prompt, user_prompt, expected_keys)

    def interpret_results(self, hypothesis, experiment, results):
        """
        Analyzes the experimental results to validate, reject or mark the hypothesis as inconclusive.
        """
        system_prompt = (
            "Eres un metodólogo y filósofo de la ciencia riguroso. Tu tarea es analizar los "
            "resultados numéricos de un experimento y contrastarlos con la hipótesis original y su criterio de falsación.\n"
            "Debes dar un veredicto científico honesto y proponer refinamientos.\n"
            "Debes responder en formato JSON con la siguiente estructura exacta:\n"
            "{\n"
            '  "verdict": "validated" | "rejected" | "inconclusive",\n'
            '  "confidence_posterior": 0.85,\n'
            '  "reasoning": "Explicación detallada respaldada por los datos de por qué se toma la decisión.",\n'
            "  \"refined_hypothesis\": \"Si el veredicto es 'rejected' o 'validated', una versión mejorada, más precisa o expandida de la hipótesis (opcional).\",\n"
            '  "next_steps": "Sugerencias metodológicas para experimentos subsiguientes."\n'
            "}"
        )

        user_prompt = (
            f"Analiza los resultados del experimento:\n"
            f"Hypothesis: {hypothesis.get('hypothesis_text')}\n"
            f"Prediction: {hypothesis.get('prediction')}\n"
            f"Experiment: {experiment.get('experiment_description')}\n"
            f"Falsification Criterion: {experiment.get('falsification_criterion')}\n"
            f"Results of execution:\n{json.dumps(results, indent=2)}\n"
        )

        expected_keys = ["verdict", "confidence_posterior", "reasoning", "next_steps"]
        return self._query_json(system_prompt, user_prompt, expected_keys)

    # --- SECTION D: Memoria de conversación ---
    def start_session(self, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return session_id

    def add_to_history(self, session_id, role, content):
        if session_id in self.sessions:
            self.sessions[session_id].append({"role": role, "content": content})

    def get_history(self, session_id):
        return self.sessions.get(session_id, [])
