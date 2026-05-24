"""
EVALUATOR DB -- Herramienta de Memoria Local del Agente (Fase 6A)
=================================================================
Restricciones estrictas:
  - CERO llamadas a APIs externas.
  - Compatible con Windows: NO usa la libreria `resource`.
  - Usa subprocess.run(..., timeout=15) para control de ejecucion.
  - Telemetria de Redundancia y Costes automatica.
  - NUEVO (6A): Soporte para tabla de artefactos vinculados a nodos.

Comandos:
  python core/evaluator_db.py init <problema>
  python core/evaluator_db.py eval <parent_id> <framework_family> <framework> <ruta_archivo.py> [--notes "notas"] [--artifact "tipo|ruta"]
  python core/evaluator_db.py read_insights [--domain <dominio>]
  python core/evaluator_db.py add_insight '<json_string>'
"""

import os
import sys
import io

# Forzar stdout a UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import sqlite3
import subprocess
import time
import argparse
import textwrap
import json

# -- Rutas --
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(ROOT_DIR, "runs")
DB_PATH = os.path.join(RUNS_DIR, "math_search.db")

EXEC_TIMEOUT = 15

# ===========================================================================
# UTILIDADES DE CONEXION
# ===========================================================================


def _ensure_runs_dir():
    os.makedirs(RUNS_DIR, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    _ensure_runs_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===========================================================================
# ESQUEMA DE BASE DE DATOS (Fase 6A: incluye artifacts)
# ===========================================================================


def _create_schema(conn: sqlite3.Connection):
    """Crea todas las tablas si no existen. Idempotente."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS config (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS nodes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id        INTEGER REFERENCES nodes(id),
            framework_family TEXT    NOT NULL,
            framework        TEXT    NOT NULL,
            code             TEXT    NOT NULL,
            output           TEXT,
            status           TEXT    NOT NULL CHECK(status IN ('SUCCESS','ERROR','TIMEOUT')),
            cost_metric      REAL    NOT NULL,
            redundancy_flag  INTEGER NOT NULL,
            redundant_to_id  INTEGER REFERENCES nodes(id),
            semantic_notes   TEXT
        );

        CREATE TABLE IF NOT EXISTS meta_insights (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type         TEXT    NOT NULL,
            trigger_conditions   TEXT    NOT NULL,  -- JSON array
            recommended_strategy TEXT    NOT NULL,
            confidence           REAL    NOT NULL,
            supporting_nodes     TEXT    NOT NULL DEFAULT '[]',  -- JSON array de IDs
            counterexamples      TEXT    NOT NULL DEFAULT '[]',  -- JSON array de IDs
            domains              TEXT    NOT NULL DEFAULT '[]'   -- JSON array de strings
        );
        
        CREATE TABLE IF NOT EXISTS artifacts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id       INTEGER NOT NULL REFERENCES nodes(id),
            artifact_type TEXT    NOT NULL,
            file_path     TEXT    NOT NULL,
            metadata_json TEXT
        );

        CREATE TABLE IF NOT EXISTS structural_embeddings (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id            INTEGER,
            system_name        TEXT,
            lyapunov_max       REAL,
            spectral_entropy   REAL,
            dominant_frequency REAL,
            variance           REAL,
            autocorr_decay     REAL,
            kurtosis           REAL,
            skewness           REAL,
            energy             REAL,
            embedding_json     TEXT,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        CREATE TABLE IF NOT EXISTS generated_conjectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hypothesis_text TEXT,
            confidence_score REAL,
            supporting_systems TEXT,
            contradictory_systems TEXT,
            evidence_json TEXT,
            status TEXT DEFAULT 'provisional',
            generated_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def _drop_and_recreate(conn: sqlite3.Connection):
    """Borra y recrea todas las tablas. Usado por `init`."""
    conn.executescript("""
        DROP TABLE IF EXISTS artifacts;
        DROP TABLE IF EXISTS meta_insights;
        DROP TABLE IF EXISTS nodes;
        DROP TABLE IF EXISTS config;
    """)
    conn.commit()
    _create_schema(conn)


# ===========================================================================
# VISUALIZACION DEL ARBOL DE NODOS
# ===========================================================================

STATUS_ICON = {
    "SUCCESS": "[OK]",
    "ERROR": "[ER]",
    "TIMEOUT": "[TO]",
}


def _print_tree(conn: sqlite3.Connection):
    rows = conn.execute(
        "SELECT id, parent_id, framework_family, framework, status, cost_metric, redundancy_flag, redundant_to_id FROM nodes ORDER BY id"
    ).fetchall()

    problem_row = conn.execute(
        "SELECT value FROM config WHERE key='problem'"
    ).fetchone()

    # Obtener el conteo de artefactos por nodo
    artifacts_rows = conn.execute(
        "SELECT node_id, COUNT(*) as count FROM artifacts GROUP BY node_id"
    ).fetchall()
    artifacts_count = {r["node_id"]: r["count"] for r in artifacts_rows}

    SEP = "=" * 64
    print()
    print(SEP)
    print("  ARBOL DE INVESTIGACION  --  math_search.db")
    print(SEP)

    if problem_row:
        problem_text = textwrap.shorten(problem_row["value"], width=58)
        print(f"  Problema: {problem_text}")

    if not rows:
        print("  (sin nodos todavia)")
        print()
        return

    children: dict = {}
    for r in rows:
        pid = r["parent_id"]
        children.setdefault(pid, []).append(r)

    print()
    print(
        f"  {'ID':>4}  {'PARENT':>6}  {'STATUS':^9}  {'COST(s)':>7}  FRAMEWORK_FAMILY / FRAMEWORK / REDUNDANCY"
    )
    print(
        f"  {'----':>4}  {'------':>6}  {'---------':^9}  {'-------':>7}  {'--------------------------------------------------'}"
    )

    for r in rows:
        icon = STATUS_ICON.get(r["status"], "?")
        parent = str(r["parent_id"]) if r["parent_id"] is not None else "ROOT"

        red_str = ""
        if r["redundancy_flag"] == 1:
            red_str = f" [R -> Nodo {r['redundant_to_id']}]"

        print(
            f"  {r['id']:>4}  {parent:>6}  "
            f"{icon:<9}  "
            f"{r['cost_metric']:>6.2f}s  "
            f"{r['framework_family']} : {r['framework']}{red_str}"
        )

    print()
    print("  Jerarquia:")

    def _draw_node(node_id_or_none, prefix="  ", is_last=True):
        kids = children.get(node_id_or_none, [])
        for i, kid in enumerate(kids):
            last = i == len(kids) - 1
            branch = "`-" if last else "+-"
            icon = STATUS_ICON.get(kid["status"], "?")

            red_str = ""
            if kid["redundancy_flag"] == 1:
                red_str = f" [R -> Nodo {kid['redundant_to_id']}]"

            art_count = artifacts_count.get(kid["id"], 0)
            art_str = f" [+ {art_count} Artifacts]" if art_count > 0 else ""

            print(
                f"{prefix}{branch} [{kid['id']}] {icon} {kid['framework_family']} ({kid['framework']})  ({kid['status']}, {kid['cost_metric']:.2f}s){red_str}{art_str}"
            )
            next_prefix = prefix + ("   " if last else "|  ")
            _draw_node(kid["id"], next_prefix, last)

    _draw_node(None)
    print()


# ===========================================================================
# CMD: init
# ===========================================================================


def cmd_init(problema: str):
    conn = _get_connection()
    _drop_and_recreate(conn)
    conn.execute("INSERT INTO config (key, value) VALUES ('problem', ?)", (problema,))
    conn.commit()

    SEP = "=" * 64
    print()
    print(SEP)
    print("  EVALUATOR DB  --  INICIALIZADO (FASE 6A HIBRIDA)")
    print(SEP)
    print(f"  DB       : {DB_PATH}")
    print(f"  Problema : {problema}")
    print("  Tablas   : config, nodes, meta_insights, artifacts  ->  limpias y listas.")
    print()

    conn.close()


# ===========================================================================
# CMD: eval
# ===========================================================================


def cmd_eval(
    parent_id_str: str,
    framework_family: str,
    framework: str,
    filepath: str,
    notes: str,
    artifacts: list,
    signatures: list = None,
):
    # -- Resolver parent_id --
    parent_id = None
    if parent_id_str.upper() not in ("NONE", "NULL", "0", "ROOT"):
        try:
            parent_id = int(parent_id_str)
        except ValueError:
            print(
                f"[ERROR] parent_id debe ser entero o 'none'. Recibido: {parent_id_str!r}"
            )
            sys.exit(1)

    # -- Truncar semantic notes --
    semantic_notes = None
    if notes:
        semantic_notes = notes[:300]

    # -- Redundancy Sensor --
    conn = _get_connection()
    _create_schema(conn)

    redundancy_flag = 0
    redundant_to_id = None

    if parent_id is None:
        query = "SELECT id FROM nodes WHERE parent_id IS NULL AND framework_family = ?"
        cursor = conn.execute(query, (framework_family,))
    else:
        query = "SELECT id FROM nodes WHERE parent_id = ? AND framework_family = ?"
        cursor = conn.execute(query, (parent_id, framework_family))

    row = cursor.fetchone()
    if row:
        redundancy_flag = 1
        redundant_to_id = row["id"]

    # -- Leer el codigo fuente --
    abs_filepath = (
        filepath if os.path.isabs(filepath) else os.path.join(ROOT_DIR, filepath)
    )
    if not os.path.isfile(abs_filepath):
        print(f"[ERROR] Archivo no encontrado: {abs_filepath}")
        sys.exit(1)

    with open(abs_filepath, encoding="utf-8") as f:
        source_code = f.read()

    print()
    print(
        f"  [EVAL] family={framework_family!r}  framework={framework!r}  parent={parent_id}  file={filepath}"
    )
    if redundancy_flag == 1:
        print(f"  [WARN] Redundancia detectada con el Nodo {redundant_to_id}.")

    # -- Ejecutar en proceso hijo aislado --
    t0 = time.time()
    status = "ERROR"
    output = ""

    try:
        result = subprocess.run(
            [sys.executable, abs_filepath],
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT,
            cwd=ROOT_DIR,
        )
        elapsed = time.time() - t0

        if result.returncode == 0:
            status = "SUCCESS"
            output = result.stdout or "(sin salida en stdout)"
        else:
            status = "ERROR"
            parts = []
            if result.stdout:
                parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                parts.append(f"STDERR:\n{result.stderr}")
            output = (
                "\n".join(parts)
                if parts
                else f"(exit code {result.returncode}, sin output)"
            )

    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        status = "TIMEOUT"
        output = f"Proceso eliminado tras {EXEC_TIMEOUT}s sin respuesta."

    except Exception as exc:
        elapsed = time.time() - t0
        status = "ERROR"
        output = f"Excepcion al lanzar proceso: {exc}"

    cost_metric = round(elapsed, 4)

    # -- Persistir en DB --
    cursor = conn.execute(
        """
        INSERT INTO nodes (parent_id, framework_family, framework, code, output, status, cost_metric, redundancy_flag, redundant_to_id, semantic_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            parent_id,
            framework_family,
            framework,
            source_code,
            output,
            status,
            cost_metric,
            redundancy_flag,
            redundant_to_id,
            semantic_notes,
        ),
    )
    new_id = cursor.lastrowid

    # -- Insertar artefactos --
    if artifacts:
        for art in artifacts:
            parts = art.split("|", 1)
            if len(parts) == 2:
                art_type, art_path = parts
                conn.execute(
                    """
                    INSERT INTO artifacts (node_id, artifact_type, file_path, metadata_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (new_id, art_type, art_path, None),
                )
            else:
                print(f"[WARN] Formato de artefacto invalido (ignorando): {art}")

    # -- Ingestar Embeddings Estructurales (--signature) --
    embedding_fields = [
        "lyapunov_max",
        "spectral_entropy",
        "dominant_frequency",
        "variance",
        "autocorr_decay",
        "kurtosis",
        "skewness",
        "energy",
    ]
    if signatures and status == "SUCCESS":
        for sig_entry in signatures:
            sig_parts = sig_entry.split("|", 1)
            if len(sig_parts) != 2:
                print(f"[WARN] Formato de signature invalido (ignorando): {sig_entry}")
                continue
            sig_name, sig_path = sig_parts
            abs_sig = (
                sig_path
                if os.path.isabs(sig_path)
                else os.path.join(ROOT_DIR, sig_path)
            )
            if not os.path.isfile(abs_sig):
                print(f"[WARN] Archivo de signature no encontrado: {abs_sig}")
                continue
            try:
                with open(abs_sig, encoding="utf-8") as sf:
                    sig_data = json.load(sf)
                vals = [sig_data.get(f) for f in embedding_fields]
                conn.execute(
                    """
                    INSERT INTO structural_embeddings
                        (node_id, system_name, lyapunov_max, spectral_entropy,
                         dominant_frequency, variance, autocorr_decay, kurtosis,
                         skewness, energy, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (new_id, sig_name, *vals, json.dumps(sig_data, ensure_ascii=False)),
                )
                print(
                    f"  [EMB] Embedding ingestado para '{sig_name}' (node_id={new_id})"
                )
            except Exception as exc:
                print(f"[WARN] Error al ingestar signature '{sig_name}': {exc}")
    conn.commit()

    # -- Resumen en consola --
    icon = STATUS_ICON.get(status, "?")
    red_str = f" [Redundant -> {redundant_to_id}]" if redundancy_flag == 1 else ""

    art_count_str = f" [+ {len(artifacts)} Artifacts]" if artifacts else ""

    print(f"  {icon} [{new_id}] {status}  ({cost_metric:.2f}s){red_str}{art_count_str}")

    if semantic_notes:
        print(f"  * Notas Semanticas: {semantic_notes}")

    lines = output.splitlines()
    preview = lines[:10]
    for line in preview:
        print(f"       | {line}")
    if len(lines) > 10:
        print(f"       | ... ({len(lines) - 10} lineas mas)")

    # -- Imprimir arbol completo --
    _print_tree(conn)
    conn.close()


# ===========================================================================
# CMD: add_insight  (Fase 5B)
# ===========================================================================

INSIGHT_FIELDS = {
    "pattern_type": str,
    "trigger_conditions": (list, str),  # acepta lista o string JSON
    "recommended_strategy": str,
    "confidence": float,
    "supporting_nodes": (list, str),
    "counterexamples": (list, str),
    "domains": (list, str),
}


def _coerce_json_field(value, field_name: str) -> str:
    """Convierte listas Python o strings JSON a string JSON normalizado."""
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            print(f"[ERROR] El campo '{field_name}' no es JSON valido: {value!r}")
            sys.exit(1)
    # Si es otro tipo escalar, envuelve en lista
    return json.dumps([value], ensure_ascii=False)


def cmd_add_insight(json_string: str):
    """Inserta una nueva regla heuristica en meta_insights."""
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] JSON invalido: {exc}")
        sys.exit(1)

    # Validar campos obligatorios
    required = [
        "pattern_type",
        "trigger_conditions",
        "recommended_strategy",
        "confidence",
    ]
    for field in required:
        if field not in data:
            print(f"[ERROR] Campo obligatorio ausente: '{field}'")
            sys.exit(1)

    # Normalizar campos JSON
    trigger_conditions = _coerce_json_field(
        data.get("trigger_conditions", []), "trigger_conditions"
    )
    supporting_nodes = _coerce_json_field(
        data.get("supporting_nodes", []), "supporting_nodes"
    )
    counterexamples = _coerce_json_field(
        data.get("counterexamples", []), "counterexamples"
    )
    domains = _coerce_json_field(data.get("domains", []), "domains")

    confidence = float(data["confidence"])
    if not (0.0 <= confidence <= 1.0):
        print(
            f"[WARN] confidence={confidence} esta fuera del rango [0,1]. Se permite, pero revisa."
        )

    conn = _get_connection()
    _create_schema(conn)

    cursor = conn.execute(
        """
        INSERT INTO meta_insights
            (pattern_type, trigger_conditions, recommended_strategy,
             confidence, supporting_nodes, counterexamples, domains)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(data["pattern_type"]),
            trigger_conditions,
            str(data["recommended_strategy"]),
            confidence,
            supporting_nodes,
            counterexamples,
            domains,
        ),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    SEP = "=" * 64
    print()
    print(SEP)
    print(f"  META-INSIGHT INSERTADO  --  ID={new_id}")
    print(SEP)
    print(f"  pattern_type         : {data['pattern_type']}")
    print(f"  recommended_strategy : {data['recommended_strategy']}")
    print(f"  confidence           : {confidence:.2f}")
    print(f"  trigger_conditions   : {trigger_conditions}")
    print(f"  domains              : {domains}")
    print(f"  supporting_nodes     : {supporting_nodes}")
    print(f"  counterexamples      : {counterexamples}")
    print()


# ===========================================================================
# CMD: read_insights  (Fase 5B)
# ===========================================================================


def cmd_read_insights(domain: str | None):
    """Consulta meta_insights y los imprime como JSON legible."""
    conn = _get_connection()
    _create_schema(conn)

    if domain:
        # Buscar dominio como elemento dentro del JSON array
        rows = conn.execute(
            "SELECT * FROM meta_insights WHERE domains LIKE ?", (f'%"{domain}"%',)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM meta_insights ORDER BY confidence DESC"
        ).fetchall()

    conn.close()

    SEP = "=" * 64
    print()
    print(SEP)
    title = f"  META-INSIGHTS  --  {'dominio: ' + domain if domain else 'todos'}"
    print(title)
    print(SEP)

    if not rows:
        print("  (sin reglas heuristicas almacenadas)")
        print()
        return

    print(f"  Total encontrados: {len(rows)}")
    print()

    insights = []
    for r in rows:
        entry = {
            "id": r["id"],
            "pattern_type": r["pattern_type"],
            "trigger_conditions": json.loads(r["trigger_conditions"]),
            "recommended_strategy": r["recommended_strategy"],
            "confidence": r["confidence"],
            "supporting_nodes": json.loads(r["supporting_nodes"]),
            "counterexamples": json.loads(r["counterexamples"]),
            "domains": json.loads(r["domains"]),
        }
        insights.append(entry)

    # Imprimir JSON bonito y legible
    print(json.dumps(insights, indent=2, ensure_ascii=False))
    print()


# ===========================================================================
# ENTRY POINT
# ===========================================================================


def main():
    parser = argparse.ArgumentParser(
        prog="evaluator_db.py",
        description="Herramienta de memoria local HIBRIDA para investigacion matematica (Fase 6A).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- Sub-comando: init --
    p_init = subparsers.add_parser(
        "init", help="Inicializa (o reinicia) la base de datos."
    )
    p_init.add_argument(
        "problema", type=str, help="Descripcion del problema de investigacion."
    )

    # -- Sub-comando: eval --
    p_eval = subparsers.add_parser(
        "eval", help="Evalua un script Python y registra el resultado."
    )
    p_eval.add_argument(
        "parent_id", type=str, help="ID del nodo padre o 'none'/'root'."
    )
    p_eval.add_argument(
        "framework_family", type=str, help="Familia del framework (e.g. SYMBOLIC)."
    )
    p_eval.add_argument(
        "framework", type=str, help="Framework especifico (e.g. sympy)."
    )
    p_eval.add_argument("filepath", type=str, help="Ruta al archivo .py a ejecutar.")
    p_eval.add_argument(
        "--notes", type=str, default="", help="Notas semanticas (max 300 chars)."
    )
    p_eval.add_argument(
        "--artifact",
        type=str,
        action="append",
        help="Vincula un artefacto en formato 'tipo|ruta'",
    )
    p_eval.add_argument(
        "--signature",
        type=str,
        action="append",
        help="Ingestión de embedding en formato 'system_name|ruta/al/json'",
    )

    # -- Sub-comando: read_insights (Fase 5B) --
    p_read = subparsers.add_parser(
        "read_insights", help="Muestra las leyes heuristicas almacenadas."
    )
    p_read.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Filtrar por dominio matematico (opcional).",
    )

    # -- Sub-comando: add_insight (Fase 5B) --
    p_add = subparsers.add_parser(
        "add_insight", help="Inserta una nueva regla heuristica en JSON."
    )
    p_add.add_argument(
        "json_string",
        type=str,
        help="String JSON con los campos de meta_insights (sin 'id').",
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.problema)
    elif args.command == "eval":
        cmd_eval(
            args.parent_id,
            args.framework_family,
            args.framework,
            args.filepath,
            args.notes,
            args.artifact,
            args.signature,
        )
    elif args.command == "read_insights":
        cmd_read_insights(args.domain)
    elif args.command == "add_insight":
        cmd_add_insight(args.json_string)


if __name__ == "__main__":
    main()
