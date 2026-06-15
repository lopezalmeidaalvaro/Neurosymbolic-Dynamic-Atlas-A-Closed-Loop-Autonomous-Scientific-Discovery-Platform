import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class FormalKnowledgeBase:
    def __init__(
        self, db_path: str | Path = "mathematics/artifacts/knowledge.db"
    ) -> None:
        self.db_path = Path(db_path)
        # Ensure parent directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Enforce foreign key constraints in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            conn.close()
            raise
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            with conn:
                # Create theorems table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS theorems (
                        id TEXT PRIMARY KEY,
                        domain TEXT NOT NULL,
                        schema_version TEXT NOT NULL,
                        statement TEXT NOT NULL,
                        lean_proof TEXT NOT NULL,
                        proof_hash TEXT NOT NULL,
                        verified BOOLEAN NOT NULL CHECK (verified IN (0, 1)),
                        created_at TEXT NOT NULL,
                        provenance TEXT
                    );
                    """)

                # Dynamic schema migration for older databases
                cursor = conn.execute("PRAGMA table_info(theorems);")
                columns = [r["name"] for r in cursor.fetchall()]
                if columns and "provenance" not in columns:
                    conn.execute("ALTER TABLE theorems ADD COLUMN provenance TEXT;")

                # Create dependencies table with foreign key ON DELETE CASCADE
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS theorem_dependencies (
                        theorem_id TEXT NOT NULL,
                        dependency_id TEXT NOT NULL,
                        PRIMARY KEY (theorem_id, dependency_id),
                        FOREIGN KEY (theorem_id) REFERENCES theorems(id) ON DELETE CASCADE
                    );
                    """)
                # Index dependencies for fast cascade updates/checks
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_theorem_dependencies_dep 
                    ON theorem_dependencies(dependency_id);
                    """)

                # Create mcts_runs table for reinforcement learning search telemetry
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS mcts_runs (
                        run_id TEXT PRIMARY KEY,
                        theorem_id TEXT NOT NULL,
                        total_simulations INTEGER NOT NULL,
                        success BOOLEAN NOT NULL CHECK (success IN (0, 1)),
                        nodes_explored INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    """)

                # Create proof_trajectories table for DPO dataset generation
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS proof_trajectories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id TEXT NOT NULL,
                        state_context TEXT NOT NULL,
                        tactic_applied TEXT NOT NULL,
                        status TEXT NOT NULL,
                        reward REAL NOT NULL,
                        created_at TEXT NOT NULL,
                        metadata TEXT
                    );
                    """)

                # Dynamic schema migration for older databases
                cursor = conn.execute("PRAGMA table_info(proof_trajectories);")
                columns = [r["name"] for r in cursor.fetchall()]
                if columns and "metadata" not in columns:
                    conn.execute(
                        "ALTER TABLE proof_trajectories ADD COLUMN metadata TEXT;"
                    )
        finally:
            conn.close()

    def add_theorem(
        self,
        theorem_id: str,
        domain: str,
        schema_version: str,
        statement: str,
        lean_proof: str,
        verified: bool,
        provenance: str,
        dependencies: list[str] | None = None,
    ) -> None:
        """Saves a theorem and its dependency relationships to the knowledge base.

        This runs as an atomic transaction. It automatically calculates the SHA-256
        hash of the proof and records the provenance lineage.
        """
        if dependencies is None:
            dependencies = []

        if provenance not in (
            "DETERMINISTIC_RULE",
            "AUTO_FORMALIZED",
            "MCTS_DISCOVERY",
        ):
            raise ValueError(
                f"Invalid provenance value: '{provenance}'. "
                f"Must be one of 'DETERMINISTIC_RULE', 'AUTO_FORMALIZED', 'MCTS_DISCOVERY'."
            )

        proof_hash = hashlib.sha256(lean_proof.encode("utf-8")).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()

        conn = self._connect()
        try:
            with conn:
                # 1. Insert the theorem
                conn.execute(
                    """
                    INSERT INTO theorems (id, domain, schema_version, statement, lean_proof, proof_hash, verified, created_at, provenance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        theorem_id,
                        domain,
                        schema_version,
                        statement,
                        lean_proof,
                        proof_hash,
                        1 if verified else 0,
                        created_at,
                        provenance,
                    ),
                )

                # 2. Insert dependencies
                for dep_id in dependencies:
                    conn.execute(
                        """
                        INSERT INTO theorem_dependencies (theorem_id, dependency_id)
                        VALUES (?, ?)
                        """,
                        (theorem_id, dep_id),
                    )
        finally:
            conn.close()

    def log_mcts_run(
        self,
        run_id: str,
        theorem_id: str,
        total_simulations: int,
        success: bool,
        nodes_explored: int,
    ) -> None:
        """Persists MCTS tree search stats for downstream Reinforcement Learning feedback."""
        created_at = datetime.now(timezone.utc).isoformat()

        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO mcts_runs (run_id, theorem_id, total_simulations, success, nodes_explored, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        theorem_id,
                        total_simulations,
                        1 if success else 0,
                        nodes_explored,
                        created_at,
                    ),
                )
        finally:
            conn.close()

    def log_trajectory(
        self,
        run_id: str,
        state_context: str,
        tactic_applied: str,
        status: str,
        reward: float,
        metadata: dict = None,
    ) -> None:
        """Logs a proof step trajectory in the database for DPO or reinforcement learning."""
        created_at = datetime.now(timezone.utc).isoformat()
        metadata_str = json.dumps(metadata) if metadata is not None else None

        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO proof_trajectories (run_id, state_context, tactic_applied, status, reward, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        state_context,
                        tactic_applied,
                        status,
                        reward,
                        created_at,
                        metadata_str,
                    ),
                )
        finally:
            conn.close()

    def get_all_trajectories(self) -> list[dict]:
        """Retrieves all proof step trajectories from the knowledge base."""
        conn = self._connect()
        try:
            rows = conn.execute("SELECT * FROM proof_trajectories").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_theorem(self, theorem_id: str) -> dict | None:
        """Retrieves theorem data along with its dependencies by its ID.

        Returns None if the theorem does not exist.
        """
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM theorems WHERE id = ?", (theorem_id,)
            ).fetchone()

            if not row:
                return None

            result = dict(row)
            # Parse verified back to boolean
            result["verified"] = bool(result["verified"])

            # Query dependencies
            dep_rows = conn.execute(
                "SELECT dependency_id FROM theorem_dependencies WHERE theorem_id = ?",
                (theorem_id,),
            ).fetchall()
            result["dependencies"] = [r["dependency_id"] for r in dep_rows]

            return result
        finally:
            conn.close()

    def get_dependents(self, theorem_id: str) -> list[str]:
        """Finds all theorem IDs that depend directly on the specified theorem ID."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT theorem_id FROM theorem_dependencies WHERE dependency_id = ?",
                (theorem_id,),
            ).fetchall()
            return [r["theorem_id"] for r in rows]
        finally:
            conn.close()
