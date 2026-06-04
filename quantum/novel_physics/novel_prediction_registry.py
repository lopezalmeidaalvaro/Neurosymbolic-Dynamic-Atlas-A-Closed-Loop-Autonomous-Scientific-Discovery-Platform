import sqlite3
import os
import json
from typing import Dict, Any, List

class NovelPredictionRegistry:
    """
    Phase 4F: Blind Novel Physics Challenge - Prediction Registry.
    Registers predictions to a local SQLite database to prevent modifications.
    """

    def __init__(self, db_path: str = "databases/novel_predictions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS locked_predictions (
                case_id TEXT PRIMARY KEY,
                theory_id TEXT,
                sha256 TEXT,
                frozen_json TEXT
            )
        """)
        conn.commit()
        conn.close()

    def register_locked_predictions(self, locked_data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for r in locked_data["records"]:
            c.execute(
                "INSERT OR REPLACE INTO locked_predictions (case_id, theory_id, sha256, frozen_json) VALUES (?, ?, ?, ?)",
                (r["case_id"], r["theory_id"], r["sha256"], json.dumps(r["frozen_record"]))
            )
        conn.commit()
        conn.close()

    def get_registered_predictions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT case_id, theory_id, sha256, frozen_json FROM locked_predictions")
        rows = c.fetchall()
        conn.close()

        records = []
        for r in rows:
            records.append({
                "case_id": r[0],
                "theory_id": r[1],
                "sha256": r[2],
                "frozen_record": json.loads(r[3])
            })
        return records
