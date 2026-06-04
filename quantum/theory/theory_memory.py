import os
import json
import sqlite3
from typing import Dict, Any, List, Optional

class TheoryMemory:
    """
    Component M: Scientific Memory.
    Manages structured storage for candidate, accepted, and rejected theories,
    prediction histories, mechanism histories, and meta-laws using SQLite databases.
    """

    def __init__(self, db_path: str = "theory_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create theories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS theories (
                id TEXT PRIMARY KEY,
                name TEXT,
                laws_explained TEXT,
                mechanism_graph TEXT,
                assumptions TEXT,
                predictions TEXT,
                confidence REAL,
                status TEXT
            )
        """)
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                originating_theory TEXT,
                prediction_statement TEXT,
                antecedents TEXT,
                consequent TEXT,
                trend TEXT,
                effect_size REAL,
                confidence REAL,
                status TEXT
            )
        """)
        
        # Create mechanisms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanisms (
                theory_id TEXT PRIMARY KEY,
                graph_json TEXT,
                status TEXT
            )
        """)
        
        # Create meta_laws table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta_laws (
                id TEXT PRIMARY KEY,
                statement TEXT,
                status TEXT
            )
        """)
        
        # Create preregistered_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preregistered_predictions (
                id TEXT PRIMARY KEY,
                expected_effect REAL,
                expected_direction TEXT,
                expected_confidence REAL,
                timestamp TEXT,
                hash TEXT
            )
        """)
        
        # Create hardware_executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hardware_executions (
                id TEXT PRIMARY KEY,
                backend TEXT,
                device TEXT,
                shots INTEGER,
                error_rate REAL,
                calibration_state TEXT,
                timestamp TEXT
            )
        """)
        
        # Create negative_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS negative_results (
                id TEXT PRIMARY KEY,
                type TEXT,
                target_id TEXT,
                reason TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def save_theory(self, theory: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO theories (id, name, laws_explained, mechanism_graph, assumptions, predictions, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            theory["id"],
            theory.get("name", ""),
            json.dumps(theory.get("laws_explained", [])),
            json.dumps(theory.get("mechanism_graph", {})),
            json.dumps(theory.get("assumptions", [])),
            json.dumps(theory.get("predictions", [])),
            theory.get("confidence", 0.0),
            theory.get("status", "CANDIDATE")
        ))
        
        conn.commit()
        conn.close()

    def get_theory(self, theory_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, laws_explained, mechanism_graph, assumptions, predictions, confidence, status FROM theories WHERE id = ?", (theory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return {
            "id": row[0],
            "name": row[1],
            "laws_explained": json.loads(row[2]),
            "mechanism_graph": json.loads(row[3]),
            "assumptions": json.loads(row[4]),
            "predictions": json.loads(row[5]),
            "confidence": row[6],
            "status": row[7]
        }

    def get_all_theories(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT id, name, laws_explained, mechanism_graph, assumptions, predictions, confidence, status FROM theories WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT id, name, laws_explained, mechanism_graph, assumptions, predictions, confidence, status FROM theories")
            
        rows = cursor.fetchall()
        conn.close()
        
        theories = []
        for row in rows:
            theories.append({
                "id": row[0],
                "name": row[1],
                "laws_explained": json.loads(row[2]),
                "mechanism_graph": json.loads(row[3]),
                "assumptions": json.loads(row[4]),
                "predictions": json.loads(row[5]),
                "confidence": row[6],
                "status": row[7]
            })
        return theories

    def save_prediction(self, prediction: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO predictions (id, originating_theory, prediction_statement, antecedents, consequent, trend, effect_size, confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction["id"],
            prediction["originating_theory"],
            prediction["prediction_statement"],
            json.dumps(prediction.get("antecedents", [])),
            prediction.get("consequent", ""),
            prediction.get("trend", ""),
            prediction.get("effect_size", 0.0),
            prediction.get("confidence", 0.0),
            prediction.get("status", "UNCONFIRMED")
        ))
        
        conn.commit()
        conn.close()

    def get_prediction(self, pred_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, originating_theory, prediction_statement, antecedents, consequent, trend, effect_size, confidence, status FROM predictions WHERE id = ?", (pred_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return {
            "id": row[0],
            "originating_theory": row[1],
            "prediction_statement": row[2],
            "antecedents": json.loads(row[3]),
            "consequent": row[4],
            "trend": row[5],
            "effect_size": row[6],
            "confidence": row[7],
            "status": row[8]
        }

    def get_all_predictions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT id, originating_theory, prediction_statement, antecedents, consequent, trend, effect_size, confidence, status FROM predictions WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT id, originating_theory, prediction_statement, antecedents, consequent, trend, effect_size, confidence, status FROM predictions")
            
        rows = cursor.fetchall()
        conn.close()
        
        preds = []
        for row in rows:
            preds.append({
                "id": row[0],
                "originating_theory": row[1],
                "prediction_statement": row[2],
                "antecedents": json.loads(row[3]),
                "consequent": row[4],
                "trend": row[5],
                "effect_size": row[6],
                "confidence": row[7],
                "status": row[8]
            })
        return preds

    def save_meta_law(self, id_val: str, statement: str, status: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO meta_laws (id, statement, status)
            VALUES (?, ?, ?)
        """, (id_val, statement, status))
        
        conn.commit()
        conn.close()

    def get_all_meta_laws(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, statement, status FROM meta_laws")
        rows = cursor.fetchall()
        conn.close()
        
        meta_laws = []
        for row in rows:
            meta_laws.append({
                "id": row[0],
                "statement": row[1],
                "status": row[2]
            })
        return meta_laws

    def save_preregistered_prediction(self, pred: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preregistered_predictions (id, expected_effect, expected_direction, expected_confidence, timestamp, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pred["id"],
            pred["expected_effect"],
            pred["expected_direction"],
            pred["expected_confidence"],
            pred["timestamp"],
            pred["hash"]
        ))
        conn.commit()
        conn.close()

    def get_preregistered_prediction(self, pred_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, expected_effect, expected_direction, expected_confidence, timestamp, hash FROM preregistered_predictions WHERE id = ?", (pred_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "expected_effect": row[1],
            "expected_direction": row[2],
            "expected_confidence": row[3],
            "timestamp": row[4],
            "hash": row[5]
        }

    def get_all_preregistered_predictions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, expected_effect, expected_direction, expected_confidence, timestamp, hash FROM preregistered_predictions")
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "expected_effect": r[1],
            "expected_direction": r[2],
            "expected_confidence": r[3],
            "timestamp": r[4],
            "hash": r[5]
        } for r in rows]

    def save_hardware_execution(self, exec_data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO hardware_executions (id, backend, device, shots, error_rate, calibration_state, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            exec_data["id"],
            exec_data["backend"],
            exec_data["device"],
            exec_data["shots"],
            exec_data["error_rate"],
            exec_data["calibration_state"],
            exec_data["timestamp"]
        ))
        conn.commit()
        conn.close()

    def get_all_hardware_executions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, backend, device, shots, error_rate, calibration_state, timestamp FROM hardware_executions")
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "backend": r[1],
            "device": r[2],
            "shots": r[3],
            "error_rate": r[4],
            "calibration_state": r[5],
            "timestamp": r[6]
        } for r in rows]

    def save_negative_result(self, neg: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO negative_results (id, type, target_id, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            neg["id"],
            neg["type"],
            neg["target_id"],
            neg["reason"],
            neg["timestamp"]
        ))
        conn.commit()
        conn.close()

    def get_all_negative_results(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, target_id, reason, timestamp FROM negative_results")
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "type": r[1],
            "target_id": r[2],
            "reason": r[3],
            "timestamp": r[4]
        } for r in rows]

    def clear(self) -> None:
        """Clear all tables in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM theories")
        cursor.execute("DELETE FROM predictions")
        cursor.execute("DELETE FROM mechanisms")
        cursor.execute("DELETE FROM meta_laws")
        cursor.execute("DELETE FROM preregistered_predictions")
        cursor.execute("DELETE FROM hardware_executions")
        cursor.execute("DELETE FROM negative_results")
        conn.commit()
        conn.close()
