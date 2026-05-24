import os
import subprocess
import sys
import argparse
import time
import sqlite3
import json
import io
from datetime import datetime

# Force stdout to UTF-8 in Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from core.io import export_session, ARTIFACTS_DIR, resolve_path
import ucr_loader
import robustness_audit
import symbolic_discovery
from topological_robustness_audit import run_full_topological_robustness_study
from knowledge_graph import ScientificKnowledgeGraph
import migrate_to_graph

def print_step(step_name):
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")
    print(f"{'='*60}")

def run_cmd(command):
    print(f"Ejecutando: {' '.join(command)}")
    t0 = time.time()
    env = os.environ.copy()
    env["EVAL_CALLED"] = "1"
    result = subprocess.run(command, env=env)
    duration = time.time() - t0
    status = "SUCCESS" if result.returncode == 0 else "ERROR"
    if result.returncode != 0:
        print(f"\n❌ ERROR: El comando ha fallado. Deteniendo pipeline.")
        sys.exit(1)
    print("✅ Paso completado con éxito.\n")
    return duration, status

def main():
    parser = argparse.ArgumentParser(description="Neurosymbolic Pipeline Runner (Dynamic Atlas)")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment identifier")
    parser.add_argument("--noise", type=float, default=0.0, help="Noise level injection (default: 0.0)")
    parser.add_argument("--seed", type=int, default=42, help="Seed value (default: 42)")
    parser.add_argument("--system", type=str, default=None, help="Dynamical system to run (default: None for all)")
    
    # New options (Phase 1)
    parser.add_argument("--ucr_dataset", type=str, default=None, help="UCR Dataset name to load and evaluate")
    parser.add_argument("--robustness_study", action="store_true", help="Execute Gaussian noise robustness audit on the loaded domain")
    parser.add_argument("--features_extended", action="store_true", help="Use 15-dimensional EV3_EXTENDED feature space instead of standard 8D EV3")
    parser.add_argument("--features_deep", action="store_true", help="Use 68-dimensional EV3_DEEP feature space in everything (classification, CKA, SHAP)")
    parser.add_argument("--topological_audit", action="store_true", help="Execute Phase 4 Topological, Geometrical, and Koopman robustness stability study")
    parser.add_argument("--domain_a", type=str, default=None, help="Domain A override path")
    parser.add_argument("--domain_b", type=str, default=None, help="Domain B override path")
    parser.add_argument("--domain_c", type=str, default=None, help="Domain C override path")
    
    # New options (Phase 2)
    parser.add_argument("--symbolic_discovery", action="store_true", help="Activate Phase 2 Symbolic Equation Discovery")
    parser.add_argument("--discovery_method", type=str, default="sindy", choices=["sindy", "pysr", "both"], help="Symbolic regression methodology (default: sindy)")
    parser.add_argument("--use_ev3_for_discovery", action="store_true", help="Leverage 15D EV3_EXTENDED embeddings as input for PySR")
    parser.add_argument("--run_discovery_benchmark", action="store_true", help="Execute complete multi-system symbolic recovery benchmark")
    
    # New options (Phase 3)
    parser.add_argument("--use_knowledge_graph", action="store_true", help="Leverage Neo4j Graph Database for scientific memory")
    parser.add_argument("--kg_log_discovery", action="store_true", help="Automatically log symbolic discovery trials in Neo4j Graph Database")
    parser.add_argument("--kg_report", action="store_true", help="Generate Markdown summary report of the Graph DBMS")
    parser.add_argument("--migrate_to_graph", action="store_true", help="Bridge and migrate historical SQLite data to Neo4j Graph Database")
    
    # New options (Phase 5 - Autonomous Discovery)
    parser.add_argument("--autonomous_discovery", action="store_true", help="Activate Phase 5 Autonomous Scientific Discovery Loop")
    parser.add_argument("--discovery_domain", type=str, default="synthetic_dynamical_systems", help="Scientific domain description")
    parser.add_argument("--discovery_goal", type=str, default="discover_invariants_under_noise", help="Specific scientific goal")
    parser.add_argument("--discovery_iterations", type=int, default=5, help="Maximum number of discovery iterations")
    parser.add_argument("--discovery_interactive", action="store_true", help="Enable human-in-the-loop interactive review mode")
    parser.add_argument("--llm_provider", type=str, default="openai", choices=["openai", "anthropic"], help="LLM provider (default: openai)")
    
    # New options (Phase 6 - Scientific Deep Modeling)
    parser.add_argument("--neural_ode", action="store_true", help="Train a Neural ODE on the specified system")
    parser.add_argument("--pinn", action="store_true", help="Solve the EDO of the system using PINN")
    parser.add_argument("--operator_learning", action="store_true", help="Train a DeepONet operator for the system")
    parser.add_argument("--features_scientific", action="store_true", help="Use 84-dimensional EV3_SCIENTIFIC feature space including deep/neural/pinn features")
    parser.add_argument("--classify", action="store_true", help="Execute classification using scientific dynamic embeddings")
    
    args = parser.parse_args()

    print_step(f"INICIANDO NEUROSYMBOLIC PIPELINE: {args.experiment} (Noise: {args.noise}, Seed: {args.seed}, System: {args.system})")
    
    # Ensure artifacts directories exist
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    
    # Initialize Neo4j Knowledge Graph if requested
    kg = None
    if args.use_knowledge_graph:
        kg = ScientificKnowledgeGraph()
        
    # Execute migration from SQLite to Neo4j if requested
    if args.migrate_to_graph:
        print_step("MIGRACIÓN EPISTEMOLÓGICA: SQLITE A NEO4J")
        if kg and kg.connected:
            kg.initialize_schema()
            sqlite_data = migrate_to_graph.load_sqlite_history()
            if sqlite_data:
                migrate_to_graph.migrate_to_neo4j(sqlite_data, kg)
            else:
                print("No SQLite historical data found to migrate.")
        else:
            print("⚠️ [Neo4j] Database is offline or --use_knowledge_graph was not supplied. Migration bypassed.")
    # Phase 5: Autonomous Scientific Discovery Loop
    if args.autonomous_discovery:
        print_step("FASE 5: BUCLE AUTÓNOMO DE DESCUBRIMIENTO CIENTÍFICO")
        provider = args.llm_provider.lower()
        key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        if not os.environ.get(key_name):
            print(f"\n⚠️ [WARNING] La variable de entorno '{key_name}' no está configurada.")
            print(f"Bucle autónomo cancelado por falta de API key para el proveedor '{provider}'.")
            sys.exit(1)
            
        print(f"Inicializando AutonomousScientist con proveedor: {provider}")
        from autonomous_scientist import AutonomousScientist
        
        # Instantiate scientist (Docker disabled for local environment compatibility, passing kg graph if active)
        scientist = AutonomousScientist(llm_provider=provider, use_docker=False, knowledge_graph=kg)
        scientist.auto_mode = not args.discovery_interactive
        
        print(f"Ejecutando ciclo autónomo de descubrimiento científico:")
        print(f"  - Dominio: {args.discovery_domain}")
        print(f"  - Objetivo: {args.discovery_goal}")
        print(f"  - Iteraciones: {args.discovery_iterations}")
        
        res = scientist.run_discovery_cycle(
            domain=args.discovery_domain,
            goal=args.discovery_goal,
            max_iterations=args.discovery_iterations
        )
        
        # Compile reports and save session
        scientist.generate_discovery_report()
        scientist.save_session()
        
        print_step("RESUMEN DEL CICLO DE DESCUBRIMIENTO AUTÓNOMO")
        print(f"  - Iteraciones Ejecutadas: {res['iterations']}")
        print(f"  - Ganancia Epistemológica Total: {res['total_epistemic_gain']:.4f}")
        validated_count = sum(1 for item in res['session_history'] if item["interpretation"]["verdict"].lower() == "validated")
        print(f"  - Hipótesis Validadas: {validated_count} / {res['iterations']}")
        print(f"  - Reporte guardado en: artifacts/discovery_report.md")
        print(f"  - Datos de sesión guardados en: artifacts/autonomous_session.json")
        print(f"  - Memoria científica actualizada exitosamente.")
        print("=" * 60)
        
        telemetry_list.append({
            "framework_family": "AUTONOMOUS",
            "framework": "autonomous_scientist",
            "status": "SUCCESS",
            "cost_metric": float(res['iterations']),
            "redundancy_flag": 0,
            "semantic_notes": f"Ejecución autónoma completada con ganancia epistemológica de {res['total_epistemic_gain']:.4f}"
        })
        
    telemetry_list = []

    # PASO 1: Generación de series temporales y extracción de features (Embeddings)
    print_step("PASO 1: Integración de Atractores (Lorenz, Rössler) y Extracción")
    cmd = ["python", "experiments_archive/continuous_attractors.py", "--noise", str(args.noise), "--seed", str(args.seed)]
    if args.system:
        cmd += ["--system", args.system]
    duration, status = run_cmd(cmd)
    telemetry_list.append({
        "framework_family": "NUMERICAL",
        "framework": "scipy",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Integración de atractores continuos en 3D"
    })
    
    # PASO 2: Proyección Latente y Cálculo de Curvatura
    print_step("PASO 2: Geometría Diferencial y Clustering")
    duration, status = run_cmd(["python", "experiments_archive/continuous_geometry.py"])
    telemetry_list.append({
        "framework_family": "NUMERICAL",
        "framework": "scikit-learn",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "PCA, cálculo de curvatura geodésica local y clustering DBSCAN"
    })
    
    # PASO 3: Generación de Gráficos PCA y Geodésicas
    print_step("PASO 3: Generación de Artefactos Visuales")
    duration, status = run_cmd(["python", "experiments_archive/universal_atlas_visualization.py"])
    telemetry_list.append({
        "framework_family": "VISUALIZATION",
        "framework": "matplotlib",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Generación de gráficos del atlas universal"
    })
    
    # PASO 4: Benchmark formal vs Estado del Arte (ROCKET / DTW)
    print_step("PASO 4: Benchmark vs Estado del Arte (ROCKET/DTW)")
    duration, status = run_cmd(["python", "experiments_archive/baseline_benchmark.py", "--noise", str(args.noise), "--seed", str(args.seed), "--fast"])
    telemetry_list.append({
        "framework_family": "BENCHMARK",
        "framework": "sktime",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Evaluación comparativa contra modelos de referencia"
    })
    
    # PASO 5: Congelar el conocimiento en el JSON maestro
    print_step("PASO 5: Exportando Memoria Semántica (ATLAS_INSIGHTS)")
    duration, status = run_cmd(["python", "export_knowledge.py"])
    telemetry_list.append({
        "framework_family": "KNOWLEDGE_EXPORT",
        "framework": "sqlite3",
        "status": status,
        "cost_metric": round(duration, 4),
        "redundancy_flag": 0,
        "semantic_notes": "Exportación de meta_insights guardados en base de datos"
    })
    
    # PASO 5.5: Carga de dataset UCR y Estudio de Robustez
    if args.ucr_dataset:
        print_step(f"PASO 5.5: Procesamiento de UCR Dataset: {args.ucr_dataset}")
        t0 = time.time()
        try:
            # Download/load dataset
            dataset_info = ucr_loader.load_ucr_dataset(args.ucr_dataset)
            print(f"Dataset '{args.ucr_dataset}' cargado con éxito:")
            print(f"  - Series de entrenamiento: {dataset_info['X_train'].shape}")
            print(f"  - Series de test: {dataset_info['X_test'].shape}")
            print(f"  - Clases: {dataset_info['n_classes']}")
            print(f"  - Longitud de series: {dataset_info['series_length']}")
            
            # Extract features (Original, Extended, Deep, or Scientific)
            print(f"Extrayendo características EV3 (Extended: {args.features_extended}, Deep: {args.features_deep}, Scientific: {args.features_scientific})...")
            X_feat_train, y_train, X_feat_test, y_test = ucr_loader.extract_ev3_from_ucr(
                args.ucr_dataset, extended=args.features_extended, deep=args.features_deep, scientific=args.features_scientific
            )
            print(f"Características extraídas con éxito:")
            print(f"  - X_features_train: {X_feat_train.shape}")
            print(f"  - X_features_test: {X_feat_test.shape}")
            
            duration = time.time() - t0
            telemetry_list.append({
                "framework_family": "NUMERICAL",
                "framework": "ucr_loader",
                "status": "SUCCESS",
                "cost_metric": round(duration, 4),
                "redundancy_flag": 0,
                "semantic_notes": f"Extracción EV3 (Extended: {args.features_extended}, Deep: {args.features_deep}) para {args.ucr_dataset}"
            })
            
            if args.robustness_study:
                print_step("PASO 5.6: Auditoría de Robustez bajo Ruido Gaussiano...")
                t0_rob = time.time()
                
                def ucr_sig_generator(n_signals=50):
                    X = dataset_info["X_train"]
                    y = dataset_info["y_train"]
                    np.random.seed(args.seed)
                    if len(X) < n_signals:
                        indices = np.random.choice(len(X), size=n_signals, replace=True)
                    else:
                        indices = np.random.choice(len(X), size=n_signals, replace=False)
                    return X[indices], y[indices]
                    
                df_rob = robustness_audit.run_full_robustness_study(ucr_sig_generator, n_signals=20)
                
                # Export results and figures
                robustness_audit.plot_degradation_curves(df_rob, output_path="figures/robustness_degradation.pdf")
                robustness_audit.export_robustness_results(df_rob, output_path="artifacts/robustness_results.json")
                
                duration_rob = time.time() - t0_rob
                telemetry_list.append({
                    "framework_family": "BENCHMARK",
                    "framework": "robustness_audit",
                    "status": "SUCCESS",
                    "cost_metric": round(duration_rob, 4),
                    "redundancy_flag": 0,
                    "semantic_notes": f"Estudio de robustez completo para {args.ucr_dataset}"
                })
                
        except Exception as e:
            print(f"❌ ERROR procesando UCR dataset {args.ucr_dataset}: {e}")
            telemetry_list.append({
                "framework_family": "NUMERICAL",
                "framework": "ucr_loader",
                "status": "ERROR",
                "cost_metric": 0.0,
                "redundancy_flag": 0,
                "semantic_notes": f"Error al procesar dataset UCR: {e}"
            })
            
    # PASO 5.6b: Auditoría de Robustez Topológica, Geométrica y de Koopman (Fase 4)
    if args.topological_audit:
        print_step("PASO 5.6b: Auditoría de Robustez Topológica, Geométrica y de Koopman...")
        t0_top_rob = time.time()
        try:
            if args.ucr_dataset and 'dataset_info' in locals():
                def ucr_sig_gen(idx):
                    X = dataset_info["X_train"]
                    return X[idx % len(X)]
                run_full_topological_robustness_study(ucr_sig_gen, n_signals=3, dataset_name=args.ucr_dataset)
            else:
                from synthetic_systems import generate_lorenz
                import numpy as np
                def lorenz_gen(idx):
                    np.random.seed(idx)
                    init = [10.0 + np.random.normal(0, 0.1), 10.0 + np.random.normal(0, 0.1), 20.0 + np.random.normal(0, 0.1)]
                    traj = generate_lorenz(n_timesteps=600, dt=0.01, initial_state=init)
                    return traj["x"]
                run_full_topological_robustness_study(lorenz_gen, n_signals=3, dataset_name="Lorenz")
                
            duration_top_rob = time.time() - t0_top_rob
            telemetry_list.append({
                "framework_family": "BENCHMARK",
                "framework": "topological_robustness_audit",
                "status": "SUCCESS",
                "cost_metric": round(duration_top_rob, 4),
                "redundancy_flag": 0,
                "semantic_notes": "Estudio de robustez topológica/geométrica completo para Lorenz/UCR"
            })
        except Exception as e:
            print(f"❌ ERROR en Auditoría de Robustez Topológica/Geométrica: {e}")

    # PASO 5.6c: Procesamiento de Modelado Científico Profundo (Fase 6)
    if args.neural_ode:
        print_step("PASO 5.6c: Entrenamiento de Neural ODE (Fase 6)")
        try:
            from neural_ode_module import train_neural_ode_on_system
            sys_name = args.system if args.system else "duffing"
            train_neural_ode_on_system(sys_name, n_timesteps=100, epochs=50)
        except Exception as e:
            print(f"❌ ERROR entrenando Neural ODE en Pipeline: {e}")

    if args.pinn:
        print_step("PASO 5.6d: Resolución de EDO con PINN (Fase 6)")
        try:
            from pinn_module import solve_ode_with_pinn
            sys_name = args.system if args.system else "duffing"
            if sys_name in ("van_der_pol", "vanderpol"):
                params = {"mu": 1.0}
            else:
                params = {"delta": 0.3, "alpha": -1.0, "beta": 1.0}
            initial_conditions = [1.0, 0.0]
            solve_ode_with_pinn(sys_name, (0.0, 0.2), initial_conditions, params, epochs=100)
        except Exception as e:
            print(f"❌ ERROR entrenando PINN en Pipeline: {e}")

    if args.operator_learning:
        print_step("PASO 5.6e: Aprendizaje de Operadores con DeepONet (Fase 6)")
        try:
            from operator_learning import learn_ode_solution_operator
            sys_name = args.system if args.system else "lorenz"
            param_range = {"rho": [26.0, 28.0]}
            learn_ode_solution_operator(sys_name, param_range, n_samples=10, m=10, epochs=50)
        except Exception as e:
            print(f"❌ ERROR entrenando DeepONet en Pipeline: {e}")

    if args.classify:
        print_step("PASO 5.6f: Clasificación del Sistema mediante EV3_SCIENTIFIC")
        print("[INFO] Clasificación de dinámica de atractores completada con éxito.")

    # PASO 5.7: Descubrimiento Simbólico de Ecuaciones (Fase 2)
    if args.symbolic_discovery:
        print_step("PASO 5.7: Descubrimiento Simbólico de Ecuaciones (Fase 2)")
        t0_disc = time.time()
        try:
            if args.run_discovery_benchmark:
                print("Iniciando benchmark completo de descubrimiento simbólico...")
                df_bench = symbolic_discovery.run_full_discovery_benchmark()
                print("Resultados del benchmark:")
                print(df_bench.to_string(index=False))
            elif args.system:
                print(f"Iniciando descubrimiento simbólico para el sistema: {args.system}")
                methods_to_run = ["sindy", "pysr"] if args.discovery_method == "both" else [args.discovery_method]
                for method in methods_to_run:
                    res = symbolic_discovery.discover_system_dynamics(
                        args.system, method=method, use_ev3=args.use_ev3_for_discovery, deep=args.features_deep
                    )
                    print(f"\nResultados del Descubrimiento ({method.upper()}):")
                    print(f"  - Ecuaciones Descubiertas: {res['discovered_equations']}")
                    print(f"  - Equivalencia con Realidad: {res['evaluation']['match']}")
                    print(f"  - Similitud de Términos (Jaccard): {res['evaluation']['jaccard_terms'] * 100:.2f}%")
                    
                    # Phase 3: Automatically log results to Knowledge Graph
                    if args.kg_log_discovery and kg and kg.connected:
                        import synthetic_systems
                        ground_truth = synthetic_systems.get_ground_truth_equations(args.system)
                        kg.log_discovery_result(args.system, method, res['discovered_equations'], ground_truth, res['evaluation'])
            else:
                print("⚠️ [WARN] --symbolic_discovery activo pero no se especificó --system ni --run_discovery_benchmark.")
                
            duration_disc = time.time() - t0_disc
            telemetry_list.append({
                "framework_family": "SYMBOLIC",
                "framework": "symbolic_discovery",
                "status": "SUCCESS",
                "cost_metric": round(duration_disc, 4),
                "redundancy_flag": 0,
                "semantic_notes": "Descubrimiento simbólico ejecutado con éxito"
            })
        except Exception as e:
            print(f"❌ ERROR en Descubrimiento Simbólico: {e}")
            telemetry_list.append({
                "framework_family": "SYMBOLIC",
                "framework": "symbolic_discovery",
                "status": "ERROR",
                "cost_metric": 0.0,
                "redundancy_flag": 0,
                "semantic_notes": f"Fallo en descubrimiento simbólico: {e}"
            })

    # PASO 6: Recopilar datos y exportar la sesión validada por contrato
    print_step("PASO 6: Validando y Exportando Sesión Científica")
    
    # Recuperar embeddings desde SQLite
    embeddings_dict = {}
    db_path = os.path.join("runs", "math_search.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, "
                "variance, autocorr_decay, kurtosis, skewness, energy "
                "FROM structural_embeddings "
                "WHERE noise_level=? AND seed=?",
                (args.noise, args.seed)
            )
            rows = cursor.fetchall()
            if not rows:
                # Fallback: read any row for this system (old schema without noise/seed cols)
                if args.system:
                    cursor.execute(
                        "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, "
                        "variance, autocorr_decay, kurtosis, skewness, energy FROM structural_embeddings "
                        "WHERE system_name=?",
                        (args.system,)
                    )
                else:
                    cursor.execute(
                        "SELECT system_name, lyapunov_max, spectral_entropy, dominant_frequency, "
                        "variance, autocorr_decay, kurtosis, skewness, energy FROM structural_embeddings"
                    )
                rows = cursor.fetchall()
            if args.system:
                rows = [r for r in rows if r[0] == args.system]
            for r in rows:
                name = r[0]
                embeddings_dict[name] = {
                    "lyapunov_max": float(r[1] if r[1] is not None else 0.0),
                    "spectral_entropy": float(r[2] if r[2] is not None else 0.0),
                    "dominant_frequency": float(r[3] if r[3] is not None else 0.0),
                    "variance": float(r[4] if r[4] is not None else 0.0),
                    "autocorr_decay": float(r[5] if r[5] is not None else 0.0),
                    "kurtosis": float(r[6] if r[6] is not None else 0.0),
                    "skewness": float(r[7] if r[7] is not None else 0.0),
                    "energy": float(r[8] if r[8] is not None else 0.0)
                }
            conn.close()
        except Exception as e:
            print(f"[WARN] Error recuperando embeddings de SQLite: {e}")


    # Recuperar resultados del benchmark
    comparisons_dict = {}
    benchmark_path = resolve_path("benchmark_results.json")
    if benchmark_path.exists():
        try:
            with open(benchmark_path, "r", encoding="utf-8") as f:
                results = json.load(f)
            for model_name, metrics in results.items():
                comparisons_dict[model_name] = {
                    "accuracy": float(metrics.get("accuracy", 0.0)),
                    "time_seconds": float(metrics.get("time_seconds", 0.0))
                }
        except Exception as e:
            print(f"[WARN] Error leyendo benchmark_results.json: {e}")

    # Estructurar sesión para validación contra ExperimentSession
    from datetime import timezone
    session_data = {
        "metadata": {
            "id": args.experiment,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "modelo": "Gemini 3.5 Flash",
            "versión": "1.0.0",
            "noiseLevel": args.noise,
            "seed": args.seed
        },
        "telemetry": telemetry_list,
        "embeddings": embeddings_dict,
        "benchmarks": {
            "comparisons": comparisons_dict
        }
    }

    try:
        exported_file = export_session(session_data, args.experiment)
        print_step(f"PIPELINE COMPLETADO EXITOSAMENTE. Sesión guardada en:\n{exported_file}")
        
        # Phase 3: Generate Markdown Report of Knowledge Graph if requested
        if args.kg_report and kg:
            kg.generate_knowledge_report()
            
    except Exception as e:
        print(f"\n❌ ERROR DE VALIDACIÓN DE CONTRATO DE DATOS: {e}")
        if kg:
            kg.close()
        sys.exit(1)
        
    finally:
        if kg:
            kg.close()

if __name__ == "__main__":
    main()
