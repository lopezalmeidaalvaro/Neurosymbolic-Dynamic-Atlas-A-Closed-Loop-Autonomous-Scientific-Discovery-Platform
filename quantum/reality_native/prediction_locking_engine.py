import os
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

class PredictionLockingEngine:
    """
    Phase 3B.2C: Prediction Locking Engine.
    Generates new predictions, computes SHA-256 hashes, freezes them in SQLite,
    prevents modifications, and generates docs/LOCKED_PREDICTIONS.md.
    """

    def __init__(self, reality_db_path: str = "reality_native.db"):
        self.reality_db_path = reality_db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.reality_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locked_predictions (
                id TEXT PRIMARY KEY,
                theory_id TEXT,
                predicted_val REAL,
                condition_json TEXT,
                timestamp TEXT,
                checksum TEXT
            )
        """)
        conn.commit()
        conn.close()

    def lock_predictions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.reality_db_path)
        cursor = conn.cursor()
        
        locked_records = []
        timestamp = datetime.now(timezone.utc).isoformat()

        for pred in predictions:
            p_id = pred["id"]
            
            # Check if prediction with this ID is already locked (prevent modification)
            cursor.execute("SELECT id, predicted_val, checksum FROM locked_predictions WHERE id = ?", (p_id,))
            existing = cursor.fetchone()
            if existing:
                print(f"Warning: Prediction {p_id} is already locked. Modification prevented.")
                locked_records.append({
                    "id": existing[0],
                    "predicted_val": existing[1],
                    "checksum": existing[2],
                    "status": "LOCKED_PREVENTED_MUTATION"
                })
                continue

            theory_id = pred["theory_id"]
            predicted_val = pred["predicted_val"]
            cond_str = json.dumps(pred["condition"])
            
            # Compute SHA-256 checksum over predicted value + condition details
            hash_input = f"{p_id}:{theory_id}:{predicted_val:.6f}:{cond_str}:{timestamp}"
            checksum = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

            cursor.execute("""
                INSERT INTO locked_predictions (id, theory_id, predicted_val, condition_json, timestamp, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (p_id, theory_id, predicted_val, cond_str, timestamp, checksum))
            
            locked_records.append({
                "id": p_id,
                "theory_id": theory_id,
                "predicted_val": predicted_val,
                "condition": pred["condition"],
                "timestamp": timestamp,
                "checksum": checksum,
                "status": "NEW_LOCKED"
            })

        conn.commit()
        conn.close()

        # Write report
        self._write_markdown_report(locked_records)
        return locked_records

    def _write_markdown_report(self, records: List[Dict[str, Any]]) -> None:
        lines = [
            "# Preregistered Prediction Lock Ledger — Phase 3B.2",
            "",
            "Documents the frozen prediction specifications and cryptographic checksum locks prior to execution verification trials.",
            "",
            "| Prediction ID | Origin Theory | Target Backend | Predicted Value | Lock Timestamp | Cryptographic Hash Lock (SHA-256) |",
            "| :---: | :--- | :--- | :---: | :--- | :--- |"
        ]
        
        for r in records:
            if "condition" in r:
                device = r["condition"]["device"]
            else:
                device = "unknown"
            
            ts = r.get("timestamp", datetime.now(timezone.utc).isoformat())
            lines.append(
                f"| `{r['id']}` | `{r.get('theory_id', 'RTHEORY_001')}` | `{device}` | "
                f"`{r['predicted_val']:.6f}` | `{ts}` | `{r['checksum']}` |"
            )
            
        lines.append("")
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/LOCKED_PREDICTIONS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    locker = PredictionLockingEngine()
    test_preds = [
        {
            "id": "LOCK_TEST_001",
            "theory_id": "RTHEORY_001",
            "predicted_val": 0.355102,
            "condition": {"device": "superconducting_odin", "gate_error": 0.005, "readout_error": 0.010}
        }
    ]
    print(locker.lock_predictions(test_preds))
