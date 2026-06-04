import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class RealityNativeMemory:
    """
    Manages SQLite relational database storage for all Phase 3B discovery results
    (gaps, clusters, laws, mechanisms, candidate theories, predictions).
    Nothing may be deleted.
    """

    def __init__(self, db_path: str = "reality_native.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. reality_gaps table (GAP_DATABASE)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reality_gaps (
                id TEXT PRIMARY KEY,
                prediction_id TEXT,
                device TEXT,
                metric TEXT,
                observed REAL,
                predicted REAL,
                gap REAL,
                timestamp TEXT
            )
        """)
        
        # 2. anomaly_families table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_families (
                id TEXT PRIMARY KEY,
                name TEXT,
                prediction_ids TEXT,
                mean_gap REAL,
                cluster_id INTEGER
            )
        """)
        
        # 3. discovered_laws table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_laws (
                id TEXT PRIMARY KEY,
                equation TEXT,
                confidence REAL,
                complexity REAL,
                supporting_observations TEXT,
                cross_platform_support TEXT
            )
        """)
        
        # 4. discovered_mechanisms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_mechanisms (
                id TEXT PRIMARY KEY,
                law_id TEXT,
                graph_json TEXT,
                vendors TEXT,
                paradigms TEXT,
                calibration_drift_robust TEXT
            )
        """)
        
        # 5. candidate_theories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_theories (
                id TEXT PRIMARY KEY,
                name TEXT,
                assumptions TEXT,
                equations TEXT,
                mechanisms TEXT,
                predictions TEXT,
                failure_modes TEXT,
                validity_domain TEXT,
                status TEXT
            )
        """)
        
        # 6. novel_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS novel_predictions (
                id TEXT PRIMARY KEY,
                theory_id TEXT,
                predicted_effect REAL,
                condition TEXT,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    # Reality Gaps methods
    def save_reality_gap(self, gap_data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO reality_gaps (id, prediction_id, device, metric, observed, predicted, gap, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gap_data["id"],
            gap_data["prediction_id"],
            gap_data["device"],
            gap_data["metric"],
            gap_data["observed"],
            gap_data["predicted"],
            gap_data["gap"],
            now
        ))
        
        conn.commit()
        conn.close()

    def get_all_gaps(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, prediction_id, device, metric, observed, predicted, gap, timestamp FROM reality_gaps")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "prediction_id": r[1],
            "device": r[2],
            "metric": r[3],
            "observed": r[4],
            "predicted": r[5],
            "gap": r[6],
            "timestamp": r[7]
        } for r in rows]

    # Anomaly Families methods
    def save_anomaly_family(self, fam: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO anomaly_families (id, name, prediction_ids, mean_gap, cluster_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            fam["id"],
            fam["name"],
            json.dumps(fam["prediction_ids"]),
            fam["mean_gap"],
            fam["cluster_id"]
        ))
        conn.commit()
        conn.close()

    def get_all_anomaly_families(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, prediction_ids, mean_gap, cluster_id FROM anomaly_families")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "name": r[1],
            "prediction_ids": json.loads(r[2]),
            "mean_gap": r[3],
            "cluster_id": r[4]
        } for r in rows]

    # Discovered Laws methods
    def save_discovered_law(self, law: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO discovered_laws (id, equation, confidence, complexity, supporting_observations, cross_platform_support)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            law["id"],
            law["equation"],
            law["confidence"],
            law["complexity"],
            json.dumps(law.get("supporting_observations", [])),
            json.dumps(law.get("cross_platform_support", {}))
        ))
        conn.commit()
        conn.close()

    def get_all_discovered_laws(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, equation, confidence, complexity, supporting_observations, cross_platform_support FROM discovered_laws")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "equation": r[1],
            "confidence": r[2],
            "complexity": r[3],
            "supporting_observations": json.loads(r[4]),
            "cross_platform_support": json.loads(r[5])
        } for r in rows]

    # Discovered Mechanisms methods
    def save_discovered_mechanism(self, mech: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO discovered_mechanisms (id, law_id, graph_json, vendors, paradigms, calibration_drift_robust)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mech["id"],
            mech["law_id"],
            json.dumps(mech["graph_json"]),
            json.dumps(mech["vendors"]),
            json.dumps(mech["paradigms"]),
            mech["calibration_drift_robust"]
        ))
        conn.commit()
        conn.close()

    def get_all_discovered_mechanisms(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, law_id, graph_json, vendors, paradigms, calibration_drift_robust FROM discovered_mechanisms")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "law_id": r[1],
            "graph_json": json.loads(r[2]),
            "vendors": json.loads(r[3]),
            "paradigms": json.loads(r[4]),
            "calibration_drift_robust": r[5]
        } for r in rows]

    # Candidate Theories methods
    def save_candidate_theory(self, theory: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO candidate_theories (id, name, assumptions, equations, mechanisms, predictions, failure_modes, validity_domain, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            theory["id"],
            theory["name"],
            json.dumps(theory.get("assumptions", [])),
            json.dumps(theory.get("equations", [])),
            json.dumps(theory.get("mechanisms", [])),
            json.dumps(theory.get("predictions", [])),
            json.dumps(theory.get("failure_modes", [])),
            json.dumps(theory.get("validity_domain", {})),
            theory.get("status", "CANDIDATE")
        ))
        conn.commit()
        conn.close()

    def get_all_candidate_theories(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, assumptions, equations, mechanisms, predictions, failure_modes, validity_domain, status FROM candidate_theories")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "name": r[1],
            "assumptions": json.loads(r[2]),
            "equations": json.loads(r[3]),
            "mechanisms": json.loads(r[4]),
            "predictions": json.loads(r[5]),
            "failure_modes": json.loads(r[6]),
            "validity_domain": json.loads(r[7]),
            "status": r[8]
        } for r in rows]

    # Novel Predictions methods
    def save_novel_prediction(self, pred: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO novel_predictions (id, theory_id, predicted_effect, condition, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            pred["id"],
            pred["theory_id"],
            pred["predicted_effect"],
            json.dumps(pred.get("condition", {})),
            pred.get("status", "UNCONFIRMED")
        ))
        conn.commit()
        conn.close()

    def get_all_novel_predictions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, theory_id, predicted_effect, condition, status FROM novel_predictions")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "theory_id": r[1],
            "predicted_effect": r[2],
            "condition": json.loads(r[3]),
            "status": r[4]
        } for r in rows]

    def clear(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reality_gaps")
        cursor.execute("DELETE FROM anomaly_families")
        cursor.execute("DELETE FROM discovered_laws")
        cursor.execute("DELETE FROM discovered_mechanisms")
        cursor.execute("DELETE FROM candidate_theories")
        cursor.execute("DELETE FROM novel_predictions")
        conn.commit()
        conn.close()
