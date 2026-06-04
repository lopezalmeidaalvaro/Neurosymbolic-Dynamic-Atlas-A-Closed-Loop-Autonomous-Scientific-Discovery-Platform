import os
import json
import sqlite3
from typing import Dict, Any, List
from datetime import datetime, timezone

class EvidenceMemory:
    """
    Component M: Evidence Memory.
    Manages structured storage for all audit scores, warning flags, weaknesses,
    and unresolved risks in evidence_memory.db using SQLite.
    """

    def __init__(self, db_path: str = "evidence_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create audit_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_results (
                id TEXT PRIMARY KEY,
                score REAL,
                details TEXT,
                timestamp TEXT
            )
        """)
        
        # Create warnings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id TEXT PRIMARY KEY,
                type TEXT,
                message TEXT,
                severity TEXT,
                timestamp TEXT
            )
        """)
        
        # Create weaknesses_risks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weaknesses_risks (
                id TEXT PRIMARY KEY,
                category TEXT,
                description TEXT,
                status TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def save_audit_result(self, audit_id: str, score: float, details: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO audit_results (id, score, details, timestamp)
            VALUES (?, ?, ?, ?)
        """, (audit_id, score, json.dumps(details), now))
        
        conn.commit()
        conn.close()

    def save_warning(self, warning_id: str, warning_type: str, message: str, severity: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO warnings (id, type, message, severity, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (warning_id, warning_type, message, severity, now))
        
        conn.commit()
        conn.close()

    def save_weakness_risk(self, risk_id: str, category: str, description: str, status: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO weaknesses_risks (id, category, description, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (risk_id, category, description, status, now))
        
        conn.commit()
        conn.close()

    def get_all_audit_results(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, score, details, timestamp FROM audit_results")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "score": r[1],
            "details": json.loads(r[2]),
            "timestamp": r[3]
        } for r in rows]

    def get_all_warnings(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, message, severity, timestamp FROM warnings")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "type": r[1],
            "message": r[2],
            "severity": r[3],
            "timestamp": r[4]
        } for r in rows]

    def get_all_weaknesses_risks(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, category, description, status, timestamp FROM weaknesses_risks")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "category": r[1],
            "description": r[2],
            "status": r[3],
            "timestamp": r[4]
        } for r in rows]

    def clear(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_results")
        cursor.execute("DELETE FROM warnings")
        cursor.execute("DELETE FROM weaknesses_risks")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    mem = EvidenceMemory()
    print("Database initialised and tested.")
