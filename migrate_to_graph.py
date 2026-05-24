import os
import sqlite3
import json
from knowledge_graph import ScientificKnowledgeGraph

# Ensure UTF-8 output encoding for Windows terminal
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def load_sqlite_history(db_path="runs/math_search.db"):
    """
    Tries to load historical research logs from the local SQLite database.
    Checks multiple possible file locations (including default brain/state.db)
    and dynamically detects existing tables to avoid failures.
    """
    candidate_paths = [
        db_path,
        "brain/state.db",
        "runs/math_search.db",
        "../runs/math_search.db",
    ]
    actual_path = None
    for path in candidate_paths:
        if os.path.isfile(path):
            actual_path = path
            break

    if not actual_path:
        print(
            "  [SQLite BRIDGE] No SQLite database found in candidate paths. Skipping migration."
        )
        return {}

    print(f"  [SQLite BRIDGE] Loading historical data from: {actual_path}")
    conn = sqlite3.connect(actual_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query all tables in the database to understand what schemas are present
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row["name"] for row in cursor.fetchall()]
    print(f"  [SQLite BRIDGE] Found tables: {tables}")

    data = {}

    # Load nodes / experiments
    if "nodes" in tables:
        cursor.execute("SELECT * FROM nodes")
        data["nodes"] = [dict(row) for row in cursor.fetchall()]
    elif "experiments" in tables:
        cursor.execute("SELECT * FROM experiments")
        data["nodes"] = [dict(row) for row in cursor.fetchall()]

    # Load meta_insights / hypotheses
    if "meta_insights" in tables:
        cursor.execute("SELECT * FROM meta_insights")
        data["meta_insights"] = [dict(row) for row in cursor.fetchall()]
    elif "hypotheses" in tables:
        cursor.execute("SELECT * FROM hypotheses")
        data["meta_insights"] = [dict(row) for row in cursor.fetchall()]

    # Load structural_embeddings / features
    if "structural_embeddings" in tables:
        cursor.execute("SELECT * FROM structural_embeddings")
        data["structural_embeddings"] = [dict(row) for row in cursor.fetchall()]
    elif "features" in tables:
        cursor.execute("SELECT * FROM features")
        data["structural_embeddings"] = [dict(row) for row in cursor.fetchall()]

    # Load generated_conjectures
    if "generated_conjectures" in tables:
        cursor.execute("SELECT * FROM generated_conjectures")
        data["generated_conjectures"] = [dict(row) for row in cursor.fetchall()]

    # Load artifacts
    if "artifacts" in tables:
        cursor.execute("SELECT * FROM artifacts")
        data["artifacts"] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return data


def migrate_to_neo4j(sqlite_data, kg: ScientificKnowledgeGraph):
    """
    Iterates over the SQLite historical data and inserts the respective
    entities and relationships inside Neo4j.
    """
    if not kg.connected:
        print("  [Neo4j OFFLINE] Neo4j is offline. Aborting migration.")
        return False

    print("\n" + "=" * 60)
    print("🚀 MIGRATING SQLITE MEMORY TO NEO4J KNOWLEDGE GRAPH")
    print("=" * 60)

    # 1. Create the 15 standard EV3 features as Observable nodes in Neo4j
    ev3_observables = [
        (
            "lyapunov_max",
            "Exponente de Lyapunov máximo",
            "DYNAMICAL_ESTIMATOR",
            "Mide la tasa de divergencia de órbitas adyacentes.",
        ),
        (
            "correlation_dimension",
            "Dimensión de correlación",
            "TOPOLOGICAL_ESTIMATOR",
            "Mide la dimensión fractal de correlación Grassberger-Procaccia.",
        ),
        (
            "recurrence_rate",
            "RQA Recurrence Rate",
            "RECURRENCE_ESTIMATOR",
            "Porcentaje de estados recurrentes en el espacio.",
        ),
        (
            "determinism",
            "RQA Determinism",
            "RECURRENCE_ESTIMATOR",
            "Porcentaje de puntos recurrentes diagonales.",
        ),
        (
            "l_max",
            "RQA Diagonal Line Max Length",
            "RECURRENCE_ESTIMATOR",
            "Longitud máxima de línea diagonal en matriz de recurrencia.",
        ),
        (
            "recurrence_entropy",
            "RQA Shannon Entropy",
            "RECURRENCE_ESTIMATOR",
            "Entropía de la distribución diagonal.",
        ),
        (
            "multiscale_entropy",
            "Entropía multiescala",
            "ENTROPY_ESTIMATOR",
            "Espectro de entropía de muestra a múltiples escalas de tiempo.",
        ),
        (
            "sample_entropy",
            "Entropía de muestra (Sample Entropy)",
            "ENTROPY_ESTIMATOR",
            "Mide la regularidad y complejidad de la serie temporal.",
        ),
        (
            "spectral_entropy",
            "Entropía espectral",
            "SPECTRAL_ESTIMATOR",
            "Entropía de Shannon aplicada a la densidad espectral de potencia.",
        ),
        (
            "dominant_frequency",
            "Frecuencia dominante",
            "SPECTRAL_ESTIMATOR",
            "La frecuencia con mayor amplitud en el espectro.",
        ),
        (
            "variance",
            "Varianza de la señal",
            "STATISTICAL_ESTIMATOR",
            "Dispersión de los valores de la serie temporal.",
        ),
        (
            "autocorr_decay",
            "Decaimiento de autocorrelación",
            "STATISTICAL_ESTIMATOR",
            "Tiempo para que la autocorrelación decaiga a 1/e.",
        ),
        (
            "kurtosis",
            "Curtosis robusta",
            "STATISTICAL_ESTIMATOR",
            "Medida del apuntamiento y colas de la distribución.",
        ),
        (
            "skewness",
            "Asimetría robusta",
            "STATISTICAL_ESTIMATOR",
            "Medida de la asimetría de la distribución.",
        ),
        (
            "energy",
            "Energía total de la señal",
            "STATISTICAL_ESTIMATOR",
            "Suma de los cuadrados de las amplitudes espectrales.",
        ),
    ]

    obs_count = 0
    for obs_id, name, type_val, desc in ev3_observables:
        kg.create_observable(
            f"obs_{obs_id}", name=name, type=type_val, description=desc
        )
        obs_count += 1
    print(f"  [MIGRATE] Created {obs_count} EV3 Observable definition nodes.")

    # 2. Migrate nodes (Experiments)
    nodes = sqlite_data.get("nodes", [])
    node_migrated = 0
    for node in nodes:
        node_id = node.get("id")
        experiment_id = f"exp_node_{node_id}"
        notes = node.get("semantic_notes") or ""
        desc = f"Framework: {node.get('framework')} | Family: {node.get('framework_family')} | Status: {node.get('status')} | Notes: {notes}"
        kg.create_experiment(
            experiment_id,
            description=desc,
            dataset_name="UCR or Synthetic Trajectory",
            method=node.get("framework"),
        )
        node_migrated += 1

        # Connect parent/child relations
        parent_id = node.get("parent_id")
        if parent_id is not None:
            parent_exp_id = f"exp_node_{parent_id}"
            # Custom relation for node hierarchy
            kg._execute_write(
                "MATCH (p:Experiment {id: $parent_id}), (c:Experiment {id: $child_id}) MERGE (p)-[r:PREV_TRIAL]->(c) RETURN r",
                parent_id=parent_exp_id,
                child_id=experiment_id,
            )

        # Connect redundancy if applicable
        if node.get("redundancy_flag") == 1 and node.get("redundant_to_id") is not None:
            red_exp_id = f"exp_node_{node.get('redundant_to_id')}"
            kg._execute_write(
                "MATCH (c:Experiment {id: $child_id}), (r:Experiment {id: $red_id}) MERGE (c)-[rel:REDUNDANT_TO]->(r) RETURN rel",
                child_id=experiment_id,
                red_id=red_exp_id,
            )

    print(f"  [MIGRATE] Migrated {node_migrated} historical experiments/trials.")

    # 3. Migrate structural embeddings (Observations)
    embeddings = sqlite_data.get("structural_embeddings", [])
    emb_migrated = 0
    for emb in embeddings:
        node_id = emb.get("node_id")
        sys_name = emb.get("system_name") or "Unknown"
        experiment_id = f"exp_node_{node_id}"

        # Link to observables if the experiment node exists
        for obs_key, _, _, _ in ev3_observables:
            val = emb.get(obs_key)
            if val is not None:
                query = """
                MATCH (ex:Experiment {id: $ex_id}), (o:Observable {id: $obs_id})
                MERGE (ex)-[r:MEASURED]->(o)
                SET r.value = $val, r.system_name = $sys_name
                RETURN r
                """
                kg._execute_write(
                    query,
                    ex_id=experiment_id,
                    obs_id=f"obs_{obs_key}",
                    val=float(val),
                    sys_name=sys_name,
                )
                emb_migrated += 1

    print(f"  [MIGRATE] Logged {emb_migrated} dynamic observability value links.")

    # 4. Migrate meta_insights & conjectures (Hypotheses)
    insights = sqlite_data.get("meta_insights", [])
    ins_migrated = 0
    for ins in insights:
        ins_id = ins.get("id")
        hypothesis_id = f"hyp_insight_{ins_id}"
        pattern = ins.get("pattern_type")
        strategy = ins.get("recommended_strategy")
        text = f"Meta-Insight: {pattern} | Recommended Strategy: {strategy}"
        confidence = float(ins.get("confidence", 0.5))
        kg.create_hypothesis(
            hypothesis_id, text=text, confidence=confidence, state="validated"
        )
        ins_migrated += 1

        # Relate supporting nodes if they exist in SQLite data
        supp_nodes_str = ins.get("supporting_nodes", "[]")
        try:
            supp_ids = json.loads(supp_nodes_str)
            for node_id in supp_ids:
                kg.relate_experiment_to_hypothesis(
                    f"exp_node_{node_id}", hypothesis_id, outcome="VALIDATED"
                )
        except Exception:
            pass

    conjectures = sqlite_data.get("generated_conjectures", [])
    conj_migrated = 0
    for conj in conjectures:
        conj_id = conj.get("id")
        hypothesis_id = f"hyp_conjecture_{conj_id}"
        text = conj.get("hypothesis_text")
        confidence = float(conj.get("confidence_score", 0.5))
        status = conj.get("status") or "pending"
        state = (
            "validated"
            if status == "validated"
            else ("rejected" if status == "rejected" else "pending")
        )
        kg.create_hypothesis(
            hypothesis_id, text=text, confidence=confidence, state=state
        )
        conj_migrated += 1

    print(
        f"  [MIGRATE] Created {ins_migrated + conj_migrated} validated heuristics & conjectures."
    )
    print("=" * 60 + "\n")
    return True


def run_migration():
    """
    Orchestrates the entire migration workflow.
    """
    # Create the Neo4j Knowledge Graph connector
    with ScientificKnowledgeGraph() as kg:
        if not kg.connected:
            print(
                "  [SQLite BRIDGE] Neo4j is offline. Skipping database migration bridge."
            )
            return

        kg.initialize_schema()

        # Load SQLite historical datasets
        sqlite_data = load_sqlite_history()

        if not sqlite_data:
            print("  [SQLite BRIDGE] No historical data loaded. Skipping migration.")
            return

        migrate_to_neo4j(sqlite_data, kg)
        print("  [SQLite BRIDGE] Epistemological migration completed successfully!")


if __name__ == "__main__":
    run_migration()
