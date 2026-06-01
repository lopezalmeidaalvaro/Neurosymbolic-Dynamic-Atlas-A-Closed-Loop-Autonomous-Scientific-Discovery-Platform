# Mission Database & Telemetry Warehouse

This module manages the storage, partitioning, and retrieval of orbital thermal telemetry, augmented EKF twin parameter histories, symbolic structural discoveries, and multi-tenant SaaS accounts.

---

## 1. TimescaleDB Schema (`init.sql`)

The database maps six critical telemetry nodes partitioned by time:
* **missions**: Traces spacecraft LEO parameters.
* **telemetry**: Hypertable partitioned at 1-day intervals tracking sensor node temperatures, power disspation budgets, and anomalies flags.
* **ekf_history**: Records EKF state estimation arrays and flattened covariance P-matrices.
* **anomaly_logs**: Records in-orbit alerts, severities, and resolutions.
* **symbolic_discoveries**: Logs structural physics equations found by PySR.
* **SaaS Accounts**: Registers organizations, roles (`admin`, `member`, `viewer`), Stripe webhooks, and JWT keys.

---

## 2. Ingestion & Fallback Manager (`telemetry_warehouse.py`)

To ensure robust deployments across continuous integration (CI/CD) environments, the `TelemetryWarehouse` includes a **self-healing fallback**:
1. **TimescaleDB Mode**: Utilizes high-performance `psycopg2` batch execution commands (`execute_values`) when connected to a TimescaleDB PostgreSQL cluster.
2. **SQLite Fallback Mode**: Gracefully degrades to a local SQLite database (`satellite/api/auth.db`) if the PostgreSQL connection fails. Schema setups and insertions remain fully functional.

---

## 3. Operations & Usage

To initialize tables manually:
```bash
python satellite/db/telemetry_warehouse.py
```

### Time Range Queries
```python
from satellite.db.telemetry_warehouse import TelemetryWarehouse

warehouse = TelemetryWarehouse()
# Retrieves timeseries logs between t_start and t_end
logs = warehouse.query_telemetry_range(mission_id, t_start, t_end)
```
