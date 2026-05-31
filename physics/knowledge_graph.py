import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
from datetime import datetime
import sympy as sp

# Ensure UTF-8 output encoding for Windows terminal
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class ScientificKnowledgeGraph:
    """
    Encapsulates interactions with the Neo4j Graph Database for mathematical
    epistemology, hypotheses, equations, experiments, datasets, and observables.
    """

    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.connected = False

        try:
            from neo4j import GraphDatabase

            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            # Test connectivity immediately
            self.driver.verify_connectivity()
            self.connected = True
            print(f"  [Neo4j CONNECT] Successfully connected to Graph DBMS at {uri}")
        except Exception as e:
            self.connected = False
            print(
                f"  [Neo4j WARNING] Could not connect to Neo4j database ({e}). "
                "Graph operations will be bypassed gracefully."
            )

    def close(self):
        """Closes the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.connected = False
            print("  [Neo4j CLOSE] Driver connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ─────────────────────────────────────────────────────────────────────────────
    # TRANSACTION HELPERS
    # ─────────────────────────────────────────────────────────────────────────────

    def _execute_write(self, query, **kwargs):
        """Executes a write query within a transaction."""
        if not self.connected:
            return None
        try:
            with self.driver.session() as session:
                return session.execute_write(lambda tx: tx.run(query, **kwargs).data())
        except Exception as e:
            print(f"  [Neo4j WRITE ERROR] Query failed: {query} | Error: {e}")
            return None

    def _execute_read(self, query, **kwargs):
        """Executes a read query within a transaction."""
        if not self.connected:
            return []
        try:
            with self.driver.session() as session:
                return session.execute_read(lambda tx: tx.run(query, **kwargs).data())
        except Exception as e:
            print(f"  [Neo4j READ ERROR] Query failed: {query} | Error: {e}")
            return []

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN A: CONFIGURACIÓN INICIAL & ESQUEMA
    # ─────────────────────────────────────────────────────────────────────────────

    def clear_database(self, force=False):
        """
        Deletes all nodes and relationships from the active database.
        Requires explicit confirmation unless force=True.
        """
        if not self.connected:
            print("  [Neo4j OFFLINE] Database clear bypassed.")
            return False

        if not force:
            confirm = input(
                "CAUTION: Are you sure you want to completely WIPE the Graph Database? (y/N): "
            )
            if confirm.strip().lower() != "y":
                print("Clear database aborted.")
                return False

        print("  [Neo4j WIPE] Purging all nodes and relationships...")
        self._execute_write("MATCH (n) DETACH DELETE n")
        return True

    def initialize_schema(self):
        """
        Creates indexes and constraints on primary identifiers.
        """
        if not self.connected:
            print("  [Neo4j OFFLINE] Schema initialization bypassed.")
            return

        print("  [Neo4j SCHEMA] Initializing indexes for primary keys...")

        # In Neo4j 5.x, CREATE INDEX FOR (n:Label) ON (n.property) is standard.
        index_queries = [
            "CREATE INDEX hypothesis_id_idx IF NOT EXISTS FOR (n:Hypothesis) ON (n.id)",
            "CREATE INDEX equation_id_idx IF NOT EXISTS FOR (n:Equation) ON (n.id)",
            "CREATE INDEX experiment_id_idx IF NOT EXISTS FOR (n:Experiment) ON (n.id)",
            "CREATE INDEX observable_id_idx IF NOT EXISTS FOR (n:Observable) ON (n.id)",
            "CREATE INDEX dataset_id_idx IF NOT EXISTS FOR (n:Dataset) ON (n.id)",
        ]

        for query in index_queries:
            self._execute_write(query)

        print("  [Neo4j SCHEMA] Schema indexes configured successfully.")

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN B: NODE FACTORIES
    # ─────────────────────────────────────────────────────────────────────────────

    def create_hypothesis(self, hypothesis_id, text, confidence, state="pending"):
        """
        Idempotently merges a Hypothesis node into the graph.
        """
        query = """
        MERGE (h:Hypothesis {id: $id})
        ON CREATE SET h.text = $text, h.confidence = $confidence, h.state = $state, h.timestamp = $timestamp
        ON MATCH SET h.text = $text, h.confidence = $confidence, h.state = $state
        RETURN h
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            id=hypothesis_id,
            text=text,
            confidence=float(confidence),
            state=state,
            timestamp=timestamp,
        )

    def create_equation(self, equation_id, latex, sympy_str, variables, params):
        """
        Idempotently merges an Equation node into the graph.
        """
        query = """
        MERGE (e:Equation {id: $id})
        ON CREATE SET e.latex = $latex, e.sympy_str = $sympy_str, e.variables = $variables, e.params = $params, e.timestamp = $timestamp
        ON MATCH SET e.latex = $latex, e.sympy_str = $sympy_str, e.variables = $variables, e.params = $params
        RETURN e
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            id=equation_id,
            latex=latex,
            sympy_str=sympy_str,
            variables=list(variables),
            params=list(params),
            timestamp=timestamp,
        )

    def create_experiment(self, experiment_id, description, dataset_name, method):
        """
        Idempotently merges an Experiment node into the graph.
        """
        query = """
        MERGE (ex:Experiment {id: $id})
        ON CREATE SET ex.description = $description, ex.dataset_name = $dataset_name, ex.method = $method, ex.timestamp = $timestamp
        ON MATCH SET ex.description = $description, ex.dataset_name = $dataset_name, ex.method = $method
        RETURN ex
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            id=experiment_id,
            description=description,
            dataset_name=dataset_name,
            method=method,
            timestamp=timestamp,
        )

    def create_dataset(self, dataset_id, name, n_samples, n_features, domain):
        """
        Idempotently merges a Dataset node into the graph.
        """
        query = """
        MERGE (d:Dataset {id: $id})
        ON CREATE SET d.name = $name, d.n_samples = $n_samples, d.n_features = $n_features, d.domain = $domain, d.timestamp = $timestamp
        ON MATCH SET d.name = $name, d.n_samples = $n_samples, d.n_features = $n_features, d.domain = $domain
        RETURN d
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            id=dataset_id,
            name=name,
            n_samples=int(n_samples),
            n_features=int(n_features),
            domain=domain,
            timestamp=timestamp,
        )

    def create_observable(self, observable_id, name, type, description=""):
        """
        Idempotently merges an Observable node into the graph.
        """
        query = """
        MERGE (o:Observable {id: $id})
        ON CREATE SET o.name = $name, o.type = $type, o.description = $description, o.timestamp = $timestamp
        ON MATCH SET o.name = $name, o.type = $type, o.description = $description
        RETURN o
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            id=observable_id,
            name=name,
            type=type,
            description=description,
            timestamp=timestamp,
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN C: RELATIONSHIP FACTORIES
    # ─────────────────────────────────────────────────────────────────────────────

    def relate_hypothesis_to_equation(
        self, hypothesis_id, equation_id, relationship="DERIVES"
    ):
        """
        Creates a directed relationship from a Hypothesis to an Equation.
        """
        allowed = ["DERIVES", "ASSUMES", "PREDICTS", "GENERALIZES"]
        rel_type = (
            relationship.upper() if relationship.upper() in allowed else "DERIVES"
        )

        query = f"""
        MATCH (h:Hypothesis {{id: $h_id}}), (e:Equation {{id: $e_id}})
        MERGE (h)-[r:{rel_type}]->(e)
        RETURN r
        """
        return self._execute_write(query, h_id=hypothesis_id, e_id=equation_id)

    def relate_experiment_to_hypothesis(self, experiment_id, hypothesis_id, outcome):
        """
        Creates an EVALUATES relationship with an outcome property.
        """
        allowed_outcomes = ["VALIDATED", "REJECTED", "INCONCLUSIVE"]
        out_val = (
            outcome.upper() if outcome.upper() in allowed_outcomes else "INCONCLUSIVE"
        )

        query = """
        MATCH (ex:Experiment {id: $ex_id}), (h:Hypothesis {id: $h_id})
        MERGE (ex)-[r:EVALUATES]->(h)
        SET r.outcome = $outcome, r.timestamp = $timestamp
        RETURN r
        """
        timestamp = datetime.now().isoformat()
        return self._execute_write(
            query,
            ex_id=experiment_id,
            h_id=hypothesis_id,
            outcome=out_val,
            timestamp=timestamp,
        )

    def relate_equation_to_observable(self, equation_id, observable_id, role):
        """
        Creates a DEPENDS_ON relationship between an Equation and an Observable.
        """
        allowed_roles = ["INPUT", "OUTPUT"]
        role_val = role.upper() if role.upper() in allowed_roles else "INPUT"

        query = """
        MATCH (e:Equation {id: $e_id}), (o:Observable {id: $o_id})
        MERGE (e)-[r:DEPENDS_ON]->(o)
        SET r.role = $role
        RETURN r
        """
        return self._execute_write(
            query, e_id=equation_id, o_id=observable_id, role=role_val
        )

    def relate_dataset_to_experiment(self, dataset_id, experiment_id):
        """
        Creates a USED_IN relationship from a Dataset to an Experiment.
        """
        query = """
        MATCH (d:Dataset {id: $d_id}), (ex:Experiment {id: $ex_id})
        MERGE (d)-[r:USED_IN]->(ex)
        RETURN r
        """
        return self._execute_write(query, d_id=dataset_id, ex_id=experiment_id)

    def relate_hypothesis_refinement(self, next_id, prev_id):
        """
        Creates a REFINES relationship from a newer Hypothesis to an older one.
        """
        query = """
        MATCH (h_next:Hypothesis {id: $next_id}), (h_prev:Hypothesis {id: $prev_id})
        MERGE (h_next)-[r:REFINES]->(h_prev)
        RETURN r
        """
        return self._execute_write(query, next_id=next_id, prev_id=prev_id)

    def relate_hypotheses_contradiction(self, source_id, target_id, evidence="", score=0.0):
        """
        Creates a CONTRADICTS relationship between two Hypothesis nodes.
        Stores only metadata; heavy evidence artifacts should live on disk.
        """
        query = """
        MATCH (h1:Hypothesis {id: $source_id}), (h2:Hypothesis {id: $target_id})
        MERGE (h1)-[r:CONTRADICTS]->(h2)
        SET r.evidence = $evidence, r.score = $score, r.timestamp = $timestamp
        RETURN r
        """
        return self._execute_write(
            query,
            source_id=source_id,
            target_id=target_id,
            evidence=evidence,
            score=float(score),
            timestamp=datetime.now().isoformat(),
        )

    def get_scientific_entities(self):
        """
        Returns scientific graph entities that can be embedded.
        Vectors are intentionally not stored in Neo4j; only hashes and paths.
        """
        query = """
        MATCH (n)
        WHERE any(label IN labels(n) WHERE label IN ['Hypothesis','Equation','Experiment','Dataset','Observable'])
        RETURN labels(n)[0] AS label, properties(n) AS props
        """
        rows = self._execute_read(query)
        entities = []
        for row in rows:
            props = dict(row.get("props") or {})
            entity_id = props.get("id")
            if entity_id:
                entities.append({"id": entity_id, "label": row.get("label"), "properties": props})
        return entities

    def update_entity_embedding_metadata(self, label, entity_id, embedding_hash, embedding_path, metadata=None):
        """
        Stores embedding metadata on an existing node. The vector itself stays on disk.
        """
        safe_label = label if label in {"Hypothesis", "Equation", "Experiment", "Dataset", "Observable"} else "Hypothesis"
        query = f"""
        MATCH (n:{safe_label} {{id: $id}})
        SET n.embedding_hash = $embedding_hash,
            n.embedding_path = $embedding_path,
            n.embedding_metadata = $metadata,
            n.embedding_updated_at = $timestamp
        RETURN n
        """
        return self._execute_write(
            query,
            id=entity_id,
            embedding_hash=embedding_hash,
            embedding_path=embedding_path,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
        )

    def get_knowledge_evolution_edges(self, root_hypothesis_id):
        """
        Traces REFINES, DERIVES and CONTRADICTS relations around a root hypothesis.
        """
        query = """
        MATCH (root:Hypothesis {id: $root_id})
        OPTIONAL MATCH p=(root)-[:REFINES|DERIVES|CONTRADICTS*0..5]-(n)
        UNWIND relationships(p) AS rel
        RETURN startNode(rel).id AS source, endNode(rel).id AS target,
               type(rel) AS type, properties(rel) AS props
        """
        rows = self._execute_read(query, root_id=root_hypothesis_id)
        return [
            {
                "source": row.get("source"),
                "target": row.get("target"),
                "type": row.get("type"),
                "properties": row.get("props") or {},
            }
            for row in rows
            if row.get("source") and row.get("target")
        ]

    def get_experiment_records(self):
        """
        Returns Experiment nodes with related dataset/hypothesis metadata for meta-learning.
        """
        query = """
        MATCH (ex:Experiment)
        OPTIONAL MATCH (d:Dataset)-[:USED_IN]->(ex)
        OPTIONAL MATCH (ex)-[ev:EVALUATES]->(h:Hypothesis)
        RETURN properties(ex) AS experiment,
               properties(d) AS dataset,
               properties(h) AS hypothesis,
               properties(ev) AS evaluation
        """
        rows = self._execute_read(query)
        return [
            {
                "experiment": row.get("experiment") or {},
                "dataset": row.get("dataset") or {},
                "hypothesis": row.get("hypothesis") or {},
                "evaluation": row.get("evaluation") or {},
            }
            for row in rows
        ]

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN D: EPISTEMOLOGICAL QUERIES & ANALYTICS
    # ─────────────────────────────────────────────────────────────────────────────

    def get_all_hypotheses(self, state=None):
        """
        Returns all stored Hypotheses, optionally filtered by state.
        """
        if state:
            query = "MATCH (h:Hypothesis) WHERE h.state = $state RETURN h"
            return [r["h"] for r in self._execute_read(query, state=state)]
        else:
            query = "MATCH (h:Hypothesis) RETURN h"
            return [r["h"] for r in self._execute_read(query)]

    def get_equations_for_hypothesis(self, hypothesis_id):
        """
        Traverses nodes to return all Equations associated with a Hypothesis.
        """
        query = """
        MATCH (h:Hypothesis {id: $h_id})-[:DERIVES|ASSUMES|PREDICTS|GENERALIZES]->(e:Equation)
        RETURN e
        """
        return [r["e"] for r in self._execute_read(query, h_id=hypothesis_id)]

    def get_experiments_for_hypothesis(self, hypothesis_id):
        """
        Returns all Experiments evaluating a specific Hypothesis.
        """
        query = """
        MATCH (ex:Experiment)-[r:EVALUATES]->(h:Hypothesis {id: $h_id})
        RETURN ex, r.outcome AS outcome
        """
        rows = self._execute_read(query, h_id=hypothesis_id)
        return [{"experiment": r["ex"], "outcome": r["outcome"]} for r in rows]

    def get_hypothesis_lineage(self, hypothesis_id):
        """
        Traces the historical ancestry tree of a refined Hypothesis.
        Returns a list of connected Hypothesis nodes.
        """
        query = """
        MATCH (h:Hypothesis {id: $h_id})
        OPTIONAL MATCH p=(h)-[:REFINES*1..]->(ancestor:Hypothesis)
        RETURN h, nodes(p) AS lineage_nodes
        """
        rows = self._execute_read(query, h_id=hypothesis_id)
        if not rows:
            return []

        lineage = []
        # Add root hypothesis
        lineage.append(rows[0]["h"])

        # Add ancestors if path exists
        if rows[0]["lineage_nodes"]:
            for node in rows[0]["lineage_nodes"]:
                if node and node != rows[0]["h"] and node not in lineage:
                    lineage.append(node)

        return lineage

    def query_scientific_question(self, question_text):
        """
        Performs a semantic keyword regular-expression match on scientific nodes,
        returning a structured summary.
        """
        words = [w.strip("?,.()[]").lower() for w in question_text.split()]
        stopwords = {
            "what",
            "is",
            "the",
            "a",
            "an",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "about",
            "by",
            "system",
            "equations",
            "discovered",
        }
        keywords = [w for w in words if w and w not in stopwords and len(w) > 2]

        summary = {
            "query_keywords": keywords,
            "hypotheses": [],
            "equations": [],
            "observables": [],
        }

        if not self.connected or not keywords:
            return summary

        # Match hypotheses containing keywords
        hyp_query = """
        MATCH (h:Hypothesis)
        WHERE any(kw IN $keywords WHERE toLower(h.text) CONTAINS kw)
        RETURN h
        """
        summary["hypotheses"] = [
            r["h"] for r in self._execute_read(hyp_query, keywords=keywords)
        ]

        # Match equations containing keywords
        eq_query = """
        MATCH (e:Equation)
        WHERE any(kw IN $keywords WHERE toLower(e.latex) CONTAINS kw OR toLower(e.sympy_str) CONTAINS kw)
        RETURN e
        """
        summary["equations"] = [
            r["e"] for r in self._execute_read(eq_query, keywords=keywords)
        ]

        # Match observables containing keywords
        obs_query = """
        MATCH (o:Observable)
        WHERE any(kw IN $keywords WHERE toLower(o.name) CONTAINS kw OR toLower(o.description) CONTAINS kw)
        RETURN o
        """
        summary["observables"] = [
            r["o"] for r in self._execute_read(obs_query, keywords=keywords)
        ]

        return summary

    def export_to_networkx(self):
        """
        Exports the entire knowledge graph database to a networkx.DiGraph object.
        """
        import networkx as nx

        G = nx.DiGraph()

        if not self.connected:
            return G

        # Fetch all nodes
        nodes_query = "MATCH (n) RETURN labels(n)[0] AS label, properties(n) AS props"
        nodes_data = self._execute_read(nodes_query)
        for row in nodes_data:
            props = row["props"]
            node_id = props.get("id")
            if node_id:
                G.add_node(node_id, label=row["label"], **props)

        # Fetch all relationships
        rels_query = "MATCH (n)-[r]->(m) RETURN n.id AS start_id, m.id AS end_id, type(r) AS rel_type, properties(r) AS rel_props"
        rels_data = self._execute_read(rels_query)
        for row in rels_data:
            start = row["start_id"]
            end = row["end_id"]
            if start and end:
                G.add_edge(start, end, type=row["rel_type"], **row["rel_props"])

        return G

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN E: EXPERIMENT LOGGING BRIDGE
    # ─────────────────────────────────────────────────────────────────────────────

    def log_discovery_result(
        self, system_name, method, discovered_eqs, ground_truth, evaluation_result
    ):
        """
        Translates a symbolic discovery trial into a set of connected epistemological nodes.
        """
        if not self.connected:
            print("  [Neo4j OFFLINE] Logging discovery result bypassed.")
            return {}

        print(
            f"  [Neo4j LOGGING] Storing discovery metadata for {system_name} ({method})..."
        )

        # Determine deterministic IDs
        hypothesis_id = f"hyp_{system_name}_{method}"
        experiment_id = f"exp_{system_name}_{method}"
        dataset_id = f"dataset_{system_name}"

        # 1. Create Dataset
        n_samples = 5000 if system_name != "logistic" else 2000
        n_features = len(discovered_eqs)
        self.create_dataset(
            dataset_id,
            name=f"Synthetic {system_name} Trajectory",
            n_samples=n_samples,
            n_features=n_features,
            domain="Chaos Physics",
        )

        # 2. Create Experiment
        self.create_experiment(
            experiment_id,
            description=f"Symbolic discovery on {system_name} using {method}",
            dataset_name=f"Synthetic {system_name} Trajectory",
            method=method,
        )
        self.relate_dataset_to_experiment(dataset_id, experiment_id)

        # 3. Create Hypothesis
        hyp_text = f"El sistema {system_name} está gobernado por la(s) ecuación(es) descubierta(s) mediante {method}."
        match = bool(evaluation_result.get("match", False))
        state = "validated" if match else "rejected"
        confidence = float(evaluation_result.get("jaccard_terms", 0.5))
        self.create_hypothesis(
            hypothesis_id, text=hyp_text, confidence=confidence, state=state
        )

        # 4. Create Equations and Relate to Hypothesis & Observables
        equation_ids = []
        for var_name, eq_str in discovered_eqs.items():
            eq_id = f"eq_{system_name}_{method}_{var_name}"
            equation_ids.append(eq_id)

            # Create Equation Node
            variables = ground_truth.get("variables", [var_name])
            params = ground_truth.get("params_names", [])
            self.create_equation(
                eq_id,
                latex=eq_str,
                sympy_str=eq_str,
                variables=variables,
                params=params,
            )

            # Relate Hypothesis to Equation
            self.relate_hypothesis_to_equation(
                hypothesis_id, eq_id, relationship="DERIVES"
            )

            # Create Observable Nodes and Relate
            obs_id = f"obs_{var_name}"
            self.create_observable(
                obs_id,
                name=var_name,
                type="State Variable",
                description=f"Coordinate {var_name} of the {system_name} dynamical system.",
            )
            self.relate_equation_to_observable(eq_id, obs_id, role="OUTPUT")

        # 5. Relate Experiment to Hypothesis
        outcome = "VALIDATED" if match else "REJECTED"
        self.relate_experiment_to_hypothesis(
            experiment_id, hypothesis_id, outcome=outcome
        )

        return {
            "hypothesis_id": hypothesis_id,
            "experiment_id": experiment_id,
            "dataset_id": dataset_id,
            "equation_ids": equation_ids,
        }

    # ─────────────────────────────────────────────────────────────────────────────
    # SECCIÓN F: EXPORT REPORT GENERATOR
    # ─────────────────────────────────────────────────────────────────────────────

    def generate_knowledge_report(self, output_path="artifacts/knowledge_report.md"):
        """
        Generates a consolidated Markdown knowledge report summarising hypotheses,
        equations, and experiments stored in Neo4j.
        """
        print(f"Generating knowledge graph report at: {output_path}")

        # Ensure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if not self.connected:
            content = """# Epistemological Knowledge Graph Report (Neo4j)

> [!WARNING]
> **Neo4j Offline:**
> The local Neo4j database was offline or inaccessible during this run. Therefore, this report has been populated with local fallback placeholders.

## Database Offline
Unable to query the Graph DBMS. Make sure Neo4j is running locally at `bolt://localhost:7687` with default credentials `neo4j/password`.
"""
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return

        # 1. Fetch Statistics
        tot_hyp = self._execute_read("MATCH (h:Hypothesis) RETURN count(h) AS count")[
            0
        ]["count"]
        tot_eq = self._execute_read("MATCH (e:Equation) RETURN count(e) AS count")[0][
            "count"
        ]
        tot_ex = self._execute_read("MATCH (ex:Experiment) RETURN count(ex) AS count")[
            0
        ]["count"]
        tot_obs = self._execute_read("MATCH (o:Observable) RETURN count(o) AS count")[
            0
        ]["count"]

        # Hypotheses by state
        hyp_states = self._execute_read(
            "MATCH (h:Hypothesis) RETURN h.state AS state, count(h) AS count"
        )
        hyp_state_summary = {r["state"]: r["count"] for r in hyp_states}

        # Equations list
        eqs_list = self._execute_read("MATCH (e:Equation) RETURN e ORDER BY e.id")

        # Experiments and outcomes
        exps_list = self._execute_read("""
        MATCH (ex:Experiment)
        OPTIONAL MATCH (ex)-[r:EVALUATES]->(h:Hypothesis)
        RETURN ex.id AS id, ex.description AS desc, ex.method AS method, r.outcome AS outcome
        ORDER BY ex.id
        """)

        # Observables frequency
        obs_freq = self._execute_read("""
        MATCH (e:Equation)-[r:DEPENDS_ON]->(o:Observable)
        RETURN o.name AS name, o.type AS type, count(r) AS freq
        ORDER BY freq DESC, name
        """)

        # Assemble Markdown
        md = []
        md.append("# Epistemological Knowledge Graph Summary Report")
        md.append(
            f"\n*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        )

        md.append("\n## 1. Graph Summary Statistics")
        md.append("| Entity Type | Total Count |")
        md.append("| :--- | :---: |")
        md.append(f"| :brain: **Hypotheses** | {tot_hyp} |")
        md.append(f"| :symbols: **Equations** | {tot_eq} |")
        md.append(f"| :test_tube: **Experiments** | {tot_ex} |")
        md.append(f"| :eye: **Observables** | {tot_obs} |")

        md.append("\n### Hypotheses by Verification State")
        md.append("| State | Count | Status |")
        md.append("| :--- | :---: | :--- |")
        for state in ["validated", "rejected", "pending", "refined"]:
            cnt = hyp_state_summary.get(state, 0)
            status_icon = (
                "✅ Approved"
                if state == "validated"
                else ("❌ Rejected" if state == "rejected" else "⏳ Awaiting Review")
            )
            md.append(f"| **{state.capitalize()}** | {cnt} | {status_icon} |")

        md.append("\n## 2. Epistemological Hypotheses & Claims")
        hyps_all = self._execute_read("MATCH (h:Hypothesis) RETURN h ORDER BY h.id")
        if hyps_all:
            for idx, r in enumerate(hyps_all):
                h = r["h"]
                state_badge = (
                    "🟢 Validated"
                    if h["state"] == "validated"
                    else ("🔴 Rejected" if h["state"] == "rejected" else "🟡 Pending")
                )
                md.append(f"\n### [{idx+1}] Hypothesis: `{h['id']}`")
                md.append(f"- **Statement**: *\"{h['text']}\"*")
                md.append(f"- **State**: {state_badge}")
                md.append(f"- **Confidence**: `{h['confidence'] * 100:.2f}%`")
                md.append(f"- **Registered**: `{h['timestamp']}`")
        else:
            md.append("\n*(No hypotheses logged in Graph DBMS)*")

        md.append("\n## 3. Discovered Symbolic Equations")
        if eqs_list:
            md.append("| Equation ID | Symbolic Expression | Variables | Parameters |")
            md.append("| :--- | :--- | :--- | :--- |")
            for r in eqs_list:
                e = r["e"]
                vars_str = ", ".join(e["variables"])
                params_str = ", ".join(e["params"]) if e["params"] else "None"
                md.append(
                    f"| `{e['id']}` | **${e['latex']}$** | `{vars_str}` | `{params_str}` |"
                )
        else:
            md.append("\n*(No equations logged in Graph DBMS)*")

        md.append("\n## 4. Scientific Trials & Experiments")
        if exps_list:
            md.append("| Experiment ID | Method | Description | Outcome |")
            md.append("| :--- | :---: | :--- | :---: |")
            for r in exps_list:
                outcome_str = r["outcome"] if r["outcome"] else "INCONCLUSIVE"
                outcome_badge = (
                    "🟩 VALIDATED"
                    if outcome_str == "VALIDATED"
                    else (
                        "🟥 REJECTED"
                        if outcome_str == "REJECTED"
                        else "🟨 INCONCLUSIVE"
                    )
                )
                md.append(
                    f"| `{r['id']}` | `{r['method'].upper()}` | {r['desc']} | {outcome_badge} |"
                )
        else:
            md.append("\n*(No experiments logged in Graph DBMS)*")

        md.append("\n## 5. Frequency of Observables")
        if obs_freq:
            md.append("| Observable Name | Type | Interaction Frequency |")
            md.append("| :--- | :--- | :---: |")
            for r in obs_freq:
                md.append(f"| **{r['name']}** | *{r['type']}* | {r['freq']} |")
        else:
            md.append("\n*(No observables active in the active graph)*")

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        print(f"Successfully generated scientific knowledge report at {output_path}!")
