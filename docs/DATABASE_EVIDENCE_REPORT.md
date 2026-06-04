# Database Evidence Report — SQLite Forensics

Presents a complete audit of all SQLite database files in the repository.

---

## 1. Database Registry

| Database Filename | Size (Bytes) | Table Count | Total Records | Primary Role |
| :--- | :---: | :---: | :---: | :--- |
| `reality_native.db` | `24,576` | 8 | 62 | Storage for Phase 3B discovery & Phase 3B.1 confirmation data. |
| `theory_memory.db` | `110,592` | 7 | 233 | Central repository for baseline theories, predictions, and history. |
| `evidence_memory.db` | `53,248` | 3 | 13 | Pre-discovery evidence verification storage (Phase 3A.5). |
| `scientific_kb.db` | `28,672` | 3 | 3 | Legacy scientific knowledge graph storage. |

---

## 2. Table-by-Table Forensics

### **Database: `reality_native.db`**
*   **Table `reality_gaps`** (50 records)
    *   *Schema*:
        ```sql
        CREATE TABLE reality_gaps (
            id TEXT PRIMARY KEY,
            prediction_id TEXT,
            device TEXT,
            metric TEXT,
            observed REAL,
            predicted REAL,
            gap REAL,
            timestamp TEXT
        )
        ```
*   **Table `anomaly_families`** (1 record)
    *   *Schema*:
        ```sql
        CREATE TABLE anomaly_families (
            id TEXT PRIMARY KEY,
            name TEXT,
            prediction_ids TEXT,
            mean_gap REAL,
            cluster_id INTEGER
        )
        ```
*   **Table `discovered_laws`** (1 record)
    *   *Schema*:
        ```sql
        CREATE TABLE discovered_laws (
            id TEXT PRIMARY KEY,
            equation TEXT,
            confidence REAL,
            complexity REAL,
            supporting_observations TEXT,
            cross_platform_support TEXT
        )
        ```
*   **Table `discovered_mechanisms`** (1 record)
    *   *Schema*:
        ```sql
        CREATE TABLE discovered_mechanisms (
            id TEXT PRIMARY KEY,
            law_id TEXT,
            graph_json TEXT,
            vendors TEXT,
            paradigms TEXT,
            calibration_drift_robust TEXT
        )
        ```
*   **Table `candidate_theories`** (1 record)
    *   *Schema*:
        ```sql
        CREATE TABLE candidate_theories (
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
        ```
*   **Table `novel_predictions`** (2 records)
    *   *Schema*:
        ```sql
        CREATE TABLE novel_predictions (
            id TEXT PRIMARY KEY,
            theory_id TEXT,
            predicted_effect REAL,
            condition TEXT,
            status TEXT
        )
        ```
*   **Table `confirmation_predictions`** (4 records)
    *   *Schema*:
        ```sql
        CREATE TABLE confirmation_predictions (
            id TEXT PRIMARY KEY,
            theory_id TEXT,
            device TEXT,
            predicted_val REAL,
            observed_val REAL,
            abs_err REAL,
            sq_err REAL,
            rel_err REAL,
            status TEXT
        )
        ```
*   **Table `confirmation_metadata`** (2 records)
    *   *Schema*:
        ```sql
        CREATE TABLE confirmation_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ```

### **Database: `theory_memory.db`**
*   **Table `theories`** (16 records)
    *   *Schema*:
        ```sql
        CREATE TABLE theories (
            id TEXT PRIMARY KEY,
            name TEXT,
            laws_explained TEXT,
            mechanism_graph TEXT,
            assumptions TEXT,
            predictions TEXT,
            confidence REAL,
            status TEXT
        )
        ```
*   **Table `predictions`** (10 records)
    *   *Schema*:
        ```sql
        CREATE TABLE predictions (
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
        ```
*   **Table `mechanisms`** (0 records)
*   **Table `meta_laws`** (3 records)
    *   *Schema*:
        ```sql
        CREATE TABLE meta_laws (
            id TEXT PRIMARY KEY,
            statement TEXT,
            status TEXT
        )
        ```
*   **Table `preregistered_predictions`** (10 records)
*   **Table `hardware_executions`** (190 records)
    *   *Schema*:
        ```sql
        CREATE TABLE hardware_executions (
            id TEXT PRIMARY KEY,
            backend TEXT,
            device TEXT,
            shots INTEGER,
            error_rate REAL,
            calibration_state TEXT,
            timestamp TEXT
        )
        ```
*   **Table `negative_results`** (4 records)

---

## 3. Database Integrity & Linkages

All keys map correctly. The predictions in `confirmation_predictions` link directly via `theory_id = RTHEORY_001` to `candidate_theories` table records. The gaps in `reality_gaps` map directly to the baseline predictions in `theory_memory.db` via `prediction_id` (e.g. `PRED_001` to `PRED_011`).
