#!/usr/bin/env python3
"""
Mission Database & Telemetry Warehouse Interface
Autonomous Spacecraft Thermal OS
Manages TimescaleDB historical persistence, batch ingestion, and time-range queries.
"""

import os
import sys
import csv
import json
import uuid
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import psycopg2
    from psycopg2.extras import execute_values

    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://thermal_user:thermal_secure_password_99@localhost:5432/thermal_twin",
)
SQLITE_FALLBACK_PATH = Path(__file__).resolve().parents[1] / "api" / "auth.db"


class TelemetryWarehouse:
    def __init__(self):
        self.use_postgres = HAS_POSTGRES
        self.conn = None
        self.connect()

    def connect(self):
        """Attempts connection to TimescaleDB with a graceful SQLite fallback."""
        if self.use_postgres:
            try:
                self.conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
                self.conn.autocommit = True
                return
            except Exception as e:
                print(
                    f"[Warehouse] TimescaleDB connection failed ({str(e)}). Falling back to SQLite."
                )
                self.use_postgres = False

        # SQLite Fallback Setup
        os.makedirs(SQLITE_FALLBACK_PATH.parent, exist_ok=True)
        self.conn = sqlite3.connect(str(SQLITE_FALLBACK_PATH), check_same_thread=False)

    def execute_sql(self, sql, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, params or ())
            if not self.use_postgres:
                self.conn.commit()
            return cursor
        except Exception as e:
            if self.use_postgres:
                self.conn.rollback()
            raise e

    def create_tables(self):
        """Initializes database tables using the structured SQL schema."""
        init_sql_path = Path(__file__).resolve().parent / "init.sql"
        if not init_sql_path.exists():
            return

        with open(init_sql_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        if self.use_postgres:
            try:
                self.execute_sql(schema_sql)
                print("[Warehouse] TimescaleDB schema bootstrapped successfully.")
            except Exception as e:
                print(f"[Warehouse] Failed to execute init.sql on Postgres: {e}")
        else:
            # Recreate vital tables in SQLite fallback format
            cursor = self.conn.cursor()
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE,
                plan TEXT DEFAULT 'free',
                quota_limit INTEGER DEFAULT 100
            );
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                hashed_password TEXT,
                org_id TEXT,
                role TEXT DEFAULT 'viewer'
            );
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                key_hash TEXT UNIQUE,
                user_id TEXT,
                revoked BOOLEAN DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS waitlist (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                company TEXT,
                use_case TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS missions (
                id TEXT PRIMARY KEY,
                name TEXT,
                satellite_id TEXT,
                org_id TEXT,
                start_time TEXT,
                end_time TEXT,
                orbit_params TEXT
            );
            CREATE TABLE IF NOT EXISTS telemetry (
                time TEXT,
                mission_id TEXT,
                node_id TEXT,
                temperature REAL,
                power REAL,
                radiator_state REAL,
                anomaly_flags TEXT
            );
            CREATE TABLE IF NOT EXISTS ekf_history (
                time TEXT,
                mission_id TEXT,
                state_vector TEXT,
                covariance_matrix TEXT,
                innovation REAL,
                status TEXT
            );
            CREATE TABLE IF NOT EXISTS anomaly_logs (
                time TEXT,
                mission_id TEXT,
                anomaly_type TEXT,
                severity TEXT,
                description TEXT,
                action_taken TEXT,
                resolved BOOLEAN DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS symbolic_discoveries (
                id TEXT PRIMARY KEY,
                mission_id TEXT,
                equation_latex TEXT,
                complexity INTEGER,
                r2_score REAL,
                patentability_score REAL,
                created_at TEXT
            );
            
            -- Insert defaults
            INSERT OR IGNORE INTO organizations VALUES ('c4b8e212-0000-4000-a000-000000000001', 'ESA NewSpace Incubator', 'pro', 1000);
            INSERT OR IGNORE INTO users VALUES ('u4b8e212-0000-4000-a000-000000000001', 'mission-director@esa-bic.org', '$2b$12$V.oAasq36/6f7Zg6PjSw8OVt/Vv.qj3Lq/V/Sw4HwG0uW5SwXfG6u', 'c4b8e212-0000-4000-a000-000000000001', 'admin');
            INSERT OR IGNORE INTO api_keys VALUES ('k4b8e212-0000-4000-a000-000000000001', 'pro_enterprise_key_xyz987', 'u4b8e212-0000-4000-a000-000000000001', 0);
            """)
            self.conn.commit()
            print("[Warehouse] SQLite fallback tables bootstrapped successfully.")

    def insert_telemetry_batch(self, rows):
        """Inserts telemetry records in high-performance batches."""
        if not rows:
            return

        if self.use_postgres:
            cursor = self.conn.cursor()
            sql = "INSERT INTO telemetry (time, mission_id, node_id, temperature, power, radiator_state, anomaly_flags) VALUES %s"
            # Parse rows into lists/tuples for executemany/values
            execute_values(cursor, sql, rows)
        else:
            cursor = self.conn.cursor()
            sql = "INSERT INTO telemetry (time, mission_id, node_id, temperature, power, radiator_state, anomaly_flags) VALUES (?, ?, ?, ?, ?, ?, ?)"
            # SQLite does not support list of tags directly, stringify lists
            processed_rows = []
            for r in rows:
                time_val, m_id, n_id, temp, pwr, rad_state, flags = r
                flags_str = ",".join(flags) if flags else ""
                processed_rows.append(
                    (str(time_val), str(m_id), n_id, temp, pwr, rad_state, flags_str)
                )
            cursor.executemany(sql, processed_rows)
            self.conn.commit()

    def query_telemetry_range(self, mission_id, t_start, t_end):
        """Queries historical telemetry ranges for a designated mission."""
        if self.use_postgres:
            sql = """
            SELECT time, node_id, temperature, power, radiator_state, anomaly_flags 
            FROM telemetry 
            WHERE mission_id = %s AND time BETWEEN %s AND %s 
            ORDER BY time ASC
            """
            cursor = self.execute_sql(sql, (mission_id, t_start, t_end))
        else:
            sql = """
            SELECT time, node_id, temperature, power, radiator_state, anomaly_flags 
            FROM telemetry 
            WHERE mission_id = ? AND time BETWEEN ? AND ? 
            ORDER BY time ASC
            """
            cursor = self.execute_sql(sql, (str(mission_id), str(t_start), str(t_end)))

        results = cursor.fetchall()
        parsed_results = []
        for r in results:
            t, n_id, temp, pwr, rad_state, flags = r
            flags_list = (
                flags.split(",") if isinstance(flags, str) and flags else (flags or [])
            )
            parsed_results.append(
                {
                    "time": t,
                    "node_id": n_id,
                    "temperature": temp,
                    "power": pwr,
                    "radiator_state": rad_state,
                    "anomaly_flags": flags_list,
                }
            )
        return parsed_results

    def get_anomaly_summary(self, mission_id):
        """Returns isolated lists of anomalies logged for a mission."""
        if self.use_postgres:
            sql = "SELECT time, anomaly_type, severity, description, action_taken, resolved FROM anomaly_logs WHERE mission_id = %s ORDER BY time DESC"
            cursor = self.execute_sql(sql, (mission_id,))
        else:
            sql = "SELECT time, anomaly_type, severity, description, action_taken, resolved FROM anomaly_logs WHERE mission_id = ? ORDER BY time DESC"
            cursor = self.execute_sql(sql, (str(mission_id),))

        results = cursor.fetchall()
        return [
            {
                "time": r[0],
                "anomaly_type": r[1],
                "severity": r[2],
                "description": r[3],
                "action_taken": r[4],
                "resolved": bool(r[5]),
            }
            for r in results
        ]

    def export_mission_csv(self, mission_id, filepath):
        """Compiles historical telemetry logs into standard engineering CSV files."""
        if self.use_postgres:
            sql = "SELECT time, node_id, temperature, power, radiator_state FROM telemetry WHERE mission_id = %s ORDER BY time ASC"
            cursor = self.execute_sql(sql, (mission_id,))
        else:
            sql = "SELECT time, node_id, temperature, power, radiator_state FROM telemetry WHERE mission_id = ? ORDER BY time ASC"
            cursor = self.execute_sql(sql, (str(mission_id),))

        rows = cursor.fetchall()

        os.makedirs(Path(filepath).parent, exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Timestamp",
                    "Node_ID",
                    "Temperature_C",
                    "Power_W",
                    "Radiator_Emissivity",
                ]
            )
            writer.writerows(rows)

        print(f"[Warehouse] Mission {mission_id} exported to CSV: {filepath}")

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Test execution
    warehouse = TelemetryWarehouse()
    warehouse.create_tables()

    # Ingest test mission
    test_mission_id = str(uuid.uuid4())
    params = json.dumps({"altitude": 400, "eclipse": 35})

    if warehouse.use_postgres:
        warehouse.execute_sql(
            "INSERT INTO missions (id, name, satellite_id, org_id, orbit_params) VALUES (%s, %s, %s, %s, %s)",
            (
                test_mission_id,
                "Test Orbit Alpha",
                "SAT-01",
                "c4b8e212-0000-4000-a000-000000000001",
                params,
            ),
        )
    else:
        warehouse.execute_sql(
            "INSERT INTO missions (id, name, satellite_id, org_id, orbit_params) VALUES (?, ?, ?, ?, ?)",
            (
                test_mission_id,
                "Test Orbit Alpha",
                "SAT-01",
                "c4b8e212-0000-4000-a000-000000000001",
                params,
            ),
        )

    # Ingest batch
    now = datetime.now(timezone.utc)
    batch = [
        (now, test_mission_id, "CPU", 25.4, 15.0, 0.85, ["NOMINAL"]),
        (now, test_mission_id, "Battery", 20.1, 2.0, 0.85, ["NOMINAL"]),
    ]
    warehouse.insert_telemetry_batch(batch)

    # Export CSV
    test_csv = Path(__file__).resolve().parent / "test_telemetry.csv"
    warehouse.export_mission_csv(test_mission_id, str(test_csv))

    # Clean up test files
    if test_csv.exists():
        os.remove(test_csv)

    warehouse.close()
